"""
Jarvis main entry point.
Uses Flask to serve the frontend and expose Python functions via JSON API.
(Replaces eel/gevent which requires native DLLs blocked by Windows policy)
"""
import json
import os
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

# ── App setup ─────────────────────────────────────────────────────────────────
WWW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
app = Flask(__name__, static_folder=WWW_DIR)
CORS(app)

# ── Serve frontend ────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/index.html")
def index():
    return send_from_directory(WWW_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(WWW_DIR, filename)

# ── System stats API ──────────────────────────────────────────────────────────
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

# ── Voice / command API ───────────────────────────────────────────────────────
@app.route("/api/speak", methods=["POST"])
def api_speak():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if text:
        threading.Thread(target=_speak_bg, args=(text,), daemon=True).start()
    return jsonify({"ok": True})

def _speak_bg(text):
    try:
        from engine.command import speak
        speak(text)
    except Exception as e:
        print(f"[speak] {e}")

@app.route("/api/command", methods=["POST"])
def api_command():
    data   = request.get_json(silent=True) or {}
    query  = data.get("query", "").strip()
    if not query:
        return jsonify({"ok": False, "error": "empty query"})
    threading.Thread(target=_run_command, args=(query,), daemon=True).start()
    return jsonify({"ok": True})

def _run_command(query):
    try:
        from engine.features import (
            chatBot, findContact, makeCall, openCommand,
            PlayYoutube, sendMessage, whatsApp,
        )
        from engine.command import speak, takecommand

        if "open" in query:
            openCommand(query)
        elif "on youtube" in query:
            PlayYoutube(query)
        elif any(k in query for k in ("send message", "phone call", "video call")):
            contact_no, name = findContact(query)
            if contact_no:
                chatBot(query)   # simplified — full flow needs mic
        else:
            chatBot(query)
    except Exception as e:
        print(f"[command] {e}")

@app.route("/api/listen", methods=["POST"])
def api_listen():
    """Trigger microphone listen and return recognised text."""
    def _listen():
        try:
            from engine.command import takecommand
            return takecommand()
        except Exception:
            return ""
    text = _listen()
    return jsonify({"text": text})

# ── Auth API ──────────────────────────────────────────────────────────────────
@app.route("/api/auth", methods=["POST"])
def api_auth():
    result = Recognize.AuthenticateFace()
    return jsonify({"authenticated": result == 1})

# ── Utilities ─────────────────────────────────────────────────────────────────
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
    url = f"http://localhost:{port}/index.html"
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[browser] {e}")

def _run_device_setup():
    if os.name != "nt" or not os.path.exists("device.bat"):
        return
    try:
        subprocess.call(["cmd", "/c", "device.bat"], shell=False)
    except Exception as e:
        print(f"[device] {e}")

# ── Entry ─────────────────────────────────────────────────────────────────────
def start():
    init_database()
    _run_device_setup()

    port = _find_free_port()
    print(f"Starting Jarvis at http://127.0.0.1:{port}/index.html")

    # Open browser after short delay (let Flask start first)
    threading.Timer(1.2, _open_browser, args=[port]).start()

    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    start()
