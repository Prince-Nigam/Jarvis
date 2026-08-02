"""
desktop_control.py — Full Desktop Control for Jarvis
Voice se laptop control karo:
- Window management (minimize, maximize, close, switch)
- Keyboard shortcuts (copy, paste, undo, redo, select all, etc.)
- Mouse control (click, scroll, move)
- File/Folder operations (open folder, create folder, delete)
- System actions (lock, sleep, empty recycle bin, task manager)
- Media control (play/pause, next, previous, stop)
- Screenshot (full, region)
- Typing text
- Brightness control
- Clipboard operations
- Search on desktop
"""
import os
import subprocess
import time

try:
    import pyautogui
    pyautogui.FAILSAFE = True   # move mouse to corner to abort
    pyautogui.PAUSE    = 0.05
    _HAS_GUI = True
except Exception:
    pyautogui = None
    _HAS_GUI  = False

from engine.command import speak


# ═══════════════════════════════════════════════════════════════
#  WINDOW MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def minimize_window():
    """Minimize current active window."""
    if not _HAS_GUI:
        speak("PyAutoGUI not available")
        return
    pyautogui.hotkey("win", "down")
    speak("Window minimized")


def maximize_window():
    """Maximize current active window."""
    if not _HAS_GUI:
        speak("PyAutoGUI not available")
        return
    pyautogui.hotkey("win", "up")
    speak("Window maximized")


def close_window():
    """Close current active window."""
    if not _HAS_GUI:
        speak("PyAutoGUI not available")
        return
    pyautogui.hotkey("alt", "f4")
    speak("Window closed")


def switch_window():
    """Open Alt+Tab to switch windows."""
    if not _HAS_GUI:
        speak("PyAutoGUI not available")
        return
    pyautogui.hotkey("alt", "tab")
    speak("Switching window")


def show_desktop():
    """Show desktop — minimizes all windows."""
    if not _HAS_GUI:
        speak("PyAutoGUI not available")
        return
    pyautogui.hotkey("win", "d")
    speak("Showing desktop")


def snap_left():
    """Snap window to left half."""
    if not _HAS_GUI:
        return
    pyautogui.hotkey("win", "left")
    speak("Snapped to left")


def snap_right():
    """Snap window to right half."""
    if not _HAS_GUI:
        return
    pyautogui.hotkey("win", "right")
    speak("Snapped to right")


def open_task_view():
    """Open Windows Task View (all virtual desktops)."""
    if not _HAS_GUI:
        return
    pyautogui.hotkey("win", "tab")
    speak("Opening task view")


# ═══════════════════════════════════════════════════════════════
#  KEYBOARD SHORTCUTS
# ═══════════════════════════════════════════════════════════════

def copy():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "c")
    speak("Copied")

def paste():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "v")
    speak("Pasted")

def cut():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "x")
    speak("Cut")

def undo():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "z")
    speak("Undo done")

def redo():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "y")
    speak("Redo done")

def select_all():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "a")
    speak("Selected all")

def save_file():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "s")
    speak("Saved")

def new_tab():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "t")
    speak("New tab opened")

def close_tab():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "w")
    speak("Tab closed")

def refresh_page():
    if not _HAS_GUI: return
    pyautogui.press("f5")
    speak("Refreshed")

def go_back():
    if not _HAS_GUI: return
    pyautogui.hotkey("alt", "left")
    speak("Going back")

def go_forward():
    if not _HAS_GUI: return
    pyautogui.hotkey("alt", "right")
    speak("Going forward")

def zoom_in():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "+")
    speak("Zoomed in")

def zoom_out():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "-")
    speak("Zoomed out")

def find_on_page():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "f")
    speak("Find opened")

def open_new_window():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "n")
    speak("New window opened")


# ═══════════════════════════════════════════════════════════════
#  MEDIA CONTROL
# ═══════════════════════════════════════════════════════════════

def media_play_pause():
    if not _HAS_GUI: return
    pyautogui.press("playpause")
    speak("Play pause toggled")

def media_next():
    if not _HAS_GUI: return
    pyautogui.press("nexttrack")
    speak("Next track")

def media_previous():
    if not _HAS_GUI: return
    pyautogui.press("prevtrack")
    speak("Previous track")

