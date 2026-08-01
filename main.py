"""
Jarvis main entry point — Flask REST API backend.
Fixes applied:
  - /api/listen uses a dedicated thread with a queue so it doesn't
    block Flask's request thread beyond a timeout
  - /api/speak removed (speak() is called inside run_command directly)
  - Unused json import removed
"""
import os
import queue
import socket
import subprocess
import sys
import threading
import webbrowser

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from engine.auth import Recognize
from engine.init_db import init_database
import engine.system_info as sysinfo

# ── App setup ──────────────────────────────────────────────────────────────────
WWW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
app = Flask(__name__, static_folder=WWW_DIR)
CORS(app)

# ── Frontend ───────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/index.html")
def index():
    return send_from_directory(WWW_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(WWW_DIR, filename)

# ── System stats ───────────────────────────────────────────────────────────────
@app.route("/api/system_stats")
def api_system_stats():
    return jsonify(sysinfo.getSystemStats())

@app.route("/api/drives")
def api_drives():
    return jsonify(sysinfo.getDrives())

@app.route("/api/list_directory")
def api_list_directory():
    path = request.args.get("path", "C:\\")
    return jsonify(sysinfo.listDirectory(path))

@app.route("/api/open_file", methods=["POST"])
def api_open_file():
    data = request.get_json(silent=True) or {}
    return jsonify(sysinfo.openFile(data.get("path", "")))

@app.route("/api/open_explorer", methods=["POST"])
def api_open_explorer():
    data = request.get_json(silent=True) or {}
    return jsonify(sysinfo.openInExplorer(data.get("path", "")))

# ── Command API ────────────────────────────────────────────────────────────────
@app.route("/api/command", methods=["POST"])
def api_command():
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"ok": False, "error": "empty query"})
    try:
        from engine.command import run_command
        response = run_command(query)
        return jsonify({"ok": True, "response": response or ""})
    except Exception as e:
        print(f"[command error] {e}")
        return jsonify({"ok": False, "error": str(e), "response": "Something went wrong."})

# ── Greet API ──────────────────────────────────────────────────────────────────
@app.route("/api/greet", methods=["POST"])
def api_greet():
    try:
        from engine.features import playAssistantSound
        from engine.command import speak
        from datetime import datetime

        playAssistantSound()

        hour = datetime.now().hour
        if hour < 12:
            greet = "Good morning Sir. Jarvis at your service. All systems operational."
        elif hour < 17:
            greet = "Good afternoon Sir. Jarvis at your service. All systems operational."
        else:
            greet = "Good evening Sir. Jarvis at your service. All systems operational."

        speak(greet)
        return jsonify({"ok": True, "message": greet})
    except Exception as e:
        print(f"[greet error] {e}")
        return jsonify({"ok": False, "error": str(e)})

# ── Listen API — runs mic in thread, returns within timeout ────────────────────
@app.route("/api/listen", methods=["POST"])
def api_listen():
    """
    Starts mic listening in a background thread and waits up to 12 seconds
    for a result. Returns immediately with whatever was heard (or empty string).
    This keeps Flask's request thread from being tied up indefinitely.
    """
    result_q = queue.Queue()

    def _do_listen():
        try:
            from engine.command import takecommand
            text = takecommand()
            result_q.put(text or "")
        except Exception as e:
            print(f"[listen error] {e}")
            result_q.put("")

    t = threading.Thread(target=_do_listen, daemon=True)
    t.start()

    try:
        text = result_q.get(timeout=12)   # max 12s wait
    except queue.Empty:
        text = ""

    return jsonify({"text": text})

# ── Auth API ───────────────────────────────────────────────────────────────────
@app.route("/api/auth", methods=["POST"])
def api_auth():
    try:
        result = Recognize.AuthenticateFace()
        return jsonify({"authenticated": result == 1})
    except Exception as e:
        print(f"[auth error] {e}")
        return jsonify({"authenticated": False})

# ── Utilities ──────────────────────────────────────────────────────────────────
def _find_free_port(start=8000):
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                port += 1

def _open_browser(port):
    try:
        from engine.window_manager import show_jarvis_window
        show_jarvis_window(f"http://localhost:{port}/index.html")
    except Exception as e:
        print(f"[browser] {e}")

def _run_device_setup():
    if os.name != "nt" or not os.path.exists("device.bat"):
        return
    try:
        subprocess.call(["cmd", "/c", "device.bat"], shell=False)
    except Exception as e:
        print(f"[device] {e}")

# ── Entry ──────────────────────────────────────────────────────────────────────
def start():
    init_database()
    _run_device_setup()

    port = _find_free_port()
    print(f"\n{'='*50}")
    print(f"  J.A.R.V.I.S  starting at http://127.0.0.1:{port}")
    print(f"  Say 'Hey Jarvis' to activate anytime")
    print(f"{'='*50}\n")

    # Start hotword listener before Flask blocks
    try:
        from engine.hotword import start as start_hotword, set_port
        set_port(port)
        start_hotword()
        print("[Jarvis] Hotword listener active")
    except Exception as e:
        print(f"[Jarvis] Hotword listener failed: {e}")

    # Open browser after Flask has a chance to bind
    threading.Timer(1.5, _open_browser, args=[port]).start()

    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    start()
