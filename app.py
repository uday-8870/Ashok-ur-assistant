from flask import Flask, render_template, request, jsonify
import datetime
import webbrowser
import requests
import re
import sympy as sp
import subprocess
import ecapture

app = Flask(__name__)
exit_flag = False

@app.route("/")
def home():
    greeting = wishMe()
    return render_template("index.html", greeting=greeting)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("query").lower()
    response = process_query(user_input)
    return jsonify({"response": response})

def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

def process_query(query):
    response = ""

    if 'exit' in query or 'stop' in query:
        response = "Goodbye!"
        global exit_flag
        exit_flag = True
    elif 'weather' in query:
        city_name = query.split("in")[-1].strip()
        response = get_weather(city_name)
    elif 'time' in query:
        response = datetime.datetime.now().strftime("%H:%M:%S")
    elif is_math_expression(query):
        response = solve_math(query)
    elif 'open' in query:
        response = open_website_or_app(query)
    elif 'camera' in query:
        response = take_photo()
    elif 'news' in query:
        response = open_news()

    elif 'hello' in query or 'hi' in query:
        response = "Hello... How can I help you?"
    elif 'who are you' in query or 'who made you' in query or 'what is your work' in query or 'what you do' in query or 'your work' in query:
        response = "I am a personalized desktop assistant model made by my boss Dinesh. I can perform small tasks like opening applications, solving math problems, and other features."
    else:
        response = "Sorry, I am not sure how to help with that."

    return response


def get_weather(city_name):
    api_key = "your_openweathermap_api_key"  # Replace with your actual OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        current_humidity = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        return (f"Temperature in Kelvin: {current_temperature:.2f}\n"
                f"Humidity in percentage: {current_humidity}\n"
                f"Description: {weather_description}")
    else:
        return "City Not Found"

def is_math_expression(query):
    math_keywords = ['plus', 'minus', 'times', 'divided by', 'power', 'log', 'factorial', 'sin', 'cos', 'tan', '+', '-', '*', '/']
    return any(keyword in query for keyword in math_keywords)

def solve_math(query):
    try:
        query = re.sub(r'what is|calculate|solve', '', query).strip()
        query = query.replace('plus', '+').replace('minus', '-').replace('times', '*').replace('divided by', '/')
        expr = sp.sympify(query)
        result = sp.simplify(expr)
        return f"The result is {result}"
    except Exception as e:
        return "Sorry, I could not solve the math problem."

def open_website_or_app(command):
    if 'open youtube' in command:
        webbrowser.open_new_tab("https://www.youtube.com")
        return "YouTube is open now"
    elif 'open google' in command:
        webbrowser.open_new_tab("https://www.google.com")
        return "Google is open now"
    elif 'open gmail' in command:
        webbrowser.open_new_tab("https://mail.google.com")
        return "Gmail is open now"
    elif 'open maps' in command:
        webbrowser.open_new_tab("https://www.google.com/maps")
        return "Google Maps is open now"
    elif 'open news' in command:
        webbrowser.open_new_tab("https://indianexpress.com/latest-news/")
        return "News is open now"
    else:
        app_name = command.replace('open ', '')
        return open_application(app_name)

def open_application(app_name):
    apps = {
        "notepad.": "notepad",
        "calculator.": "calc",
        "settings.": "start ms-settings:",
        "microsoft edge.": "msedge",
        "camera.":"camera",
        "chrome.": "chrome",
        "file manager.": "explorer",
        "whatsapp.": r"C:\Users\<YourUsername>\AppData\Local\WhatsApp\WhatsApp.exe",  # Update with your path to WhatsApp
        "vscode.": r"C:\Users\dines\OneDrive\Desktop\DINESH SAI\VSCodeUserSetup-x64-1.63.2.exe",
        "word.": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk",
        "edge.": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Edge.lnk",
        "excel.": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk",
        "powerpoint.": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"
    }

    if app_name in apps:
        try:
            subprocess.Popen(apps[app_name], shell=True)
            return f"{app_name} is open now"
        except Exception as e:
            return f"Sorry, I could not open {app_name}. Error: {str(e)}"
    else:
        return f"Sorry, I don't know how to open {app_name}"

def take_photo():
    try:
        from ecapture import ecapture as ec
        ec.capture(0, "Bravoo Camera", "img.jpg")
        return "Photo taken"
    except Exception as e:
        return f"Sorry, I could not take a photo. Error: {str(e)}"

def open_news():
    try:
        webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
        return 'Here are some headlines from the Times of India. Happy reading!'
    except Exception as e:
        return f"Sorry, I could not open the news. Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)