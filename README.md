# memoryscreen

Briefly summarize the requirements and goals of the app you developed. What user needs was this app designed to address?

ANSWER: The inventory tracking app must include a login screen and the functionality for adding a new user. The user must be added to a SQLite database in a separate table from the inventory table. The password text box must hide the characters as the user types them
     The app must have a separate table for adding inventory items. The items must be maintained through re-laoding the applications and device. The user must be ba able to add, remove, and delete inventory entries. The inventory must be able to be viewed in a table format.
     The app must ask the user for SMS Messaging permission. SMS messaging could be used to notify the user of consitions like low inventory.
     The application must adhere to ANdorid design standards.


What screens and features were necessary to support user needs and produce a user-centered UI for the app? How did your UI designs keep users in mind? Why were your designs successful?

ANSWER: The first screen displayed to the user is the login screen where the user enters user name and passowrd. There is also a button and subsequent user screen for adding a new user. The new user screen has field for user name, passowrd, first name, and last name. 
       Off the login screen is the incventory screen that has buttons for looking up/modifying an inventory item, a button for adding an inventory item, and a button for displaying all inventory items.
       The item look-up/modify screen has a field for the item name and a find button underneath that. The user types in the iten name and clicks find. The fields for item description and quantity are populated after the item is found. The user can modify the fields and click the 'UPDATE' button or click the 'DELETE' button to delet the item. The user can also take no action and go back to the main screen by clicking 'CANCEL'
       The ADD button on the main screen takes the user to another activity where there are fields for item name, description, and quantity. The user populates the fields and clicks 'SAVE' to add the new inventory item to the inventory table. There is a 'CANCEL' button to go back to the main screen. 
       The display all button takes the user to the tbale view of all the inventory items entered. 
       The screens available give the user access to all the necessary functionality. The desing of the app was kept very simple to ease the use of the app.

How did you approach the process of coding your app? What techniques or strategies did you use? How could those be applied in the future?

ANSWER: The UI screens were designed first which servered as a framework for the requirements of the app. The next step was to develop the code for the SQLite database and tables. After the SQLite infrastructure was created attention was turned back to the UI screens and filling in the code behind the fields and buttons using the Database code created. I think designing the user invterface first or the View portion of MVC proved effective. I think this is a good technique that I could utilize in the future. 

How did you test to ensure your code was functional? Why is this process important and what did it reveal?

ANSWER: I performed functional testing of the application throughout development. I also performed UI testing, checking each Edit Text and button for functionality throughout the application.

Considering the full app design and development process, from initial planning to finalization, where did you have to innovate to overcome a challenge?

ANSWER: I had to innovate to fulfill the requirements. that innovation involved a lot of trial and error for small features like when the use clicks a text fiels the default text clears the field before the user edits the field. I at first used the 'onClick' feature of the button but this prooved clunky because the user had to click an additional time once the user gave the field focus. I ended up using the 'onFocus' event to clear the field. 

In what specific component from your mobile app were you particularly successful in demonstrating your knowledge, skills, and experience?

ANSWER: I think the specific component I demonstrated knowledge on was the use of SQLite in creating the database. Databases are such crucual components of applications. I think I was able to create a basic databse that performed every function the app required. 
