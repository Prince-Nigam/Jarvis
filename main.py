"""
Jarvis — Flask REST API backend
"""
import os
import queue
import socket
import subprocess
import threading
import webbrowser
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS

from engine.authenticator import Recognize
from engine.init_db import init_database
import engine.system_info as sysinfo

# ── Event Log (Activity Log → frontend polling) ────────────────────────────────
import collections
_event_log   = collections.deque(maxlen=200)   # circular buffer, newest last
_event_seq   = 0                                # ever-increasing sequence id
_event_lock  = threading.Lock()

def push_event(message: str, level: str = "info"):
    """
    Push one log entry. level: info | success | warn | cmd | dim
    Called from anywhere — hotword.py, command.py, etc.
    """
    global _event_seq
    with _event_lock:
        _event_seq += 1
        _event_log.append({"id": _event_seq, "msg": message, "level": level})

# ── App setup ──────────────────────────────────────────────────────────────────
WWW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
app = Flask(__name__, static_folder=WWW_DIR)
CORS(app)

# ── No-cache helper ────────────────────────────────────────────────────────────
def _no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"]        = "no-cache"
    response.headers["Expires"]       = "0"
    return response

# ── Frontend ───────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/index.html")
def index():
    return _no_cache(make_response(send_from_directory(WWW_DIR, "index.html")))

@app.route("/<path:filename>")
def static_files(filename):
    resp = make_response(send_from_directory(WWW_DIR, filename))
    if filename.endswith(('.js', '.css')):
        return _no_cache(resp)
    return resp

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

# ── Greet API ──────────────────────────────────────────────────────────────────
@app.route("/api/greet", methods=["POST"])
def api_greet():
    hour = datetime.now().hour
    if hour < 12:
        greet = "Good morning Sir. Jarvis at your service."
    elif hour < 17:
        greet = "Good afternoon Sir. Jarvis at your service."
    else:
        greet = "Good evening Sir. Jarvis at your service."
    try:
        from engine.command import speak
        speak(greet)
    except Exception as e:
        print(f"[greet] {e}")
    return jsonify({"ok": True, "message": greet})

# ── Events API (Activity Log polling) ─────────────────────────────────────────
@app.route("/api/events")
def api_events():
    """
    Frontend polls this. Returns all events with id > after_id.
    Response: { events: [{id, msg, level}] }
    """
    try:
        after = int(request.args.get("after", 0))
    except (ValueError, TypeError):
        after = 0
    with _event_lock:
        result = [e for e in _event_log if e["id"] > after]
    return jsonify({"events": result})

# ── Command API ────────────────────────────────────────────────────────────────
@app.route("/api/command", methods=["POST"])
def api_command():
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"ok": False, "error": "empty query", "response": ""})
    push_event(f"USER ▶ {query}", "cmd")
    try:
        from engine.command import run_command
        response = run_command(query)
        if response:
            push_event(f"JARVIS ◀ {response}", "success")
        return jsonify({"ok": True, "response": response or ""})
    except Exception as e:
        print(f"[command] {e}")
        push_event(f"ERROR: {e}", "warn")
        return jsonify({"ok": False, "error": str(e), "response": "Something went wrong."})

# ── Listen API ─────────────────────────────────────────────────────────────────
@app.route("/api/listen", methods=["POST"])
def api_listen():
    result_q = queue.Queue()

    def _do_listen():
        try:
            from engine.command import takecommand
            result_q.put(takecommand() or "")
        except Exception as e:
            print(f"[listen] {e}")
            result_q.put("")

    push_event("Mic activated — listening...", "info")
    threading.Thread(target=_do_listen, daemon=True).start()
    try:
        text = result_q.get(timeout=12)
    except queue.Empty:
        text = ""
    if text:
        push_event(f"Heard: {text}", "cmd")
    else:
        push_event("No speech detected", "warn")
    return jsonify({"text": text})

# ── Activate API (force wake from browser mic button) ─────────────────────────
@app.route("/api/activate", methods=["POST"])
def api_activate():
    try:
        from engine.hotword import force_activate, is_active
        if not is_active():
            force_activate()
        return jsonify({"ok": True, "active": True})
    except Exception as e:
        print(f"[activate] {e}")
        return jsonify({"ok": False, "error": str(e)})

# ── Status API ─────────────────────────────────────────────────────────────────
@app.route("/api/status")
def api_status():
    try:
        from engine.hotword import is_active
        return jsonify({"active": is_active(), "ok": True})
    except Exception:
        return jsonify({"active": False, "ok": True})

# ── Auth API ───────────────────────────────────────────────────────────────────
@app.route("/api/auth", methods=["POST"])
def api_auth():
    try:
        result = Recognize.AuthenticateFace()
        return jsonify({"authenticated": result == 1})
    except Exception as e:
        print(f"[auth] {e}")
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
    url = f"http://localhost:{port}/index.html"
    try:
        from engine.window_manager import show_jarvis_window
        show_jarvis_window(url)
    except Exception:
        webbrowser.open(url)

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
    print(f"  J.A.R.V.I.S  http://127.0.0.1:{port}")
    print(f"  Listen kar raha hoon — sirf boliye 'Wakeup Jarvish'")
    print(f"{'='*50}\n")

    # Window manager port
    try:
        from engine.window_manager import set_port as set_window_port
        set_window_port(port)
    except Exception:
        pass

    # Hotword listener
    try:
        from engine.hotword import start as start_hotword, set_port
        set_port(port)
        start_hotword()
        push_event("Background listener active", "success")
        push_event("Say 'Wakeup Jarvish' to activate", "dim")
        print("[Jarvis] Background listener active — tab 'Wakeup Jarvish' boliye tabhi online hoga")
    except Exception as e:
        print(f"[Jarvis] Hotword failed: {e}")
        push_event(f"Hotword init failed: {e}", "warn")

    # NOTE: Startup mein auto browser NAHI kholenge.
    # Sirf user jab "wakeup jarvish" bolega tabhi window + TTS trigger hoga
    # (user ka requirement: bina kuch kare sirf bol ke activate)

    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    start()
