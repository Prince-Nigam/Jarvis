"""
hotword.py — Always-On Wake Word Listener for Jarvis
=====================================================
HOW IT WORKS:
  1. Background mein hamesha microphone sun raha hota hai
  2. Jab "Jarvish" / "Hey Jarvis" sune → ACTIVE mode mein aata hai
  3. Active mode mein baar baar commands sunta hai (laptop touch kiye bina)
  4. "Stop" / "Sleep" / "Go to sleep" bolo → wapas wake word mode mein
  5. 30 second silence ke baad bhi auto-sleep ho jaata hai

WAKE WORDS:  "jarvish", "hey jarvis", "ok jarvis", etc.
SLEEP WORDS: "stop", "sleep", "go to sleep", "goodbye", "bye jarvis"
"""

import threading
import time
import os
import ctypes

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# ── Config ─────────────────────────────────────────────────────────────────────
WAKE_WORDS = [
    "wake up jarvis", "wakeup jarvis", "wake jarvis",
    "hey jarvis", "jarvis", "ok jarvis", "hi jarvis",
    "hello jarvis", "activate jarvis",
    "jarvish", "jarves", "javis",
    "wake up jarvish", "wakeup jarvish", "wake jarvish",
    "hey jarvish", "ok jarvish", "hi jarvish", "hello jarvish",
]

# Bolo "stop" ya "sleep" → Jarvis wapas sleep mode mein
SLEEP_WORDS = [
    "stop", "sleep", "go to sleep", "goodbye", "bye",
    "bye jarvis", "bye jarvish", "that's all", "thats all",
    "ok stop", "jarvis stop", "jarvish stop",
]

# Kitne seconds baad auto-sleep (koi command nahi aaya toh)
AUTO_SLEEP_SECONDS = 30

JARVIS_URL  = "http://localhost:8000/index.html"
_jarvis_port = 8000

# ── Global State ───────────────────────────────────────────────────────────────
_listening       = False   # hotword thread running?
_active_mode     = False   # Jarvis command sun raha hai?
_active_mode_lock = threading.Lock()


def set_port(port):
    global _jarvis_port, JARVIS_URL
    _jarvis_port = port
    JARVIS_URL   = f"http://localhost:{port}/index.html"


# ── Sounds ────────────────────────────────────────────────────────────────────

def _beep_wake():
    """Double beep — Jarvis active hua."""
    try:
        import winsound
        winsound.Beep(1000, 150)
        time.sleep(0.05)
        winsound.Beep(1400, 200)
    except Exception:
        pass


def _beep_sleep():
    """Single low beep — Jarvis sleep mode."""
    try:
        import winsound
        winsound.Beep(600, 300)
    except Exception:
        pass


def _beep_listening():
    """Short soft beep — listening for command."""
    try:
        import winsound
        winsound.Beep(900, 100)
    except Exception:
        pass


# ── Window Management ─────────────────────────────────────────────────────────

def _open_jarvis_browser():
    try:
        from engine.window_manager import show_jarvis_window
        show_jarvis_window(JARVIS_URL)
        print(f"[HOTWORD] Jarvis window opened: {JARVIS_URL}")
    except Exception as e:
        print(f"[HOTWORD] Browser open failed: {e}")


# ── Word Detection Helpers ────────────────────────────────────────────────────

def _contains_wake_word(text: str) -> bool:
    text = text.lower().strip()
    for ww in WAKE_WORDS:
        if ww in text:
            return True
    # Fuzzy match — agar koi bhi word mein "jarvis/jarvish" ho
    for w in text.split():
        if any(t in w for t in ["jarvis", "jarvish", "jarves", "javis"]):
            return True
    return False


def _contains_sleep_word(text: str) -> bool:
    text = text.lower().strip()
    for sw in SLEEP_WORDS:
        if sw in text:
            return True
    return False


# ── TTS Wait Helper ───────────────────────────────────────────────────────────

def _wait_for_tts(seconds=1.5):
    """TTS finish hone ka wait karo (queue drain)."""
    time.sleep(seconds)


# ── Main Recognizer ───────────────────────────────────────────────────────────

def _make_recognizer(energy=100, dynamic=False, pause=0.6):
    r = sr.Recognizer()
    r.energy_threshold          = energy
    r.dynamic_energy_threshold  = dynamic
    r.pause_threshold           = pause
    return r


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND LOOP — Active mode mein baar baar commands sunta hai
# ═══════════════════════════════════════════════════════════════════════════════

