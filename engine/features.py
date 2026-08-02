import os
import sqlite3
import subprocess
import time
import webbrowser
from urllib.parse import quote

try:
    from playsound import playsound
except ModuleNotFoundError:
    playsound = None

try:
    import eel
except ModuleNotFoundError:
    eel = None

try:
    import pyaudio
except ModuleNotFoundError:
    pyaudio = None

try:
    import pywhatkit as kit
except ModuleNotFoundError:
    kit = None

try:
    import pyautogui
except ModuleNotFoundError:
    pyautogui = None

try:
    from hugchat import hugchat
except ModuleNotFoundError:
    hugchat = None

from engine.command import speak
from engine.config import ASSISTANT_NAME, PORCUPINE_ACCESS_KEY
from engine.helper import extract_yt_term, remove_words
from engine.init_db import DB_PATH, init_database

init_database()


def _get_cursor():
    """Return a fresh connection and cursor. Caller must close the connection."""
    con = sqlite3.connect(DB_PATH)
    return con, con.cursor()

START_SOUND = os.path.join("www", "assets", "audio", "start_sound.mp3")


def playAssistantSound():
    if playsound is None:
        print("playsound is not installed; skipping assistant sound")
        return
    if not os.path.exists(START_SOUND):
        print("Startup sound file not found; skipping")
        return
    try:
        playsound(START_SOUND)
    except Exception as exc:
        print(f"Startup sound skipped: {exc}")


if eel is not None:
    eel.expose(playAssistantSound)


EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def _open_in_browser(url):
    if os.path.exists(EDGE_PATH):
        subprocess.Popen([EDGE_PATH, url])
    else:
        webbrowser.open(url)


# ── Known Windows desktop app paths ───────────────────────────────────────────
# Maps voice command name → possible install paths (first found is used)
_DESKTOP_APPS = {
    "whatsapp": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"WhatsApp\WhatsApp.exe"),
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\WhatsApp.lnk"),
        "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    ],
    "telegram": [
        os.path.join(os.environ.get("APPDATA", ""), r"Telegram Desktop\Telegram.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Telegram Desktop\Telegram.exe"),
    ],
    "spotify": [
        os.path.join(os.environ.get("APPDATA", ""), r"Spotify\Spotify.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\WindowsApps\Spotify.exe"),
    ],
    "discord": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Discord\Update.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Discord\app-*\Discord.exe"),
    ],
    "vscode": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "visual studio code": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "notepad": [r"C:\Windows\notepad.exe"],
    "notepad++": [
        r"C:\Program Files\Notepad++\notepad++.exe",
        r"C:\Program Files (x86)\Notepad++\notepad++.exe",
    ],
    "calculator": [r"C:\Windows\System32\calc.exe"],
    "paint": [r"C:\Windows\System32\mspaint.exe"],
    "word": [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
    ],
    "excel": [
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
    ],
    "powerpoint": [
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
    ],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "google chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "vlc": [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ],
    "file explorer": [r"C:\Windows\explorer.exe"],
    "explorer": [r"C:\Windows\explorer.exe"],
    "task manager": [r"C:\Windows\System32\Taskmgr.exe"],
    "control panel": [r"C:\Windows\System32\control.exe"],
    "settings": ["ms-settings:"],   # UWP settings URI
    "camera": ["microsoft.windows.camera:"],
    "photos": ["ms-photos:"],
    "store": ["ms-windows-store:"],
}

# Web fallbacks for apps that open better in browser
_WEB_FALLBACKS = {
    "whatsapp": "https://web.whatsapp.com/",
    "telegram": "https://web.telegram.org/",
    "spotify":  "https://open.spotify.com/",
    "discord":  "https://discord.com/app",
    "gmail":    "https://mail.google.com/",
    "google":   "https://www.google.com/",
    "youtube":  "https://www.youtube.com/",
    "maps":     "https://maps.google.com/",
    "google maps": "https://maps.google.com/",
    "instagram": "https://www.instagram.com/",
    "facebook":  "https://www.facebook.com/",
    "twitter":   "https://x.com/",
    "github":    "https://github.com/",
    "chatgpt":   "https://chatgpt.com/",
    "linkedin":  "https://www.linkedin.com/",
    "reddit":    "https://www.reddit.com/",
    "netflix":   "https://www.netflix.com/",
    "amazon":    "https://www.amazon.in/",
    "flipkart":  "https://www.flipkart.com/",
    "hotstar":   "https://www.hotstar.com/",
}


