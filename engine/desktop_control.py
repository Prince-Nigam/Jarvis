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
    speak("Enter pressed")

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
    speak("Backspace pressed")


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
#  MOUSE CONTROL
# ═══════════════════════════════════════════════════════════════

def left_click():
    if not _HAS_GUI: return
    pyautogui.click()
    speak("Left clicked")

def right_click():
    if not _HAS_GUI: return
    pyautogui.rightClick()
    speak("Right clicked")

def double_click():
    if not _HAS_GUI: return
    pyautogui.doubleClick()
    speak("Double clicked")

def middle_click():
    if not _HAS_GUI: return
    pyautogui.middleClick()
    speak("Middle clicked")

def move_mouse(x_offset=0, y_offset=0):
    if not _HAS_GUI: return
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x + x_offset, y + y_offset, duration=0.3)
        if x_offset != 0 or y_offset != 0:
            speak("Mouse moved")
    except Exception:
        pass

def mouse_to_center():
    if not _HAS_GUI: return
    try:
        w, h = pyautogui.size()
        pyautogui.moveTo(w // 2, h // 2, duration=0.3)
        speak("Mouse moved to center")
    except Exception:
        pass

def drag_select(x1, y1, x2, y2):
    if not _HAS_GUI: return
    try:
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=0.4, button='left')
        speak("Selection done")
    except Exception:
        pass

def scroll_left(clicks=5):
    if not _HAS_GUI: return
    pyautogui.hscroll(clicks)
    speak("Scrolled left")

def scroll_right(clicks=5):
    if not _HAS_GUI: return
    pyautogui.hscroll(-clicks)
    speak("Scrolled right")

def scroll_to_top():
    if not _HAS_GUI: return
    pyautogui.scroll(1000)
    speak("Scrolled to top")

def scroll_to_bottom():
    if not _HAS_GUI: return
    pyautogui.scroll(-1000)
    speak("Scrolled to bottom")


# ═══════════════════════════════════════════════════════════════
#  MORE KEYBOARD SHORTCUTS (Text editing, browser, system)
# ═══════════════════════════════════════════════════════════════

def text_bold():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "b")
    speak("Bold applied")

def text_italic():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "i")
    speak("Italic applied")

def text_underline():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "u")
    speak("Underline applied")

def text_strikethrough():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "s")
    speak("Strikethrough applied")

def find_and_replace():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "h")
    speak("Find and replace opened")

def print_document():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "p")
    speak("Print dialog opened")

def open_task_manager_shortcut():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "esc")
    speak("Task manager opened")

def fullscreen_toggle():
    if not _HAS_GUI: return
    pyautogui.press("f11")
    speak("Fullscreen toggled")

def exit_app():
    if not _HAS_GUI: return
    pyautogui.hotkey("alt", "f4")
    speak("Closing app")

def new_document():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "n")
    speak("New document")

def open_document():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "o")
    speak("Open file dialog")

def rename_item():
    if not _HAS_GUI: return
    pyautogui.press("f2")
    speak("Rename mode")

def refresh_everything():
    if not _HAS_GUI: return
    pyautogui.press("f5")
    pyautogui.hotkey("ctrl", "r")
    speak("Refreshed")

def restore_tab():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "t")
    speak("Tab restored")

def close_all_tabs():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "w")
    speak("All tabs closed")

def switch_to_next_tab():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "tab")
    speak("Next tab")

def switch_to_previous_tab():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "tab")
    speak("Previous tab")

def jump_to_tab(n):
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", str(n))
    speak(f"Switched to tab {n}")

def go_to_address_bar():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "l")
    speak("Address bar focused")

def open_history():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "h")
    speak("History opened")

def open_bookmarks():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "o")
    speak("Bookmarks opened")

def open_downloads():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "j")
    speak("Downloads opened")

def open_developer_tools():
    if not _HAS_GUI: return
    pyautogui.press("f12")
    speak("Developer tools opened")

def open_incognito():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "n")
    speak("Incognito window opened")

def open_private_window():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "shift", "p")
    speak("Private window opened")

