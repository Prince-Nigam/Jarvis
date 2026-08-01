"""
System information and file browser — pure Python, no eel dependency.
Called directly from main.py Flask routes.
"""
import os
import string
import subprocess

try:
    import psutil
except ModuleNotFoundError:
    psutil = None


def _bytes_to_gb(b):
    return round(b / (1024 ** 3), 1)


def _format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024**2):.1f} MB"
    else:
        return f"{size_bytes / (1024**3):.2f} GB"


# ── System Stats ──────────────────────────────────────────────────────────────

def getSystemStats():
    """Return CPU, RAM, disk and temperature info as a dict."""
    if psutil is None:
        return {
            "cpu": 0, "ram_used": 0, "ram_total": 0, "ram_percent": 0,
            "disk_used": 0, "disk_total": 0, "disk_percent": 0,
            "cpu_temp": None, "battery": None, "battery_charging": False
        }

    cpu = psutil.cpu_percent(interval=0.3)

    ram = psutil.virtual_memory()
    ram_used  = _bytes_to_gb(ram.used)
    ram_total = _bytes_to_gb(ram.total)
    ram_pct   = ram.percent

    try:
        disk = psutil.disk_usage("C:\\")
        disk_used  = _bytes_to_gb(disk.used)
        disk_total = _bytes_to_gb(disk.total)
        disk_pct   = disk.percent
    except Exception:
        disk_used = disk_total = disk_pct = 0

    # Temperature
    cpu_temp = None
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for key in ("coretemp", "cpu_thermal", "k10temp", "acpitz"):
                if key in temps:
                    cpu_temp = round(temps[key][0].current, 1)
                    break
    except Exception:
        pass

    # Battery
    battery  = None
    charging = False
    try:
        bat = psutil.sensors_battery()
        if bat:
            battery  = round(bat.percent)
            charging = bat.power_plugged
    except Exception:
        pass

    return {
        "cpu":            cpu,
        "ram_used":       ram_used,
        "ram_total":      ram_total,
        "ram_percent":    ram_pct,
        "disk_used":      disk_used,
        "disk_total":     disk_total,
        "disk_percent":   disk_pct,
        "cpu_temp":       cpu_temp,
        "battery":        battery,
        "battery_charging": charging,
    }


# ── File Browser ──────────────────────────────────────────────────────────────

def getDrives():
    """Return list of available drives on Windows."""
    drives = []
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            try:
                usage = psutil.disk_usage(path) if psutil else None
                drives.append({
                    "name":  path,
                    "label": letter + ":",
                    "free":  _bytes_to_gb(usage.free)  if usage else "?",
                    "total": _bytes_to_gb(usage.total) if usage else "?",
                })
            except Exception:
                drives.append({"name": path, "label": letter + ":", "free": "?", "total": "?"})
    return drives


def listDirectory(path):
    """
    List contents of a directory.
    Returns {"dirs": [...], "files": [...], "current": path, "parent": parent}
    """
    try:
        path = os.path.normpath(path)
        dirs  = []
        files = []

        with os.scandir(path) as entries:
            for e in sorted(entries, key=lambda x: (not x.is_dir(), x.name.lower())):
                try:
                    if e.is_dir(follow_symlinks=False):
                        dirs.append({"name": e.name, "path": e.path})
                    else:
                        size = e.stat().st_size
                        ext  = os.path.splitext(e.name)[1].lower()
                        files.append({
                            "name": e.name,
                            "path": e.path,
                            "size": _format_size(size),
                            "ext":  ext,
                        })
                except PermissionError:
                    pass

        parent = str(os.path.dirname(path))
        if parent == path:   # root drive
            parent = None

        return {"dirs": dirs, "files": files, "current": path, "parent": parent, "error": None}
    except PermissionError:
        return {"dirs": [], "files": [], "current": path, "parent": None, "error": "Access denied"}
    except Exception as exc:
        return {"dirs": [], "files": [], "current": path, "parent": None, "error": str(exc)}


def openFile(path):
    """Open a file with its default application."""
    try:
        os.startfile(path)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def openInExplorer(path):
    """Open a folder in Windows Explorer."""
    try:
        subprocess.Popen(f'explorer "{path}"')
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