def _try_open_desktop_app(app_name):
    """
    Try to open a known desktop app by name.
    Returns True if opened successfully, False otherwise.
    """
    import glob
    paths = _DESKTOP_APPS.get(app_name, [])
    for path in paths:
        # Handle UWP protocol URIs (e.g. ms-settings:, ms-photos:)
        if path.startswith("ms-") or path.startswith("microsoft."):
            try:
                os.startfile(path)
                return True
            except Exception:
                continue
        # Handle shell:AppsFolder URIs for Store/UWP apps
        if path.startswith("shell:"):
            try:
                subprocess.Popen(["explorer.exe", path], shell=False)
                return True
            except Exception:
                try:
                    os.system(f'start "" "{path}"')
                    return True
                except Exception:
                    continue
        # Handle glob patterns (e.g. Discord app-* folders)
        if "*" in path:
            matches = glob.glob(path)
            if matches:
                try:
                    subprocess.Popen([matches[0]], shell=False)
                    return True
                except Exception:
                    continue
        # .lnk shortcut files
        if path.endswith(".lnk") and os.path.exists(path):
            try:
                os.startfile(path)
                return True
            except Exception:
                continue
        # Direct executable path
        if os.path.exists(path):
            try:
                subprocess.Popen([path], shell=False)
                return True
            except Exception:
                continue
    return False


