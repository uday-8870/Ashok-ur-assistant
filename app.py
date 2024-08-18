from flask import Flask, render_template, request, jsonify
import datetime
import webbrowser
import requests
import re
import sympy as sp
import subprocess
import os
import speech_recognition as sr
from transformers import pipeline

app = Flask(__name__)

# Load pre-trained NLP model for intent classification
nlp_pipeline = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

@app.route("/")
def home():
    greeting = wishMe()
    return render_template("index.html", greeting=greeting)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("query", "").lower()
    response = process_query(user_input)
    return jsonify({"response": response})

@app.route("/recognize", methods=["POST"])
def recognize():
    audio_file = request.files.get("audio")
    if audio_file:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                response = process_query(text.lower())
                return jsonify({"response": response})
        except sr.UnknownValueError:
            return jsonify({"response": "Sorry, I could not understand the audio."})
        except sr.RequestError:
            return jsonify({"response": "Sorry, there was an error with the speech recognition service."})
    else:
        return jsonify({"response": "No audio file provided."})

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

    # Use NLP model to classify the query
    try:
        result = nlp_pipeline(query)
        intent = result[0]['label']
    except Exception as e:
        return f"Error processing query: {str(e)}"

    if 'exit' in query or 'stop' in query:
        response = "Goodbye!"
    elif 'weather' in query:
        city_name = re.search(r'in\s(.+)', query)
        if city_name:
            city_name = city_name.group(1).strip()
            response = get_weather(city_name)
        else:
            response = "Please specify the city after 'weather in'."
    elif 'time' in query:
        response = datetime.datetime.now().strftime("%H:%M:%S")
    elif is_math_expression(query):
        response = solve_math(query)
    elif 'shutdown' in query:
        response = "Shutting down your computer..."
        subprocess.run(["shutdown", "/s", "/t", "1"])
    elif 'open' in query:
        response = open_website_or_app(query)
    elif 'camera' in query:
        response = take_photo()
    elif 'news' in query:
        response = open_news()
    elif 'hello' in query or 'hi' in query:
        response = "Hello... How can I help you?"
    elif 'who are you' in query or 'who made you' in query or 'what is your work' in query or 'what you do' in query or 'your work' in query:
        response = "I am a personalized desktop assistant model known as ASHOK. I can perform small tasks like opening applications, solving math problems, and other features."
    else:
        response = "Sorry, I am not sure how to help with that."

    return response

def get_weather(city_name):
    api_key = ""  
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city_name}&units=metric"  
    try:
        response = requests.get(complete_url)
        response.raise_for_status()  
        data = response.json()
        if data.get("cod") != 404:
            main = data.get("main", {})
            temperature = main.get("temp")
            humidity = main.get("humidity")
            weather = data.get("weather", [{}])[0]
            description = weather.get("description", "No description")
            return (f"Temperature: {temperature:.2f}°C\n"
                    f"Humidity: {humidity}%\n"
                    f"Description: {description.capitalize()}")
        else:
            return "City Not Found"
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"

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
        "notepad": "notepad",
        "calculator": "calc",
        "settings": "start ms-settings:",
        "microsoft edge": "msedge",
        "camera": "camera",
        "chrome": "chrome",
        "file manager": "explorer",
        "whatsapp": r"C:\Users\<YourUsername>\AppData\Local\WhatsApp\WhatsApp.exe",  # Update with your path to WhatsApp
        "vscode": r"C:\Users\dines\OneDrive\Desktop\DINESH SAI\VSCodeUserSetup-x64-1.63.2.exe",
        "word": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk",
        "edge": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Edge.lnk",
        "excel": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk",
        "powerpoint": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"
    }
    app_path = apps.get(app_name.lower())
    if app_path:
        try:
            os.startfile(app_path)
            return f"{app_name.capitalize()} is now open."
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    else:
        return f"Application {app_name} not found."

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