def media_stop():
    if not _HAS_GUI: return
    pyautogui.press("stop")
    speak("Media stopped")

def volume_up(steps=5):
    if not _HAS_GUI: return
    pyautogui.press("volumeup", presses=steps)
    speak("Volume increased")

def volume_down(steps=5):
    if not _HAS_GUI: return
    pyautogui.press("volumedown", presses=steps)
    speak("Volume decreased")

def mute_volume():
    if not _HAS_GUI: return
    pyautogui.press("volumemute")
    speak("Muted")


# ═══════════════════════════════════════════════════════════════
#  SCREENSHOT
# ═══════════════════════════════════════════════════════════════

def take_screenshot(filename=None):
    """Take full screenshot and save to Desktop."""
    if not _HAS_GUI:
        speak("Screenshot not available")
        return None
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if filename is None:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(desktop, f"screenshot_{ts}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        speak(f"Screenshot saved to Desktop")
        print(f"[Screenshot] Saved: {filename}")
        return filename
    except Exception as e:
        print(f"[Screenshot] Error: {e}")
        speak("Could not take screenshot")
        return None


# ═══════════════════════════════════════════════════════════════
#  TYPE TEXT
# ═══════════════════════════════════════════════════════════════

def type_text(text):
    """Type text at current cursor position."""
    if not _HAS_GUI:
        speak("Typing not available")
        return
    try:
        pyautogui.write(text, interval=0.05)
        speak(f"Typed: {text}")
    except Exception as e:
        print(f"[Type] Error: {e}")
        speak("Could not type text")


def press_enter():
    if not _HAS_GUI: return
    pyautogui.press("enter")

def press_escape():
    if not _HAS_GUI: return
    pyautogui.press("escape")
    speak("Escaped")

def press_delete():
    if not _HAS_GUI: return
    pyautogui.press("delete")
    speak("Deleted")

def press_backspace():
    if not _HAS_GUI: return
    pyautogui.press("backspace")


# ═══════════════════════════════════════════════════════════════
#  SCROLL
# ═══════════════════════════════════════════════════════════════

def scroll_down(clicks=5):
    if not _HAS_GUI: return
    pyautogui.scroll(-clicks)
    speak("Scrolled down")

def scroll_up(clicks=5):
    if not _HAS_GUI: return
    pyautogui.scroll(clicks)
    speak("Scrolled up")


# ═══════════════════════════════════════════════════════════════
#  FILE / FOLDER OPERATIONS
# ═══════════════════════════════════════════════════════════════

def open_folder(folder_name):
    """Open a common folder by voice name."""
    folder_map = {
        "desktop":    os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads":  os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents":  os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures":   os.path.join(os.path.expanduser("~"), "Pictures"),
        "music":      os.path.join(os.path.expanduser("~"), "Music"),
        "videos":     os.path.join(os.path.expanduser("~"), "Videos"),
        "c drive":    "C:\\",
        "d drive":    "D:\\",
        "e drive":    "E:\\",
        "recycle bin": "shell:RecycleBinFolder",
        "this pc":    "shell:MyComputerFolder",
        "my computer": "shell:MyComputerFolder",
    }
    path = folder_map.get(folder_name.lower())
    if path:
        try:
            if path.startswith("shell:"):
                subprocess.Popen(["explorer.exe", path])
            else:
                os.startfile(path)
            speak(f"Opening {folder_name}")
        except Exception as e:
            print(f"[Folder] Error: {e}")
            speak("Could not open folder")
    else:
        # Try to open as direct path
        if os.path.exists(folder_name):
            os.startfile(folder_name)
            speak(f"Opening {folder_name}")
        else:
            speak(f"Folder {folder_name} not found")


def empty_recycle_bin():
    """Empty the Recycle Bin silently."""
    try:
        import winshell
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        speak("Recycle bin emptied")
    except ImportError:
        # Fallback using PowerShell
        try:
            subprocess.run(
                ["powershell", "-Command",
                 "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                capture_output=True, timeout=10
            )
            speak("Recycle bin emptied")
        except Exception as e:
            print(f"[RecycleBin] Error: {e}")
            speak("Could not empty recycle bin")
    except Exception as e:
        print(f"[RecycleBin] Error: {e}")
        speak("Could not empty recycle bin")


# ═══════════════════════════════════════════════════════════════
#  SYSTEM ACTIONS
# ═══════════════════════════════════════════════════════════════

def lock_screen():
    """Lock the Windows screen."""
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        speak("Screen locked")
    except Exception as e:
        print(f"[Lock] Error: {e}")
        speak("Could not lock screen")


def sleep_system():
    """Put system to sleep."""
    speak("Putting system to sleep")
    time.sleep(1)
    try:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    except Exception as e:
        print(f"[Sleep] Error: {e}")


def open_task_manager():
    """Open Task Manager."""
    try:
        subprocess.Popen(["taskmgr.exe"])
        speak("Opening Task Manager")
    except Exception as e:
        print(f"[TaskManager] Error: {e}")
        speak("Could not open Task Manager")


def open_settings():
    """Open Windows Settings."""
    try:
        subprocess.Popen(["ms-settings:"])
        speak("Opening Settings")
    except Exception:
        try:
            subprocess.Popen(["control.exe"])
            speak("Opening Control Panel")
        except Exception as e:
            print(f"[Settings] Error: {e}")


def open_run_dialog():
    """Open Windows Run dialog."""
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "r")
    speak("Run dialog opened")


def open_search():
    """Open Windows Search."""
    if not _HAS_GUI: return
    pyautogui.press("win")
    speak("Search opened")


def open_notification_center():
    """Open Windows Notification Center."""
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "a")
    speak("Notification center opened")


