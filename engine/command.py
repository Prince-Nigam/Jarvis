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
        from engine import desktop_control as dc

        # ══════════════════════════════════════════════════════════
        #  WINDOW MANAGEMENT
        # ══════════════════════════════════════════════════════════

        if any(k in query for k in ("minimize window", "minimise window", "window minimize")):
            dc.minimize_window()
            response = "Window minimized"

        elif any(k in query for k in ("maximize window", "maximise window", "window maximize", "full screen")):
            dc.maximize_window()
            response = "Window maximized"

        elif any(k in query for k in ("close window", "close this", "window close")):
            dc.close_window()
            response = "Window closed"

        elif any(k in query for k in ("switch window", "alt tab", "change window")):
            dc.switch_window()
            response = "Switching window"

        elif any(k in query for k in ("show desktop", "hide all", "minimize all")):
            dc.show_desktop()
            response = "Showing desktop"

        elif any(k in query for k in ("snap left", "window left")):
            dc.snap_left()
            response = "Snapped to left"

        elif any(k in query for k in ("snap right", "window right")):
            dc.snap_right()
            response = "Snapped to right"

        elif any(k in query for k in ("task view", "virtual desktop", "show all windows")):
            dc.open_task_view()
            response = "Task view opened"

        # ══════════════════════════════════════════════════════════
        #  MEDIA CONTROL
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("play music", "pause music", "play pause", "resume music")):
            dc.media_play_pause()
            response = "Play/Pause toggled"

        elif any(k in query for k in ("next song", "next track", "skip song", "next music")):
            dc.media_next()
            response = "Next track"

        elif any(k in query for k in ("previous song", "prev song", "last song", "previous track")):
            dc.media_previous()
            response = "Previous track"

        elif "stop music" in query or "stop media" in query:
            dc.media_stop()
            response = "Media stopped"

        elif "volume up" in query or "increase volume" in query or "louder" in query:
            dc.volume_up()
            response = "Volume increased"

        elif "volume down" in query or "decrease volume" in query or "lower volume" in query or "quieter" in query:
            dc.volume_down()
            response = "Volume decreased"

        elif "mute" in query:
            dc.mute_volume()
            response = "Muted"

        # ══════════════════════════════════════════════════════════
        #  KEYBOARD SHORTCUTS
        # ══════════════════════════════════════════════════════════

        elif "copy" in query and "open" not in query:
            dc.copy()
            response = "Copied"

        elif "paste" in query:
            dc.paste()
            response = "Pasted"

        elif "cut" in query and "open" not in query:
            dc.cut()
            response = "Cut"

        elif any(k in query for k in ("undo", "go back one step")):
            dc.undo()
            response = "Undo done"

        elif "redo" in query:
            dc.redo()
            response = "Redo done"

        elif "select all" in query:
            dc.select_all()
            response = "Selected all"

        elif any(k in query for k in ("save file", "save this", "ctrl s")):
            dc.save_file()
            response = "Saved"

        elif any(k in query for k in ("new tab", "open tab")):
            dc.new_tab()
            response = "New tab opened"

        elif any(k in query for k in ("close tab", "close current tab")):
            dc.close_tab()
            response = "Tab closed"

        elif any(k in query for k in ("refresh", "reload page", "reload")):
            dc.refresh_page()
            response = "Refreshed"

        elif any(k in query for k in ("go back", "browser back", "previous page")):
            dc.go_back()
            response = "Going back"

        elif any(k in query for k in ("go forward", "browser forward", "next page")):
            dc.go_forward()
            response = "Going forward"

        elif any(k in query for k in ("zoom in", "increase zoom")):
            dc.zoom_in()
            response = "Zoomed in"

        elif any(k in query for k in ("zoom out", "decrease zoom")):
            dc.zoom_out()
            response = "Zoomed out"

        elif any(k in query for k in ("find on page", "search on page", "ctrl f")):
            dc.find_on_page()
            response = "Find opened"

        elif any(k in query for k in ("new window", "open new window")):
            dc.open_new_window()
            response = "New window opened"

        elif any(k in query for k in ("press enter", "hit enter", "enter")):
            dc.press_enter()
            response = "Enter pressed"

        elif any(k in query for k in ("press escape", "escape", "cancel")):
            dc.press_escape()
            response = "Escaped"

        # ══════════════════════════════════════════════════════════
        #  SCROLL
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("scroll down", "page down", "move down")):
            dc.scroll_down()
            response = "Scrolled down"

        elif any(k in query for k in ("scroll up", "page up", "move up")):
            dc.scroll_up()
            response = "Scrolled up"

        # ══════════════════════════════════════════════════════════
        #  SCREENSHOT
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("screenshot", "take screenshot", "capture screen", "screen capture")):
            dc.take_screenshot()
            response = "Screenshot saved to Desktop"

        # ══════════════════════════════════════════════════════════
        #  TYPE TEXT
        # ══════════════════════════════════════════════════════════

        elif query.startswith("type "):
            text_to_type = query[5:].strip()
            if text_to_type:
                dc.type_text(text_to_type)
                response = f"Typed: {text_to_type}"
            else:
                speak("What should I type?")
                text_to_type = takecommand()
                if text_to_type:
                    dc.type_text(text_to_type)
                    response = f"Typed: {text_to_type}"

        elif query.startswith("write "):
            text_to_type = query[6:].strip()
            if text_to_type:
                dc.type_text(text_to_type)
                response = f"Typed: {text_to_type}"

        # ══════════════════════════════════════════════════════════
        #  FOLDER / FILE OPERATIONS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("open downloads", "downloads folder")):
            dc.open_folder("downloads")
            response = "Opening Downloads"

        elif any(k in query for k in ("open desktop", "desktop folder")):
            dc.open_folder("desktop")
            response = "Opening Desktop"

        elif any(k in query for k in ("open documents", "documents folder", "my documents")):
            dc.open_folder("documents")
            response = "Opening Documents"

        elif any(k in query for k in ("open pictures", "pictures folder", "my pictures", "open photos")):
            dc.open_folder("pictures")
            response = "Opening Pictures"

        elif any(k in query for k in ("open music", "music folder", "my music")):
            dc.open_folder("music")
            response = "Opening Music"

        elif any(k in query for k in ("open videos", "videos folder", "my videos")):
            dc.open_folder("videos")
            response = "Opening Videos"

        elif any(k in query for k in ("open c drive", "open c:", "c drive")):
            dc.open_folder("c drive")
            response = "Opening C Drive"

        elif any(k in query for k in ("open d drive", "open d:", "d drive")):
            dc.open_folder("d drive")
            response = "Opening D Drive"

        elif any(k in query for k in ("my computer", "this pc", "open my computer", "open this pc")):
            dc.open_folder("this pc")
            response = "Opening This PC"

        elif any(k in query for k in ("recycle bin", "open recycle bin")):
            dc.open_folder("recycle bin")
            response = "Opening Recycle Bin"

        elif any(k in query for k in ("empty recycle bin", "clear recycle bin", "delete recycle bin")):
            dc.empty_recycle_bin()
            response = "Recycle bin emptied"

        # ══════════════════════════════════════════════════════════
        #  SYSTEM ACTIONS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("lock screen", "lock computer", "lock laptop", "lock pc")):
            dc.lock_screen()
            response = "Screen locked"

        elif any(k in query for k in ("sleep", "go to sleep", "hibernate")):
            dc.sleep_system()
            response = "Going to sleep"

        elif any(k in query for k in ("task manager", "open task manager", "process manager")):
            dc.open_task_manager()
            response = "Opening Task Manager"

        elif any(k in query for k in ("open settings", "windows settings", "system settings")):
            dc.open_settings()
            response = "Opening Settings"

        elif any(k in query for k in ("run dialog", "open run", "win r")):
            dc.open_run_dialog()
            response = "Run dialog opened"

        elif any(k in query for k in ("windows search", "open search", "search bar")):
            dc.open_search()
            response = "Search opened"

        elif any(k in query for k in ("notification", "action center", "notifications")):
            dc.open_notification_center()
            response = "Notification center opened"

        elif any(k in query for k in ("clipboard", "clipboard history", "win v")):
            dc.open_clipboard_history()
            response = "Clipboard history opened"

        elif any(k in query for k in ("virtual keyboard", "on screen keyboard", "osk")):
            dc.virtual_keyboard()
            response = "Virtual keyboard opened"

        elif any(k in query for k in ("magnifier", "zoom screen")):
            dc.open_magnifier()
            response = "Magnifier opened"

        elif "shutdown" in query:
            speak("For safety, please shutdown manually.")
            response = "Please shutdown manually for safety."

        elif "restart" in query:
            speak("For safety, please restart manually.")
            response = "Please restart manually for safety."

        # ══════════════════════════════════════════════════════════
        #  BRIGHTNESS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("brightness up", "increase brightness", "brighter")):
            dc.brightness_up()
            response = "Brightness increased"

        elif any(k in query for k in ("brightness down", "decrease brightness", "darker", "dim screen")):
            dc.brightness_down()
            response = "Brightness decreased"

        elif "brightness" in query:
            # Extract number: "set brightness to 70"
            import re
            nums = re.findall(r'\d+', query)
            if nums:
                dc.set_brightness(int(nums[0]))
                response = f"Brightness set to {nums[0]}%"
            else:
                speak("Please say brightness level from 0 to 100")
                response = "Brightness level not clear"

        # ══════════════════════════════════════════════════════════
        #  SEARCH (Google / YouTube)
        # ══════════════════════════════════════════════════════════

        elif "search google" in query or "google search" in query:
            term = query.replace("search google for", "").replace(
                "search google", "").replace("google search", "").strip()
            if term:
                dc.search_google(term)
                response = f"Searching Google for {term}"
            else:
                speak("What should I search?")
                term = takecommand()
                if term:
                    dc.search_google(term)
                    response = f"Searching Google for {term}"

        elif "search youtube" in query or "youtube search" in query:
            term = query.replace("search youtube for", "").replace(
                "search youtube", "").replace("youtube search", "").strip()
            if term:
                dc.search_youtube(term)
                response = f"Searching YouTube for {term}"
            else:
                speak("What should I search on YouTube?")
                term = takecommand()
                if term:
                    dc.search_youtube(term)
                    response = f"Searching YouTube for {term}"

        # ══════════════════════════════════════════════════════════
        #  OPEN APP / WEBSITE
        # ══════════════════════════════════════════════════════════

        elif "open" in query:
            from engine.features import openCommand
            app = query.replace("open", "").strip()
            openCommand(query)
            response = f"Opening {app}" if app else "Opening"

        # ══════════════════════════════════════════════════════════
        #  YOUTUBE PLAY
        # ══════════════════════════════════════════════════════════

        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
            response = "Playing on YouTube"

        # ══════════════════════════════════════════════════════════
        #  CONTACTS / WHATSAPP
        # ══════════════════════════════════════════════════════════

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

        # ══════════════════════════════════════════════════════════
        #  TIME / DATE
        # ══════════════════════════════════════════════════════════

        elif "time" in query:
            from datetime import datetime
            t = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {t}"
            speak(response)

        elif "date" in query:
            from datetime import datetime
            d = datetime.now().strftime("%B %d, %Y")
            response = f"Today is {d}"
            speak(response)

        # ══════════════════════════════════════════════════════════
        #  GREETINGS / IDENTITY
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("hello", "hi ", " hi", "hey")):
            response = "Hello Sir! How can I assist you?"
            speak(response)

        elif "your name" in query or "who are you" in query:
            response = "I am Jarvis, your personal AI assistant."
            speak(response)

        elif "joke" in query:
            response = "Why do programmers prefer dark mode? Because light attracts bugs!"
            speak(response)

        # ══════════════════════════════════════════════════════════
        #  CHATBOT FALLBACK
        # ══════════════════════════════════════════════════════════

        else:
            from engine.features import chatBot
            response = chatBot(query) or f"I heard: {query}"

    except Exception as e:
        print(f"[CMD Error]: {e}")
        response = "Sorry, something went wrong."
        speak(response)

    return response