def toggle_bookmark():
    if not _HAS_GUI: return
    pyautogui.hotkey("ctrl", "d")
    speak("Bookmark toggled")

def take_printscreen():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "printscreen")
    speak("Screenshot captured")

def open_snipping_tool():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "shift", "s")
    speak("Snipping tool activated")

def open_emoji_panel():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", ".")
    speak("Emoji panel opened")

def open_dictation():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "h")
    speak("Dictation mode started")

def open_game_bar():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "g")
    speak("Game bar opened")

def project_screen():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "p")
    speak("Project menu opened")

def open_quick_link_menu():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "x")
    speak("Quick link menu opened")

def minimize_all_windows():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "m")
    speak("All windows minimized")

def restore_all_windows():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "shift", "m")
    speak("All windows restored")

def window_menu():
    if not _HAS_GUI: return
    pyautogui.hotkey("alt", "space")
    speak("Window menu opened")

def minimize_others():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "home")
    speak("Other windows minimized")

def snap_up():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "up")
    speak("Window snapped up")

def snap_down():
    if not _HAS_GUI: return
    pyautogui.hotkey("win", "down")
    speak("Window snapped down")

def tile_windows():
    """Tile windows side by side using Win+Left / Win+Right."""
    if not _HAS_GUI: return
    try:
        # Snap current window to left half, then switch and snap next to right
        pyautogui.hotkey("win", "left")
        time.sleep(0.3)
        pyautogui.hotkey("win", "right")
        speak("Windows tiled")
    except Exception as e:
        print(f"[TileWindows] Error: {e}")

def restart_windows_explorer():
    """Restart explorer.exe if desktop/taskbar hangs."""
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, timeout=10)
        time.sleep(1)
        subprocess.Popen(["explorer.exe"])
        speak("Windows explorer restarted")
    except Exception as e:
        print(f"[Explorer] Error: {e}")
        speak("Could not restart explorer")


# ═══════════════════════════════════════════════════════════════
#  MORE FILE / FOLDER OPERATIONS
# ═══════════════════════════════════════════════════════════════

def create_new_folder(folder_name="New Folder"):
    """Create folder on Desktop by default."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, folder_name)
        counter = 1
        while os.path.exists(path):
            path = os.path.join(desktop, f"{folder_name} ({counter})")
            counter += 1
        os.makedirs(path, exist_ok=True)
        speak(f"Folder {folder_name} created on Desktop")
        print(f"[Folder] Created: {path}")
    except Exception as e:
        print(f"[CreateFolder] Error: {e}")
        speak("Could not create folder")

def create_new_text_file(filename="New Text File"):
    """Create text file on Desktop."""
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, f"{filename}.txt")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(desktop, f"{filename} ({counter}).txt")
            counter += 1
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        speak(f"Text file {filename} created on Desktop")
        print(f"[File] Created: {path}")
        os.startfile(path)
    except Exception as e:
        print(f"[CreateFile] Error: {e}")
        speak("Could not create file")

def delete_selected_item():
    if not _HAS_GUI: return
    pyautogui.press("delete")
    speak("Moved to recycle bin")

def delete_permanently():
    if not _HAS_GUI: return
    pyautogui.hotkey("shift", "delete")
    speak("Item permanently deleted")

def copy_path_of_selected():
    """Copy the path of selected file (Shift+Right-click -> Copy as path)."""
    if not _HAS_GUI: return
    try:
        pyautogui.hotkey("shift", "f10")
        time.sleep(0.3)
        pyautogui.press("a")
        speak("File path copied")
    except Exception:
        pass

def open_command_prompt():
    """Open cmd in current folder or default."""
    try:
        subprocess.Popen(["cmd.exe"], cwd=os.path.expanduser("~"))
        speak("Command prompt opened")
    except Exception as e:
        print(f"[CMD] Error: {e}")
        speak("Could not open command prompt")

def open_powershell():
    """Open PowerShell."""
    try:
        subprocess.Popen(["powershell.exe"], cwd=os.path.expanduser("~"))
        speak("PowerShell opened")
    except Exception as e:
        print(f"[PowerShell] Error: {e}")
        speak("Could not open PowerShell")

def open_windows_terminal():
    """Open Windows Terminal if available."""
    try:
        subprocess.Popen(["wt.exe"], cwd=os.path.expanduser("~"), shell=True)
        speak("Windows terminal opened")
    except Exception:
        try:
            subprocess.Popen(["powershell.exe"], cwd=os.path.expanduser("~"))
            speak("PowerShell opened")
        except Exception as e:
            print(f"[Terminal] Error: {e}")

def run_shell_command(cmd):
    """Run a shell command safely (non-blocking, capture output)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True,
                                text=True, timeout=30)
        output = (result.stdout or "") + (result.stderr or "")
        print(f"[Cmd] {cmd}\n{output[:500]}")
        return output
    except Exception as e:
        print(f"[Cmd] Error: {e}")
        return str(e)

