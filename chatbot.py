import psycopg2  # PostgreSQL database connector
import pyttsx3  # Text-to-speech library
import datetime
import wikipedia
import webbrowser
import os
import time
import random
import re
from bs4 import BeautifulSoup
import requests

b = "Spartan: "  # Prefix for chatbot responses

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

# Auto-select an English voice
for voice in voices:
    if 'english' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

conn = psycopg2.connect( # PostgreSQL database connection setup
    host="localhost",
    port="5432",
    dbname="postgres",
    user="postgres",
    password="aa901216"
)
cursor = conn.cursor()

def speak(text): # Function to speak text aloud
    engine.say(text)
    engine.runAndWait()

# Greet user based on current time
def greetings():
    h = int(datetime.datetime.now().hour)
    if 8 < h < 12:
        greet = "Good morning. My name is Spartan. Version 1.00"
    elif 12 <= h < 17:
        greet = "Good afternoon. My name is Spartan. Version 1.00"
    else:
        greet = "Good evening. My name is Spartan. Version 1.00"
    print(b, greet)
    speak(greet)
    msg = "How can I help you, EE104?"
    print(b, msg)
    speak(msg)

def vaccine_query(query): # Process and answer vaccine-related queries
    try:
        query_lower = query.lower()
        stopwords = {"what", "is", "the", "email", "phone", "number", "of", "who", "has", "received"}

      
        if "whose phone" in query_lower or "who owns the number" in query_lower:  # Lookup by phone number to get person's name
            phone_match = re.findall(r"\d{10,}", query)
            if phone_match:
                phone = phone_match[0]
                cursor.execute("""
                    SELECT "First_Name", "Last_Name" FROM vaccination_records WHERE "Phone_Number"=%s
                """, (phone,))
                result = cursor.fetchone()
                if result:
                    msg = f"The phone number {phone} belongs to {result[0]} {result[1]}."
                else:
                    msg = f"Phone number {phone} not found."
            else:
                msg = "I couldn’t detect a phone number in your question."

        # Check if someone has received the second dose
        elif ("has" in query_lower and "second dose" in query_lower) or ("received" in query_lower and "second dose" in query_lower):
            names = [word for word in re.findall(r"[a-zA-Z]+", query) if word.lower() not in stopwords]
            if len(names) >= 2:
                fname, lname = names[0].lower(), names[1].lower()
                cursor.execute("""
                    SELECT "Second_Dose_Date" FROM vaccination_records
                    WHERE lower("First_Name")=%s AND lower("Last_Name")=%s
                """, (fname, lname))
                result = cursor.fetchone()
                if result and result[0]:
                    msg = f"{fname.title()} {lname.title()} received the second dose on {result[0]}."
                else:
                    msg = f"{fname.title()} {lname.title()} has not received the second dose."
            else:
                msg = "Please provide both first and last name."

      
        elif "email" in query_lower:   # Find email by first and last name
            names = [word for word in re.findall(r"[a-zA-Z]+", query) if word.lower() not in stopwords]
            if len(names) >= 2:
                fname, lname = names[0].lower(), names[1].lower()
                cursor.execute("SELECT \"Email\" FROM vaccination_records WHERE lower(\"First_Name\")=%s AND lower(\"Last_Name\")=%s", (fname, lname))
                result = cursor.fetchone()
                if result:
                    msg = f"{fname.title()} {lname.title()}'s email is {result[0]}."
                else:
                    msg = f"No email found for {fname.title()} {lname.title()}."
            else:
                msg = "Please provide both first and last name."

      
        elif "phone" in query_lower:    # Find phone number by name
            names = [word for word in re.findall(r"[a-zA-Z]+", query) if word.lower() not in stopwords]
            if len(names) >= 2:
                fname, lname = names[0].lower(), names[1].lower()
                cursor.execute("SELECT \"Phone_Number\" FROM vaccination_records WHERE lower(\"First_Name\")=%s AND lower(\"Last_Name\")=%s", (fname, lname))
                result = cursor.fetchone()
                if result:
                    msg = f"{fname.title()} {lname.title()}'s phone number is {result[0]}."
                else:
                    msg = f"No phone number found for {fname.title()} {lname.title()}."
            else:
                msg = "Please provide both first and last name."

        
        elif ("only one dose" in query_lower or "not received second" in query_lower): # List people who received only one dose
            cursor.execute("""
                SELECT "First_Name", "Last_Name" FROM vaccination_records WHERE "Second_Dose_Date" IS NULL
            """)
            results = cursor.fetchall()
            names = ", ".join([f"{r[0]} {r[1]}" for r in results])
            msg = f"People who received only one dose: {names}" if names else "Everyone has completed two doses."

        # List people who received both doses
        elif ("both doses" in query_lower or "completed two dose" in query_lower or "completed two doses" in query_lower or "completed vaccination" in query_lower):
            cursor.execute("""
                SELECT "First_Name", "Last_Name" FROM vaccination_records WHERE "Second_Dose_Date" IS NOT NULL
            """)
            results = cursor.fetchall()
            names = ", ".join([f"{r[0]} {r[1]}" for r in results])
            msg = f"People who have received both doses: {names}" if names else "No one has received both doses yet."

        else:
            msg = "Sorry, I didn’t understand your vaccine-related query."

        print(b, msg)
        speak(msg)

    except Exception as e:
        print(b, "Error while querying database.")
        speak("Database query error")


def takeCommand(): # Take user input and determine if it's a vaccine-related question
    while True:
        print(" ")
        query = input("EE104: ")
        if any(k in query.lower() for k in ["query", "vaccine", "dose", "email", "phone", "who", "completed"]):
            vaccine_query(query)
        elif query.lower() in ["exit", "bye"]:
            print(b, "Goodbye!")
            speak("Goodbye!")
            break
        else:
            print(b, "I haven’t learned that function yet, but you can ask about vaccinations!")
            speak("I haven’t learned that function yet, but you can ask about vaccinations!")


print("Initializing...")
time.sleep(1)
print("Spartan is preparing...")
time.sleep(1)
print("Environment is building...")
time.sleep(1)
greetings()
takeCommand()

