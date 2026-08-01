"""
install_startup.py
Run this ONCE to add Jarvis to Windows startup.
Creates a shortcut in the Startup folder.
"""
import os
import sys
import subprocess

def install():
    # Windows Startup folder path
    startup_folder = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    project_dir = os.path.dirname(os.path.abspath(__file__))
    pyw_path    = os.path.join(project_dir, "start_jarvis.pyw")
    python_exe  = sys.executable
    shortcut_path = os.path.join(startup_folder, "Jarvis.lnk")

    if not os.path.exists(startup_folder):
        print(f"[ERROR] Startup folder not found: {startup_folder}")
        return False

    # Use PowerShell to create a proper .lnk shortcut
    ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath   = "{python_exe}"
$Shortcut.Arguments    = '"{pyw_path}"'
$Shortcut.WorkingDirectory = "{project_dir}"
$Shortcut.WindowStyle  = 7
$Shortcut.Description  = "Jarvis AI Assistant"
$Shortcut.Save()
"""

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"[SUCCESS] Jarvis added to Windows Startup!")
            print(f"  Shortcut: {shortcut_path}")
            print(f"  Jarvis will auto-start on every login.")
            return True
        else:
            print(f"[ERROR] PowerShell failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def uninstall():
    startup_folder = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut_path = os.path.join(startup_folder, "Jarvis.lnk")
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        print("[SUCCESS] Jarvis removed from Windows Startup.")
    else:
        print("[INFO] Jarvis shortcut not found in Startup folder.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        install()
        print("\nPress Enter to close...")
        input()