def clear_temp_files():
    """Clear Windows temp files (user temp)."""
    import shutil
    temp_dir = os.environ.get("TEMP", os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp"))
    count = 0
    try:
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    count += 1
            except Exception:
                continue
        speak(f"Temp folder cleaned. {count} items removed")
    except Exception as e:
        print(f"[TempClean] Error: {e}")
        speak(f"Could not clean temp. {count} items removed")


# ═══════════════════════════════════════════════════════════════
#  MORE SYSTEM ACTIONS
# ═══════════════════════════════════════════════════════════════

def sign_out_user():
    """Log off current user."""
    speak("Signing out in 3 seconds")
    time.sleep(3)
    try:
        subprocess.Popen(["shutdown.exe", "/l"])
    except Exception as e:
        print(f"[SignOut] Error: {e}")

def hibernate_system():
    """Hibernate system."""
    speak("Hibernating system")
    time.sleep(1)
    try:
        subprocess.run(["shutdown.exe", "/h"])
    except Exception as e:
        print(f"[Hibernate] Error: {e}")

def restart_pc():
    """Restart PC with warning."""
    speak("Restarting computer in 10 seconds. Save your work.")
    for i in range(9, 0, -1):
        time.sleep(1)
        print(f"[Restart] {i} seconds...")
    try:
        subprocess.Popen(["shutdown.exe", "/r", "/t", "0"])
    except Exception as e:
        print(f"[Restart] Error: {e}")

def shutdown_pc():
    """Shutdown PC with warning."""
    speak("Shutting down computer in 10 seconds. Save your work.")
    for i in range(9, 0, -1):
        time.sleep(1)
        print(f"[Shutdown] {i} seconds...")
    try:
        subprocess.Popen(["shutdown.exe", "/s", "/t", "0"])
    except Exception as e:
        print(f"[Shutdown] Error: {e}")

def abort_shutdown():
    """Cancel pending shutdown/restart."""
    try:
        subprocess.run(["shutdown.exe", "/a"], capture_output=True, timeout=5)
        speak("Shutdown cancelled")
    except Exception as e:
        print(f"[AbortShutdown] Error: {e}")
        speak("No pending shutdown found")

def open_device_manager():
    try:
        subprocess.Popen(["devmgmt.msc"])
        speak("Device manager opened")
    except Exception as e:
        print(f"[DeviceMgr] Error: {e}")
        speak("Could not open device manager")

def open_disk_cleanup():
    try:
        subprocess.Popen(["cleanmgr.exe"])
        speak("Disk cleanup opened")
    except Exception as e:
        print(f"[DiskClean] Error: {e}")

def open_disk_defragment():
    try:
        subprocess.Popen(["dfrgui.exe"])
        speak("Disk defragmenter opened")
    except Exception as e:
        print(f"[Defrag] Error: {e}")

def open_event_viewer():
    try:
        subprocess.Popen(["eventvwr.msc"])
        speak("Event viewer opened")
    except Exception as e:
        print(f"[EventVwr] Error: {e}")

def open_registry_editor():
    try:
        speak("Warning: editing registry can break your system")
        subprocess.Popen(["regedit.exe"])
        speak("Registry editor opened")
    except Exception as e:
        print(f"[RegEdit] Error: {e}")

def open_services():
    try:
        subprocess.Popen(["services.msc"])
        speak("Services opened")
    except Exception as e:
        print(f"[Services] Error: {e}")

def open_system_properties():
    try:
        subprocess.Popen(["sysdm.cpl"])
        speak("System properties opened")
    except Exception as e:
        print(f"[SysProp] Error: {e}")

def open_control_panel_item(item):
    """Open a specific control panel applet."""
    cpl_map = {
        "display": "desk.cpl",
        "sound": "mmsys.cpl",
        "mouse": "main.cpl",
        "keyboard": "main.cpl",
        "printers": "printers.cpl",
        "network": "ncpa.cpl",
        "power": "powercfg.cpl",
        "date": "timedate.cpl",
        "time": "timedate.cpl",
        "user": "nusrmgr.cpl",
        "firewall": "firewall.cpl",
    }
    cpl = cpl_map.get(item.lower())
    if cpl:
        try:
            subprocess.Popen(["control.exe", cpl])
            speak(f"Opening {item} settings")
            return
        except Exception:
            pass
    try:
        subprocess.Popen(["control.exe"])
        speak("Control panel opened")
    except Exception:
        pass

def open_sticky_notes():
    try:
        subprocess.Popen(["explorer.exe", r"shell:AppsFolder\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe!App"], shell=False)
        speak("Sticky notes opened")
    except Exception:
        try:
            os.system('start ms-sticky-notes:')
        except Exception as e:
            print(f"[StickyNotes] Error: {e}")

def open_steps_recorder():
    try:
        subprocess.Popen(["psr.exe"])
        speak("Steps recorder opened")
    except Exception as e:
        print(f"[PSR] Error: {e}")

def open_character_map():
    try:
        subprocess.Popen(["charmap.exe"])
        speak("Character map opened")
    except Exception as e:
        print(f"[CharMap] Error: {e}")

def open_narrator():
    try:
        subprocess.Popen(["narrator.exe"])
        speak("Narrator started")
    except Exception as e:
        print(f"[Narrator] Error: {e}")

def open_wordpad():
    try:
        subprocess.Popen(["write.exe"])
        speak("WordPad opened")
    except Exception as e:
        print(f"[WordPad] Error: {e}")

def open_task_scheduler():
    try:
        subprocess.Popen(["taskschd.msc"])
        speak("Task scheduler opened")
    except Exception as e:
        print(f"[TaskSched] Error: {e}")

def open_computer_management():
    try:
        subprocess.Popen(["compmgmt.msc"])
        speak("Computer management opened")
    except Exception as e:
        print(f"[CompMgmt] Error: {e}")

def open_local_group_policy():
    try:
        subprocess.Popen(["gpedit.msc"])
        speak("Local group policy editor opened")
    except Exception as e:
        print(f"[GPEdit] Error: {e}")

def open_character_map_alt():
    try:
        subprocess.Popen(["charmap.exe"])
        speak("Character map opened")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
#  MORE SEARCH ENGINES + OPEN UTILITIES
# ═══════════════════════════════════════════════════════════════

def search_bing(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://www.bing.com/search?q={quote(query)}")
    speak(f"Searching Bing for {query}")

def search_duckduckgo(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://duckduckgo.com/?q={quote(query)}")
    speak(f"Searching DuckDuckGo for {query}")

def search_wikipedia(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://en.wikipedia.org/wiki/Special:Search?search={quote(query)}")
    speak(f"Searching Wikipedia for {query}")

def search_stackoverflow(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://stackoverflow.com/search?q={quote(query)}")
    speak(f"Searching Stack Overflow for {query}")

def search_quora(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://www.quora.com/search?q={quote(query)}")
    speak(f"Searching Quora for {query}")

def search_github(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://github.com/search?q={quote(query)}")
    speak(f"Searching GitHub for {query}")

def search_amazon(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://www.amazon.in/s?k={quote(query)}")
    speak(f"Searching Amazon for {query}")

def search_flipkart(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://www.flipkart.com/search?q={quote(query)}")
    speak(f"Searching Flipkart for {query}")

def search_google_maps(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://www.google.com/maps/search/{quote(query)}")
    speak(f"Searching Maps for {query}")

def search_google_scholar(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://scholar.google.com/scholar?q={quote(query)}")
    speak(f"Searching Google Scholar for {query}")

def search_gmail(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://mail.google.com/mail/u/0/#search/{quote(query)}")
    speak(f"Searching Gmail for {query}")

def search_chatgpt(query):
    from urllib.parse import quote
    import webbrowser
    webbrowser.open(f"https://chatgpt.com/?q={quote(query)}")
    speak(f"Opening ChatGPT with query: {query}")

def translate_text(text, source="auto", target="hi"):
    """Translate text via Google Translate in browser."""
    from urllib.parse import quote
    import webbrowser
    url = f"https://translate.google.com/?sl={source}&tl={target}&text={quote(text)}&op=translate"
    webbrowser.open(url)
    speak(f"Translating: {text[:50]}")


# ═══════════════════════════════════════════════════════════════
#  MATH / CALCULATOR (basic eval)
# ═══════════════════════════════════════════════════════════════

def _safe_calc(expr):
    """Very limited safe math evaluator."""
    import ast
    import operator
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
           ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos}
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")
    return _eval(ast.parse(expr, mode='eval'))

def calculate_expression(expr):
    try:
        result = _safe_calc(expr)
        speak(f"The result is {result}")
        return result
    except Exception as e:
        print(f"[Calc] Error: {e}")
        # Fallback: open calculator app
        try:
            subprocess.Popen(["calc.exe"])
            speak("Opening calculator")
        except Exception:
            pass
        return None


# ═══════════════════════════════════════════════════════════════
#  WIFI / NETWORK (info only, no toggles without admin)
# ═══════════════════════════════════════════════════════════════

def show_wifi_passwords():
    """List saved WiFi names (Windows only). Passwords need admin."""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True, text=True, timeout=10
        )
        names = []
        for line in result.stdout.split("\n"):
            if "All User Profile" in line:
                name = line.split(":", 1)[1].strip()
                if name:
                    names.append(name)
        if names:
            speak(f"Found {len(names)} saved Wi-Fi networks")
            for i, n in enumerate(names[:10], 1):
                print(f"  {i}. {n}")
            return names
        else:
            speak("No saved Wi-Fi found")
            return []
    except Exception as e:
        print(f"[WiFi] Error: {e}")
        return []

def show_ip_address():
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        # Get public IP if possible
        pub_ip = ""
        try:
            import urllib.request
            pub_ip = urllib.request.urlopen("https://api.ipify.org", timeout=3).read().decode()
        except Exception:
            pass
        msg = f"Local IP: {local_ip}"
        if pub_ip:
            msg += f", Public IP: {pub_ip}"
        speak(msg)
        print(f"[IP] {msg}")
        return local_ip, pub_ip
    except Exception as e:
        print(f"[IP] Error: {e}")
        speak("Could not get IP address")
        return None, None


# ═══════════════════════════════════════════════════════════════
#  BATTERY / POWER INFO
# ═══════════════════════════════════════════════════════════════

def show_battery_status():
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery is None:
            speak("No battery detected - this is a desktop PC")
            return None
        pct = battery.percent
        plugged = battery.power_plugged
        if plugged:
            msg = f"Battery at {pct} percent, charger connected"
        else:
            mins_left = battery.secsleft // 60 if battery.secsleft != -1 else 0
            hrs, mins = divmod(mins_left, 60) if mins_left > 0 else (0, 0)
            if hrs > 0:
                msg = f"Battery at {pct} percent, approximately {hrs} hour {mins} minutes remaining"
            else:
                msg = f"Battery at {pct} percent, approximately {mins} minutes remaining"
        speak(msg)
        print(f"[Battery] {msg}")
        return battery
    except Exception as e:
        print(f"[Battery] Error: {e}")
        speak("Could not read battery status")
        return None

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
        os.startfile("ms-settings:")
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
