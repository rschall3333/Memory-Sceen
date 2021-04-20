# !/usr/bin/env python
#
# GrovePi Example for using the Grove Temperature & Humidity Sensor Pro 
# (http://www.seeedstudio.com/wiki/Grove_-_Temperature_and_Humidity_Sensor_Pro)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  
# You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#
'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import grovepi
import math
import json
import time
import ftplib
import mysql.connector
from datetime import datetime
from grove_rgb_lcd import *

# Configuration JSON
with open('/home/pi/Dexter/GrovePi/Software/Python/configuration.json') as f:
    configuration = json.load(f)

# Connect the Grove Temperature & Humidity Sensor Pro to digital port
temperature_humidity_sensor_port = configuration["temperature humidity sensor"]["port"]
temperature_humidity_sensor_type = configuration["temperature humidity sensor"]["type"]
read_index = 0

# Buffer for JSON output data
weather_data = [[0, 0, 0]]

# Offsets for temperature and humidity
temp_offset = configuration["offsets"]["temperature"]
humidity_offset = configuration["offsets"]["humidity"]

# Configuration for the green output LED
green_led_port = configuration["output LEDs"]["green"]["port"]
green_led_min_temp = configuration["output LEDs"]["green"]["min temp"]
green_led_max_temp = configuration["output LEDs"]["green"]["max temp"]
green_led_humidity_max = configuration["output LEDs"]["green"]["max humidity"]

# Configuration for the red output LED
red_led_port = configuration["output LEDs"]["red"]["port"]
red_led_min_temp = configuration["output LEDs"]["red"]["min temp"]

# Configuration for the blue output LED
blue_led_port = configuration["output LEDs"]["blue"]["port"]
blue_led_min_temp = configuration["output LEDs"]["blue"]["min temp"]
blue_led_max_temp = configuration["output LEDs"]["blue"]["max temp"]
blue_led_humidity_max = configuration["output LEDs"]["blue"]["max humidity"]

# Time restrictions
read_hour_start = configuration["reading window and frequency"]["hour start"]
read_hour_stop = configuration["reading window and frequency"]["hour stop"]
read_frequency = configuration["reading window and frequency"]["frequency"]

# Colors for LCD backcolor
color_red = (configuration["colors"]["red"]["red hex"],
             configuration["colors"]["red"]["green hex"],
             configuration["colors"]["red"]["blue hex"])
color_green = (configuration["colors"]["green"]["red hex"],
               configuration["colors"]["green"]["green hex"],
               configuration["colors"]["green"]["blue hex"])
color_blue = (configuration["colors"]["blue"]["red hex"],
              configuration["colors"]["blue"]["green hex"],
              configuration["colors"]["blue"]["blue hex"])

# Buffer to hold temperature statistics: (min, max, average)
temperature_statistics = (300.0, 0.0, 0.0)
temperature_buffer = []

# Buffer to hold humidity statistics: (min, max, average)
humidity_statistics = (300.0, 0.0, 0.0)
humidity_buffer = []


# Create a class for the MySQL (MariaDB)
class Server:
    def __init__(self, host, user,
                 password, database,
                 city_, state_, zipcode_,
                 temperature_, humidity_,
                 date_time_):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.city_ = city_
        self.state = state_
        self.zipcode_ = zipcode_
        self.temperature_ = temperature_
        self.humidity_ = humidity_,
        self.date_time_ = date_time_

    # Routine for writing data to MySQL
    def write_to_sql(self):
        # connect to MySQL (mariaDB) database
        my_db = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        # Create a cursor
        my_cursor = my_db.cursor()

        # Create SQL statement
        sql = "INSERT INTO temperature_humidity(city, state, zipcode, " \
              "temperature, humidity, date_time) " \
              "VALUES (%s, %s, %s, %s, %s, %s)"
        # Insert values
        val = (self.city_, self.state,
               self.zipcode_, float(self.temperature_),
               float(humidity), self.date_time_)

        # Execute SQL
        my_cursor.execute(sql, val)

        # Commit changes
        my_db.commit()

        # Print confirmation
        print(my_cursor.rowcount, " record inserted.")

        # Disconnect
        my_db.close()


# Function for resetting LEDs to OFF
def reset_led():
    grovepi.digitalWrite(green_led_port, 0)
    grovepi.digitalWrite(blue_led_port, 0)
    grovepi.digitalWrite(red_led_port, 0)


# Function for updating the LCD message and color
def set_lcd(message, color):
    # Set message
    setText(message)

    # Set LCD backcolor
    setRGB(color[0], color[1], color[2])


# Algorithm for converting Celsius to Fahrenheit
def celsius_to_fahrenheit(temperature_in_celsius, temperature_offset):
    freezing_point = 32.0
    rate_change = 1.8

    # conversion
    return ((temperature_in_celsius * rate_change) + freezing_point) + temperature_offset


# Algorithm for adding temperature data to a list and then displaying the min, max, and average
def update_temperature_statistics(temperature, temperature_stats_previous):
    minimum_temperature = temperature_stats_previous[0]
    maximum_temperature = temperature_stats_previous[1]
    average_temperature = 0.0

    # Insert new temperature into the temperature buffer
    temperature_buffer.insert(0, temperature)

    # Pop last temperature off list if list is greater than or equal to 10
    if len(temperature_buffer) >= 11:
        temperature_buffer.pop()

    # Update minimum temperature if less than previous
    if temperature < minimum_temperature:
        minimum_temperature = temperature

    # Update maximum temperature if greater than previous
    if temperature > maximum_temperature:
        maximum_temperature = temperature

    # Compute new average
    average_temperature = sum(temperature_buffer) / len(temperature_buffer)

    return_data = (minimum_temperature, maximum_temperature, average_temperature)

    return return_data


