from bs4 import BeautifulSoup
import urllib.request
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import requests
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
app.config['TESTING'] = False


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("postgres://skvwytewzhwhif:f3cd2c31d95c338549255545c0ecc13ecaff46a8ff0100b8bc4aad5f953da7ee@ec2-54-204-40-248.compute-1.amazonaws.com:5432/d2b9rvmmb9q621")
db = SQL("sqlite:///finance.db")


lunch = []
dinner = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/track")
@login_required
def track():
    def load_foods(link, meal):
        # Check if nutrition info already loaded
        if not meal in session:
            # Function to identify the calories, carbs, fat, and protein
            def value_for(soup, keyword):
                info = soup.find("b", string=keyword)
                try:
                    return ((str(info.next_sibling)).replace("g", "")).strip()
                except:
                    return "no value found"
            # Load HUDS link into a variable
            url = link
            content = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(content, features="lxml")
            # Store all menu items in a variable
            titles = soup.find_all(class_="item_wrap")
            # Create an array for an item and an array for the link to the item
            items = []
            links = []
            for item in titles:
                items.append(((str(item.text)).replace("|", "")).strip())
                links.append(item.a.get('href'))

            # List to store each item's nutrition info. Create counter to iterate through titles
            i = 0
            Nutrition_info = []
            for item in links:
                # Open link to food items
                url = item
                content = urllib.request.urlopen(url).read()
                soup = BeautifulSoup(content, features="lxml")
                # Store nutrition info in a dict
                indiv_nutrition = {}
                indiv_nutrition['title'] = items[i]
                indiv_nutrition['serving_size'] = (value_for(soup, "Serving Size:")).replace(u'\xa0', u' ')
                indiv_nutrition['calories'] = value_for(soup, "Calories:")
                indiv_nutrition['fat'] = value_for(soup, "Total Fat:")
                indiv_nutrition['carbs'] = value_for(soup, "Total Carbs:")
                indiv_nutrition['protein'] = value_for(soup, "Protein:")
                # Append the nutrition info of each item to a list
                Nutrition_info.append(indiv_nutrition)
                i = i + 1
            # Load nutrition info into session data, so we don't have to reload
            session[meal] = Nutrition_info
        return session[meal]

    # Use global to change variable outside function
    global lunch
    global dinner
    # Links to HUDS menu of foods
    lunch = load_foods("http://www.foodpro.huds.harvard.edu/foodpro/menu_items.asp?type=30&meal=1", "lunch")
    dinner = load_foods("http://www.foodpro.huds.harvard.edu/foodpro/menu_items.asp?type=30&meal=2", "dinner")

    # Select sum today's calories, carbs, fat, etc. to display at the bottom of page
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    sum = db.execute("SELECT SUM(calories), SUM(fat), SUM(carbs), SUM(protein) FROM food WHERE user_id=:user_id AND date=:date", user_id=session["user_id"], date=date)[0]
    print(sum)
    return render_template("track.html", lunch=lunch, dinner=dinner, sum=sum)

# Insert food into the table


def insert(meal, counter, serving_size):
    # Retrieve the nutritional info by indexing into a global variable of meals
    food = meal[counter]['title']
    calories = float(meal[counter]['calories'])*serving_size
    fat = float(meal[counter]['fat'])*serving_size
    carbs = float(meal[counter]['carbs'])*serving_size
    protein = float(meal[counter]['protein'])*serving_size
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO food (food,calories,fat,carbs,protein,user_id,date) VALUES(:food,:calories,:fat,:carbs,:protein,:user_id,:date)", food=food, calories=calories, fat=fat, carbs=carbs, protein=protein, user_id=session['user_id'], date=date)

# If user inputted lunch, call function that inserts food into database


@app.route("/lunch", methods=["POST"])
@login_required
def insert_lunch():
    # returns the food item number that the user submits
    counter = int(request.form.get("food")) - 1
    serving_size = float(request.form.get("serving_size"))
    insert(lunch, counter, serving_size)
    return redirect('/track')


# If user submits dinner, insert


@app.route("/dinner", methods=["POST"])
@login_required
def table():
    # returns the food item number
    counter = int(request.form.get("food")) - 1
    serving_size = float(request.form.get("serving_size"))
    insert(dinner, counter, serving_size)
    return redirect('/track')


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    # Select users' food log distinct dates
    dates = db.execute("SELECT DISTINCT date FROM food WHERE user_id=:user_id", user_id=session['user_id'])
    if request.method == "POST":
        # If date submitted, then retrieve food items on that date
        history_date = request.form.get("history_date")
        food_history = db.execute("SELECT food, calories, fat, carbs, protein FROM food WHERE user_id=:user_id AND date=:date",user_id=session['user_id'], date=history_date)
        sum = db.execute("SELECT SUM(calories),SUM(fat),SUM(carbs),SUM(protein) FROM food WHERE user_id=:user_id AND date=:date",user_id=session['user_id'], date=history_date)[0]
        return render_template("history.html", dates=dates, history=food_history, sum=sum)
    return render_template("history.html", dates=dates)


# Define global variable food to acccess when inserting food into database


@app.route("/mfp", methods=["GET", "POST"])
@login_required
def mfp():
    # If food has been submitted, then query the Myfitnesspal website
    if request.method == "POST":
        if request.form.get("query"):
            query = request.form.get("query")
            # Selenium webdriver to submit user food request to myfitnesspal, change executable path to path of webdriver
            FormData={
            'search':query,
            'commit':'search',
            'authenticity_token':'QrlBkUY0PIGkfC/QXemwtqMK8+QNMcC4/j2iPR2xE5s='
            }
            s = requests.Session()
            html = s.post("https://www.myfitnesspal.com/food/search",data=FormData)
            soup = BeautifulSoup(html.text, features="lxml")
            food = []
            # Make an array an add all of the titles of the food names
            titles = []
            for iteration, item in enumerate(soup.find_all(class_="brand")):
                titles.append(item.get_text())

            # Returns a list of each food's nutritional info
            nutrition = soup.find_all(class_="nutritional_info")
            # Iterate through each food in the list and extract and beautify calories, fat, etc.
            for iteration, item in enumerate(nutrition):
                item_info = {}
                item_info['serving_size'] = (item.find("label", string="Serving Size: ")).next_sibling.replace(",", "").strip()
                item_info['calories'] = (item.find("label", string="Calories: ")).next_sibling.replace(",", "").strip()
                item_info['fat'] = (item.find("label", string="Fat: ")).next_sibling.replace("g,", "").strip()
                item_info['protein'] = (item.find("label", string="Protein: ")).next_sibling.replace("g", "").strip()
                item_info['carbs'] = (item.find("label", string="Carbs: ")).next_sibling.replace("g,", "").strip()
                item_info['item_number'] = iteration
                item_info['title'] = titles[iteration]
                # Add the nutritional info dictionary to the list of foods
                food.append(item_info)
            session['food'] = food
            return render_template("mfp.html", food=food)
        elif request.form.get("mfp_index"):
            counter = int(request.form.get("mfp_index"))
            serving_size = float(request.form.get("serving_size"))
            insert(session['food'],counter,serving_size)
    return render_template("mfp.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Get username
    username = request.args.get("username")

    # Check for username
    if not len(username) or db.execute("SELECT 1 FROM users WHERE username = :username", username=username.lower()):
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # Add user to database
        id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                        username=request.form.get("username"),
                        hash=generate_password_hash(request.form.get("password")))
        if not id:
            return apology("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
