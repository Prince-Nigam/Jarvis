"""
start_jarvis.pyw
Run as .pyw so NO console window opens on startup.
Placed in Windows Startup folder to auto-launch Jarvis.
"""
import subprocess
import sys
import os

# Path to this project
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON      = sys.executable   # same python that's running this

subprocess.Popen(
    [PYTHON, "run.py"],
    cwd=PROJECT_DIR,
    creationflags=0x00000008,   # DETACH_PROCESS — no console window
)
