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
WAKE_WORDS = ["wake jarvis", "hey jarvis", "jarvis", "ok jarvis"]
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


def _open_jarvis_browser():
    """Open Jarvis in the default browser."""
    try:
        webbrowser.open(JARVIS_URL)
        print(f"[HOTWORD] Opened Jarvis at {JARVIS_URL}")
    except Exception as e:
        print(f"[HOTWORD] Browser open failed: {e}")


def _contains_wake_word(text: str) -> bool:
    text = text.lower().strip()
    for ww in WAKE_WORDS:
        if ww in text:
            return True
    return False


def _listen_for_wake_word():
    """
    Continuously listens for the wake word using the microphone.
    Uses short 3-second windows to keep it responsive.
    """
    global _jarvis_active

    if sr is None:
        print("[HOTWORD] speech_recognition not installed — hotword disabled")
        return

    recognizer = sr.Recognizer()
    recognizer.energy_threshold          = 300
    recognizer.dynamic_energy_threshold  = True
    recognizer.pause_threshold           = 0.6

    print("[HOTWORD] Listening for wake word... (say 'hey jarvis' or 'wake jarvis')")

    while _listening:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

            try:
                text = recognizer.recognize_google(audio, language="en-in")
                print(f"[HOTWORD] Heard: {text}")

                if _contains_wake_word(text):
                    print("[HOTWORD] Wake word detected!")
                    _play_activation_sound()
                    _open_jarvis_browser()
                    _jarvis_active = True
                    # Give Jarvis time to load, then start listening for commands
                    time.sleep(3)
                    _handle_post_wake()

            except sr.UnknownValueError:
                pass   # silence / unrecognised — keep looping
            except sr.RequestError as e:
                print(f"[HOTWORD] Google API error: {e}")
                time.sleep(5)

        except sr.WaitTimeoutError:
            pass   # no speech in 3s, keep looping
        except OSError as e:
            print(f"[HOTWORD] Mic error: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"[HOTWORD] Unexpected: {e}")
            time.sleep(1)


def _handle_post_wake():
    """After wake word, listen for a command and execute it."""
    try:
        from engine.command import takecommand, run_command, speak
        speak("Yes Sir, how can I help you?")
        time.sleep(0.5)
        query = takecommand()
        if query:
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
