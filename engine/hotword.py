"""
hotword.py — Background wake-word listener for Jarvis
Wake phrase: "wake jarvis" / "hey jarvis" / "jarvis"

Runs in a background thread. When wake word is detected:
  1. Opens browser to Jarvis UI
  2. Plays a beep sound
  3. Starts listening for commands
"""
import threading
import time
import webbrowser
import os

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# ── Config ─────────────────────────────────────────────────────────────────────
WAKE_WORDS = [
    "wake up jarvis", "wakeup jarvis", "wake jarvis", 
    "hey jarvis", "jarvis", "ok jarvis", "hi jarvis", 
    "hello jarvis", "activate jarvis", "jarvish", "jarves", 
    "javis", "wake up jarvish", "wakeup jarvish", "wake jarvish",
    "hey jarvish", "ok jarvish", "hi jarvish"
]
JARVIS_URL = "http://localhost:8000/index.html"

# Global state
_listening      = False
_jarvis_active  = False
_jarvis_port    = 8000

def set_port(port):
    global _jarvis_port, JARVIS_URL
    _jarvis_port = port
    JARVIS_URL   = f"http://localhost:{port}/index.html"


def _play_activation_sound():
    """Play a simple beep to confirm wake word detected."""
    try:
        import winsound
        winsound.Beep(1000, 200)   # 1000 Hz, 200ms
        time.sleep(0.1)
        winsound.Beep(1200, 200)
    except Exception:
        pass   # non-Windows or winsound unavailable


EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

import ctypes

def _bring_jarvis_to_front():
    """Force the Jarvis window to top of desktop screen using Win32 API."""
    if os.name != 'nt':
        return
    try:
        user32 = ctypes.windll.user32

        def enum_windows_callback(hwnd, extra):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                if "jarvis" in title or "localhost:8000" in title or "127.0.0.1:8000" in title:
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    user32.ShowWindow(hwnd, 5)  # SW_SHOW
                    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
                    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
                    if fg_thread and target_thread and fg_thread != target_thread:
                        user32.AttachThreadInput(fg_thread, target_thread, True)
                        user32.SetForegroundWindow(hwnd)
                        user32.BringWindowToTop(hwnd)
                        user32.AttachThreadInput(fg_thread, target_thread, False)
                    else:
                        user32.SetForegroundWindow(hwnd)
                        user32.BringWindowToTop(hwnd)
                    return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
    except Exception as e:
        print(f"[HOTWORD] Win32 focus error: {e}")

def _open_jarvis_browser():
    """Open Jarvis window on the active desktop screen."""
    try:
        from engine.window_manager import show_jarvis_window
        show_jarvis_window(JARVIS_URL)
        print(f"[HOTWORD] Opened & focused Jarvis at {JARVIS_URL}")
    except Exception as e:
        print(f"[HOTWORD] Browser open failed: {e}")


def _contains_wake_word(text: str) -> bool:
    text = text.lower().strip()
    for ww in WAKE_WORDS:
        if ww in text:
            return True
    words = text.split()
    for w in words:
        if any(target in w for target in ["jarvis", "jarvish", "jarves", "javis"]):
            return True
    return False


def _listen_for_wake_word():
    """
    Continuously listens for the wake word using the microphone stream.
    """
    global _jarvis_active

    if sr is None:
        print("[HOTWORD] speech_recognition not installed — hotword disabled")
        return

    recognizer = sr.Recognizer()
    recognizer.energy_threshold          = 100
    recognizer.dynamic_energy_threshold  = False
    recognizer.pause_threshold           = 0.5

    print("[HOTWORD] Listening for wake word... (say 'hey jarvis' or 'wakeup jarvis')")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            while _listening:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        text = recognizer.recognize_google(audio, language="en-US")
                        print(f"[HOTWORD] Heard: {text}")

                        if _contains_wake_word(text):
                            print("[HOTWORD] Wake word detected!")
                            _play_activation_sound()
                            _open_jarvis_browser()
                            _jarvis_active = True
                            time.sleep(0.5)
                            _handle_post_wake()

                    except sr.UnknownValueError:
                        pass   # silence / unrecognised — keep looping
                    except sr.RequestError as e:
                        print(f"[HOTWORD] Google API error: {e}")
                        time.sleep(2)
                except sr.WaitTimeoutError:
                    pass   # no speech in window, keep listening continuously
                except Exception as e:
                    print(f"[HOTWORD] Inner audio error: {e}")
                    time.sleep(0.3)
    except OSError as e:
        print(f"[HOTWORD] Microphone access error: {e}")
    except Exception as e:
        print(f"[HOTWORD] Hotword thread error: {e}")


def _handle_post_wake():
    """After wake word, listen for command, execute it, push response to browser."""
    try:
        from engine.command import takecommand, run_command, speak
        speak("Yes Sir, how can I help you?")

        # Push "listening" status to browser via API
        try:
            import urllib.request, json as _json
            _push = lambda path, body: urllib.request.urlopen(
                urllib.request.Request(
                    f"http://localhost:{_jarvis_port}{path}",
                    data=_json.dumps(body).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                ), timeout=3
            )
        except Exception:
            _push = None

        time.sleep(1.2)  # wait for TTS to finish saying "Yes Sir"

        query = takecommand()
        if query and query.strip():
            print(f"[HOTWORD] Command: {query}")
            response = run_command(query)
            if response:
                print(f"[HOTWORD] Response: {response}")
        else:
            speak("I didn't catch that. Please try again.")

    except Exception as e:
        print(f"[HOTWORD] Post-wake error: {e}")


def start():
    """Start the hotword listener in a background daemon thread."""
    global _listening
    if _listening:
        print("[HOTWORD] Already running")
        return

    _listening = True
    t = threading.Thread(target=_listen_for_wake_word, daemon=True, name="hotword-listener")
    t.start()
    print("[HOTWORD] Background listener started")
    return t


def stop():
    """Stop the hotword listener."""
    global _listening
    _listening = False
    print("[HOTWORD] Listener stopped")
