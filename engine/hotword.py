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
import difflib

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# #region debug-point helpers:wakeup-jarvish-no-response
import json as _dbg_json, urllib.request as _dbg_req, os as _dbg_os
_DBG_P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.dbg', 'wakeup-jarvish-no-response.env')
_DBG_U, _DBG_S = 'http://127.0.0.1:7777/event', 'wakeup-jarvish-no-response'
try:
    with open(_DBG_P) as _f: _c = _f.read()
    for _l in _c.split('\n'):
        if _l.startswith('DEBUG_SERVER_URL='): _DBG_U = _l.split('=',1)[1].strip()
        elif _l.startswith('DEBUG_SESSION_ID='): _DBG_S = _l.split('=',1)[1].strip()
except Exception: pass
_DBG_ITER = 0
def _dbg(hid, msg, **kw):
    global _DBG_ITER; _DBG_ITER += 1
    try:
        d = {"sessionId":_DBG_S,"runId":"post-fix","hypothesisId":hid,"location":f"hotword.py","msg":f"[DEBUG] {msg}","data":{"iter":_DBG_ITER, **kw},"ts":int(__import__('time').time()*1000)}
        r = _dbg_req.Request(_DBG_U, data=_dbg_json.dumps(d).encode(), headers={"Content-Type":"application/json"})
        _dbg_req.urlopen(r, timeout=0.6).read()
    except Exception: pass
# #endregion

# ── Config ─────────────────────────────────────────────────────────────────────

# ── LEVEL 0 (DEEP SLEEP) — sirf ye hi phrase sun ke online aayega ──
WAKE_WORDS = [
    "wakeup jarvish",
    "wake up jarvish",
    "wake jarvish",
    "wakeupjarvish",
    "wakeup jarvis",
    "wake up jarvis",
    "wake jarvis",
    "wakeupjarvis",
    "wakeup jarwish",
    "wake up jarwish",
    "wakeup jurvish",
    "wake up jurvish",
    "wakeup jervish",
    "wake up jervish",
    "wakeup jarbish",
    "wake up jarbish",
    "wakeup garvish",
    "wake up garvish",
    "wakeup garvis",
    "wake up garvis",
    "wakeup jarvees",
    "wake up jarvees",
    "wakeup jarveesh",
    "wake up jarveesh",
    "wakeup jarviss",
    "wake up jarviss",
    "wakeup javis",
    "wake up javis",
    "wakeup javish",
    "wake up javish",
    "wakeup jervis",
    "wake up jervis",
    "wakeup gervish",
    "wake up gervish",
    "ok wakeup jarvish",
    "okay wake up jarvish",
    "oh wakeup jarvish",
    "the wakeup jarvish",
    # ── "jarvish wakeup" order bhi kaam kare ──
    "jarvish wakeup",
    "jarvish wake up",
    "jarvis wakeup",
    "jarvis wake up",
    "jarwish wakeup",
    "jervish wakeup",
]

_WAKE_SEEDS = []

# ── LEVEL 1 (IDLE) — sirf "jarvish" naam sun ke command-ready hoga ──
# (User: "jarvish" bolo → ready for command)
NAME_TRIGGER_WORDS = [
    "jarvish", "jarvis", "jarwish", "jervish", "jarbish",
    "garvish", "garvis", "jarvees", "jarveesh", "jarviss",
    "javis", "javish", "jervis", "gervish", "jurvish",
    "jarvis ji", "jarvish ji", "hey jarvis", "hey jarvish",
    "ok jarvis", "ok jarvish", "okay jarvis", "okay jarvish",
    "o jarvis", "o jarvish",
]

_NAME_SEEDS = [
    "jarvish", "jarvis", "jarwish", "jervish", "jurvish",
    "garvish", "javish", "jervis", "gervish",
]

# ── Sleep / Stop words (koi bhi level se deep sleep mein jao) ──
# ── Sleep trigger — sirf "jarvish shutdown" se deep sleep ──
SLEEP_WORDS = [
    "jarvish shutdown",
    "jarvis shutdown",
    "jarwish shutdown",
    "jervish shutdown",
    "hey jarvish shutdown",
    "hey jarvis shutdown",
    "ok jarvish shutdown",
    "okay jarvish shutdown",
]

# Level 1 idle mein itni silence ke baad auto deep sleep
IDLE_AUTO_SLEEP_SECONDS = 120

# Level 2 command mode mein timeout (command nahi suna toh wapas idle)
COMMAND_TIMEOUT_SECONDS = 20

