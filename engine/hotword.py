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
SLEEP_WORDS = [
    "stop", "sleep", "go to sleep", "goodbye", "bye",
    "bye jarvis", "bye jarvish", "that's all", "thats all",
    "ok stop", "jarvis stop", "jarvish stop",
    "shutdown", "shut down", "shut it down",
    "jarvis shutdown", "jarvish shutdown",
    "jarvis shut down", "jarvish shut down",
    "power off", "power off karo", "band kar do",
    "bas karo", "bas kar", "band kar", "band karo",
    "chup raho", "chup ho ja", "so jao", "so ja",
    "roko", "ruk jao", "ruk ja",
    "shutdown karo", "shutdown ho ja",
    "shutdown ho jao", "shutdown kar do",
    "shut down karo", "shut down kar do",
    "shut down ho ja", "shut down ho jao",
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
    Sirf tab True jab DONO conditions hon:
      1. "wake" type token ho (wake, wakeup, woke, wek)
      2. "jarvish" type token ho (jarvish/jarvis/...)
    Sirf "jarvish" akela ya "hey jarvis" — FALSE.
    """
    text = text.lower().strip()
    if not text:
        return False
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

    if not _has_wake_token(words):
        return False
    if not _has_jarvish_token(words):
        return False

    for ww in WAKE_WORDS:
        if ww in text:
            return True

    joined_pairs = []
    for i in range(len(words) - 1):
        joined_pairs.append(words[i] + words[i + 1])
    for i in range(len(words) - 2):
        joined_pairs.append(words[i] + words[i + 1] + words[i + 2])
    for j in joined_pairs:
        for seed in ("jarvish", "jarvis", "jarwish"):
            if seed in j:
                return True

    if len(text) >= 10:
        for ww in WAKE_WORDS:
            if " " in ww and abs(len(ww) - len(text)) <= 8:
                if _fuzzy_ratio(text, ww) >= 0.70:
                    return True

    return True


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
    text = text.lower().strip()
    if not text:
        return False
    words = text.split()

    def _has_non_sleep_context(ws):
        for w in ws:
            if w in ("open", "show", "kholo", "khol", "dikhao", "dikhana",
                     "start", "chalu", "launch", "dialog", "menu", "setting"):
                return True
        return False

    if _has_non_sleep_context(words):
        return False

    for sw in SLEEP_WORDS:
        if sw in text:
            return True
    for w in text.split():
        for sw in SLEEP_WORDS:
            if " " not in sw and 3 <= len(w) <= 8 and 3 <= len(sw) <= 8:
                if _fuzzy_ratio(w, sw) >= 0.78:
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
    - Dynamic energy with aggressive damping → noise ke saath adapt karega
    - Longer pause (0.7s) → slow speech ko cut nahi karega
    - Longer phrase threshold → chhote phrases miss nahi honge
    """
    r = sr.Recognizer()
    r.energy_threshold                     = energy
    r.dynamic_energy_threshold             = dynamic
    r.dynamic_energy_adjustment_damping    = 0.15
    r.dynamic_energy_ratio                 = 1.3
    r.pause_threshold                      = pause
    r.phrase_threshold                     = 0.1
    r.non_speaking_duration                = 0.5
    r.operation_timeout                    = 15
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
    3-Level State Machine (inner thread, holds NO microphone itself):
      STATE_IDLE    (Level 1) — listens for just "jarvish" naam
      STATE_COMMAND (Level 2) — listens for actual user command, executes, speaks,
                                then immediately wapas STATE_IDLE
    takecommand() khud mic open/close karta hai — outer loop ka mic nahi chahiye.
    """
    from engine.command import takecommand, run_command, speak

    last_activity = time.time()
    print(f"[HOTWORD] 🟡 IDLE mode — bolo 'Jarvish' to give command")

    while _listening:
        with _state_lock:
            current = _state
        if current == STATE_DEEP_SLEEP:
            break

        # ── Idle auto deep-sleep (2 min no activity) ─────────────────────
        if current == STATE_IDLE:
            if time.time() - last_activity > IDLE_AUTO_SLEEP_SECONDS:
                print("[HOTWORD] 💤 Idle timeout — going deep sleep")
                speak("Long time no command — going to sleep. Say wakeup jarvish to wake me up again.")
                _beep_sleep()
                _wait_for_tts(3)
                with _state_lock:
                    _state = STATE_DEEP_SLEEP
                break

        # ── STATE_IDLE: suno "jarvish" naam YA "jarvish + command" combined ──
        if current == STATE_IDLE:
            print("[HOTWORD] 🟡 IDLE — bolo 'Jarvish' ya seedha 'Jarvish <command>'...")
            heard = takecommand()
            if not heard or not heard.strip():
                continue
            last_activity = time.time()
            heard_lower = heard.lower().strip()
            print(f"[HOTWORD] 👂 (idle) Heard: '{heard_lower}'")

            if _contains_sleep_word(heard_lower):
                speak("Going to sleep Sir. Say wakeup jarvish to wake me up again.")
                _beep_sleep()
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_DEEP_SLEEP
                print("[HOTWORD] ⏸ Deep sleep — only 'wakeup jarvish' will work now")
                break

            if _contains_wake_word(heard_lower):
                speak("Main already online hoon Sir. Bas 'Jarvish' boliye — ya seedha 'Jarvish command_ka naam' boliye.")
                _wait_for_tts(3.5)
                continue

            if _contains_name_trigger(heard_lower):
                print("[HOTWORD] 🔔 NAME TRIGGER (short) — switching to COMMAND listen mode")
                _beep_listening()
                speak("Haan Sir, boliye.")
                _wait_for_tts(1.8)
                with _state_lock:
                    _state = STATE_COMMAND
                continue

            # ══════════════════════════════════════════════════════════════
            #  FIX: "Jarvis open YouTube" jaisa COMBINED query (3+ words)
            #  with jarvis naam somewhere in it → naam hata ke DIRECT command execute
            # ══════════════════════════════════════════════════════════════
            def _has_any_name_seed(txt):
                seeds = ("jarvish","jarvis","jarwish","jervish","jurvish",
                         "garvish","javish","jervis","gervish","jarbish",
                         "jarvees","jarveesh","jarviss","javis","garvis")
                words = txt.replace("?", "").replace("!", "").replace(".", "").split()
                joined_all = "".join(words)
                for s in seeds:
                    if s in joined_all:
                        return True
                for w in words:
                    for s in seeds:
                        if s in w:
                            return True
                        if 4 <= len(w) <= 14:
                            import difflib as _dl
                            if _dl.SequenceMatcher(None, w, s).ratio() >= 0.75:
                                return True
                if len(words) >= 2:
                    for i in range(len(words)-1):
                        pair = words[i] + words[i+1]
                        for s in seeds:
                            if s in pair:
                                return True
                return False

            words = heard_lower.split()
            if len(words) >= 3 and _has_any_name_seed(heard_lower):
                print("[HOTWORD] ⚡ COMBINED QUERY detected (naam + command) — extracting and executing directly")
                _beep_listening()
                cleanup_prefixes = (
                    "jarvish ", "jarvis ", "jarwish ", "jervish ", "jurvish ",
                    "garvish ", "javish ", "jervis ", "gervish ", "jarbish ",
                    "jarvees ", "jarveesh ", "jarviss ", "javis ", "garvis ",
                    "hey jarvish ", "hey jarvis ", "ok jarvish ", "ok jarvis ",
                    "o jarvish ", "o jarvis ", "okay jarvish ", "okay jarvis ",
                    "listen jarvish ", "listen jarvis ", "sun jarvish ", "sun jarvis ",
                    "suna jarvish ", "suna jarvis ",
                )
                query_clean = heard_lower
                for p in cleanup_prefixes:
                    if query_clean.startswith(p):
                        query_clean = query_clean[len(p):]
                        break
                suffixes = (" jarvish", " jarvis", " jarwish", " jervish", " garvish")
                for s in suffixes:
                    if query_clean.endswith(s):
                        query_clean = query_clean[:-len(s)]
                        break
                mid_removals = (" jarvish ", " jarvis ", " jarwish ", " jervish ",
                                " garvish ", " javish ", " jervis ")
                for mr in mid_removals:
                    query_clean = query_clean.replace(mr, " ")
                query_clean = " ".join(query_clean.split()).strip()

                if not query_clean or len(query_clean.split()) < 1:
                    print("[HOTWORD] Only naam extracted, no command — asking user...")
                    speak("Haan Sir, boliye — kya karna hai?")
                    _wait_for_tts(2.2)
                    with _state_lock:
                        _state = STATE_COMMAND
                    continue

                print(f"[HOTWORD] 🎤 Extracted command: '{query_clean}'")
                # Execute DIRECTLY (no second listen needed)
                try:
                    response = run_command(query_clean) or ""
                except Exception as e:
                    print(f"[HOTWORD] Combined run_command error: {e}")
                    speak("Maaf kijiye, command execute mein problem aayi.")
                    _wait_for_tts(2.5)
                    continue
                print(f"[HOTWORD] ✅ Done (combined): {response}")
                _wait_for_tts(1.2)
                continue

            # Naam nahi tha, sirf random baat — ignore
            print("[HOTWORD] (idle) Naam nahi suna — ignoring")
            continue

        # ── STATE_COMMAND: suno actual command ───────────────────────────
        if current == STATE_COMMAND:
            print("[HOTWORD] 🟢 COMMAND — listening for your command...")
            start_ts = time.time()
            query = ""
            while time.time() - start_ts < COMMAND_TIMEOUT_SECONDS:
                piece = takecommand()
                if piece and piece.strip():
                    query = piece
                    break
            if not query:
                print("[HOTWORD] ⏱ No command heard — back to idle")
                speak("Koi command nahi suna. Dobara 'Jarvish' boliye.")
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_IDLE
                continue

            last_activity = time.time()
            print(f"[HOTWORD] 🎤 Command: '{query}'")

            if _contains_sleep_word(query):
                speak("Going to sleep Sir. Say wakeup jarvish to wake me up again.")
                _beep_sleep()
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_DEEP_SLEEP
                print("[HOTWORD] ⏸ Deep sleep")
                break

            if _contains_wake_word(query):
                speak("Main abhi bhi listening hoon Sir. Aap apna command bol sakte hain.")
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_IDLE
                continue

            if _contains_name_trigger(query) and len(query.split()) <= 3:
                speak("Haan Sir, main yahin hoon. Apna command boliye.")
                _wait_for_tts(2.5)
                continue

            # ── Execute command ─────────────────────────────────────────
            # NOTE: All command paths (desktop_control.py, features.py,
            # and run_command branches) already call speak() internally
            # for the final result. We don't speak(response) here to
            # avoid double-speaking.
            try:
                response = run_command(query) or ""
            except Exception as e:
                print(f"[HOTWORD] run_command error: {e}")
                speak("Maaf kijiye, command execute mein problem aayi.")
                _wait_for_tts(2.5)
                with _state_lock:
                    _state = STATE_IDLE
                continue

            print(f"[HOTWORD] ✅ Done: {response}")
            _wait_for_tts(1.2)
            with _state_lock:
                _state = STATE_IDLE
            print("[HOTWORD] 🟡 Back to IDLE — bolo 'Jarvish' for next command")

    # Thread exits — ensure state is deep_sleep (if not already)
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
    # #region debug-point A:wake-loop-entry
    _dbg('A', 'wake_loop_thread_ENTERED', sr_available=(sr is not None), listening_flag=_listening)
    # #endregion

    if sr is None:
        _dbg('A', 'speech_recognition_IMPORT_MISSING_hotword_disabled', error='sr is None')
        print("[HOTWORD] ❌ speech_recognition not installed — hotword disabled")
        return

    recognizer = _make_recognizer(energy=20, dynamic=True, pause=0.7)

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
                _dbg('A', 'sr_Microphone_BLOCK_ENTERED_ok', source_type=type(source).__name__, initial_energy=recognizer.energy_threshold, pause=recognizer.pause_threshold, dynamic=recognizer.dynamic_energy_threshold)
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                if recognizer.energy_threshold > 30:
                    recognizer.energy_threshold = 20
                _dbg('B', 'ambient_noise_adjust_done_after_1s_HIGH_SENSITIVITY', post_adjust_energy=recognizer.energy_threshold, dynamic_energy=recognizer.dynamic_energy_threshold, damping=recognizer.dynamic_energy_adjustment_damping, ratio=recognizer.dynamic_energy_ratio)
                print(f"[HOTWORD] 🎤 Mic ready (HIGH SENSITIVITY, energy={recognizer.energy_threshold:.0f}) — bolo 'Wakeup Jarvish'...")

                while _listening:
                    with _state_lock:
                        if _state != STATE_DEEP_SLEEP:
                            break
                    try:
                        audio = recognizer.listen(source, timeout=8, phrase_time_limit=8)
                        _dbg('B', 'listen_call_SUCCESS_audio_captured_HIGH_SENS', audio_duration_sec=getattr(audio,'frame_data',None) and round(len(audio.frame_data)/(audio.sample_rate*audio.sample_width),2) if audio else 0, current_energy=recognizer.energy_threshold)

                        try:
                            text = _recognize_google_multi_lang(audio)
                            print(f"[HOTWORD] 👂 (deep) Heard: '{text}'")
                            _silence_counter = 0
                            _dbg('C', 'recognize_google_multi_RETURNED_TEXT', raw_text=text, text_lower=text.lower(), word_count=len(text.split()))

                            _matched = _contains_wake_word(text)
                            _dbg('C', 'wake_word_match_RESULT', match=_matched, text=text.lower().strip(), words=text.lower().split())

                            if _matched:
                                print("[HOTWORD] 🔔 DEEP SLEEP WAKE DETECTED!")
                                _dbg('E', 'wake_DETECTED_about_to_call_beep_and_browser_and_speak_ready', text=text.lower())
                                _beep_wake()
                                _dbg('E', 'beep_wake_FINISHED_no_error', text=text.lower())

                                try:
                                    from engine.command import speak as _speak
                                    _speak("Jarvis online, command ke liye ready hai.")
                                except Exception:
                                    pass
                                try:
                                    _open_jarvis_browser()
                                except Exception as _be:
                                    print(f"[HOTWORD] Browser open (non-fatal): {_be}")
                                _dbg('E', '_open_jarvis_browser_AND_ready_TTS_done', url=JARVIS_URL, text=text.lower())

                                with _state_lock:
                                    _state = STATE_IDLE

                                t = threading.Thread(
                                    target=_idle_command_loop,
                                    daemon=True,
                                    name="jarvis-idle-command"
                                )
                                t.start()
                                _dbg('E', 'idle_command_THREAD_STARTED', thread_alive=t.is_alive(), state_after=_state)
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
    Manually activate (browser mic button). Goes straight to IDLE mode.
    """
    if _state == STATE_DEEP_SLEEP:
        _beep_wake()
        try:
            from engine.command import speak as _speak
            _speak("Jarvis online, command ke liye ready hai.")
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
        print("[HOTWORD] Force activated from UI → IDLE")
