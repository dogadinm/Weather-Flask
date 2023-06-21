from flask import Flask, flash, redirect, render_template, request, session
import requests
from datetime import datetime, timezone
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import apology, login_required



# Configure application
app = Flask(__name__)



db = SQL("sqlite:///city.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# If user logged in, append all city in list which saved by user
def data_info():
    if "user_id" in session :
        info = db.execute("SELECT city FROM city WHERE user_id = ?", session["user_id"])
        all_cities = []
        for i in info:
            all_cities.append(i['city'])

        return all_cities

# Getting weather data
def weather_data(city):
    # Api, enter your api if you want
    api = 'your api'

    # Weather api for wearther now and forecats
    url_now = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric'
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api}&units=metric'

    response_now = requests.get(url_now).json()
    response = requests.get(url).json()

    print(response_now)

    weather_data = {}
    weather_data_now = {}

    # List of all cities
    all_cities = data_info()

    # Skip if user put wrong city
    try:
        # Looping through the data from api for forecast
        for data in response['list']:
            timestamp = data['dt']
            dt_object = datetime.fromtimestamp(timestamp, timezone.utc)
            date = dt_object.strftime("%A, %B %d")
            time = dt_object.strftime("%H:%M")
            description = data['weather'][0]['description']
            icon = data['weather'][0]['icon']
            temperature_celsius = int(f"{data['main']['temp']:.0f}")
            temperature_fahrenheit = round(temperature_celsius * 9/5 + 32, 2)
            temperature_kelvin = round(temperature_celsius + 273.15, 2)

            # Append data in library where key is date
            if date not in weather_data:
                weather_data[date] = []

            weather_data[date].append({
                'time': time,
                'description': description,
                'icon': icon,
                'temperature_celsius': temperature_celsius,
                'temperature_fahrenheit': temperature_fahrenheit,
                'temperature_kelvin': temperature_kelvin
            })


        # Add date of weather now to dictionary
        name_city = response_now['name']
        description = response_now['weather'][0]['description']
        icon = response_now['weather'][0]['icon']
        feels_like = f"{response_now['main']['feels_like']:.0f}"
        temperature_celsius = int(f"{response_now['main']['temp']:.0f}")
        temperature_fahrenheit = round(temperature_celsius * 9/5 + 32, 2)
        temperature_kelvin = round(temperature_celsius + 273.15, 2)

        weather_data_now ={

                "date": date,
                "description": description,
                "icon": icon,
                "temperature_celsius": temperature_celsius,
                "feels_like": feels_like,
                "temperature_fahrenheit": temperature_fahrenheit,
                "temperature_kelvin": temperature_kelvin
        }
        # If user login or not
        if "user_id" in session :
            return render_template('index.html', city = city.capitalize() ,name_city = name_city, weather_data = weather_data, weather_data_now = weather_data_now, all_cities = all_cities)
        else:
            return render_template('index.html', city = city.capitalize() ,name_city = name_city, weather_data = weather_data, weather_data_now = weather_data_now)

    except KeyError:
         if "user_id" in session :
            return render_template('index.html', massage = "I coudn't find this city:", wrong_city = city, all_cities = all_cities)
         else:
             return render_template('index.html', massage = "I coudn't find this city:", wrong_city = city)



@app.route('/', methods=['GET', 'POST'])
def index():

    # For serach weather
    if request.method == 'POST' and 'city' in request.form:
        city = request.form['city']
        return weather_data(city)

    # For add city in db and stay on the page
    elif request.method == 'POST' and 'add' in request.form:
        city = request.form['add']
        user_id = session["user_id"]

        # Check if city already in db
        if len(db.execute("SELECT city FROM city WHERE user_id = ? AND city = ?",user_id, city)) == 0:
            db.execute("INSERT INTO city (city, user_id) VALUES(?, ?)", city, user_id)

        return weather_data(city)

    # Delet city in db and stay on the page
    elif request.method == 'POST' and 'delete_city' and 'stay_city'in request.form:
        delete_city = request.form['delete_city']
        city = request.form['stay_city']

        db.execute("DELETE FROM city WHERE user_id = ? AND city = ?", session["user_id"], delete_city)
        return weather_data(city)

    # If user login or not
    else:
        if "user_id" in session :
            all_cities = data_info()
            return render_template('index.html', all_cities = all_cities)
        else:
            return render_template('index.html')






@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # To get data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Checking for the same password
        if password != confirmation:
            return apology('Passwords are not the same', 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?;", username)

        # Check if user already exists
        if len(rows) != 0:
            return apology('Username already exists', 403)

        # Generate hash key
        hash = generate_password_hash(password)

        # Add new user in db
        new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        session["user_id"] = new_user

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        # To get data
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        user_id = session["user_id"]

        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        # Check existing password
        if not check_password_hash(rows[0]["hash"], current_password):
            return apology("Wrong current password", 403)

        # Checking for the same password
        elif new_password != confirmation:
            return apology('Passwords are not the same', 403)

        # Checking old password and new
        elif current_password == new_password:
            return apology('The new password cannot be the same as the old password.', 403)

        # Generate hash key
        hash = generate_password_hash(new_password)

        # Update password in db
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, user_id)

        session.clear()

        return redirect("/")

    else:
        return render_template("password.html")



if __name__ == '__main__':
    app.run(debug=True)