JARVIS_URL  = "http://localhost:8000/index.html"
_jarvis_port = 8000

# ── States ─────────────────────────────────────────────────────────────────────
STATE_DEEP_SLEEP = "deep_sleep"   # Level 0: only "wakeup jarvish"
STATE_IDLE       = "idle"         # Level 1: only "jarvish" naam
STATE_COMMAND    = "command"      # Level 2: actual command

# ── Global State ───────────────────────────────────────────────────────────────
_listening       = False
_state           = STATE_DEEP_SLEEP
_state_lock      = threading.Lock()


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

def _fuzzy_ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _contains_wake_word(text: str) -> bool:
    """
    LEVEL 0 — STRICT wake detector.
    True jab:
      - WAKE_WORDS mein koi phrase match ho, OR
      - "wake/wakeup" token + "jarvish" token dono hon
    """
    text = text.lower().strip()
    if not text:
        return False

    # ── Direct WAKE_WORDS list check (fastest path) ──────────────────────
    for ww in WAKE_WORDS:
        if ww in text:
            return True

    words = [w.strip("?!.,;:") for w in text.split() if w.strip("?!.,;:")]

    def _has_wake_token(ws):
        for w in ws:
            for seed in ("wake", "wakeup", "woke", "wek", "wakeups"):
                if seed in w:
                    return True
                if 3 <= len(w) <= 8 and _fuzzy_ratio(w, seed) >= 0.78:
                    return True
        return False

    def _has_jarvish_token(ws):
        seeds = ["jarvish", "jarvis", "jarwish", "jervish", "jurvish",
                 "garvish", "javish", "jervis", "gervish", "jarbish",
                 "jarvees", "jarveesh", "jarviss", "javis", "garvis"]
        joined_all = "".join(ws)
        for seed in seeds:
            if seed in joined_all:
                return True
        for w in ws:
            for seed in seeds:
                if seed in w:
                    return True
                if 4 <= len(w) <= 14 and _fuzzy_ratio(w, seed) >= 0.72:
                    return True
        if len(ws) >= 2:
            joined_pairs = []
            for i in range(len(ws) - 1):
                joined_pairs.append(ws[i] + ws[i + 1])
            for j in joined_pairs:
                for seed in seeds:
                    if seed in j:
                        return True
                    if 5 <= len(j) <= 12 and _fuzzy_ratio(j, seed) >= 0.72:
                        return True
        return False

    # ── Token-level check: wake token + jarvish token dono chahiye ───────
    if _has_wake_token(words) and _has_jarvish_token(words):
        return True

    # ── Fuzzy full-phrase match ───────────────────────────────────────────
    if len(text) >= 8:
        for ww in WAKE_WORDS:
            if " " in ww and abs(len(ww) - len(text)) <= 8:
                if _fuzzy_ratio(text, ww) >= 0.70:
                    return True

    return False


def _contains_name_trigger(text: str) -> bool:
    """LEVEL 1 detector — sirf 'jarvish' naam (short phrases, <=2 words)."""
    text = text.lower().strip()
    if not text:
        return False
    words = text.split()

    if len(words) > 2:
        return False

    for nw in NAME_TRIGGER_WORDS:
        if nw == text:
            return True
        if nw in text and len(words) <= 2:
            return True

    for w in words:
        for seed in _NAME_SEEDS:
            if seed in w and len(w) <= len(seed) + 3:
                return True

    joined_pairs = []
    for i in range(len(words) - 1):
        joined_pairs.append(words[i] + words[i + 1])
    for j in joined_pairs:
        for seed in _NAME_SEEDS:
            if seed in j:
                return True
            if 5 <= len(j) <= 12 and _fuzzy_ratio(j, seed) >= 0.75:
                return True

    for w in words:
        if len(w) < 4 or len(w) > 14:
            continue
        for seed in _NAME_SEEDS:
            if _fuzzy_ratio(w, seed) >= 0.77:
                return True

    return False


def _contains_sleep_word(text: str) -> bool:
    """
    Sirf "jarvish shutdown" (aur variants) se True.
    Koi aur phrase deep sleep trigger nahi karega.
    """
    text = text.lower().strip()
    if not text:
        return False
    for sw in SLEEP_WORDS:
        if sw in text:
            return True
    return False


# ── TTS Wait Helper ───────────────────────────────────────────────────────────

def _wait_for_tts(seconds=1.5):
    """TTS finish hone ka wait karo (queue drain)."""
    time.sleep(seconds)


# ── Main Recognizer ───────────────────────────────────────────────────────────

