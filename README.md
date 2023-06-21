# Weather
# Video Demo:
Youtube - https://www.youtube.com/watch?v=4XP1nsJZ8eQ

## CS50
>This is my final project for the CS50 Introduction to Computer Sciense.

>CS, python, flask, flask web framework, web development, CS50


## Features
- [SQLite](https://www.sqlite.org/index.html)
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)

I used the Flask web framework based in Python for crerating web site and SQLite for database.


# Importing libraries
- flask
- requests
- datetime
- flask_session
- werkzeug.security
- cs50


# Explaining the project and the database
My final project is a web site based on Flask. The main idea of the site is to find out the weather in a certain city.
The site shows the weather at the moment and for a period of 6 days
also describe the weather conditions (for example: rain).

The site can save and delete the cities that the user wanted to add to the quick search.



# SQLite3 and schema
There are two tables in city.db: users and city.

Three columns in the 'users' table: id , username and hash.

- id - personal number
- username - nickname of user
- hash - hashed password

And three columns in the 'city' table: id , user_id and city.

- id - personal number
- user_id - id from table 'users'
- city - city name

# First funtion
The first "data_info" function is needed to add all saved cities by the user to the list from the city.db database.

```python
    if "user_id" in session :
        info = db.execute("SELECT city FROM city WHERE user_id = ?", session["user_id"])
        all_cities = []
        for i in info:
            all_cities.append(i['city'])

        return all_cities

```


# Api and second funtion

The "weather_data" function takes one variable "city", this variable stores the name of the city. The function finds the necessary .weather and time data for the "city" variable.

The "api" variable stores the personal weather api from https://openweathermap.org/.

Variables "url_now" and "url" store links about current weather and weather prediction, respectively.

"response_now" and "response" store all weather information in a dictionary.
```python
    api = '...'

    url_now = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric'
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api}&units=metric'

    response_now = requests.get(url_now).json()
    response = requests.get(url).json()

```

In the same function, the necessary information is further selected from "response_now" and "response"
and stored in the "weather_data_now" and "weather_data" libraries.

```python
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


        # Add date of weather now to library
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
```

The function returns information about the weather, depending on whether the user is logged in or not, and also if the user entered an incorrect city, it return an error.

```python
        if "user_id" in session :
            return render_template('index.html', city = city.capitalize() ,name_city = name_city, weather_data = weather_data, weather_data_now = weather_data_now, all_cities = all_cities)
        else:
            return render_template('index.html', city = city.capitalize() ,name_city = name_city, weather_data = weather_data, weather_data_now = weather_data_now)

    except KeyError:
         if "user_id" in session :
            return render_template('index.html', massage = "I coudn't find this city:", wrong_city = city, all_cities = all_cities)
         else:
             return render_template('index.html', massage = "I coudn't find this city:", wrong_city = city)
```


## Documentation
- SQLight - https://www.sqlite.org/index.html

- Flask - https://flask.palletsprojects.com/en/1.1.x/

- Openweather - https://openweathermap.org/api/one-call-3



