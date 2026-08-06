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
WAKE_WORDS = [
    # ── English (Jarvis) ──────────────────────────────────────────────
    "wake up jarvis", "wakeup jarvis", "wake jarvis",
    "hey jarvis", "jarvis", "ok jarvis", "hi jarvis",
    "hello jarvis", "activate jarvis", "listen jarvis", "jarvis listen",
    "yo jarvis", "okay jarvis", "o.k. jarvis", "okey jarvis",
    # ── English (Jarvish / common misspellings) ───────────────────────
    "jarvish", "jarves", "javis",
    "wake up jarvish", "wakeup jarvish", "wake jarvish",
    "hey jarvish", "ok jarvish", "hi jarvish", "hello jarvish",
    "activate jarvish", "listen jarvish", "jarvish listen",
    "yo jarvish", "okay jarvish", "okey jarvish",
    # ── Common Google SR mis-transcriptions ───────────────────────────
    "jarbish", "jurvish", "gervish", "jervish",
    "jarvees", "jarveesh", "jarviss", "jarwish",
    "javish", "jervis", "garvis", "garvish",
    "wake up jarwish", "wakeup jarwish",
    # ── Hinglish / Hindi variants ─────────────────────────────────────
    "haan jarvish", "han jarvish", "haaan jarvish",
    "haan jarvis", "han jarvis",
    "namaste jarvish", "namaste jarvis",
    "suno jarvish", "sun jarvish", "suna jarvish",
    "suno jarvis", "sun jarvis",
    "utho jarvish", "utho jarvis",
    "jago jarvish", "jago jarvis",
    "bol jarvish", "bolo jarvish",
    "bol jarvis", "bolo jarvis",
    "chalu ho ja jarvish", "chalu hoja jarvish",
    "start ho ja jarvish", "start hoja jarvish",
    "aaja jarvish", "aa ja jarvish",
    "idhar aao jarvish", "idhar aao jarvis",
    "chalo jarvish", "chalein jarvish",
    "theek hai jarvish", "thik hai jarvish",
    "theek hai jarvis", "thik hai jarvis",
    "bas kar jarvish", "bus kar jarvish",
]

# Short fuzzy seeds — any word matching 65%+ of any seed below counts as wake
_WAKE_SEEDS = [
    "jarvis", "jarvish", "jarves", "javis",
    "jarbish", "jurvish", "jervish", "jarwish",
    "javish", "jervis", "garvish", "garvis",
]