def _make_recognizer(energy=20, dynamic=True, pause=0.7):
    """
    HIGH SENSITIVITY recognizer — halki voice ko capture karega.
    - Very low energy threshold (20) → soft speech bhi detect hogi
    - Dynamic energy OFF for wake loop (ON for command loop)
    - Longer pause (0.7s) → slow speech ko cut nahi karega
    """
    r = sr.Recognizer()
    r.energy_threshold                     = energy
    r.dynamic_energy_threshold             = dynamic
    r.dynamic_energy_adjustment_damping    = 0.15
    r.dynamic_energy_ratio                 = 1.05   # was 1.3 — bahut slow badhega ab
    r.pause_threshold                      = pause
    r.phrase_threshold                     = 0.05   # was 0.1 — chhoti phrases bhi catch hogi
    r.non_speaking_duration                = 0.3    # was 0.5
    r.operation_timeout                    = None   # no operation timeout
    return r


def _recognize_google_multi_lang(audio) -> str:
    """
    Try Google SR with multiple languages:
    1) en-IN (Indian English) first
    2) hi-IN (Hindi) fallback for Hinglish phrases
    Returns first non-empty text OR raises the original exception.
    """
    last_err = None
    for lang in ("en-IN", "hi-IN", "en-US"):
        try:
            text = sr.Recognizer().recognize_google(audio, language=lang)
            if text and text.strip():
                return text
        except sr.UnknownValueError as e:
            last_err = e
        except sr.RequestError as e:
            last_err = e
            # On first RequestError (network issue) still try other languages —
            # but RequestErrors are global so break early and re-raise last.
            break
        except Exception as e:
            last_err = e
    if last_err is not None:
        raise last_err
    raise sr.UnknownValueError()


# ═══════════════════════════════════════════════════════════════════════════════
#  IDLE + COMMAND LOOP (Levels 1 & 2) — runs inside its own thread
# ═══════════════════════════════════════════════════════════════════════════════

