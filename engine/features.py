import os
import sqlite3
import struct
import subprocess
import time
import webbrowser
from urllib.parse import quote

try:
    from playsound import playsound
except ModuleNotFoundError:
    playsound = None

try:
    import eel
except ModuleNotFoundError:
    eel = None

try:
    import pyaudio
except ModuleNotFoundError:
    pyaudio = None

try:
    import pywhatkit as kit
except ModuleNotFoundError:
    kit = None

try:
    import pyautogui
except ModuleNotFoundError:
    pyautogui = None

try:
    from hugchat import hugchat
except ModuleNotFoundError:
    hugchat = None

from engine.command import speak
from engine.config import ASSISTANT_NAME, PORCUPINE_ACCESS_KEY
from engine.helper import extract_yt_term, remove_words
from engine.init_db import DB_PATH, init_database

init_database()


def _get_cursor():
    """Return a fresh connection and cursor. Caller must close the connection."""
    con = sqlite3.connect(DB_PATH)
    return con, con.cursor()

START_SOUND = os.path.join("www", "assets", "audio", "start_sound.mp3")


def playAssistantSound():
    if playsound is None:
        print("playsound is not installed; skipping assistant sound")
        return
    if not os.path.exists(START_SOUND):
        print("Startup sound file not found; skipping")
        return
    try:
        playsound(START_SOUND)
    except Exception as exc:
        print(f"Startup sound skipped: {exc}")


if eel is not None:
    eel.expose(playAssistantSound)


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower().strip()
    app_name = query

    if not app_name:
        return

    con, cursor = _get_cursor()
    try:
        cursor.execute(
            "SELECT path FROM sys_command WHERE LOWER(name) = ?", (app_name,)
        )
        results = cursor.fetchall()

        if results:
            speak("Opening " + app_name)
            os.startfile(results[0][0])
            return

        cursor.execute(
            "SELECT url FROM web_command WHERE LOWER(name) = ?", (app_name,)
        )
        results = cursor.fetchall()

        if results:
            speak("Opening " + app_name)
            webbrowser.open(results[0][0])
            return

        speak("Opening " + app_name)
        # Safe: no shell=True, app_name passed as separate argument
        subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=False)
    except Exception:
        speak("Something went wrong")
    finally:
        con.close()


def PlayYoutube(query):
    if kit is None:
        speak("YouTube feature is not available")
        return

    search_term = extract_yt_term(query)
    if not search_term:
        speak("Please tell me what to play on YouTube")
        return

    speak("Playing " + search_term + " on YouTube")
    kit.playonyt(search_term)


def findContact(query):
    words_to_remove = [
        ASSISTANT_NAME,
        "make",
        "a",
        "to",
        "phone",
        "call",
        "send",
        "message",
        "whatsapp",
        "video",
    ]
    query = remove_words(query, words_to_remove)

    con, cursor = _get_cursor()
    try:
        query = query.strip().lower()
        cursor.execute(
            "SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
            ("%" + query + "%", query + "%"),
        )
        results = cursor.fetchall()
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith("+91"):
            mobile_number_str = "+91" + mobile_number_str

        return mobile_number_str, query
    except Exception:
        speak("Contact not found")
        return 0, 0
    finally:
        con.close()


def whatsApp(mobile_no, message, flag, name):
    if flag == "message":
        target_tab = 12
        jarvis_message = "Message sent successfully to " + name
    elif flag == "call":
        target_tab = 7
        message = ""
        jarvis_message = "Calling " + name
    else:
        target_tab = 6
        message = ""
        jarvis_message = "Starting video call with " + name

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'cmd /c start "" "{whatsapp_url}"'
    subprocess.run(full_command, shell=True)

    if pyautogui is None:
        speak(jarvis_message)
        return

    time.sleep(5)
    pyautogui.hotkey("ctrl", "f")

    for _ in range(1, target_tab):
        pyautogui.press("tab")

    pyautogui.press("enter")
    speak(jarvis_message)


def _simple_chat_fallback(query):
    from datetime import datetime

    text = query.lower()
    if "time" in text:
        return f"The time is {datetime.now().strftime('%I:%M %p')}"
    if "date" in text:
        return f"Today is {datetime.now().strftime('%B %d, %Y')}"
    if "hello" in text or "hi" in text:
        return "Hello Sir, how can I help you?"
    return f"I heard: {query}. Configure HugChat cookies for full chat support."


# Reuse chatbot session across calls so conversation history is preserved
_chatbot_instance = None
_chatbot_conv_id  = None

def chatBot(query):
    global _chatbot_instance, _chatbot_conv_id

    cookie_path = os.path.join(os.path.dirname(__file__), "cookies.json")

    if hugchat is None or not os.path.exists(cookie_path):
        response = _simple_chat_fallback(query)
        speak(response)
        return response

    try:
        user_input = query.lower()

        # Create session once, reuse afterwards
        if _chatbot_instance is None:
            _chatbot_instance = hugchat.ChatBot(cookie_path=cookie_path)
            _chatbot_conv_id  = _chatbot_instance.new_conversation()

        _chatbot_instance.change_conversation(_chatbot_conv_id)
        response = str(_chatbot_instance.chat(user_input))
        speak(response)
        return response
    except Exception as exc:
        print(f"Chat error: {exc}")
        # Reset on error so next call gets a fresh session
        _chatbot_instance = None
        _chatbot_conv_id  = None
        response = _simple_chat_fallback(query)
        speak(response)
        return response


def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    os.system(
        "adb shell am start -a android.intent.action.CALL -d tel:" + mobileNo
    )


def sendMessage(message, mobileNo, name):
    from engine.helper import (
        adbInput,
        goback,
        keyEvent,
        replace_spaces_with_percent_s,
        tapEvents,
    )

    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("Sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    tapEvents(136, 2220)
    tapEvents(819, 2192)
    adbInput(mobileNo)
    tapEvents(601, 574)
    tapEvents(390, 2270)
    adbInput(message)
    tapEvents(957, 1397)
    speak("Message sent successfully to " + name)
