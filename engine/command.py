"""
command.py — TTS + Speech Recognition for Jarvis
- Single dedicated TTS thread (avoids SAPI5/COM conflicts)
- Queue-based speak() — non-blocking, thread-safe
- takecommand() with proper error handling
- run_command() routes queries to correct feature
"""
import subprocess
import threading
import time
import queue as _queue

# ── TTS setup ─────────────────────────────────────────────────────────────────
try:
    import pyttsx3
    _HAS_TTS = True
except ModuleNotFoundError:
    pyttsx3 = None
    _HAS_TTS = False

_tts_q      = _queue.Queue()
_tts_engine = None
_tts_thread = None


def _tts_worker():
    """Single dedicated thread — all TTS runs here to avoid COM conflicts."""
    global _tts_engine
    while True:
        text = _tts_q.get()
        if text is None:          # sentinel to shut down
            break
        try:
            if _tts_engine is None:
                _tts_engine = pyttsx3.init("sapi5")
                voices = _tts_engine.getProperty("voices")
                if voices:
                    _tts_engine.setProperty("voice", voices[0].id)
                _tts_engine.setProperty("rate", 170)
            _tts_engine.say(text)
            _tts_engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error]: {e}")
            try:
                _tts_engine.stop()
            except Exception:
                pass
            _tts_engine = None    # reset so next call reinits
        finally:
            _tts_q.task_done()


def _ensure_tts_worker():
    global _tts_thread
    if not _HAS_TTS:
        return
    if _tts_thread is None or not _tts_thread.is_alive():
        _tts_thread = threading.Thread(
            target=_tts_worker, daemon=True, name="tts-worker"
        )
        _tts_thread.start()


# Start worker on import
_ensure_tts_worker()

# ── Speech Recognition ─────────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    _recognizer = sr.Recognizer()
    _recognizer.pause_threshold          = 1
    _recognizer.energy_threshold         = 300
    _recognizer.dynamic_energy_threshold = True
    _HAS_SR = True
except (ModuleNotFoundError, Exception):
    sr = None
    _recognizer = None
    _HAS_SR = False


# ── Public API ─────────────────────────────────────────────────────────────────

def speak(text):
    """
    Queue text for TTS output. Non-blocking.
    All speech is handled by a single background thread.
    """
    text = str(text).strip()
    if not text:
        return
    print(f"[JARVIS]: {text}")
    if _HAS_TTS:
        _ensure_tts_worker()
        _tts_q.put(text)


def takecommand():
    """
    Listen via microphone, return recognised text (lowercase).
    Returns '' on any failure.
    """
    if not _HAS_SR or _recognizer is None:
        print("[SR] speech_recognition not available")
        return ""

    try:
        with sr.Microphone() as source:
            print("[MIC] Adjusting for noise...")
            _recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[MIC] Listening...")
            audio = _recognizer.listen(source, timeout=8, phrase_time_limit=8)
    except sr.WaitTimeoutError:
        print("[MIC] Timeout — no speech")
        return ""
    except OSError as e:
        print(f"[MIC] Error: {e}")
        return ""
    except Exception as e:
        print(f"[MIC] Unexpected: {e}")
        return ""

    try:
        print("[SR] Recognizing...")
        query = _recognizer.recognize_google(audio, language="en-in")
        print(f"[USER]: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("[SR] Could not understand")
        return ""
    except sr.RequestError as e:
        print(f"[SR] API error: {e}")
        return ""
    except Exception as e:
        print(f"[SR] Error: {e}")
        return ""


def run_command(query):
    """
    Route query to correct feature. Returns response string for browser.
    speak() is called inside each branch — NOT on the returned value
    (to avoid double-speaking).
    """
    query = (query or "").strip().lower()
    if not query:
        return ""

    response = ""
    try:

        # ── Open app / website ─────────────────────────────────────────────
        if "open" in query:
            from engine.features import openCommand
            app = query.replace("open", "").strip()
            openCommand(query)
            response = f"Opening {app}"

        # ── YouTube ────────────────────────────────────────────────────────
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
            response = "Playing on YouTube"

        # ── Contacts / WhatsApp ────────────────────────────────────────────
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
                        response = "No message heard"
                elif "phone call" in query:
                    makeCall(name, contact_no)
                    response = f"Calling {name}"
                else:
                    whatsApp(contact_no, "", "video call", name)
                    response = f"Video call with {name}"
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
        elif any(k in query for k in ("hello", "hi ", " hi", "hey")):
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
                response = "Screenshot not available"

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

        # ── Safety ─────────────────────────────────────────────────────────
        elif "shutdown" in query or "restart" in query:
            response = "Please do that manually for safety."
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