def _idle_command_loop():
    """
    2-Level inner loop:
      STATE_IDLE    — sirf "jarvish" naam sunta hai
      STATE_COMMAND — ek command sunta hai, execute karta hai, wapas IDLE
    "wakeup jarvish" ke baad yahan aata hai STATE_IDLE se.
    """
    global _state
    from engine.command import takecommand, run_command, speak

    last_activity = time.time()
    print("[HOTWORD] 🟡 IDLE — 'Jarvish' bol ke command do")

    while _listening:
        with _state_lock:
            current = _state
        if current == STATE_DEEP_SLEEP:
            break

        # ── Auto sleep after 2 min silence ───────────────────────────────
        if time.time() - last_activity > IDLE_AUTO_SLEEP_SECONDS:
            print("[HOTWORD] 💤 Idle timeout — deep sleep")
            speak("Bahut der ho gayi. So raha hoon. 'Wakeup Jarvish' bol ke wapas bulao.")
            _beep_sleep()
            _wait_for_tts(3)
            with _state_lock:
                _state = STATE_DEEP_SLEEP
            break

        # ════════════════════════════════════════════════════════════════
        #  STATE_IDLE — sirf "jarvish" naam suno, phir command mode mein jao
        # ════════════════════════════════════════════════════════════════
        if current == STATE_IDLE:
            print("[HOTWORD] 🟡 IDLE — bolo 'Jarvish' to give a command...")
            heard = takecommand()
            if not heard or not heard.strip():
                continue

            last_activity = time.time()
            heard_lower = heard.lower().strip()
            print(f"[HOTWORD] 👂 (idle) Heard: '{heard_lower}'")

            # Sleep words — wapas deep sleep
            if _contains_sleep_word(heard_lower):
                speak("Theek hai Sir. So raha hoon. 'Wakeup Jarvish' bol ke wapas bulao.")
                _beep_sleep()
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_DEEP_SLEEP
                break

            # Wake word dobara bola — already online
            if _contains_wake_word(heard_lower):
                speak("Haan Sir, main already online hoon. 'Jarvish' bol ke command do.")
                _wait_for_tts(2.5)
                continue

            # "jarvish" + seedha command ek saath (e.g. "jarvish open youtube")
            _name_prefixes = (
                "jarvish ", "jarvis ", "jarwish ", "jervish ", "jurvish ",
                "garvish ", "javish ", "jervis ", "gervish ", "jarbish ",
                "hey jarvish ", "hey jarvis ", "ok jarvish ", "ok jarvis ",
                "okay jarvish ", "okay jarvis ", "o jarvish ", "o jarvis ",
            )
            clean_q = heard_lower
            stripped = False
            for p in _name_prefixes:
                if clean_q.startswith(p):
                    clean_q = clean_q[len(p):].strip()
                    stripped = True
                    break
            for s in (" jarvish", " jarvis", " jarwish", " jervish"):
                if clean_q.endswith(s):
                    clean_q = clean_q[:-len(s)].strip()
                    break

            # Sirf naam bola (no command after it) → COMMAND mode
            if _contains_name_trigger(heard_lower) and not clean_q:
                print("[HOTWORD] 🔔 Naam suna — COMMAND mode")
                speak("Haan Sir, boliye.")
                _wait_for_tts(1.8)
                with _state_lock:
                    _state = STATE_COMMAND
                continue

            # Naam + command combined → seedha execute
            if stripped and clean_q:
                print(f"[HOTWORD] ⚡ Combined (naam+command): '{clean_q}'")
                try:
                    run_command(clean_q)
                except Exception as e:
                    print(f"[HOTWORD] run_command error: {e}")
                    speak("Maaf kijiye, problem aayi.")
                _wait_for_tts(1.2)
                # Wapas IDLE — user ko "jarvish" phir bolna hoga
                continue

            # Random baat — naam nahi suna, ignore
            print("[HOTWORD] (idle) Naam nahi suna — ignoring")
            continue

        # ════════════════════════════════════════════════════════════════
        #  STATE_COMMAND — ek command suno aur execute karo
        # ════════════════════════════════════════════════════════════════
        if current == STATE_COMMAND:
            print("[HOTWORD] 🟢 COMMAND — boliye aapka command...")
            query = takecommand()

            if not query or not query.strip():
                # Timeout — wapas IDLE
                speak("Koi command nahi suna. 'Jarvish' bol ke dobara try karo.")
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_IDLE
                continue

            last_activity = time.time()
            query_lower = query.lower().strip()
            print(f"[HOTWORD] 🎤 Command: '{query_lower}'")

            # Sleep
            if _contains_sleep_word(query_lower):
                speak("Theek hai Sir. So raha hoon. 'Wakeup Jarvish' bol ke wapas bulao.")
                _beep_sleep()
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_DEEP_SLEEP
                break

            # Naam bola command ke jagah
            if _contains_name_trigger(query_lower) and len(query_lower.split()) <= 2:
                speak("Haan Sir, main sun raha hoon. Command boliye.")
                _wait_for_tts(2)
                continue

            # Execute command
            try:
                run_command(query_lower)
            except Exception as e:
                print(f"[HOTWORD] run_command error: {e}")
                speak("Maaf kijiye, command mein problem aayi.")

            _wait_for_tts(1.2)
            # Command done → wapas IDLE (user ko "jarvish" phir bolna hoga)
            with _state_lock:
                _state = STATE_IDLE
            print("[HOTWORD] 🟡 Back to IDLE — 'Jarvish' bol ke agla command do")

    # Thread exits
    with _state_lock:
        if _state != STATE_DEEP_SLEEP:
            _state = STATE_DEEP_SLEEP


# ═══════════════════════════════════════════════════════════════════════════════
#  WAKE WORD LOOP (Level 0) — hamesha background mein, mic hold karta hai
# ═══════════════════════════════════════════════════════════════════════════════