def open_clipboard_history():
    """Open Windows Clipboard History (Win+V)."""
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "v")
    speak("Clipboard history opened")


def virtual_keyboard():
    """Open On-Screen Keyboard."""
    try:
        subprocess.Popen(["osk.exe"])
        speak("Virtual keyboard opened")
    except Exception as e:
        print(f"[OSK] Error: {e}")


def open_magnifier():
    """Open Windows Magnifier."""
    try:
        subprocess.Popen(["magnify.exe"])
        speak("Magnifier opened")
    except Exception as e:
        print(f"[Magnifier] Error: {e}")


# ═══════════════════════════════════════════════════════════════
#  BRIGHTNESS CONTROL
# ═══════════════════════════════════════════════════════════════

def _get_brightness():
    """Get current brightness (0-100). Returns -1 if unavailable."""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            capture_output=True, text=True, timeout=5
        )
        val = result.stdout.strip()
        return int(val) if val.isdigit() else -1
    except Exception:
        return -1


def set_brightness(level):
    """Set brightness level (0-100)."""
    level = max(0, min(100, level))
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
             f".WmiSetBrightness(1,{level})"],
            capture_output=True, timeout=5
        )
        speak(f"Brightness set to {level} percent")
    except Exception as e:
        print(f"[Brightness] Error: {e}")
        speak("Could not change brightness")


def brightness_up():
    current = _get_brightness()
    if current == -1:
        set_brightness(80)
    else:
        set_brightness(min(100, current + 20))


def brightness_down():
    current = _get_brightness()
    if current == -1:
        set_brightness(40)
    else:
        set_brightness(max(0, current - 20))


# ═══════════════════════════════════════════════════════════════
#  CLIPBOARD
# ═══════════════════════════════════════════════════════════════

def get_clipboard_text():
    """Return current clipboard text."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text
    except Exception:
        return ""


def set_clipboard_text(text):
    """Copy text to clipboard."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        speak("Copied to clipboard")
    except Exception as e:
        print(f"[Clipboard] Error: {e}")


# ═══════════════════════════════════════════════════════════════
#  INTERNET / SEARCH
# ═══════════════════════════════════════════════════════════════

def search_google(query):
    """Search on Google."""
    from urllib.parse import quote
    import webbrowser
    url = f"https://www.google.com/search?q={quote(query)}"
    webbrowser.open(url)
    speak(f"Searching Google for {query}")


def search_youtube(query):
    """Search on YouTube."""
    from urllib.parse import quote
    import webbrowser
    url = f"https://www.youtube.com/results?search_query={quote(query)}"
    webbrowser.open(url)
    speak(f"Searching YouTube for {query}")
