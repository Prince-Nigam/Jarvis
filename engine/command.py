"""
command.py — TTS + Speech Recognition for Jarvis
- Edge TTS (Microsoft Neural Voice) — natural Indian English voice
- Queue-based speak() — non-blocking, thread-safe
- takecommand() with proper error handling
- run_command() routes queries to correct feature
"""
import subprocess
import threading
import time
import queue as _queue
import asyncio
import os
import tempfile

# ── Edge TTS setup ─────────────────────────────────────────────────────────────
try:
    import edge_tts
    _HAS_EDGE_TTS = True
except ModuleNotFoundError:
    edge_tts = None
    _HAS_EDGE_TTS = False

# Fallback: pyttsx3
try:
    import pyttsx3
    _HAS_PYTTSX3 = True
except ModuleNotFoundError:
    pyttsx3 = None
    _HAS_PYTTSX3 = False

# Voice to use — pyttsx3 (David - original Jarvis voice) priority
# Edge TTS sirf fallback hai agar pyttsx3 na ho
EDGE_VOICE = "en-IN-PrabhatNeural"

_tts_q      = _queue.Queue()
_tts_engine = None   # pyttsx3 fallback engine
_tts_thread = None


def _play_mp3(path: str):
    """Play MP3 file using pygame mixer."""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[TTS Play Error]: {e}")
        # Fallback — PowerShell with correct file path
        try:
            subprocess.run(
                ["powershell", "-c",
                 f'$p = New-Object Media.SoundPlayer "{path}"; $p.PlaySync()'],
                timeout=30
            )
        except Exception:
            pass


async def _edge_speak_async(text: str):
    """Generate speech via Edge TTS as MP3 and play via pygame."""
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    mp3_path = tmp.name
    tmp.close()
    try:
        communicate = edge_tts.Communicate(text, EDGE_VOICE)
        await communicate.save(mp3_path)
        _play_mp3(mp3_path)
    finally:
        try:
            os.unlink(mp3_path)
        except Exception:
            pass


def _tts_worker():
    """Single dedicated TTS thread — pyttsx3 (David voice) primary, Edge TTS fallback."""
    global _tts_engine
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        text = _tts_q.get()
        if text is None:   # sentinel
            break
        try:
            if _HAS_PYTTSX3:
                # Primary — original Jarvis David voice
                if _tts_engine is None:
                    _tts_engine = pyttsx3.init("sapi5")
                    voices = _tts_engine.getProperty("voices")
                    if voices:
                        _tts_engine.setProperty("voice", voices[0].id)  # David
                    _tts_engine.setProperty("rate", 170)
                _tts_engine.say(text)
                _tts_engine.runAndWait()
            elif _HAS_EDGE_TTS:
                # Fallback — Edge TTS
                loop.run_until_complete(_edge_speak_async(text))
        except Exception as e:
            print(f"[TTS Error]: {e}")
            if _tts_engine:
                try:
                    _tts_engine.stop()
                except Exception:
                    pass
                _tts_engine = None
        finally:
            _tts_q.task_done()

    loop.close()


def _ensure_tts_worker():
    global _tts_thread
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
    _recognizer.pause_threshold          = 1.2   # 1.2s silence ke baad hi "done speaking" samjho
    _recognizer.phrase_threshold         = 0.1   # phrase start threshold
    _recognizer.non_speaking_duration    = 0.5   # phrase end mein 0.5s silence buffer
    _recognizer.energy_threshold         = 300
    _recognizer.dynamic_energy_threshold = True
    _recognizer.dynamic_energy_ratio     = 1.2   # slowly adjust, not aggressively
    _recognizer.operation_timeout        = None
    _HAS_SR = True
except (ModuleNotFoundError, Exception):
    sr = None
    _recognizer = None
    _HAS_SR = False

# FIX1: ambient noise calibration — sirf ek baar at startup, repeat nahi
_ambient_calibrated = False
_shared_mic_source  = None   # persistent mic — bar bar open/close nahi hoga
_shared_mic_ctx     = None

def _calibrate_once():
    """Sirf pehli baar 0.3s ambient calibration — better than 0.1s for accuracy."""
    global _ambient_calibrated
    if _ambient_calibrated:
        return
    try:
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)
        _ambient_calibrated = True
        print(f"[MIC] Calibrated energy={_recognizer.energy_threshold:.0f}")
    except Exception:
        _ambient_calibrated = True


def _recognize_multi_lang(audio) -> str:
    """
    FIX3: Pehle sirf en-IN try karo (fastest).
    Sirf agar en-IN fail ho tab hi hi-IN/en-US fallback.
    Teen sequential API calls ki jagah usually sirf 1 call hogi.
    """
    # Fast path — en-IN (Indian English — Hinglish bhi samajhta hai)
    try:
        text = _recognizer.recognize_google(audio, language="en-IN")
        if text and text.strip():
            return text
    except sr.RequestError as e:
        raise e   # network error — retry karne ka fayda nahi
    except sr.UnknownValueError:
        pass      # unclear — try next lang

    # Fallback 1 — Hindi
    try:
        text = _recognizer.recognize_google(audio, language="hi-IN")
        if text and text.strip():
            return text
    except (sr.UnknownValueError, sr.RequestError):
        pass

    # Fallback 2 — US English
    try:
        text = _recognizer.recognize_google(audio, language="en-US")
        if text and text.strip():
            return text
    except sr.UnknownValueError:
        raise
    except sr.RequestError as e:
        raise e

    raise sr.UnknownValueError()


def _push_event(msg: str, level: str = "info"):
    """Push to activity log — non-fatal if main not loaded yet."""
    try:
        from main import push_event
        push_event(msg, level)
    except Exception:
        pass


# ── Public API ─────────────────────────────────────────────────────────────────

def speak(text):
    """
    Queue text for TTS output. Non-blocking.
    Uses Edge TTS (Microsoft Neural Voice) — natural Indian English.
    Falls back to pyttsx3 if edge-tts not available.
    """
    text = str(text).strip()
    if not text:
        return
    print(f"[JARVIS]: {text}")
    if _HAS_EDGE_TTS or _HAS_PYTTSX3:
        _ensure_tts_worker()
        _tts_q.put(text)


def wait_for_speak():
    """
    TTS queue drain hone tak block karo.
    Mic open karne se pehle call karo — TTS ki awaaz mic mein nahi jayegi.
    """
    _tts_q.join()


