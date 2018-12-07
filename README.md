Welcome to the HUDS calorie tracker! This is a web app that scrapes daily nutritional information from the university dining website and allows its users to track these meals. 

1. HOW TO USE THE WEBSITE 

Using the app is easy. On the app homepage, there are two options to register and login. Once you register, your login credentials will be stored in a database, and you can use the same credentials to log in again. Once logged in, there are three options: track calories, view history, and Myfitnesspal. 

On the track calories page, simply select either lunch or dinner on the select menu, and a menu of your selection will pop up. The hot entrees and sides from today's dinner will pop up, as well as the nutritional information for each food item. You can also see your food intake for the day below in order to see how many calories you have already eaten. When you want to track a food, click the blue submit button, and your food will be recorded in a database. 

On the history page, a select menu drops down to show all of the days that you have tracked food. Select a date and a table will pop up that shows all of the foods eaten on that day. 

Lastly, the MyFitnessPal tab lets you track foods that are not HUDS foods. Simply type in a food and click the blue search button. An automated web browser will search the MyFitnessPal website and display its results. Afterwards, choose a food by selecting a radio button and then submit the food to add it to your history. 

2. HOW TO COMPILE 
At the moment, this app can only be run from a local machine. 
    1. Open the project in a local IDE.
    2. Install all the dependencies onto your virtual environment: BeautifulSoup, urllib, cs50, flask, flask_session, tempfile, werzeug exceptions, werzeug.security, datetime, and selenium. 
    3. In Python 3.7, export the flask app by inputting the following command into the terminal: "export FLASK_APP=app.py" 
    4. Execute "flask run" in the terminal.  
    5. Open the link that the terminal outputs to access the website!

3. How to install a webdriver used to search the MyFitnessPal website. 

*NOTE* A webdriver must be installed in order for the app to open a browser, query the MyFitnessPal database, and retrieve nutritional information for foods not on the HUDS website *NOTE* 

    1. Download and install a version of the google chrome browser. 
    2. Download the "chromedriver" file onto your local machine. 
    3. Navigate to the file, titled "chromedriver," right click the file and copy the path to the file to the clipboard. 
    4. Navigate to line 165 in app.py. 
    5. Paste the file path after "executable_path" and save the file. 
    6. You are now ready to run the app! 



# HUDS