# Algorithm for adding humidity data to a list and then displaying the min, max, and average
def update_humidity_statistics(humidity_, humidity_stats_previous):
    minimum_humidity = humidity_stats_previous[0]
    maximum_humidity = humidity_stats_previous[1]
    average_humidity = 0.0

    # Insert new humidity into the humidity buffer
    humidity_buffer.insert(0, humidity_)

    # Pop last humidity off list if list is greater than or equal to 10
    if len(humidity_buffer) >= 11:
        humidity_buffer.pop()

    # Update minimum humidity if less than previous
    if humidity_ < minimum_humidity:
        minimum_humidity = humidity_

    # Update maximum humidity if greater than previous
    if humidity_ > maximum_humidity:
        maximum_humidity = humidity_

    # Compute new average
    average_humidity = sum(humidity_buffer) / len(humidity_buffer)

    return_data = (minimum_humidity, maximum_humidity, average_humidity)

    return return_data


# Set output LED port assignments
grovepi.pinMode(red_led_port, "OUTPUT")
grovepi.pinMode(green_led_port, "OUTPUT")
grovepi.pinMode(blue_led_port, "OUTPUT")

# Main control routine
while True:
    try:
        # Reset LEDs
        reset_led()

        # Check that the time falls inside the measurement range, if not continue to next iteration
        date_time_now = datetime.now()

        # if the time is outside the range for measurement, send error messages.
        if (date_time_now.hour < read_hour_start) or (date_time_now.hour >= read_hour_stop):
            time.sleep(10.0)

            # Update shell
            print("Outside the range for recording weather.")

            # Write results to LCD, change color to red
            set_lcd("Outside range\nfor recording!", color_red)

            continue

        # The first parameter is the port, the second parameter is the type of sensor.
        [temp, humidity] = grovepi.dht(temperature_humidity_sensor_port, temperature_humidity_sensor_type)

        if math.isnan(temp) == False and math.isnan(humidity) == False:
            read_index += 1

            # Convert from Celsius to Fahrenheit
            # temp_F = (temp * 1.8 + 32) + temp_offset
            temp_F = celsius_to_fahrenheit(temp, temp_offset)
            humidity += humidity_offset

            # Test statistics
            temperature_statistics = update_temperature_statistics(temp_F, temperature_statistics)

            # Humidity statistics
            humidity_statistics = update_humidity_statistics(humidity, humidity_statistics)

            # Reset LEDs
            reset_led()

            # print datetime
            date_time_now = datetime.now()
            print(date_time_now)

            # Print temperature and humidity
            print("temp = %.02f F humidity = %.02f%%" % (temp_F, humidity))

            # print temperature statistics
            print("temperature min = %.02f, temperature max = %.02f, temperature avg = %.02f"
                  % (temperature_statistics[0], temperature_statistics[1], temperature_statistics[2]))

            # print humidity statistics
            print("humidity min = %.02f, humidity max = %.02f, humidity avg = %.02f"
                  % (humidity_statistics[0], humidity_statistics[1], humidity_statistics[2]))

            # Turn on green LED if in range
            if ((temp_F > green_led_min_temp)
                    and (temp_F <= green_led_max_temp)
                    and (humidity < green_led_humidity_max)):
                grovepi.digitalWrite(green_led_port, 1)

            # Turn on blue LED if in range
            if ((temp_F > blue_led_min_temp)
                    and (temp_F <= blue_led_max_temp)
                    and (humidity < blue_led_humidity_max)):
                grovepi.digitalWrite(blue_led_port, 1)

            # Turn on red LED if in range
            if temp_F > red_led_min_temp:
                grovepi.digitalWrite(red_led_port, 1)

            # Append weather data list with latest data
            weather_data.append([read_index, temp_F, humidity])

            # Update json file with latest weather data
            with open('output_data.json', 'w') as outfile:
                json.dump(weather_data, outfile)

            # Create server server object
            mariaDB_server = Server(configuration["Server"]["host"],
                                    configuration["Server"]["user"],
                                    configuration["Server"]["password"],
                                    configuration["Server"]["database"],
                                    configuration["Server Data"]["city"],
                                    configuration["Server Data"]["state"],
                                    configuration["Server Data"]["zipcode"],
                                    temp_F,
                                    humidity,
                                    date_time_now)

            # Write data to server
            mariaDB_server.write_to_sql()

            # Update LCD
            set_lcd("temp = %.02f F\nhumidity = %.02f%%" % (temp_F, humidity), color_blue)

            # Copy json file to dashboard Windows PC via ftp
            ftpSession = ftplib.FTP('172.30.82.237', 'NSNA/rschall', 'th@tslikeyoUropinionman')
            file = open('/home/pi/Dexter/GrovePi/Software/Python/output_data.json', 'rb')
            ftpSession.storbinary('STOR output_data.json', file)  # send the file
            file.close()  # close file
            ftpSession.quit()  # close ftp session

            # read frequency
            time.sleep(read_frequency)
    except IOError:
        print("Error")