def _command_loop():
    """
    Jarvis active mode:
    - Continuously microphone se commands sunta hai
    - Har command execute karta hai
    - "Stop"/"Sleep" ya AUTO_SLEEP_SECONDS silence ke baad wapas sleep
    """
    global _active_mode

    from engine.command import takecommand, run_command, speak

    speak("Yes Sir, I am listening. Say stop or sleep to deactivate me.")
    _wait_for_tts(2.5)

    last_command_time = time.time()

    print(f"[HOTWORD] ▶ Active mode — listening for commands (auto-sleep in {AUTO_SLEEP_SECONDS}s)")

    while _active_mode and _listening:
        # ── Auto-sleep check ───────────────────────────────────────────────
        if time.time() - last_command_time > AUTO_SLEEP_SECONDS:
            speak("Going to sleep. Say Jarvis to wake me up.")
            _beep_sleep()
            _wait_for_tts(2)
            with _active_mode_lock:
                _active_mode = False
            print("[HOTWORD] ⏸ Auto-sleep: no command for 30 seconds")
            break

        # ── Listen for command ─────────────────────────────────────────────
        _beep_listening()
        print("[HOTWORD] 👂 Listening for command...")

        query = takecommand()

        if not query or not query.strip():
            # No speech — keep looping (don't reset timer on silence)
            continue

        print(f"[HOTWORD] 🎤 Command heard: '{query}'")
        last_command_time = time.time()

        # ── Sleep command? ─────────────────────────────────────────────────
        if _contains_sleep_word(query):
            speak("Going to sleep Sir. Say Jarvis to wake me up again.")
            _beep_sleep()
            _wait_for_tts(2.5)
            with _active_mode_lock:
                _active_mode = False
            print("[HOTWORD] ⏸ Sleep command received — back to wake word mode")
            break

        # ── Wake word again? (user repeated "hey jarvis") ──────────────────
        if _contains_wake_word(query):
            speak("I am already listening Sir. Give me your command.")
            _wait_for_tts(2)
            continue

        # ── Execute command ────────────────────────────────────────────────
        try:
            response = run_command(query)
            if response:
                print(f"[HOTWORD] ✅ Done: {response}")
        except Exception as e:
            print(f"[HOTWORD] Command error: {e}")
            speak("Sorry, something went wrong.")

        # Small pause before next listen (let TTS finish)
        _wait_for_tts(1.0)


# ═══════════════════════════════════════════════════════════════════════════════
#  WAKE WORD LOOP — Hamesha background mein chalta hai
# ═══════════════════════════════════════════════════════════════════════════════

def _wake_word_loop():
    """
    Always-on background listener:
    - Low energy threshold taaki wake word miss na ho
    - Jab wake word mile → active mode start karo
    """
    global _active_mode

    if sr is None:
        print("[HOTWORD] ❌ speech_recognition not installed — hotword disabled")
        return

    recognizer = _make_recognizer(energy=100, dynamic=False, pause=0.5)

    print("[HOTWORD] 😴 Sleeping... say 'Jarvish' or 'Hey Jarvis' to wake me up")

    try:
        with sr.Microphone() as source:
            # Initial ambient noise adjustment
            recognizer.adjust_for_ambient_noise(source, duration=1.0)

            while _listening:
                # Agar already active mode mein hai toh wait karo
                if _active_mode:
                    time.sleep(0.3)
                    continue

                try:
                    # Short listen window — wake word pakadne ke liye
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=4)

                    try:
                        text = recognizer.recognize_google(audio, language="en-IN")
                        print(f"[HOTWORD] 👂 Heard: '{text}'")

                        if _contains_wake_word(text):
                            print("[HOTWORD] 🔔 WAKE WORD DETECTED!")
                            _beep_wake()
                            _open_jarvis_browser()

                            # Active mode ON
                            with _active_mode_lock:
                                _active_mode = True

                            # Command loop separate thread mein (taaki wake word
                            # listener block na ho)
                            cmd_thread = threading.Thread(
                                target=_command_loop,
                                daemon=True,
                                name="jarvis-command-loop"
                            )
                            cmd_thread.start()

                    except sr.UnknownValueError:
                        pass   # silence — keep going
                    except sr.RequestError as e:
                        print(f"[HOTWORD] Google API error: {e}")
                        time.sleep(2)

                except sr.WaitTimeoutError:
                    pass   # no speech — keep looping
                except Exception as e:
                    print(f"[HOTWORD] Audio error: {e}")
                    time.sleep(0.3)

    except OSError as e:
        print(f"[HOTWORD] ❌ Microphone error: {e}")
    except Exception as e:
        print(f"[HOTWORD] ❌ Fatal error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def start():
    """
    Start the always-on wake word listener in background.
    Call once at startup.
    """
    global _listening
    if _listening:
        print("[HOTWORD] Already running")
        return

    _listening = True
    t = threading.Thread(
        target=_wake_word_loop,
        daemon=True,
        name="hotword-wake-listener"
    )
    t.start()
    print("[HOTWORD] ✅ Always-on listener started — say 'Jarvish' anytime!")
    return t


def stop():
    """Stop the hotword listener completely."""
    global _listening, _active_mode
    _listening   = False
    _active_mode = False
    print("[HOTWORD] ⏹ Listener stopped")


def is_active():
    """Returns True if Jarvis is currently in active/command mode."""
    return _active_mode


def force_activate():
    """
    Manually activate command mode (e.g., from browser mic button).
    Useful when user clicks the mic icon on the Jarvis UI.
    """
    global _active_mode
    if not _active_mode:
        _beep_wake()
        with _active_mode_lock:
            _active_mode = True
        cmd_thread = threading.Thread(
            target=_command_loop,
            daemon=True,
            name="jarvis-command-loop"
        )
        cmd_thread.start()
        print("[HOTWORD] 🎙 Force activated from UI")