def takecommand():
    """
    Listen via microphone, return recognised text (lowercase).
    Optimized:
    - Mic ek baar open, persistent
    - Calibration sirf pehli baar
    - pause_threshold=1.2s — poori baat sun ne ke baad hi process karo
    - phrase_time_limit=15s — lambi commands ke liye
    - en-IN first, fallback only if needed
    """
    if not _HAS_SR or _recognizer is None:
        print("[SR] speech_recognition not available")
        return ""

    _calibrate_once()

    try:
        with sr.Microphone() as source:
            print(f"[MIC] 🎙️ Listening...")
            audio = _recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=15   # 15s tak bolne ka time — lambi commands ke liye
            )
    except sr.WaitTimeoutError:
        print("[MIC] Timeout — no speech detected")
        return ""
    except OSError as e:
        print(f"[MIC] ❌ Microphone error: {e}")
        return ""
    except Exception as e:
        print(f"[MIC] Unexpected: {e}")
        return ""

    try:
        print("[SR] Recognizing...")
        query = _recognize_multi_lang(audio)
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
    speak() is called at the END for ALL commands — Jarvis har command ke
    baad verbal confirmation deta hai.
    Kuch branches (greetings, chatBot) already speak() karte hain —
    unhe _spoken flag se track karo taaki double-speaking na ho.
    """
    query = (query or "").strip().lower()
    if not query:
        return ""

    response = ""
    _spoken  = False   # True if speak() already called inside branch
    try:
        from engine import desktop_control as dc

        # ══════════════════════════════════════════════════════════
        #  ── QUICK CHECK: simple math expression (2 + 3, 15 * 4)
        # ══════════════════════════════════════════════════════════
        import re as _re
        _nums = _re.findall(r'\d+\s*[+\-*/×÷%^]\s*\d+', query)
        if _nums and not any(k in query for k in ("whatsapp", "message", "what is", "tell")):
            expr = _nums[0].replace('×', '*').replace('÷', '/').replace('^', '**')
            res = dc.calculate_expression(expr)
            if res is not None:
                return f"Result: {res}"

        # ══════════════════════════════════════════════════════════
        #  WINDOW MANAGEMENT
        # ══════════════════════════════════════════════════════════

        if any(k in query for k in ("minimize window", "minimise window", "window minimize")):
            dc.minimize_window()
            response = "Window minimized"

        elif any(k in query for k in ("maximize window", "maximise window", "window maximize")):
            dc.maximize_window()
            response = "Window maximized"

        elif any(k in query for k in ("full screen", "fullscreen", "toggle fullscreen", "f11")):
            dc.fullscreen_toggle()
            response = "Fullscreen toggled"

        elif any(k in query for k in ("close window", "close this", "window close", "exit app", "quit app")):
            dc.close_window()
            response = "Window closed"

        elif any(k in query for k in ("switch window", "alt tab", "change window")):
            dc.switch_window()
            response = "Switching window"

        elif any(k in query for k in ("show desktop", "hide all")):
            dc.show_desktop()
            response = "Showing desktop"

        elif any(k in query for k in ("minimize all windows", "minimise all windows", "minimize all")):
            dc.minimize_all_windows()
            response = "All windows minimized"

        elif any(k in query for k in ("restore all windows", "undo minimize all", "restore minimized")):
            dc.restore_all_windows()
            response = "All windows restored"

        elif any(k in query for k in ("minimize other windows", "only this window")):
            dc.minimize_others()
            response = "Other windows minimized"

        elif any(k in query for k in ("snap left", "window left")):
            dc.snap_left()
            response = "Snapped to left"

        elif any(k in query for k in ("snap right", "window right")):
            dc.snap_right()
            response = "Snapped to right"

        elif any(k in query for k in ("snap up", "window up")):
            dc.snap_up()
            response = "Snapped up"

        elif any(k in query for k in ("snap down", "window down")):
            dc.snap_down()
            response = "Snapped down"

        elif any(k in query for k in ("task view", "virtual desktop", "show all windows")):
            dc.open_task_view()
            response = "Task view opened"

        elif any(k in query for k in ("project screen", "connect to projector", "second screen")):
            dc.project_screen()
            response = "Project menu opened"

        elif any(k in query for k in ("window menu", "restore window", "move window", "resize window")):
            dc.window_menu()
            response = "Window menu opened"

        elif any(k in query for k in ("arrange windows", "tile windows", "split screen")):
            dc.tile_windows()
            response = "Arranging windows"

        elif any(k in query for k in ("restart explorer", "restart windows explorer", "restart taskbar")):
            dc.restart_windows_explorer()
            response = "Windows explorer restarted"

        # ══════════════════════════════════════════════════════════
        #  MOUSE CONTROL
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("left click", "click mouse", "mouse click", "click there")):
            dc.left_click()
            response = "Left clicked"

        elif any(k in query for k in ("right click", "open context menu", "context menu")):
            dc.right_click()
            response = "Right clicked"

        elif any(k in query for k in ("double click", "double-click", "open file", "open item")):
            if "open" not in query:
                dc.double_click()
                response = "Double clicked"

        elif any(k in query for k in ("middle click", "close tab with mouse")):
            dc.middle_click()
            response = "Middle clicked"

        elif any(k in query for k in ("mouse to center", "center mouse", "center cursor")):
            dc.mouse_to_center()
            response = "Mouse centered"

        # ══════════════════════════════════════════════════════════
        #  MEDIA CONTROL
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("play music", "pause music", "play pause", "resume music", "toggle play")):
            dc.media_play_pause()
            response = "Play/Pause toggled"

        elif any(k in query for k in ("stop", "pause", "ruko", "band karo music", "music band karo", "video band karo", "music roko", "video roko")):
            # "stop" / "pause" — youtube/spotify wala jo bhi chal raha ho
            dc.media_play_pause()
            response = "Media paused"

        elif any(k in query for k in ("chalu karo", "resume", "start music", "music chalu")) and "youtube" not in query:
            # "resume/chalu karo" — wapas chalu karo (youtube commands upar handle ho jaate hain)
            dc.media_play_pause()
            response = "Media playing"

        elif any(k in query for k in ("next song", "next track", "skip song", "next music")):
            dc.media_next()
            response = "Next track"

        elif any(k in query for k in ("previous song", "prev song", "last song", "previous track", "go back song")):
            dc.media_previous()
            response = "Previous track"

        elif "stop music" in query or "stop media" in query:
            dc.media_stop()
            response = "Media stopped"

        elif any(k in query for k in ("volume up", "increase volume", "louder", "volume badhao", "volume upar")):
            dc.volume_up()
            response = "Volume increased"

        elif any(k in query for k in ("volume down", "decrease volume", "lower volume", "quieter", "volume niche")):
            dc.volume_down()
            response = "Volume decreased"

        elif any(k in query for k in ("mute", "unmute", "mute volume")):
            dc.mute_volume()
            response = "Muted"

        # ══════════════════════════════════════════════════════════
        #  TEXT EDITING SHORTCUTS (Bold/Italic/Underline etc.)
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("bold text", "make bold", "apply bold", "bold karo")):
            dc.text_bold()
            response = "Bold applied"

        elif any(k in query for k in ("italic text", "make italic", "apply italic", "italic karo")):
            dc.text_italic()
            response = "Italic applied"

        elif any(k in query for k in ("underline text", "make underline", "apply underline", "underline karo")):
            dc.text_underline()
            response = "Underline applied"

        elif any(k in query for k in ("strikethrough", "strike through", "strike text")):
            dc.text_strikethrough()
            response = "Strikethrough applied"

        elif any(k in query for k in ("find and replace", "replace text", "find replace", "ctrl h")):
            dc.find_and_replace()
            response = "Find and replace opened"

        elif any(k in query for k in ("print document", "print page", "print this", "ctrl p")):
            dc.print_document()
            response = "Print dialog opened"

        elif any(k in query for k in ("rename", "rename item", "rename file", "rename folder")):
            dc.rename_item()
            response = "Rename mode"

        elif any(k in query for k in ("new document", "new file", "ctrl n")):
            dc.new_document()
            response = "New document"

        elif any(k in query for k in ("open document", "open file dialog", "ctrl o")):
            if "open" in query and not any(x in query for x in ("downloads", "desktop", "documents", "pictures", "videos", "music", "folder", "drive", "app", "settings", "website", "browser", "google", "chrome", "edge", "firefox", "youtube", "gmail", "whatsapp", "telegram", "notepad", "calculator", "paint", "word", "excel", "powerpoint", "vscode", "explorer", "manager", "clipboard", "screen", "keyboard", "magnifier", "c drive", "d drive")):
                dc.open_document()
                response = "Open file dialog"

        elif any(k in query for k in ("hard refresh", "refresh hard", "ctrl f5")):
            dc.refresh_everything()
            response = "Hard refresh done"

        elif any(k in query for k in ("restore tab", "undo close tab", "reopen tab", "open closed tab")):
            dc.restore_tab()
            response = "Tab restored"

        elif any(k in query for k in ("close all tabs", "close tabs", "close all windows tab")):
            dc.close_all_tabs()
            response = "All tabs closed"

        elif any(k in query for k in ("next tab", "switch tab", "tab switch")):
            dc.switch_to_next_tab()
            response = "Next tab"

        elif any(k in query for k in ("previous tab", "prev tab")):
            dc.switch_to_previous_tab()
            response = "Previous tab"

        elif any(k in query for k in ("address bar", "focus address", "go to address bar", "ctrl l")):
            dc.go_to_address_bar()
            response = "Address bar focused"

        elif any(k in query for k in ("browsing history", "show history", "history open", "ctrl h")):
            dc.open_history()
            response = "History opened"

        elif any(k in query for k in ("bookmarks", "open bookmarks", "show bookmarks")):
            dc.open_bookmarks()
            response = "Bookmarks opened"

        elif any(k in query for k in ("downloads folder", "show downloads", "downloads open", "ctrl j")):
            dc.open_downloads()
            response = "Downloads opened"

        elif any(k in query for k in ("developer tools", "dev tools", "inspect element", "open devtools", "f12")):
            dc.open_developer_tools()
            response = "Developer tools opened"

        elif any(k in query for k in ("incognito", "incognito window", "private browsing", "go incognito")):
            dc.open_incognito()
            response = "Incognito window opened"

        elif any(k in query for k in ("private window", "private mode window", "in private window")):
            dc.open_private_window()
            response = "Private window opened"

        elif any(k in query for k in ("bookmark this", "add bookmark", "save bookmark", "ctrl d")):
            dc.toggle_bookmark()
            response = "Bookmark toggled"

        # ══════════════════════════════════════════════════════════
        #  PRINT SCREEN / SNIPPING / SCREEN TOOLS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("print screen", "capture entire screen", "win prtsc", "prtsc")):
            dc.take_printscreen()
            response = "Print screen captured"

        elif any(k in query for k in ("snip", "snipping tool", "capture region", "partial screenshot", "screenshot region", "screenshot partial", "snippet")):
            dc.open_snipping_tool()
            response = "Snipping tool activated"

        elif any(k in query for k in ("screenshot", "take screenshot", "capture screen", "screen capture")):
            dc.take_screenshot()
            response = "Screenshot saved to Desktop"

        elif any(k in query for k in ("emoji panel", "emoji picker", "open emoji", "insert emoji", "win dot")):
            dc.open_emoji_panel()
            response = "Emoji panel opened"

        elif any(k in query for k in ("dictation", "dictation mode", "start dictating", "dictate mode", "win h")):
            dc.open_dictation()
            response = "Dictation mode started"

        elif any(k in query for k in ("game bar", "open game bar", "xbox game bar", "record screen", "win g")):
            dc.open_game_bar()
            response = "Game bar opened"

        elif any(k in query for k in ("quick link menu", "power user menu", "win x menu")):
            dc.open_quick_link_menu()
            response = "Quick link menu opened"

        elif any(k in query for k in ("task manager shortcut", "ctrl shift esc", "taskman")):
            dc.open_task_manager_shortcut()
            response = "Task manager opened"

        # ══════════════════════════════════════════════════════════
        #  KEYBOARD SHORTCUTS (basics)
        # ══════════════════════════════════════════════════════════

        elif "copy" in query and not any(x in query for x in ("open", "path", "file", "folder", "clipboard")):
            dc.copy()
            response = "Copied"

        elif "paste" in query:
            dc.paste()
            response = "Pasted"

        elif "cut" in query and "open" not in query:
            dc.cut()
            response = "Cut"

        elif any(k in query for k in ("undo", "go back one step", "undo karo", "ctrl z")):
            dc.undo()
            response = "Undo done"

        elif "redo" in query:
            dc.redo()
            response = "Redo done"

        elif "select all" in query:
            dc.select_all()
            response = "Selected all"

        elif any(k in query for k in ("save file", "save this", "ctrl s", "save karo")):
            dc.save_file()
            response = "Saved"

        elif any(k in query for k in ("new tab", "open tab", "new tab karo")):
            dc.new_tab()
            response = "New tab opened"

        elif any(k in query for k in ("close tab", "close current tab")):
            dc.close_tab()
            response = "Tab closed"

        elif any(k in query for k in ("refresh", "reload page", "reload", "f5", "page refresh")):
            dc.refresh_page()
            response = "Refreshed"

        elif any(k in query for k in ("go back", "browser back", "previous page", "peeche jao")):
            dc.go_back()
            response = "Going back"

        elif any(k in query for k in ("go forward", "browser forward", "next page", "aage jao")):
            dc.go_forward()
            response = "Going forward"

        elif any(k in query for k in ("zoom in", "increase zoom", "badha karo zoom")):
            dc.zoom_in()
            response = "Zoomed in"

        elif any(k in query for k in ("zoom out", "decrease zoom", "ghata karo zoom")):
            dc.zoom_out()
            response = "Zoomed out"

        elif any(k in query for k in ("find on page", "search on page", "ctrl f", "page mein dhundho")):
            dc.find_on_page()
            response = "Find opened"

        elif any(k in query for k in ("new window", "open new window", "naya window")):
            dc.open_new_window()
            response = "New window opened"

        elif any(k in query for k in ("press enter", "hit enter", "enter dabao", "enter")):
            dc.press_enter()
            response = "Enter pressed"

        elif any(k in query for k in ("press escape", "escape", "cancel karo", "esc dabao", "cancel")):
            dc.press_escape()
            response = "Escaped"

        elif any(k in query for k in ("press delete", "delete key", "hatao character")):
            dc.press_delete()
            response = "Deleted"

        elif any(k in query for k in ("press backspace", "backspace", "erase character", "mitao character")):
            dc.press_backspace()
            response = "Backspace"

        # ══════════════════════════════════════════════════════════
        #  SCROLL
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("scroll down", "page down", "move down", "neeche scroll", "scroll neeche")):
            dc.scroll_down()
            response = "Scrolled down"

        elif any(k in query for k in ("scroll up", "page up", "move up", "upar scroll", "scroll upar")):
            dc.scroll_up()
            response = "Scrolled up"

        elif any(k in query for k in ("scroll left", "move left", "left scroll")):
            dc.scroll_left()
            response = "Scrolled left"

        elif any(k in query for k in ("scroll right", "move right", "right scroll")):
            dc.scroll_right()
            response = "Scrolled right"

        elif any(k in query for k in ("scroll to top", "page top", "top of page", "shuruat mein jao", "upar le jao")):
            dc.scroll_to_top()
            response = "Scrolled to top"

        elif any(k in query for k in ("scroll to bottom", "page bottom", "end of page", "end tak le jao", "niche le jao", "bottom le jao")):
            dc.scroll_to_bottom()
            response = "Scrolled to bottom"

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

        elif query.startswith("calculate ") or query.startswith("calc ") or query.startswith("kitna "):
            expr = query.split(" ", 1)[1].strip()
            if expr:
                res = dc.calculate_expression(expr)
                response = f"Result: {res}" if res is not None else ""
            else:
                speak("What should I calculate?")
                q2 = takecommand()
                if q2:
                    res = dc.calculate_expression(q2)
                    response = f"Result: {res}" if res is not None else ""

        elif any(k in query for k in ("translate", "meaning of", "translate karo", "matlab kya hai", "matlab batao")):
            phrase = query
            for kw in ("translate ", "translate karo ", "meaning of ", "what is the meaning of ", "matlab kya hai ", "matlab batao "):
                if kw in phrase:
                    phrase = phrase.replace(kw, "").strip()
            if phrase:
                dc.translate_text(phrase)
                response = f"Translating: {phrase}"
            else:
                speak("What should I translate?")
                q2 = takecommand()
                if q2:
                    dc.translate_text(q2)
                    response = f"Translating: {q2}"

        # ══════════════════════════════════════════════════════════
        #  DELETE / FILE OPS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("delete selected", "move to recycle", "delete file selected")):
            dc.delete_selected_item()
            response = "Moved to recycle bin"

        elif any(k in query for k in ("delete permanently", "shift delete", "hamesha ke liye delete")):
            dc.delete_permanently()
            response = "Item permanently deleted"

        elif any(k in query for k in ("copy path", "copy location", "copy file path", "copy directory path")):
            dc.copy_path_of_selected()
            response = "File path copied"

        elif any(k in query for k in ("create folder", "naya folder", "folder banao", "new folder banaye")):
            speak("What should I name the folder?")
            nm = takecommand()
            if nm:
                dc.create_new_folder(nm)
                response = f"Folder {nm} created"
            else:
                dc.create_new_folder()
                response = "New folder created on Desktop"

        elif any(k in query for k in ("create file", "naya file", "file banao", "new text file", "notepad file banaye")):
            speak("What should I name the file?")
            nm = takecommand()
            if nm:
                dc.create_new_text_file(nm)
                response = f"File {nm} created"
            else:
                dc.create_new_text_file()
                response = "New text file created on Desktop"

        elif any(k in query for k in ("open command prompt", "open cmd", "cmd kholo", "command prompt kholo", "terminal cmd")):
            dc.open_command_prompt()
            response = "Command prompt opened"

        elif any(k in query for k in ("open powershell", "powershell kholo", "powershell launch")):
            dc.open_powershell()
            response = "PowerShell opened"

        elif any(k in query for k in ("open terminal", "terminal kholo", "windows terminal", "wt launch")):
            dc.open_windows_terminal()
            response = "Windows terminal opened"

        elif any(k in query for k in ("clear temp", "clean temp", "temp files delete", "temp folder clean", "cache clear", "cache clean karo")):
            dc.clear_temp_files()
            response = "Temp files cleaned"

        # ══════════════════════════════════════════════════════════
        #  FOLDER / FILE OPEN
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("open downloads", "downloads folder", "download kholo")):
            dc.open_folder("downloads")
            response = "Opening Downloads"

        elif any(k in query for k in ("open desktop", "desktop folder", "desktop kholo")):
            dc.open_folder("desktop")
            response = "Opening Desktop"

        elif any(k in query for k in ("open documents", "documents folder", "my documents", "documents kholo")):
            dc.open_folder("documents")
            response = "Opening Documents"

        elif any(k in query for k in ("open pictures", "pictures folder", "my pictures", "open photos", "photos kholo")):
            dc.open_folder("pictures")
            response = "Opening Pictures"

        elif any(k in query for k in ("open music", "music folder", "my music", "music kholo")):
            dc.open_folder("music")
            response = "Opening Music"

        elif any(k in query for k in ("open videos", "videos folder", "my videos", "videos kholo")):
            dc.open_folder("videos")
            response = "Opening Videos"

        elif any(k in query for k in ("open c drive", "open c:", "c drive", "c drive kholo")):
            dc.open_folder("c drive")
            response = "Opening C Drive"

        elif any(k in query for k in ("open d drive", "open d:", "d drive", "d drive kholo")):
            dc.open_folder("d drive")
            response = "Opening D Drive"

        elif any(k in query for k in ("open e drive", "open e:", "e drive")):
            dc.open_folder("e drive")
            response = "Opening E Drive"

        elif any(k in query for k in ("my computer", "this pc", "open my computer", "open this pc", "my computer kholo")):
            dc.open_folder("this pc")
            response = "Opening This PC"

        elif any(k in query for k in ("recycle bin", "open recycle bin", "recycle kholo")):
            dc.open_folder("recycle bin")
            response = "Opening Recycle Bin"

        elif any(k in query for k in ("empty recycle bin", "clear recycle bin", "delete recycle bin", "recycle bin khali karo")):
            dc.empty_recycle_bin()
            response = "Recycle bin emptied"

        # ══════════════════════════════════════════════════════════
        #  SYSTEM ACTIONS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("lock screen", "lock computer", "lock laptop", "lock pc", "screen lock", "lock karo")):
            dc.lock_screen()
            response = "Screen locked"

        elif any(k in query for k in ("sign out", "log off", "logout", "log out user", "sign out karo")):
            dc.sign_out_user()
            response = "Signing out"

        elif any(k in query for k in ("sleep", "go to sleep", "sleep mode", "sone jao")):
            if "hibernate" in query:
                dc.hibernate_system()
                response = "Hibernating system"
            else:
                dc.sleep_system()
                response = "Going to sleep"

        elif any(k in query for k in ("hibernate", "hibernate system")):
            dc.hibernate_system()
            response = "Hibernating system"

        elif any(k in query for k in ("restart", "restart computer", "restart pc", "system restart", "dobara chalu karo")):
            dc.restart_pc()
            response = "Restarting in 10 seconds"

        elif any(k in query for k in ("shutdown", "shutdown computer", "shutdown pc", "system off", "band karo computer")):
            dc.shutdown_pc()
            response = "Shutting down in 10 seconds"

        elif any(k in query for k in ("cancel shutdown", "abort shutdown", "shutdown cancel", "shutdown roko")):
            dc.abort_shutdown()
            response = "Shutdown cancelled"

        elif any(k in query for k in ("task manager", "open task manager", "process manager", "task manager kholo")):
            dc.open_task_manager()
            response = "Opening Task Manager"

        elif any(k in query for k in ("device manager", "open device manager", "device manager kholo")):
            dc.open_device_manager()
            response = "Device manager opened"

        elif any(k in query for k in ("disk cleanup", "clean disk", "disk clean karo")):
            dc.open_disk_cleanup()
            response = "Disk cleanup opened"

        elif any(k in query for k in ("disk defragment", "defragment disk", "defrag disk", "disk defrag karo")):
            dc.open_disk_defragment()
            response = "Disk defragmenter opened"

        elif any(k in query for k in ("event viewer", "open event viewer", "event viewer kholo")):
            dc.open_event_viewer()
            response = "Event viewer opened"

        elif any(k in query for k in ("registry editor", "open registry", "regedit", "registry kholo")):
            dc.open_registry_editor()
            response = "Registry editor opened"

        elif any(k in query for k in ("services", "open services", "services.msc", "services kholo")):
            dc.open_services()
            response = "Services opened"

        elif any(k in query for k in ("system properties", "open system properties", "sysdm", "my computer properties")):
            dc.open_system_properties()
            response = "System properties opened"

        elif any(k in query for k in ("open sticky notes", "sticky notes", "sticky notes kholo", "sticky note open")):
            dc.open_sticky_notes()
            response = "Sticky notes opened"

        elif any(k in query for k in ("steps recorder", "problem steps recorder", "psr", "steps recorder kholo")):
            dc.open_steps_recorder()
            response = "Steps recorder opened"

        elif any(k in query for k in ("character map", "charmap", "special characters", "character map kholo")):
            dc.open_character_map()
            response = "Character map opened"

        elif any(k in query for k in ("narrator", "start narrator", "narrator chalu karo")):
            dc.open_narrator()
            response = "Narrator started"

        elif any(k in query for k in ("wordpad", "open wordpad", "wordpad kholo")):
            dc.open_wordpad()
            response = "WordPad opened"

        elif any(k in query for k in ("display settings", "screen settings", "display properties", "monitor settings")):
            dc.open_control_panel_item("display")
            response = "Display settings opened"

        elif any(k in query for k in ("sound settings", "audio settings", "speaker settings", "volume settings")):
            dc.open_control_panel_item("sound")
            response = "Sound settings opened"

        elif any(k in query for k in ("mouse settings", "mouse properties", "pointer settings")):
            dc.open_control_panel_item("mouse")
            response = "Mouse settings opened"

        elif any(k in query for k in ("network settings", "wifi settings", "network connections", "internet settings")):
            dc.open_control_panel_item("network")
            response = "Network settings opened"

        elif any(k in query for k in ("power settings", "battery settings", "power options", "sleep settings")):
            dc.open_control_panel_item("power")
            response = "Power settings opened"

        elif any(k in query for k in ("date and time", "date settings", "time settings", "clock settings")):
            dc.open_control_panel_item("date")
            response = "Date/Time settings opened"

        elif any(k in query for k in ("firewall settings", "windows firewall", "firewall open")):
            dc.open_control_panel_item("firewall")
            response = "Firewall settings opened"

        elif any(k in query for k in ("open settings", "windows settings", "system settings", "settings kholo")):
            dc.open_settings()
            response = "Opening Settings"

        elif any(k in query for k in ("run dialog", "open run", "win r", "run kholo")):
            dc.open_run_dialog()
            response = "Run dialog opened"

        elif any(k in query for k in ("windows search", "open search", "search bar", "win key", "search kholo")):
            dc.open_search()
            response = "Search opened"

        elif any(k in query for k in ("notification", "action center", "notifications", "notification kholo")):
            dc.open_notification_center()
            response = "Notification center opened"

        elif any(k in query for k in ("clipboard", "clipboard history", "win v", "clipboard kholo")):
            dc.open_clipboard_history()
            response = "Clipboard history opened"

        elif any(k in query for k in ("virtual keyboard", "on screen keyboard", "osk", "screen keyboard")):
            dc.virtual_keyboard()
            response = "Virtual keyboard opened"

        elif any(k in query for k in ("magnifier", "zoom screen", "screen magnifier")):
            dc.open_magnifier()
            response = "Magnifier opened"

        # ══════════════════════════════════════════════════════════
        #  BRIGHTNESS
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("brightness up", "increase brightness", "brighter", "brightness badhao", "roshni badhao")):
            dc.brightness_up()
            response = "Brightness increased"

        elif any(k in query for k in ("brightness down", "decrease brightness", "darker", "dim screen", "brightness ghataye", "roshni ghataye")):
            dc.brightness_down()
            response = "Brightness decreased"

        elif "brightness" in query:
            import re as _re2
            nums = _re2.findall(r'\d+', query)
            if nums:
                dc.set_brightness(int(nums[0]))
                response = f"Brightness set to {nums[0]}%"
            else:
                speak("Please say brightness level from 0 to 100")
                response = "Brightness level not clear"

        # ══════════════════════════════════════════════════════════
        #  BATTERY / NETWORK / WIFI / IP
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("battery status", "battery percentage", "how much battery", "battery kitni hai", "battery check", "charging status")):
            dc.show_battery_status()
            response = "Battery status told"
            _spoken = True

        elif any(k in query for k in ("show wifi", "wifi list", "saved wifi", "wifi networks", "wifi list dikhao", "wifi password")):
            dc.show_wifi_passwords()
            response = "Wi-Fi networks listed"
            _spoken = True

        elif any(k in query for k in ("ip address", "show ip", "what is my ip", "ip kya hai", "ip address batao", "network ip")):
            dc.show_ip_address()
            response = "IP address told"
            _spoken = True

        # ══════════════════════════════════════════════════════════
        #  SEARCH (Multiple Engines)
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("search google", "google search", "google mein dhundho", "google search karo")):
            term = query
            for kw in ("search google for ", "search google ", "google search for ", "google search ", "google mein dhundho ", "google search karo "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if term:
                dc.search_google(term)
                response = f"Searching Google for {term}"
            else:
                speak("What should I search on Google?")
                term = takecommand()
                if term:
                    dc.search_google(term)
                    response = f"Searching Google for {term}"

        elif any(k in query for k in ("search bing", "bing search", "bing mein dhundho")):
            term = query
            for kw in ("search bing for ", "search bing ", "bing search for ", "bing search ", "bing mein dhundho "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if term:
                dc.search_bing(term)
                response = f"Searching Bing for {term}"
            else:
                speak("What should I search on Bing?")
                term = takecommand()
                if term:
                    dc.search_bing(term)
                    response = f"Searching Bing for {term}"

        elif any(k in query for k in ("search duckduckgo", "duckduckgo search", "ddg search")):
            term = query
            for kw in ("search duckduckgo for ", "search duckduckgo ", "duckduckgo search for ", "duckduckgo search ", "ddg search "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if term:
                dc.search_duckduckgo(term)
                response = f"Searching DuckDuckGo for {term}"

        elif any(k in query for k in ("search youtube", "youtube search", "youtube mein dhundho")):
            term = query
            for kw in ("search youtube for ", "search youtube ", "youtube search for ", "youtube search ", "youtube mein dhundho "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if term:
                dc.search_youtube(term)
                response = f"Searching YouTube for {term}"
            else:
                speak("What should I search on YouTube?")
                term = takecommand()
                if term:
                    dc.search_youtube(term)
                    response = f"Searching YouTube for {term}"

        elif any(k in query for k in ("wikipedia", "wiki search", "search wikipedia", "wikipedia mein padho", "wikipedia search karo")):
            term = query
            for kw in ("wikipedia mein ", "search wikipedia for ", "search wikipedia ", "wiki search ", "wikipedia search karo "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if term:
                dc.search_wikipedia(term)
                response = f"Searching Wikipedia for {term}"
            else:
                speak("What should I search on Wikipedia?")
                term = takecommand()
                if term:
                    dc.search_wikipedia(term)
                    response = f"Searching Wikipedia for {term}"

        elif any(k in query for k in ("stackoverflow", "stack overflow", "stack overflow search", "stackoverflow search")):
            term = query
            for kw in ("search stackoverflow for ", "search stack overflow for ", "stackoverflow search ", "stack overflow search "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if not term or len(term) < 3:
                speak("What should I search on Stack Overflow?")
                term = takecommand() or ""
            if term:
                dc.search_stackoverflow(term)
                response = f"Searching StackOverflow for {term}"

        elif "quora" in query:
            term = query.replace("quora", "").replace("search", "").replace("on", "").replace("for", "").strip()
            if not term:
                speak("What should I search on Quora?")
                term = takecommand() or ""
            if term:
                dc.search_quora(term)
                response = f"Searching Quora for {term}"
            else:
                from engine.features import openCommand
                openCommand(query)
                response = "Opening Quora"

        elif "github" in query and not any(x in query for x in ("open", "launch")):
            term = query.replace("github", "").replace("search", "").replace("on", "").replace("for", "").strip()
            if term and len(term) > 2:
                dc.search_github(term)
                response = f"Searching GitHub for {term}"
            else:
                from engine.features import openCommand
                openCommand(query)
                response = "Opening GitHub"

        elif any(k in query for k in ("amazon search", "search amazon")):
            term = query.replace("search amazon for", "").replace("search amazon", "").replace("amazon search for", "").replace("amazon search", "").strip()
            if term:
                dc.search_amazon(term)
                response = f"Searching Amazon for {term}"
            else:
                speak("What should I search on Amazon?")
                term = takecommand()
                if term:
                    dc.search_amazon(term)
                    response = f"Searching Amazon for {term}"

        elif any(k in query for k in ("flipkart search", "search flipkart")):
            term = query.replace("search flipkart for", "").replace("search flipkart", "").replace("flipkart search for", "").replace("flipkart search", "").strip()
            if term:
                dc.search_flipkart(term)
                response = f"Searching Flipkart for {term}"
            else:
                speak("What should I search on Flipkart?")
                term = takecommand()
                if term:
                    dc.search_flipkart(term)
                    response = f"Searching Flipkart for {term}"

        elif any(k in query for k in ("maps search", "search maps", "google maps search", "map mein dhundho")):
            term = query
            for kw in ("search maps for ", "maps search for ", "search google maps for ", "google maps search for ", "map mein dhundho "):
                if kw in term:
                    term = term.replace(kw, "").strip()
            if term:
                dc.search_google_maps(term)
                response = f"Searching Maps for {term}"
            else:
                speak("What location should I search on Maps?")
                term = takecommand()
                if term:
                    dc.search_google_maps(term)
                    response = f"Searching Maps for {term}"

        elif any(k in query for k in ("gmail search", "search gmail", "email search", "mail mein dhundho")):
            term = query.replace("search gmail for", "").replace("search gmail", "").replace("gmail search for", "").replace("gmail search", "").replace("email search", "").replace("mail mein dhundho", "").strip()
            if term:
                dc.search_gmail(term)
                response = f"Searching Gmail for {term}"
            else:
                speak("What should I search in Gmail?")
                term = takecommand()
                if term:
                    dc.search_gmail(term)
                    response = f"Searching Gmail for {term}"

        elif any(k in query for k in ("scholar", "google scholar", "research paper search")):
            term = query.replace("scholar", "").replace("google scholar", "").replace("search", "").replace("for", "").strip()
            if term:
                dc.search_google_scholar(term)
                response = f"Searching Google Scholar for {term}"

        elif any(k in query for k in ("chatgpt", "gpt", "open ai query", "ask chatgpt")):
            from engine.features import openCommand
            term = query.replace("chatgpt", "").replace("gpt", "").replace("open ai", "").replace("ask", "").replace("search", "").replace("for", "").strip()
            if term and len(term) > 2:
                dc.search_chatgpt(term)
                response = f"Opening ChatGPT with query: {term}"
            else:
                openCommand(query)
                response = "Opening ChatGPT"
            _spoken = True

        # ══════════════════════════════════════════════════════════
        #  YOUTUBE PLAY (check before generic "open")
        # ══════════════════════════════════════════════════════════

        # ══════════════════════════════════════════════════════════
        #  YOUTUBE PLAY — MUST be BEFORE generic "open" branch
        #  Patterns:
        #    "play X on youtube / youtube pe"
        #    "open youtube and play X"
        #    "open youtube play X"          ← NEW
        #    "youtube mein X chalao"
        #    "youtube X play karo"
        #    "play the song X on youtube"   ← NEW
        # ══════════════════════════════════════════════════════════

        elif "youtube" in query and any(k in query for k in (
            "play", "chalao", "chala do", "laga do", "play karo",
            "play kar", "song play", "music play", "video play",
            "and play", "open and play", "the song", "song"
        )):
            import re as _re_yt
            song = ""
            # Pattern list — most specific first
            for pat in (
                r"open\s+youtube\s+(?:and\s+)?play\s+(?:the\s+song\s+)?(.+)",
                r"play\s+(?:the\s+song\s+)?(.+?)\s+(?:on|pe|par|mein)\s+youtube",
                r"youtube\s+(?:pe|par|mein|on)?\s+play\s+(?:the\s+song\s+)?(.+)",
                r"youtube\s+(?:mein|pe|par|on)?\s*(.+?)\s+(?:chalao|chala\s*do|laga\s*do|play\s*karo|play\s*kar)",
                r"youtube\s+(?:mein|pe|par|on)?\s*(.+?)\s+play",
                r"(?:play|chalao|chala\s*do|laga\s*do)\s+(.+?)\s+(?:on|pe|par|mein)?\s*youtube",
                r"youtube.+?(?:and\s+play|play\s+karo|chalao|chala\s*do|laga\s*do)\s+(.+)",
            ):
                m = _re_yt.search(pat, query, _re_yt.IGNORECASE)
                if m:
                    song = m.group(1).strip()
                    break

            # Fallback — strip all youtube/play/open keywords
            if not song:
                song = query
                for kw in ("open youtube and play", "open youtube play", "play on youtube",
                           "on youtube", "youtube pe", "youtube par", "youtube mein",
                           "youtube", "open", "and play", "play the song", "play karo",
                           "chalao", "chala do", "laga do", "play kar", "play", "the song"):
                    song = song.replace(kw, " ")
                song = " ".join(song.split()).strip()

            if song and len(song) > 1:
                from engine.features import PlayYoutube
                speak(f"YouTube pe {song} chala raha hoon")
                PlayYoutube(f"play {song} on youtube")
                response = f"Playing {song} on YouTube"
                _spoken = True
            else:
                # song name nahi mila — sirf YouTube open karo
                import webbrowser
                webbrowser.open("https://www.youtube.com/")
                speak("YouTube khol diya")
                response = "Opening YouTube"
                _spoken = True

        elif "on youtube" in query or "play on youtube" in query or "youtube pe chalao" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
            response = "Playing on YouTube"
            _spoken = True

        elif "play youtube" in query or "youtube play" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
            response = "Playing on YouTube"
            _spoken = True

        # ── "play <song>" — sirf "play believer" bolne par bhi YouTube pe play ──
        elif query.startswith("play ") and len(query) > 5:
            song = query[5:].strip()
            # ignore agar ye media control keywords hain
            if not any(k == song for k in ("music", "pause", "next", "prev", "stop", "resume")):
                from engine.features import PlayYoutube
                speak(f"YouTube pe {song} chala raha hoon")
                PlayYoutube(f"play {song} on youtube")
                response = f"Playing {song} on YouTube"
                _spoken = True

        # ── Hinglish: "believer bajao", "tere bina chala do", "kesariya sunao" ──
        elif any(query.endswith(k) for k in (
            " bajao", " baja do", " chalao", " chala do",
            " laga do", " laga", " sunao", " suna do", " suna"
        )):
            song = query
            for suffix in (" bajao", " baja do", " chalao", " chala do",
                           " laga do", " laga", " sunao", " suna do", " suna"):
                if song.endswith(suffix):
                    song = song[:-len(suffix)].strip()
                    break
            # common filler prefixes remove karo
            for prefix in ("zara ", "ek baar ", "please ", "thoda ", "abhi ", "mujhe "):
                if song.startswith(prefix):
                    song = song[len(prefix):].strip()
            if song and len(song) > 1:
                from engine.features import PlayYoutube
                speak(f"YouTube pe {song} chala raha hoon")
                PlayYoutube(f"play {song} on youtube")
                response = f"Playing {song} on YouTube"
                _spoken = True

        # ══════════════════════════════════════════════════════════
        #  OPEN APP / WEBSITE (generic, catches everything else with "open")
        # ══════════════════════════════════════════════════════════

        elif "open" in query:
            from engine.features import openCommand
            app = query.replace("open", "").strip()
            openCommand(query)
            response = f"Opening {app}" if app else "Opening"
            _spoken = True

        elif "launch" in query:
            from engine.features import openCommand
            app = query.replace("launch", "").strip()
            openCommand(query.replace("launch", "open"))
            response = f"Launching {app}" if app else "Launching"
            _spoken = True

        elif "kholo" in query or "chalao" in query or "shuru karo" in query or "start karo" in query:
            from engine.features import openCommand
            app = query.replace("kholo", "").replace("chalao", "").replace("shuru karo", "").replace("start karo", "").strip()
            openCommand(f"open {app}")
            response = f"Opening {app}" if app else "Opening"
            _spoken = True

        # ══════════════════════════════════════════════════════════
        #  CONTACTS / WHATSAPP
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("send message", "phone call", "video call", "whatsapp message", "whatsapp call")):
            from engine.features import findContact, makeCall, sendMessage, whatsApp
            contact_no, name = findContact(query)
            if contact_no and contact_no != 0:
                if "send message" in query or "whatsapp message" in query:
                    speak("What message should I send?")
                    msg = takecommand()
                    if msg:
                        sendMessage(msg, contact_no, name)
                        response = f"Message sent to {name}"
                    else:
                        response = "No message heard"
                elif "video call" in query:
                    whatsApp(contact_no, "", "video call", name)
                    response = f"Video call with {name}"
                elif "phone call" in query or "whatsapp call" in query:
                    makeCall(name, contact_no)
                    response = f"Calling {name}"
                _spoken = True   # whatsApp/makeCall/sendMessage internally speak
            else:
                response = "Contact not found"
                _spoken = True; speak(response)

        # ══════════════════════════════════════════════════════════
        #  TIME / DATE (extra variants)
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("time kya hai", "kitna baj gaya", "samay kya hai", "what is time", "current time", "time batao", "samay batao")):
            from datetime import datetime
            t = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {t}"
            _spoken = True; speak(response)

        elif any(k in query for k in ("aaj ki date", "date kya hai", "today date", "what is date", "date batao")):
            from datetime import datetime
            d = datetime.now().strftime("%B %d, %Y")
            response = f"Today is {d}"
            _spoken = True; speak(response)

        elif any(k in query for k in ("aaj kaun sa din", "day kya hai", "what day", "day of week")):
            from datetime import datetime
            day = datetime.now().strftime("%A")
            response = f"Today is {day}"
            _spoken = True; speak(response)

        # ══════════════════════════════════════════════════════════
        #  GREETINGS / IDENTITY (extra variants)
        # ══════════════════════════════════════════════════════════

        elif any(k in query for k in ("hello", "hi ", " hi", "hey", "namaste", "salaam", "sasriyakal", "namaskar", "ram ram", "radhe radhe", "good morning", "good afternoon", "good evening")):
            from datetime import datetime as _dt
            h = _dt.now().hour
            if h < 12:
                gr = "Good morning Sir! Jarvis here at your service. Bataiye kya karna hai?"
            elif h < 17:
                gr = "Good afternoon Sir! Main aapki kaise madad kar sakta hoon?"
            else:
                gr = "Good evening Sir! Bataiye aaj kya challenge hai?"
            response = gr
            _spoken = True; speak(gr)

        elif any(k in query for k in ("your name", "who are you", "naam kya hai tumhara", "aap kaun ho", "kaun ho tum", "tumhara naam kya hai")):
            response = "Main Jarvis hoon, aapka personal AI assistant. Aapke liye haazir hoon!"
            _spoken = True; speak(response)

        elif any(k in query for k in ("how are you", "kaise ho", "kya haal hai", "kaise ho aap")):
            response = "Main bilkul theek hoon Sir! Dhanyavaad. Aap bataiye, aap kaise hain?"
            _spoken = True; speak(response)

        elif any(k in query for k in ("thank you", "dhanyavaad", "shukriya", "thanks", "bahut bahut dhanyavaad")):
            response = "Bas yahi toh meri naukri hai Sir! Agar aur kuch chahiye toh boliye."
            _spoken = True; speak(response)

        elif any(k in query for k in ("who made you", "banaya kisne", "creator kon hai", "developer kon hai")):
            response = "Mujhe mere pyaare coder Sir ne banaya hai, jinke liye main 24x7 khidmat mein haazir hoon!"
            _spoken = True; speak(response)

        elif "joke" in query or "chutkula" in query or "suna do ek joke" in query:
            _jokes = [
                "Programmers kyun car nahi lete? Kyunki woh har sign pe 'This is not a bug, it's a feature' padh ke confuse ho jate hain!",
                "Ek programmer ne doctor ko bola: 'Doctor sahab, main sote huye bug fix kar deta hoon!' Doctor bola: 'Aapko sleep apnea nahi, sleep API bug hai!'",
                "Jarvis ka favorite song kya hai? 'Wake me up before you go go...' kyuki hamesha wake word hi sunta rehta hai!",
                "Why did the developer go broke? Because he used up all his cache!",
                "SQL query walks into a bar, goes to two tables and asks: 'Can I JOIN you?'"
            ]
            import random as _rnd
            j = _rnd.choice(_jokes)
            response = j
            _spoken = True; speak(j)

        elif any(k in query for k in ("kya kar sakte ho", "kya kar sakta hai", "kya kar loge", "what can you do", "help me", "help jarvis", "functions", "features")):
            features_msg = ("Main aapke liye yeh sab kar sakta hoon: "
                "1. Window control: minimize, maximize, snap, close, switch. "
                "2. Media: play, pause, next, volume up/down, mute. "
                "3. Apps open: Chrome, Edge, Notepad, WhatsApp, Calculator, VS Code, Word, Excel, PowerPoint, Spotify, Discord, Zoom, Teams, Paint, CMD, PowerShell, Terminal, Settings, Task Manager, Snipping tool, Sticky notes, and 200+ more. "
                "4. 50+ websites open: Google, YouTube, Gmail, Facebook, Instagram, GitHub, ChatGPT, Netflix, Amazon, Flipkart, Zomato, Swiggy, MakeMyTrip, etc. "
                "5. Search: Google, YouTube, Bing, Wikipedia, StackOverflow, Amazon, Flipkart, Gmail, Maps, Scholar. "
                "6. Screenshot, typing text, clipboard, brightness, WiFi/IP/battery info, create files/folders, clean temp. "
                "7. Translate, calculate, WhatsApp messages/calls, YouTube play, emoji, dictation mode. "
                "Bataiye kya chahiye!")
            response = features_msg
            _spoken = True; speak(features_msg)

        # ══════════════════════════════════════════════════════════
        #  CHATBOT FALLBACK
        # ══════════════════════════════════════════════════════════

        else:
            from engine.features import chatBot
            response = chatBot(query) or f"I heard: {query}"
            _spoken = True   # chatBot() already calls speak() internally

    except Exception as e:
        print(f"[CMD Error]: {e}")
        import traceback
        traceback.print_exc()
        response = "Sorry, something went wrong."
        _spoken = True; speak(response)

    # ── Universal speak — har command ke baad Jarvis bolta hai ──────────
    if response and not _spoken:
        speak(response)

    # ── Push to activity log ─────────────────────────────────────────────
    if response:
        _push_event(f"JARVIS ◀ {response}", "success")

    return response