def _open_via_start_menu(app_name):
    """
    Try to launch app by searching Windows Start Menu using PowerShell.
    This handles UWP apps (like WhatsApp from Microsoft Store).
    Returns True if likely launched.
    """
    try:
        # Use 'start' command which Windows resolves from PATH + app aliases
        result = subprocess.run(
            ["powershell", "-Command",
             f"Start-Process '{app_name}' -ErrorAction Stop"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").strip()
    if query.lower().startswith("open "):
        target = query[5:].strip()
    elif query.lower() == "open":
        return
    else:
        target = query.replace("open", "").strip()

    if not target:
        return

    app_name = target.lower().strip()

    # 1. Check local system commands database table (user-added custom apps)
    con, cursor = _get_cursor()
    try:
        cursor.execute(
            "SELECT path FROM sys_command WHERE LOWER(name) = ?", (app_name,)
        )
        results = cursor.fetchall()
        if results:
            speak("Opening " + target)
            os.startfile(results[0][0])
            return

        # 2. Check registered web commands database table
        cursor.execute(
            "SELECT url FROM web_command WHERE LOWER(name) = ?", (app_name,)
        )
        results = cursor.fetchall()
        if results:
            speak("Opening " + target)
            _open_in_browser(results[0][0])
            return
    except Exception as e:
        print(f"[openCommand DB error]: {e}")
    finally:
        con.close()

    speak("Opening " + target)

    # 3. Try known desktop apps list first
    if app_name in _DESKTOP_APPS:
        if _try_open_desktop_app(app_name):
            print(f"[openCommand] Opened desktop app: {app_name}")
            return
        # Desktop app not found — fall through to web fallback
        if app_name in _WEB_FALLBACKS:
            _open_in_browser(_WEB_FALLBACKS[app_name])
            return

    # 4. Try web fallbacks for social/streaming apps
    if app_name in _WEB_FALLBACKS:
        _open_in_browser(_WEB_FALLBACKS[app_name])
        return

    # 5. If explicit domain or URL given (e.g. github.com, python.org)
    if any(app_name.endswith(tld) for tld in [".com", ".org", ".net", ".io", ".in", ".ai", ".co", ".gov", ".edu", ".dev"]):
        url = app_name if app_name.startswith("http") else f"https://{app_name}"
        _open_in_browser(url)
        return

    # 6. Try Windows Start Menu / app alias (handles Store apps, PATH apps)
    if _open_via_start_menu(app_name):
        print(f"[openCommand] Opened via Start Menu: {app_name}")
        return

    # 7. Single-word — try as website
    if " " not in app_name:
        _open_in_browser(f"https://www.{app_name}.com")
        return

    # 8. Multi-word — Google search & launch
    _open_in_browser(f"https://www.google.com/search?q={quote(target)}")


def PlayYoutube(query):
    if kit is None:
        speak("YouTube feature is not available")
        return

    search_term = extract_yt_term(query)
    if not search_term:
        speak("Please tell me what to play on YouTube")
        return

    speak("Playing " + search_term + " on YouTube")
    kit.playonyt(search_term)


def findContact(query):
    words_to_remove = [
        ASSISTANT_NAME,
        "make",
        "a",
        "to",
        "phone",
        "call",
        "send",
        "message",
        "whatsapp",
        "video",
    ]
    query = remove_words(query, words_to_remove)

    con, cursor = _get_cursor()
    try:
        query = query.strip().lower()
        cursor.execute(
            "SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
            ("%" + query + "%", query + "%"),
        )
        results = cursor.fetchall()
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith("+91"):
            mobile_number_str = "+91" + mobile_number_str

        return mobile_number_str, query
    except Exception:
        speak("Contact not found")
        return 0, 0
    finally:
        con.close()


def whatsApp(mobile_no, message, flag, name):
    if flag == "message":
        target_tab = 12
        jarvis_message = "Message sent successfully to " + name
    elif flag == "call":
        target_tab = 7
        message = ""
        jarvis_message = "Calling " + name
    else:
        target_tab = 6
        message = ""
        jarvis_message = "Starting video call with " + name

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'cmd /c start "" "{whatsapp_url}"'
    subprocess.run(full_command, shell=True)

    if pyautogui is None:
        speak(jarvis_message)
        return

    time.sleep(5)
    pyautogui.hotkey("ctrl", "f")

    for _ in range(1, target_tab):
        pyautogui.press("tab")

    pyautogui.press("enter")
    speak(jarvis_message)


def _simple_chat_fallback(query):
    from datetime import datetime

    text = query.lower()
    if "time" in text:
        return f"The time is {datetime.now().strftime('%I:%M %p')}"
    if "date" in text:
        return f"Today is {datetime.now().strftime('%B %d, %Y')}"
    if "hello" in text or "hi" in text:
        return "Hello Sir, how can I help you?"
    return f"I heard: {query}. Configure HugChat cookies for full chat support."


# Reuse chatbot session across calls so conversation history is preserved
_chatbot_instance = None
_chatbot_conv_id  = None

def chatBot(query):
    global _chatbot_instance, _chatbot_conv_id

    cookie_path = os.path.join(os.path.dirname(__file__), "cookies.json")

    if hugchat is None or not os.path.exists(cookie_path):
        response = _simple_chat_fallback(query)
        speak(response)
        return response

    try:
        user_input = query.lower()

        # Create session once, reuse afterwards
        if _chatbot_instance is None:
            _chatbot_instance = hugchat.ChatBot(cookie_path=cookie_path)
            _chatbot_conv_id  = _chatbot_instance.new_conversation()

        _chatbot_instance.change_conversation(_chatbot_conv_id)
        response = str(_chatbot_instance.chat(user_input))
        speak(response)
        return response
    except Exception as exc:
        print(f"Chat error: {exc}")
        # Reset on error so next call gets a fresh session
        _chatbot_instance = None
        _chatbot_conv_id  = None
        response = _simple_chat_fallback(query)
        speak(response)
        return response


def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    os.system(
        "adb shell am start -a android.intent.action.CALL -d tel:" + mobileNo
    )


def sendMessage(message, mobileNo, name):
    from engine.helper import (
        adbInput,
        goback,
        keyEvent,
        replace_spaces_with_percent_s,
        tapEvents,
    )

    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("Sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    tapEvents(136, 2220)
    tapEvents(819, 2192)
    adbInput(mobileNo)
    tapEvents(601, 574)
    tapEvents(390, 2270)
    adbInput(message)
    tapEvents(957, 1397)
    speak("Message sent successfully to " + name)
