"""
window_manager.py — Dedicated Win32 Window Manager for Jarvis
Opens Jarvis in Microsoft Edge as a guaranteed visible desktop window.
"""
import ctypes
import os
import subprocess
import time

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

_jarvis_port = 8000


def set_port(port):
    global _jarvis_port
    _jarvis_port = port


def _force_window_to_front():
    """Scan all windows, restore & bring Jarvis to front using Win32."""
    if os.name != 'nt':
        return
    try:
        user32 = ctypes.windll.user32
        port_str_1 = f"127.0.0.1:{_jarvis_port}"
        port_str_2 = f"localhost:{_jarvis_port}"

        def enum_callback(hwnd, extra):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                if "jarvis" in title or port_str_1 in title or port_str_2 in title:
                    user32.ShowWindow(hwnd, 9)   # SW_RESTORE
                    user32.ShowWindow(hwnd, 5)   # SW_SHOW
                    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
                    user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002)
                    fg = user32.GetForegroundWindow()
                    fg_tid = user32.GetWindowThreadProcessId(fg, None)
                    tgt_tid = user32.GetWindowThreadProcessId(hwnd, None)
                    if fg_tid != tgt_tid:
                        user32.AttachThreadInput(fg_tid, tgt_tid, True)
                        user32.BringWindowToTop(hwnd)
                        user32.SetForegroundWindow(hwnd)
                        user32.AttachThreadInput(fg_tid, tgt_tid, False)
                    else:
                        user32.BringWindowToTop(hwnd)
                        user32.SetForegroundWindow(hwnd)
                    return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    except Exception as e:
        print(f"[Window Manager] Win32 error: {e}")


def show_jarvis_window(url="http://127.0.0.1:8000/index.html"):
    """
    Launch Jarvis in Microsoft Edge and force it to the front of the screen.
    Uses CREATE_NEW_CONSOLE + SW_SHOWNORMAL so it's always visible.
    """
    try:
        if os.path.exists(EDGE_PATH):
            # Launch Edge with explicit window creation flags
            subprocess.Popen(
                [EDGE_PATH, "--new-window", url],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )
        else:
            # Fallback: Windows shell open
            os.startfile(url)

        # Wait for the window to appear
        time.sleep(1.5)

        # Try Win32 focus
        _force_window_to_front()

        print(f"[Window Manager] Jarvis launched at {url}")
    except Exception as e:
        print(f"[Window Manager] Launch error: {e}")
        # Last resort fallback
        try:
            os.system(f'start "" "{url}"')
        except Exception:
            pass
