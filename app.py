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

nlp_pipeline = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

@app.route("/")
def home():
    greeting = wish_me()
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
        response = handle_audio(audio_file)
        return jsonify({"response": response})
    else:
        return jsonify({"response": "No audio file provided."})

def wish_me():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

def process_query(query):
    response = ""
    try:
        result = nlp_pipeline(query)
        intent = result[0]['label']
    except Exception as e:
        return f"Error processing query: {str(e)}"

    intent_responses = {
        'weather': get_weather_response,
        'time': lambda _: datetime.datetime.now().strftime("%H:%M:%S"),
        'math': solve_math,
        'shutdown': shutdown_system,
        'open': open_website_or_app,
        'camera': take_photo,
        'news': open_news,
        'hello': lambda _: "Hello... How can I help you?",
        'who_are_you': lambda _: "I am ASHOK, your personalized desktop assistant."
    }

    for key, func in intent_responses.items():
        if key in query:
            response = func(query)
            break
    else:
        response = "Sorry, I am not sure how to help with that."

    return response

def get_weather_response(query):
    city_name_match = re.search(r'in\s(.+)', query)
    city_name = city_name_match.group(1).strip() if city_name_match else ""
    return get_weather(city_name) if city_name else "Please specify the city after 'weather in'."

def get_weather(city_name):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "appid": WEATHER_API_KEY,
        "q": city_name,
        "units": "metric"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("cod") == 200:
            main = data.get("main", {})
            temperature = main.get("temp")
            humidity = main.get("humidity")
            description = data["weather"][0]["description"].capitalize()
            return f"Temperature: {temperature}°C\nHumidity: {humidity}%\nDescription: {description}"
        else:
            return "City not found."
    except requests.RequestException as e:
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
    websites = {
        'youtube': "https://www.youtube.com",
        'google': "https://www.google.com",
        'gmail': "https://mail.google.com",
        'maps': "https://www.google.com/maps",
        'news': "https://indianexpress.com/latest-news/"
    }
    for site, url in websites.items():
        if site in command:
            webbrowser.open_new_tab(url)
            return f"{site.capitalize()} is open now."
    return "Sorry, I couldn't open the specified application."

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
        return "Here are some headlines from the Times of India. Happy reading!"
    except Exception as e:
        return f"Sorry, I could not open the news. Error: {str(e)}"

def shutdown_system(_):
    subprocess.run(["shutdown", "/s", "/t", "1"])
    return "Shutting down your computer..."

def handle_audio(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return process_query(text.lower())
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Error with the speech recognition service."

if __name__ == "__main__":
    app.run(debug=True)
