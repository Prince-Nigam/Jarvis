"""
command.py — Speech recognition + TTS for Jarvis (Flask/REST version)
Fixes:
  - RLock instead of Lock (was deadlocking on first TTS call)
  - speak() runs in background thread, does NOT return response text
  - run_command() returns response text for the frontend to display
  - takecommand() with proper timeout/error handling
  - No shell injection in openCommand
"""
import subprocess
import threading
import time

# ── TTS ───────────────────────────────────────────────────────────────────────
try:
    import pyttsx3
    _tts_engine = None
    _tts_lock   = threading.RLock()   # RLock — reentrant, prevents deadlock

    def _get_engine():
        global _tts_engine
        # Called inside _tts_lock already — safe because RLock
        if _tts_engine is None:
            _tts_engine = pyttsx3.init("sapi5")
            voices = _tts_engine.getProperty("voices")
            if voices:
                _tts_engine.setProperty("voice", voices[0].id)
            _tts_engine.setProperty("rate", 174)
        return _tts_engine

except (ModuleNotFoundError, Exception):
    pyttsx3 = None
    _tts_lock = threading.RLock()
    def _get_engine(): return None

# ── Speech Recognition ────────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    _recognizer = sr.Recognizer()
    _recognizer.pause_threshold          = 1
    _recognizer.energy_threshold         = 300
    _recognizer.dynamic_energy_threshold = True
except (ModuleNotFoundError, Exception):
    sr = None
    _recognizer = None


def speak(text):
    """
    Speak text using pyttsx3 TTS.
    Runs in a background thread — non-blocking.
    Does NOT return anything — use run_command() return value for UI text.
    """
    text = str(text)
    print(f"[JARVIS]: {text}")

    if pyttsx3 is None:
        return

    def _do_speak():
        global _tts_engine
        try:
            with _tts_lock:
                engine = _get_engine()
                if engine:
                    engine.say(text)
                    engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error]: {e}")
            # Reset engine so next call gets a fresh one
            _tts_engine = None

    threading.Thread(target=_do_speak, daemon=True).start()


def takecommand():
    """
    Listen via microphone and return recognised text (lowercase).
    Returns empty string on any failure.
    """
    if sr is None or _recognizer is None:
        print("[SR] speech_recognition not available")
        return ""

    try:
        with sr.Microphone() as source:
            print("[MIC] Adjusting for ambient noise...")
            _recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[MIC] Listening...")
            audio = _recognizer.listen(source, timeout=8, phrase_time_limit=8)
    except sr.WaitTimeoutError:
        print("[MIC] Timeout — no speech detected")
        return ""
    except OSError as e:
        print(f"[MIC] Microphone error: {e}")
        return ""
    except Exception as e:
        print(f"[MIC] Unexpected error: {e}")
        return ""

    try:
        print("[SR] Recognizing...")
        query = _recognizer.recognize_google(audio, language="en-in")
        print(f"[USER SAID]: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("[SR] Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"[SR] Google API error: {e}")
        return ""
    except Exception as e:
        print(f"[SR] Recognition error: {e}")
        return ""


def run_command(query):
    """
    Route a text query to the correct feature handler.
    Returns the response string for the browser to display.
    speak() is called separately inside each branch — NOT called on the
    returned value to avoid double-speaking.
    """
    query = (query or "").strip().lower()
    if not query:
        return ""

    response = ""
    try:
        # ── Open app / website ──────────────────────────────────────────────
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
            app = query.replace("open", "").strip()
            response = f"Opening {app}"

        # ── YouTube ────────────────────────────────────────────────────────
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
            response = "Playing on YouTube"

        # ── Contacts / Calls ───────────────────────────────────────────────
        elif any(k in query for k in ("send message", "phone call", "video call")):
            from engine.features import findContact, makeCall, sendMessage, whatsApp
            contact_no, name = findContact(query)
            if contact_no and contact_no != 0:
                if "send message" in query:
                    speak("What message should I send?")
                    msg = takecommand()
                    if msg:
                        sendMessage(msg, contact_no, name)
                        response = f"Message sent to {name}"
                    else:
                        response = "No message spoken"
                elif "phone call" in query:
                    makeCall(name, contact_no)
                    response = f"Calling {name}"
                else:
                    whatsApp(contact_no, "", "video call", name)
                    response = f"Starting video call with {name}"
            else:
                response = "Contact not found"
                speak(response)

        # ── Time ───────────────────────────────────────────────────────────
        elif "time" in query:
            from datetime import datetime
            t = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {t}"
            speak(response)

        # ── Date ───────────────────────────────────────────────────────────
        elif "date" in query:
            from datetime import datetime
            d = datetime.now().strftime("%B %d, %Y")
            response = f"Today is {d}"
            speak(response)

        # ── Greetings ──────────────────────────────────────────────────────
        elif any(k in query for k in ("hello", "hi", "hey")):
            response = "Hello Sir! How can I assist you?"
            speak(response)

        # ── Identity ───────────────────────────────────────────────────────
        elif "your name" in query or "who are you" in query:
            response = "I am Jarvis, your personal AI assistant."
            speak(response)

        # ── Joke ───────────────────────────────────────────────────────────
        elif "joke" in query:
            response = "Why do programmers prefer dark mode? Because light attracts bugs!"
            speak(response)

        # ── Screenshot ─────────────────────────────────────────────────────
        elif "screenshot" in query:
            try:
                import pyautogui
                pyautogui.screenshot("screenshot.png")
                response = "Screenshot saved"
                speak(response)
            except Exception:
                response = "Could not take screenshot. pyautogui not available."

        # ── Volume ─────────────────────────────────────────────────────────
        elif "volume up" in query:
            try:
                import pyautogui
                pyautogui.press("volumeup", presses=5)
                response = "Volume increased"
            except Exception:
                response = "Could not change volume"

        elif "volume down" in query:
            try:
                import pyautogui
                pyautogui.press("volumedown", presses=5)
                response = "Volume decreased"
            except Exception:
                response = "Could not change volume"

        elif "mute" in query:
            try:
                import pyautogui
                pyautogui.press("volumemute")
                response = "Muted"
            except Exception:
                response = "Could not mute"

        # ── Safety: no shutdown/restart via voice ──────────────────────────
        elif "shutdown" in query or "restart" in query:
            response = "For safety, please do shutdown or restart manually."
            speak(response)

        # ── Chatbot fallback ───────────────────────────────────────────────
        else:
            from engine.features import chatBot
            response = chatBot(query) or f"I heard: {query}"

    except Exception as e:
        print(f"[CMD Error]: {e}")
        response = "Sorry, something went wrong."
        speak(response)

    return response