def _wake_word_loop():
    """
    LEVEL 0 — DEEP SLEEP listener:
    - Sirf "wakeup jarvish" type phrases sunta hai
    - Detect hone par: speak("Jarvis online...") + browser kholo + state = IDLE
    - Inner thread (_idle_command_loop) start karo
    - Jab tak IDLE/COMMAND hai, MIC release rakho (takecommand ko chahiye)
    - Wapas deep sleep aane par, mic fir se grab karo
    """
    global _state
    # #region debug-point A:wake-loop-entry
    _dbg('A', 'wake_loop_thread_ENTERED', sr_available=(sr is not None), listening_flag=_listening)
    # #endregion

    if sr is None:
        _dbg('A', 'speech_recognition_IMPORT_MISSING_hotword_disabled', error='sr is None')
        print("[HOTWORD] ❌ speech_recognition not installed — hotword disabled")
        return

    # Wake loop ke liye: calibrate karo phir sun lo
    recognizer = _make_recognizer(energy=300, dynamic=True, pause=0.8)

    print("[HOTWORD] 😴 DEEP SLEEP — sirf 'Wakeup Jarvish' hi kaam karega")
    _silence_counter = 0

    while _listening:
        with _state_lock:
            st = _state

        # ── IDLE / COMMAND: mic chhod do, baaki thread handle karega ───
        if st != STATE_DEEP_SLEEP:
            time.sleep(0.3)
            continue

        # ── DEEP SLEEP: mic open, listen for "wakeup jarvish" ──────────
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"[HOTWORD] 🎤 Listening (energy={recognizer.energy_threshold:.0f}) — bolo 'Wakeup Jarvish'...")

                while _listening:
                    with _state_lock:
                        if _state != STATE_DEEP_SLEEP:
                            break
                    try:
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

                        try:
                            text = _recognize_google_multi_lang(audio)
                            print(f"[HOTWORD] 👂 (deep) Heard: '{text}'")
                            _silence_counter = 0

                            _matched = _contains_wake_word(text)
                            print(f"[HOTWORD] Wake match: {_matched}")

                            if _matched:
                                print("[HOTWORD] 🔔 DEEP SLEEP WAKE DETECTED!")
                                _beep_wake()

                                try:
                                    from engine.command import speak as _speak
                                    _speak("Jarvis online. 'Jarvish' bol ke command do.")
                                except Exception:
                                    pass
                                try:
                                    _open_jarvis_browser()
                                except Exception as _be:
                                    print(f"[HOTWORD] Browser open (non-fatal): {_be}")

                                # IDLE mein jao — user "jarvish" bol ke command dega
                                with _state_lock:
                                    _state = STATE_IDLE

                                t = threading.Thread(
                                    target=_idle_command_loop,
                                    daemon=True,
                                    name="jarvis-idle-command"
                                )
                                t.start()
                                break

                        except sr.UnknownValueError:
                            _silence_counter += 1
                            if _silence_counter % 15 == 0:
                                print(f"[HOTWORD] 💤 Listening... (noise/silence x{_silence_counter}) — bolo 'Wakeup Jarvish'")
                            _dbg('B', 'UnknownValueError_SWALLOWED_silence_or_unintelligible', reason='multi_lang_all_unknown', current_energy=recognizer.energy_threshold, silence_count=_silence_counter)
                        except sr.RequestError as e:
                            _dbg('D', 'Google_SR_RequestError', error=str(e), error_type=type(e).__name__)
                            print(f"[HOTWORD] ⚠️ Google API error: {e} — retrying...")
                            time.sleep(2)

                    except sr.WaitTimeoutError:
                        _dbg('B', 'WaitTimeoutError_no_speech_in_5s_window', timeout=5, current_energy=recognizer.energy_threshold)
                    except Exception as e:
                        _dbg('A', 'INNER_audio_loop_Exception', error=str(e), error_type=type(e).__name__)
                        print(f"[HOTWORD] Audio error: {e}")
                        time.sleep(0.3)

        except OSError as e:
            _dbg('A', 'OUTER_OSError_MICROPHONE', error=str(e), error_type=type(e).__name__)
            print(f"[HOTWORD] ❌ Microphone error: {e} — retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            _dbg('A', 'OUTER_FATAL_Exception_in_wake_loop', error=str(e), error_type=type(e).__name__, traceback=__import__('traceback').format_exc()[-800:])
            print(f"[HOTWORD] ❌ Fatal error: {e} — retrying in 5s...")
            time.sleep(5)


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def start():
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
    _dbg('A', 'hotword_start_called_thread_started', listening_flag=_listening, thread_alive=t.is_alive(), thread_name=t.name)
    print("[HOTWORD] ✅ Listener started — bolo 'Wakeup Jarvish' to bring online!")
    return t


def stop():
    """Stop the hotword listener completely."""
    global _listening, _state
    _listening = False
    with _state_lock:
        _state = STATE_DEEP_SLEEP
    print("[HOTWORD] ⏹ Listener stopped")


def is_active():
    """Returns True if Jarvis is online (idle or command mode)."""
    return _state != STATE_DEEP_SLEEP


def force_activate():
    """
    Manually activate (browser mic button). Goes to IDLE mode.
    User "jarvish" bol ke command de sakta hai.
    """
    global _state
    if _state == STATE_DEEP_SLEEP:
        _beep_wake()
        try:
            from engine.command import speak as _speak
            _speak("Jarvis online. 'Jarvish' bol ke command do.")
        except Exception:
            pass
        try:
            _open_jarvis_browser()
        except Exception:
            pass
        with _state_lock:
            _state = STATE_IDLE
        t = threading.Thread(
            target=_idle_command_loop,
            daemon=True,
            name="jarvis-idle-command"
        )
        t.start()
        print("[HOTWORD] Force activated → IDLE")
