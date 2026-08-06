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

# ── Command API ────────────────────────────────────────────────────────────────
@app.route("/api/command", methods=["POST"])
def api_command():
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"ok": False, "error": "empty query", "response": ""})
    try:
        from engine.command import run_command
        response = run_command(query)
        return jsonify({"ok": True, "response": response or ""})
    except Exception as e:
        print(f"[command] {e}")
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

    threading.Thread(target=_do_listen, daemon=True).start()
    try:
        text = result_q.get(timeout=12)
    except queue.Empty:
        text = ""
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
    print(f"  Say 'Hey Jarvis' / 'Wakeup Jarvis' anytime")
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
        print("[Jarvis] Hotword listener active")
    except Exception as e:
        print(f"[Jarvis] Hotword failed: {e}")

    # Open browser
    threading.Timer(1.5, _open_browser, args=[port]).start()

    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    start()
