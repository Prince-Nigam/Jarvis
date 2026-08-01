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
    import pyautogui
except ModuleNotFoundError:
    pyautogui = None

try:
    import pywhatkit as kit
except ModuleNotFoundError:
    kit = None

try:
    import pvporcupine
except ModuleNotFoundError:
    pvporcupine = None

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
        os.system("start " + app_name)
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


def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    if pvporcupine is None or pyaudio is None:
        print("[Hotword] Dependencies missing (pvporcupine/pyaudio). Hotword listener disabled.")
        return

    # Porcupine requires an access key from https://console.picovoice.ai/
    access_key = PORCUPINE_ACCESS_KEY
    if not access_key:
        print(
            "[Hotword] PORCUPINE_ACCESS_KEY not set in environment variables. "
            "Get a free key at https://console.picovoice.ai/ and set it. "
            "Hotword listener disabled."
        )
        return

    try:
        porcupine = pvporcupine.create(access_key=access_key, keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        print("[Hotword] Listening for wake word...")
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("[Hotword] Wake word detected!")
                if pyautogui is not None:
                    pyautogui.keyDown("win")
                    pyautogui.press("j")
                    time.sleep(2)
                    pyautogui.keyUp("win")
    except Exception as exc:
        print(f"[Hotword] Listener stopped: {exc}")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


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


def chatBot(query):
    cookie_path = os.path.join(os.path.dirname(__file__), "cookies.json")

    if hugchat is None or not os.path.exists(cookie_path):
        response = _simple_chat_fallback(query)
        speak(response)
        return response

    try:
        user_input = query.lower()
        chatbot = hugchat.ChatBot(cookie_path=cookie_path)
        conversation_id = chatbot.new_conversation()
        chatbot.change_conversation(conversation_id)
        response = chatbot.chat(user_input)
        speak(response)
        return response
    except Exception as exc:
        print(f"Chat error: {exc}")
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