# Bolo "stop" ya "sleep" → Jarvis wapas sleep mode mein
SLEEP_WORDS = [
    "stop", "sleep", "go to sleep", "goodbye", "bye",
    "bye jarvis", "bye jarvish", "that's all", "thats all",
    "ok stop", "jarvis stop", "jarvish stop",
    "bas karo", "bas kar", "band kar", "band karo",
    "chup raho", "chup ho ja", "so jao", "so ja",
    "roko", "ruk jao", "ruk ja",
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

def _fuzzy_ratio(a: str, b: str) -> float:
    """Case-insensitive fuzzy similarity 0.0 → 1.0 (difflib SequenceMatcher)."""
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _contains_wake_word(text: str) -> bool:
    text = text.lower().strip()
    if not text:
        return False
    words = text.split()

    # Tier 1 — Exact/loose WAKE_WORDS substring (fast, catches most cases).
    for ww in WAKE_WORDS:
        if ww in text:
            return True

    # Tier 2 — Per-word contains seed ("jarvishh" → contains "jarvish").
    for w in words:
        for seed in _WAKE_SEEDS:
            if seed in w:
                return True

    # Tier 3 — 2-word and 3-word sliding concat (catches "jar vish", "jar wish",
    # "ja r vish" etc. that Google SR splits across word boundaries).
    joined_pairs = []
    for i in range(len(words) - 1):
        joined_pairs.append(words[i] + words[i + 1])
    for i in range(len(words) - 2):
        joined_pairs.append(words[i] + words[i + 1] + words[i + 2])
    for j in joined_pairs:
        # Substring containment first (cheap).
        for seed in _WAKE_SEEDS:
            if seed in j:
                return True
        # Fuzzy match against each seed.
        for seed in _WAKE_SEEDS:
            if 5 <= len(j) <= 12 and _fuzzy_ratio(j, seed) >= 0.72:
                return True

    # Tier 4 — Per-word fuzzy similarity against every seed.
    # Typical length of a jarvis/jarvish pronunciation is 5-9 chars.
    for w in words:
        if len(w) < 4 or len(w) > 14:
            continue
        for seed in _WAKE_SEEDS:
            if _fuzzy_ratio(w, seed) >= 0.70:
                return True

    # Tier 5 — Whole-phrase fuzzy against multi-word wake words
    # (e.g., "wake up jar vish" → ~75% match with "wake up jarvish").
    for ww in WAKE_WORDS:
        if " " in ww and abs(len(ww) - len(text)) <= 12:
            if _fuzzy_ratio(text, ww) >= 0.72:
                return True

    return False


def _contains_sleep_word(text: str) -> bool:
    text = text.lower().strip()
    if not text:
        return False
    for sw in SLEEP_WORDS:
        if sw in text:
            return True
    # Fuzzy fallback for Hindi sleep words (short, common misspellings).
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

def _make_recognizer(energy=60, dynamic=True, pause=0.5):
    """
    Optimized recognizer for Indian-English wake word detection:
    - Low energy (60) so soft-spoken wake words also get captured.
    - Dynamic energy ON — adapts to room noise continuously.
    - Short pause (0.5s) so short 1-2 word wake phrases end quickly.
    """
    r = sr.Recognizer()
    r.energy_threshold          = energy
    r.dynamic_energy_threshold  = dynamic
    r.pause_threshold           = pause
    r.operation_timeout         = 10   # Google SR 10s timeout (no indefinite hang)
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
    - MICROPHONE RELEASE DURING ACTIVE MODE (critical fix)
      taaki takecommand() apna Microphone open kar sake
    """
    global _active_mode

    # #region debug-point A:wake-loop-entry
    _dbg('A', 'wake_loop_thread_ENTERED', sr_available=(sr is not None), listening_flag=_listening)
    # #endregion

    if sr is None:
        # #region debug-point A:sr-is-none
        _dbg('A', 'speech_recognition_IMPORT_MISSING_hotword_disabled', error='sr is None')
        # #endregion
        print("[HOTWORD] ❌ speech_recognition not installed — hotword disabled")
        return

    recognizer = _make_recognizer(energy=60, dynamic=True, pause=0.5)

    print("[HOTWORD] 😴 Sleeping... say 'Jarvish' or 'Hey Jarvis' to wake me up")
    _silence_counter = 0

    while _listening:
        # ── ACTIVE MODE: microphone RELEASED (not held by with-block) ───
        # Ye zaroori hai taaki takecommand() apna sr.Microphone() open
        # kar sake (warna OSError: device busy ho jata hai)
        if _active_mode:
            time.sleep(0.3)
            continue

        # ── SLEEP MODE: open microphone, listen until active mode ────────
        try:
            with sr.Microphone() as source:
                # #region debug-point A:microphone-opened
                _dbg('A', 'sr_Microphone_BLOCK_ENTERED_ok', source_type=type(source).__name__, initial_energy=recognizer.energy_threshold, pause=recognizer.pause_threshold, dynamic=recognizer.dynamic_energy_threshold)
                # #endregion
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # #region debug-point B:ambient-adjust-done
                _dbg('B', 'ambient_noise_adjust_done_after_0_5s', post_adjust_energy=recognizer.energy_threshold, dynamic_energy=recognizer.dynamic_energy_threshold)
                # #endregion
                print(f"[HOTWORD] 🎤 Microphone ready (energy={recognizer.energy_threshold:.0f}) — listening for wake word...")

                # Inner loop: stay inside with-block only while NOT active
                while _listening and not _active_mode:
                    try:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                        # #region debug-point B:listen-call-success-got-audio
                        _dbg('B', 'listen_call_SUCCESS_audio_captured', audio_duration_sec=getattr(audio,'frame_data',None) and round(len(audio.frame_data)/(audio.sample_rate*audio.sample_width),2) if audio else 0, current_energy=recognizer.energy_threshold)
                        # #endregion

                        try:
                            text = _recognize_google_multi_lang(audio)
                            print(f"[HOTWORD] 👂 Heard: '{text}'")
                            _silence_counter = 0
                            # #region debug-point C:recognize-returned-text
                            _dbg('C', 'recognize_google_multi_RETURNED_TEXT', raw_text=text, text_lower=text.lower(), word_count=len(text.split()))
                            # #endregion

                            _matched = _contains_wake_word(text)
                            # #region debug-point C:wake-word-match-result
                            _dbg('C', 'wake_word_match_RESULT', match=_matched, text=text.lower().strip(), words=text.lower().split())
                            # #endregion

                            if _matched:
                                print("[HOTWORD] 🔔 WAKE WORD DETECTED!")
                                # #region debug-point E:before-beep-browser
                                _dbg('E', 'wake_DETECTED_about_to_call_beep_and_browser_and_speak_ready', text=text.lower(), active_mode_before=_active_mode)
                                # #endregion
                                _beep_wake()
                                # #region debug-point E:beep-called
                                _dbg('E', 'beep_wake_FINISHED_no_error', text=text.lower())
                                # #endregion

                                try:
                                    from engine.command import speak as _speak
                                    _speak("Haan Sir, main aapki command sunne ke liye taiyaar hoon. Bataiye kya karna hai.")
                                except Exception:
                                    pass
                                try:
                                    _open_jarvis_browser()
                                except Exception as _be:
                                    print(f"[HOTWORD] Browser open (non-fatal): {_be}")
                                # #region debug-point E:browser-called
                                _dbg('E', '_open_jarvis_browser_AND_ready_TTS_done', url=JARVIS_URL, text=text.lower())
                                # #endregion

                                with _active_mode_lock:
                                    _active_mode = True

                                cmd_thread = threading.Thread(
                                    target=_command_loop,
                                    daemon=True,
                                    name="jarvis-command-loop"
                                )
                                cmd_thread.start()
                                # #region debug-point E:command-thread-started
                                _dbg('E', 'command_LOOP_THREAD_STARTED', thread_alive=cmd_thread.is_alive(), active_mode_after=_active_mode)
                                # #endregion
                                # Ye inner loop se bahar nikal jayega
                                # → with sr.Microphone() block exit → MIC RELEASED
                                break

                        except sr.UnknownValueError:
                            _silence_counter += 1
                            # Har 15 silence/noise cycles pe ek heartbeat print karo
                            # taaki user ko pata chale system zinda hai
                            if _silence_counter % 15 == 0:
                                print(f"[HOTWORD] 💤 Listening... (noise/silence x{_silence_counter}) — say 'Jarvish'")
                            # #region debug-point B:unknown-value-swallowed
                            _dbg('B', 'UnknownValueError_SWALLOWED_silence_or_unintelligible', reason='multi_lang_all_unknown', current_energy=recognizer.energy_threshold, silence_count=_silence_counter)
                            # #endregion
                        except sr.RequestError as e:
                            # #region debug-point D:google-request-error
                            _dbg('D', 'Google_SR_RequestError', error=str(e), error_type=type(e).__name__)
                            # #endregion
                            print(f"[HOTWORD] ⚠️ Google API error: {e} — retrying...")
                            time.sleep(2)

                    except sr.WaitTimeoutError:
                        # #region debug-point B:wait-timeout-no-speech
                        _dbg('B', 'WaitTimeoutError_no_speech_in_5s_window', timeout=5, current_energy=recognizer.energy_threshold)
                        # #endregion
                    except Exception as e:
                        # #region debug-point A:inner-listen-exception
                        _dbg('A', 'INNER_audio_loop_Exception', error=str(e), error_type=type(e).__name__)
                        # #endregion
                        print(f"[HOTWORD] Audio error: {e}")
                        time.sleep(0.3)

        except OSError as e:
            # #region debug-point A:mic-oserror
            _dbg('A', 'OUTER_OSError_MICROPHONE', error=str(e), error_type=type(e).__name__)
            # #endregion
            print(f"[HOTWORD] ❌ Microphone error: {e} — retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            # #region debug-point A:outer-fatal-exception
            _dbg('A', 'OUTER_FATAL_Exception_in_wake_loop', error=str(e), error_type=type(e).__name__, traceback=__import__('traceback').format_exc()[-800:])
            # #endregion
            print(f"[HOTWORD] ❌ Fatal error: {e} — retrying in 5s...")
            time.sleep(5)


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
    # #region debug-point A:start-thread-launched
    _dbg('A', 'hotword_start_called_thread_started', listening_flag=_listening, thread_alive=t.is_alive(), thread_name=t.name)
    # #endregion
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
