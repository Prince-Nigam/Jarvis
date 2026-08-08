import os
import sqlite3
import subprocess
import time
import webbrowser
from urllib.parse import quote

try:
    from playsound import playsound
except ModuleNotFoundError:
    playsound = None

try:
    import eel
except ModuleNotFoundError:
    eel = None

try:
    import pyaudio
except ModuleNotFoundError:
    pyaudio = None

try:
    import pywhatkit as kit
except ModuleNotFoundError:
    kit = None

try:
    import pyautogui
except ModuleNotFoundError:
    pyautogui = None

try:
    from hugchat import hugchat
except ModuleNotFoundError:
    hugchat = None

from engine.command import speak
from engine.config import ASSISTANT_NAME, PORCUPINE_ACCESS_KEY
from engine.helper import extract_yt_term, remove_words
from engine.init_db import DB_PATH, init_database

init_database()


def _get_cursor():
    """Return a fresh connection and cursor. Caller must close the connection."""
    con = sqlite3.connect(DB_PATH)
    return con, con.cursor()

START_SOUND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "www", "assets", "audio", "start_sound.mp3")


def playAssistantSound():
    if playsound is None:
        print("playsound is not installed; skipping assistant sound")
        return
    if not os.path.exists(START_SOUND):
        print("Startup sound file not found; skipping")
        return
    try:
        playsound(START_SOUND)
    except Exception as exc:
        print(f"Startup sound skipped: {exc}")


try:
    if eel is not None:
        eel.expose(playAssistantSound)
except Exception:
    pass


EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def _open_in_browser(url):
    if os.path.exists(EDGE_PATH):
        subprocess.Popen([EDGE_PATH, url])
    else:
        webbrowser.open(url)


# ── Known Windows desktop app paths ───────────────────────────────────────────
# Maps voice command name → possible install paths (first found is used)
_DESKTOP_APPS = {
    "whatsapp": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"WhatsApp\WhatsApp.exe"),
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\WhatsApp.lnk"),
        "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    ],
    "telegram": [
        os.path.join(os.environ.get("APPDATA", ""), r"Telegram Desktop\Telegram.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Telegram Desktop\Telegram.exe"),
    ],
    "spotify": [
        os.path.join(os.environ.get("APPDATA", ""), r"Spotify\Spotify.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\WindowsApps\Spotify.exe"),
    ],
    "discord": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Discord\Update.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Discord\app-*\Discord.exe"),
    ],
    "vscode": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "visual studio code": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "notepad": [r"C:\Windows\notepad.exe"],
    "notepad++": [
        r"C:\Program Files\Notepad++\notepad++.exe",
        r"C:\Program Files (x86)\Notepad++\notepad++.exe",
    ],
    "calculator": [r"C:\Windows\System32\calc.exe"],
    "calc": [r"C:\Windows\System32\calc.exe"],
    "paint": [r"C:\Windows\System32\mspaint.exe"],
    "ms paint": [r"C:\Windows\System32\mspaint.exe"],
    "word": [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
    ],
    "ms word": [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
    ],
    "excel": [
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
    ],
    "ms excel": [
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
    ],
    "powerpoint": [
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
    ],
    "ms powerpoint": [
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
    ],
    "outlook": [
        r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE",
    ],
    "onenote": [
        r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\ONENOTE.EXE",
    ],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "google chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "mozilla firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "microsoft edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "brave": [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"BraveSoftware\Brave-Browser\Application\brave.exe"),
    ],
    "opera": [
        r"C:\Program Files\Opera\launcher.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Opera\launcher.exe"),
    ],
    "vlc": [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ],
    "vlc media player": [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ],
    "windows media player": [r"C:\Program Files\Windows Media Player\wmplayer.exe"],
    "file explorer": [r"C:\Windows\explorer.exe"],
    "explorer": [r"C:\Windows\explorer.exe"],
    "this pc": [r"C:\Windows\explorer.exe"],
    "my computer": [r"C:\Windows\explorer.exe"],
    "task manager": [r"C:\Windows\System32\Taskmgr.exe"],
    "control panel": [r"C:\Windows\System32\control.exe"],
    "settings": ["ms-settings:"],
    "camera": ["microsoft.windows.camera:"],
    "photos": ["ms-photos:"],
    "store": ["ms-windows-store:"],
    "microsoft store": ["ms-windows-store:"],
    "windows store": ["ms-windows-store:"],
    "command prompt": [r"C:\Windows\System32\cmd.exe"],
    "cmd": [r"C:\Windows\System32\cmd.exe"],
    "powershell": [r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"],
    "terminal": ["wt.exe"],
    "windows terminal": ["wt.exe"],
    "sticky notes": ["ms-sticky-notes:"],
    "alarm": ["ms-clock:"],
    "alarms": ["ms-clock:"],
    "clock": ["ms-clock:"],
    "timer": ["ms-clock:"],
    "calculator app": ["calculator:"],
    "calendar": ["outlookcal:"],
    "mail": ["outlookmail:"],
    "maps app": ["bingmaps:"],
    "weather": ["msnweather:"],
    "news": ["msnweather:"],
    "snip and sketch": ["ms-screenclip:"],
    "snipping tool": ["ms-screenclip:"],
    "sublime text": [
        r"C:\Program Files\Sublime Text\sublime_text.exe",
        r"C:\Program Files\Sublime Text 3\sublime_text.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Sublime Text\sublime_text.exe"),
    ],
    "atom": [
        r"C:\Program Files\Atom\atom.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"atom\atom.exe"),
    ],
    "pycharm": [
        r"C:\Program Files\JetBrains\PyCharm Community Edition 2023.1\bin\pycharm64.exe",
        r"C:\Program Files\JetBrains\PyCharm 2023.1\bin\pycharm64.exe",
    ],
    "intellij": [
        r"C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2023.1\bin\idea64.exe",
    ],
    "android studio": [
        r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
    ],
    "eclipse": [
        r"C:\Users\Public\eclipse\java-2023-06\eclipse\eclipse.exe",
        r"C:\Program Files\eclipse\eclipse.exe",
    ],
    "postman": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Postman\Postman.exe"),
        r"C:\Program Files\Postman\Postman.exe",
    ],
    "docker desktop": [
        r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
    ],
    "teamviewer": [
        r"C:\Program Files\TeamViewer\TeamViewer.exe",
        r"C:\Program Files (x86)\TeamViewer\TeamViewer.exe",
    ],
    "anydesk": [
        r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe",
        r"C:\Program Files\AnyDesk\AnyDesk.exe",
    ],
    "zoom": [
        os.path.join(os.environ.get("APPDATA", ""), r"Zoom\bin\Zoom.exe"),
        r"C:\Program Files\Zoom\bin\Zoom.exe",
    ],
    "slack": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"slack\slack.exe"),
        r"C:\Program Files\Slack\slack.exe",
    ],
    "skype": [
        r"C:\Program Files (x86)\Microsoft\Skype for Desktop\Skype.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Skype for Desktop\Skype.exe"),
    ],
    "teams": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Teams\Update.exe"),
        r"C:\Program Files (x86)\Microsoft\Teams\Update.exe",
    ],
    "microsoft teams": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Teams\Update.exe"),
    ],
    "webex": [
        r"C:\Program Files (x86)\Webex\Webex\Applications\ptoneclk.exe",
    ],
    "photoshop": [
        r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
        r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",
    ],
    "illustrator": [
        r"C:\Program Files\Adobe\Adobe Illustrator 2023\Support Files\Contents\Windows\Illustrator.exe",
        r"C:\Program Files\Adobe\Adobe Illustrator 2024\Support Files\Contents\Windows\Illustrator.exe",
    ],
    "premiere pro": [
        r"C:\Program Files\Adobe\Adobe Premiere Pro 2023\Adobe Premiere Pro.exe",
        r"C:\Program Files\Adobe\Adobe Premiere Pro 2024\Adobe Premiere Pro.exe",
    ],
    "after effects": [
        r"C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\AfterFX.exe",
    ],
    "audacity": [
        r"C:\Program Files\Audacity\Audacity.exe",
        r"C:\Program Files (x86)\Audacity\Audacity.exe",
    ],
    "obs": [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
    ],
    "obs studio": [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    ],
    "xampp": [
        r"C:\xampp\xampp-control.exe",
    ],
    "wamp": [
        r"C:\wamp64\wampmanager.exe",
        r"C:\wamp\wampmanager.exe",
    ],
    "filezilla": [
        r"C:\Program Files\FileZilla FTP Client\filezilla.exe",
        r"C:\Program Files (x86)\FileZilla FTP Client\filezilla.exe",
    ],
    "7zip": [
        r"C:\Program Files\7-Zip\7zFM.exe",
        r"C:\Program Files (x86)\7-Zip\7zFM.exe",
    ],
    "winrar": [
        r"C:\Program Files\WinRAR\WinRAR.exe",
        r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
    ],
    "steam": [
        r"C:\Program Files (x86)\Steam\steam.exe",
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), r"Steam\steam.exe"),
    ],
    "epic games": [
        r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
    ],
    "blender": [
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    ],
    "canva": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Canva\Canva.exe"),
    ],
    "figma": [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Figma\Figma.exe"),
    ],
    "wordpad": [r"C:\Program Files\Windows NT\Accessories\wordpad.exe", r"C:\Windows\write.exe"],
    "character map": [r"C:\Windows\System32\charmap.exe"],
    "steps recorder": [r"C:\Windows\System32\psr.exe"],
    "narrator": [r"C:\Windows\System32\narrator.exe"],
    "magnifier": [r"C:\Windows\System32\magnify.exe"],
    "on screen keyboard": [r"C:\Windows\System32\osk.exe"],
    "virtual keyboard": [r"C:\Windows\System32\osk.exe"],
    "device manager": [r"C:\Windows\System32\devmgmt.msc"],
    "disk cleanup": [r"C:\Windows\System32\cleanmgr.exe"],
    "disk defragmenter": [r"C:\Windows\System32\dfrgui.exe"],
    "event viewer": [r"C:\Windows\System32\eventvwr.msc"],
    "registry editor": [r"C:\Windows\System32\regedit.exe"],
    "services": [r"C:\Windows\System32\services.msc"],
    "system properties": [r"C:\Windows\System32\sysdm.cpl"],
    "task scheduler": [r"C:\Windows\System32\taskschd.msc"],
    "windows firewall": [r"C:\Windows\System32\wf.msc"],
    "computer management": [r"C:\Windows\System32\compmgmt.msc"],
    "local group policy": [r"C:\Windows\System32\gpedit.msc"],
}

# Web fallbacks for apps that open better in browser + 100+ common websites
_WEB_FALLBACKS = {
    # ── Messaging / Social ─────────────────────────────────────────────
    "whatsapp": "https://web.whatsapp.com/",
    "whatsapp web": "https://web.whatsapp.com/",
    "telegram": "https://web.telegram.org/",
    "telegram web": "https://web.telegram.org/",
    "spotify":  "https://open.spotify.com/",
    "discord":  "https://discord.com/app",
    "instagram": "https://www.instagram.com/",
    "facebook":  "https://www.facebook.com/",
    "fb": "https://www.facebook.com/",
    "twitter":   "https://x.com/",
    "x": "https://x.com/",
    "linkedin":  "https://www.linkedin.com/",
    "reddit":    "https://www.reddit.com/",
    "snapchat":  "https://web.snapchat.com/",
    "pinterest": "https://www.pinterest.com/",
    "tumblr": "https://www.tumblr.com/",
    "tinder": "https://tinder.com/",
    "bumble": "https://bumble.com/",
    "threads": "https://www.threads.net/",
    "mastodon": "https://mastodon.social/",
    "wechat": "https://web.wechat.com/",
    "line": "https://line.me/en/",
    "signal": "https://signal.org/",
    "skype web": "https://web.skype.com/",
    "slack web": "https://slack.com/",
    "zoom web": "https://zoom.us/",
    "teams web": "https://teams.microsoft.com/",
    "meet": "https://meet.google.com/",
    "google meet": "https://meet.google.com/",
    "webex": "https://www.webex.com/",
    # ── Email / Productivity / Google Workspace ────────────────────────
    "gmail":    "https://mail.google.com/",
    "google":   "https://www.google.com/",
    "google drive": "https://drive.google.com/",
    "drive": "https://drive.google.com/",
    "google docs": "https://docs.google.com/document/",
    "docs": "https://docs.google.com/document/",
    "google sheets": "https://docs.google.com/spreadsheets/",
    "sheets": "https://docs.google.com/spreadsheets/",
    "google slides": "https://docs.google.com/presentation/",
    "slides": "https://docs.google.com/presentation/",
    "google forms": "https://docs.google.com/forms/",
    "forms": "https://docs.google.com/forms/",
    "google calendar": "https://calendar.google.com/",
    "calendar": "https://calendar.google.com/",
    "google classroom": "https://classroom.google.com/",
    "classroom": "https://classroom.google.com/",
    "google keep": "https://keep.google.com/",
    "keep": "https://keep.google.com/",
    "google photos": "https://photos.google.com/",
    "google translate": "https://translate.google.com/",
    "translate": "https://translate.google.com/",
    "google maps": "https://maps.google.com/",
    "maps":     "https://maps.google.com/",
    "youtube":  "https://www.youtube.com/",
    "youtube music": "https://music.youtube.com/",
    "yt music": "https://music.youtube.com/",
    "youtube studio": "https://studio.youtube.com/",
    "studio": "https://studio.youtube.com/",
    # ── AI / LLM tools ──────────────────────────────────────────────────
    "chatgpt":   "https://chatgpt.com/",
    "gpt": "https://chatgpt.com/",
    "openai": "https://chat.openai.com/",
    "gemini": "https://gemini.google.com/",
    "google gemini": "https://gemini.google.com/",
    "bard": "https://gemini.google.com/",
    "claude": "https://claude.ai/",
    "anthropic": "https://claude.ai/",
    "perplexity": "https://www.perplexity.ai/",
    "copilot": "https://copilot.microsoft.com/",
    "microsoft copilot": "https://copilot.microsoft.com/",
    "bing chat": "https://copilot.microsoft.com/",
    "hugging face": "https://huggingface.co/",
    "huggingface": "https://huggingface.co/",
    "midjourney": "https://www.midjourney.com/",
    "dalle": "https://openai.com/dall-e-3",
    "stable diffusion": "https://stablediffusionweb.com/",
    "tensorflow": "https://www.tensorflow.org/",
    "pytorch": "https://pytorch.org/",
    "kaggle": "https://www.kaggle.com/",
    "colab": "https://colab.research.google.com/",
    "google colab": "https://colab.research.google.com/",
    "jupyter": "https://jupyter.org/try",
    # ── Developer / Coding ──────────────────────────────────────────────
    "github":    "https://github.com/",
    "gitlab": "https://gitlab.com/",
    "bitbucket": "https://bitbucket.org/",
    "stackoverflow": "https://stackoverflow.com/",
    "stack overflow": "https://stackoverflow.com/",
    "stack exchange": "https://stackexchange.com/",
    "w3schools": "https://www.w3schools.com/",
    "mdn": "https://developer.mozilla.org/",
    "mdn docs": "https://developer.mozilla.org/",
    "dev.to": "https://dev.to/",
    "medium": "https://medium.com/",
    "freecodecamp": "https://www.freecodecamp.org/",
    "free code camp": "https://www.freecodecamp.org/",
    "codecademy": "https://www.codecademy.com/",
    "udemy": "https://www.udemy.com/",
    "coursera": "https://www.coursera.org/",
    "khan academy": "https://www.khanacademy.org/",
    "edx": "https://www.edx.org/",
    "pluralsight": "https://www.pluralsight.com/",
    "lynda": "https://www.linkedin.com/learning/",
    "nptel": "https://nptel.ac.in/",
    "hackerrank": "https://www.hackerrank.com/",
    "hacker rank": "https://www.hackerrank.com/",
    "codechef": "https://www.codechef.com/",
    "codeforces": "https://codeforces.com/",
    "leetcode": "https://leetcode.com/",
    "geeksforgeeks": "https://www.geeksforgeeks.org/",
    "geeks for geeks": "https://www.geeksforgeeks.org/",
    "tutorialspoint": "https://www.tutorialspoint.com/",
    "java t point": "https://www.javatpoint.com/",
    "javatpoint": "https://www.javatpoint.com/",
    "npmjs": "https://www.npmjs.com/",
    "npm": "https://www.npmjs.com/",
    "pypi": "https://pypi.org/",
    "python package index": "https://pypi.org/",
    "docker hub": "https://hub.docker.com/",
    "vercel": "https://vercel.com/",
    "netlify": "https://www.netlify.com/",
    "heroku": "https://www.heroku.com/",
    "aws": "https://aws.amazon.com/console/",
    "amazon web services": "https://aws.amazon.com/console/",
    "azure": "https://portal.azure.com/",
    "gcp": "https://console.cloud.google.com/",
    "google cloud": "https://console.cloud.google.com/",
    "firebase": "https://console.firebase.google.com/",
    "supabase": "https://supabase.com/",
    "mongodb": "https://cloud.mongodb.com/",
    "atlas": "https://cloud.mongodb.com/",
    "postman docs": "https://www.postman.com/",
    "figma web": "https://www.figma.com/",
    "canva web": "https://www.canva.com/",
    # ── OTT / Video / Streaming ─────────────────────────────────────────
    "netflix":   "https://www.netflix.com/",
    "prime video": "https://www.primevideo.com/",
    "amazon prime": "https://www.primevideo.com/",
    "hotstar":   "https://www.hotstar.com/",
    "disney plus": "https://www.disneyplus.com/",
    "disney+": "https://www.disneyplus.com/",
    "jiocinema": "https://www.jiocinema.com/",
    "zee5": "https://www.zee5.com/",
    "sonyliv": "https://www.sonyliv.com/",
    "mx player": "https://www.mxplayer.in/",
    "voot": "https://www.voot.com/",
    "alt balaji": "https://www.altbalaji.com/",
    "ullu": "https://ullu.app/",
    "hulu": "https://www.hulu.com/",
    "hbo max": "https://www.max.com/",
    "max": "https://www.max.com/",
    "apple tv": "https://tv.apple.com/",
    "paramount plus": "https://www.paramountplus.com/",
    "peacock": "https://www.peacocktv.com/",
    "crunchyroll": "https://www.crunchyroll.com/",
    "twitch": "https://www.twitch.tv/",
    "vimeo": "https://vimeo.com/",
    "dailymotion": "https://www.dailymotion.com/",
    # ── E-Commerce / Shopping / Food / Travel ───────────────────────────
    "amazon":    "https://www.amazon.in/",
    "amazon india": "https://www.amazon.in/",
    "flipkart":  "https://www.flipkart.com/",
    "myntra": "https://www.myntra.com/",
    "ajio": "https://www.ajio.com/",
    "meesho": "https://www.meesho.com/",
    "snapdeal": "https://www.snapdeal.com/",
    "paytm mall": "https://paytmmall.com/",
    "nykaa": "https://www.nykaa.com/",
    "purplle": "https://purplle.com/",
    "tatacliq": "https://www.tatacliq.com/",
    "croma": "https://www.croma.com/",
    "reliance digital": "https://www.reliancedigital.in/",
    "dmart": "https://www.dmart.in/",
    "bigbasket": "https://www.bigbasket.com/",
    "grofers": "https://www.blinkit.com/",
    "blinkit": "https://www.blinkit.com/",
    "zepto": "https://www.zepto.com/",
    "swiggy": "https://www.swiggy.com/",
    "zomato": "https://www.zomato.com/",
    "dominos": "https://www.dominos.co.in/",
    "mcdonalds": "https://www.mcdonaldsindia.com/",
    "kfc": "https://online.kfc.co.in/",
    "pizza hut": "https://www.pizzahut.co.in/",
    "ola": "https://www.olacabs.com/",
    "uber": "https://www.uber.com/in/en/",
    "rapido": "https://rapido.bike/",
    "redbus": "https://www.redbus.in/",
    "irctc": "https://www.irctc.co.in/",
    "makemytrip": "https://www.makemytrip.com/",
    "goibibo": "https://www.goibibo.com/",
    "yatra": "https://www.yatra.com/",
    "cleartrip": "https://www.cleartrip.com/",
    "booking": "https://www.booking.com/",
    "booking.com": "https://www.booking.com/",
    "airbnb": "https://www.airbnb.co.in/",
    "trivago": "https://www.trivago.in/",
    "expedia": "https://www.expedia.co.in/",
    # ── Finance / Payments / Crypto ─────────────────────────────────────
    "paytm": "https://paytm.com/",
    "phonepe": "https://www.phonepe.com/",
    "google pay": "https://pay.google.com/",
    "gpay": "https://pay.google.com/",
    "bhim": "https://bhimupi.org.in/",
    "groww": "https://groww.in/",
    "zerodha": "https://kite.zerodha.com/",
    "kite": "https://kite.zerodha.com/",
    "upstox": "https://upstox.com/",
    "angle one": "https://www.angelone.in/",
    "5paisa": "https://www.5paisa.com/",
    "hdfc netbanking": "https://netbanking.hdfcbank.com/netbanking/",
    "icici netbanking": "https://infinity.icicibank.com/corp/Login.jsp",
    "sbi netbanking": "https://retail.onlinesbi.sbi/retail/login.htm",
    "pnb netbanking": "https://www.pnbnet.net.in/",
    "binance": "https://www.binance.com/",
    "coinbase": "https://www.coinbase.com/",
    "wazirx": "https://wazirx.com/",
    "coindcx": "https://coindcx.com/",
    "cryptocurrency": "https://coinmarketcap.com/",
    "coinmarketcap": "https://coinmarketcap.com/",
    # ── Jobs / Career ───────────────────────────────────────────────────
    "naukri": "https://www.naukri.com/",
    "naukri.com": "https://www.naukri.com/",
    "indeed": "https://www.indeed.co.in/",
    "glassdoor": "https://www.glassdoor.co.in/",
    "monster": "https://www.monsterindia.com/",
    "shine": "https://www.shine.com/",
    "freshersworld": "https://www.freshersworld.com/",
    "internshala": "https://internshala.com/",
    "angel list": "https://angel.co/",
    "wellfound": "https://wellfound.com/",
    # ── News / Knowledge / Education ────────────────────────────────────
    "google news": "https://news.google.com/",
    "news google": "https://news.google.com/",
    "bbc news": "https://www.bbc.com/news",
    "cnn": "https://edition.cnn.com/",
    "ndtv": "https://www.ndtv.com/",
    "aaj tak": "https://www.aajtak.in/",
    "abp news": "https://www.abplive.com/",
    "india today": "https://www.indiatoday.in/",
    "the hindu": "https://www.thehindu.com/",
    "times of india": "https://timesofindia.indiatimes.com/",
    "toi": "https://timesofindia.indiatimes.com/",
    "hindustan times": "https://www.hindustantimes.com/",
    "wikipedia": "https://www.wikipedia.org/",
    "wiki": "https://www.wikipedia.org/",
    "britannica": "https://www.britannica.com/",
    "dictionary": "https://www.dictionary.com/",
    "merriam webster": "https://www.merriam-webster.com/",
    "oxford dictionary": "https://www.oxfordlearnersdictionaries.com/",
    "thesaurus": "https://www.thesaurus.com/",
    "quora": "https://www.quora.com/",
    "yahoo answers": "https://answers.yahoo.com/",
    # ── Sports / Cricket ────────────────────────────────────────────────
    "cricbuzz": "https://www.cricbuzz.com/",
    "cricinfo": "https://www.espncricinfo.com/",
    "espn": "https://www.espn.in/",
    "sportskeeda": "https://www.sportskeeda.com/",
    "fantasy premier league": "https://fantasy.premierleague.com/",
    "fpl": "https://fantasy.premierleague.com/",
    "dream11": "https://www.dream11.com/",
    "ipl": "https://www.iplt20.com/",
    "bcci": "https://www.bcci.tv/",
    "fifa": "https://www.fifa.com/",
    "nba": "https://www.nba.com/",
    "olympics": "https://olympics.com/",
    # ── Gaming ──────────────────────────────────────────────────────────
    "roblox": "https://www.roblox.com/",
    "minecraft": "https://www.minecraft.net/",
    "fortnite": "https://www.fortnite.com/",
    "pubg": "https://pubg.com/",
    "bgmi": "https://www.battlegroundsmobileindia.com/",
    "valorant": "https://playvalorant.com/",
    "league of legends": "https://www.leagueoflegends.com/",
    "lol": "https://www.leagueoflegends.com/",
    "dota 2": "https://www.dota2.com/",
    "csgo": "https://www.counter-strike.net/",
    "counter strike": "https://www.counter-strike.net/",
    "gta": "https://www.rockstargames.com/",
    "grand theft auto": "https://www.rockstargames.com/",
    "epic games store": "https://store.epicgames.com/",
    "ea sports": "https://www.ea.com/sports",
    "fifa game": "https://www.ea.com/games/ea-sports-fc",
    "call of duty": "https://www.callofduty.com/",
    "cod": "https://www.callofduty.com/",
    "among us": "https://www.innersloth.com/games/among-us/",
    "candy crush": "https://king.com/game/candycrush",
    # ── Misc / Utility ──────────────────────────────────────────────────
    "smallpdf": "https://smallpdf.com/",
    "ilovepdf": "https://www.ilovepdf.com/",
    "pdf drive": "https://www.pdfdrive.com/",
    "z library": "https://z-lib.io/",
    "libgen": "https://libgen.is/",
    "archive.org": "https://archive.org/",
    "wayback machine": "https://web.archive.org/",
    "speedtest": "https://www.speedtest.net/",
    "fast.com": "https://fast.com/",
    "virus total": "https://www.virustotal.com/",
    "shodan": "https://www.shodan.io/",
    "have i been pwned": "https://haveibeenpwned.com/",
    "123rf": "https://www.123rf.com/",
    "unsplash": "https://unsplash.com/",
    "pexels": "https://www.pexels.com/",
    "pixabay": "https://pixabay.com/",
    "freepik": "https://www.freepik.com/",
    "flaticon": "https://www.flaticon.com/",
    "favicon": "https://favicon.io/",
    "color picker": "https://htmlcolorcodes.com/color-picker/",
    "coolors": "https://coolors.co/",
    "canva design": "https://www.canva.com/",
    "photopea": "https://www.photopea.com/",
    "remove bg": "https://www.remove.bg/",
    "tinypng": "https://tinypng.com/",
    "tinyjpg": "https://tinyjpg.com/",
    "imgur": "https://imgur.com/",
    "cloudconvert": "https://cloudconvert.com/",
    "zamzar": "https://www.zamzar.com/",
    "regex101": "https://regex101.com/",
    "regexr": "https://regexr.com/",
    "json formatter": "https://jsonformatter.org/",
    "json validator": "https://jsonlint.com/",
    "base64": "https://www.base64decode.org/",
    "url encoder": "https://www.urlencoder.org/",
    "diff checker": "https://www.diffchecker.com/",
    "carbon now": "https://carbon.now.sh/",
    "code beautify": "https://codebeautify.org/",
    "online gdb": "https://www.onlinegdb.com/",
    "replit": "https://replit.com/",
    "code pen": "https://codepen.io/",
    "jsfiddle": "https://jsfiddle.net/",
    "codesandbox": "https://codesandbox.io/",
    "stack blitz": "https://stackblitz.com/",
    "glitch": "https://glitch.com/",
}


def _try_open_desktop_app(app_name):
    """
    Try to open a known desktop app by name.
    Returns True if opened successfully, False otherwise.
    """
    import glob
    paths = _DESKTOP_APPS.get(app_name, [])
    for path in paths:
        # Handle UWP protocol URIs (e.g. ms-settings:, ms-photos:)
        if path.startswith("ms-") or path.startswith("microsoft."):
            try:
                os.startfile(path)
                return True
            except Exception:
                continue
        # Handle shell:AppsFolder URIs for Store/UWP apps
        if path.startswith("shell:"):
            try:
                subprocess.Popen(["explorer.exe", path], shell=False)
                return True
            except Exception:
                try:
                    os.system(f'start "" "{path}"')
                    return True
                except Exception:
                    continue
        # Handle glob patterns (e.g. Discord app-* folders)
        if "*" in path:
            matches = glob.glob(path)
            if matches:
                try:
                    subprocess.Popen([matches[0]], shell=False)
                    return True
                except Exception:
                    continue
        # .lnk shortcut files
        if path.endswith(".lnk") and os.path.exists(path):
            try:
                os.startfile(path)
                return True
            except Exception:
                continue
        # Direct executable path
        if os.path.exists(path):
            try:
                subprocess.Popen([path], shell=False)
                return True
            except Exception:
                continue
    return False


def _open_via_start_menu(app_name):
    """
    Try to launch app by searching Windows Start Menu using PowerShell.
    This handles UWP apps (like WhatsApp from Microsoft Store).
    Returns True if likely launched.
    """
    try:
        # Use 'start' command which Windows resolves from PATH + app aliases
        result = subprocess.run(
            ["powershell", "-Command",
             f"Start-Process '{app_name}' -ErrorAction Stop"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").strip()
    if query.lower().startswith("open "):
        target = query[5:].strip()
    elif query.lower() == "open":
        return
    else:
        target = query.replace("open", "").strip()

    if not target:
        return

    app_name = target.lower().strip()

    # 1. Check local system commands database table (user-added custom apps)
    con, cursor = _get_cursor()
    try:
        cursor.execute(
            "SELECT path FROM sys_command WHERE LOWER(name) = ?", (app_name,)
        )
        results = cursor.fetchall()
        if results:
            speak("Opening " + target)
            os.startfile(results[0][0])
            return

        # 2. Check registered web commands database table
        cursor.execute(
            "SELECT url FROM web_command WHERE LOWER(name) = ?", (app_name,)
        )
        results = cursor.fetchall()
        if results:
            speak("Opening " + target)
            _open_in_browser(results[0][0])
            return
    except Exception as e:
        print(f"[openCommand DB error]: {e}")
    finally:
        con.close()

    speak("Opening " + target)

    # 3. Try known desktop apps list first
    if app_name in _DESKTOP_APPS:
        if _try_open_desktop_app(app_name):
            print(f"[openCommand] Opened desktop app: {app_name}")
            return
        # Desktop app not found — fall through to web fallback
        if app_name in _WEB_FALLBACKS:
            _open_in_browser(_WEB_FALLBACKS[app_name])
            return

    # 4. Try web fallbacks for social/streaming apps
    if app_name in _WEB_FALLBACKS:
        _open_in_browser(_WEB_FALLBACKS[app_name])
        return

    # 5. If explicit domain or URL given (e.g. github.com, python.org)
    if any(app_name.endswith(tld) for tld in [".com", ".org", ".net", ".io", ".in", ".ai", ".co", ".gov", ".edu", ".dev"]):
        url = app_name if app_name.startswith("http") else f"https://{app_name}"
        _open_in_browser(url)
        return

    # 6. Try Windows Start Menu / app alias (handles Store apps, PATH apps)
    if _open_via_start_menu(app_name):
        print(f"[openCommand] Opened via Start Menu: {app_name}")
        return

    # 7. Single-word — try as website
    if " " not in app_name:
        _open_in_browser(f"https://www.{app_name}.com")
        return

    # 8. Multi-word — Google search & launch
    _open_in_browser(f"https://www.google.com/search?q={quote(target)}")


def PlayYoutube(query):
    from urllib.parse import quote
    import webbrowser

    search_term = extract_yt_term(query)
    if not search_term:
        speak("Please tell me what to play on YouTube")
        return

    speak("Playing " + search_term + " on YouTube")

    # youtube-search se pehla video ID nikalo — seedha watch URL open hoga
    try:
        from youtube_search import YoutubeSearch
        results = YoutubeSearch(search_term, max_results=1).to_dict()
        if results:
            video_id = results[0]["id"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            if os.path.exists(EDGE_PATH):
                subprocess.Popen([EDGE_PATH, url])
            else:
                webbrowser.open(url)
            return
    except Exception as e:
        print(f"[YouTube] Search error: {e}")

    # Fallback — search results page (autoplay nahi hoga)
    url = f"https://www.youtube.com/results?search_query={quote(search_term)}"
    if os.path.exists(EDGE_PATH):
        subprocess.Popen([EDGE_PATH, url])
    else:
        webbrowser.open(url)


def findContact(query):
    words_to_remove = [
        ASSISTANT_NAME,
        "make",
        "a",
        "to",
        "phone",
        "call",
        "send",
        "message",
        "whatsapp",
        "video",
    ]
    query = remove_words(query, words_to_remove)

    con, cursor = _get_cursor()
    try:
        query = query.strip().lower()
        cursor.execute(
            "SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
            ("%" + query + "%", query + "%"),
        )
        results = cursor.fetchall()
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith("+91"):
            mobile_number_str = "+91" + mobile_number_str

        return mobile_number_str, query
    except Exception:
        speak("Contact not found")
        return 0, 0
    finally:
        con.close()


def whatsApp(mobile_no, message, flag, name):
    if flag == "message":
        target_tab = 12
        jarvis_message = "Message sent successfully to " + name
    elif flag == "call":
        target_tab = 7
        message = ""
        jarvis_message = "Calling " + name
    else:
        target_tab = 6
        message = ""
        jarvis_message = "Starting video call with " + name

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'cmd /c start "" "{whatsapp_url}"'
    subprocess.run(full_command, shell=True)

    if pyautogui is None:
        speak(jarvis_message)
        return

    time.sleep(5)
    pyautogui.hotkey("ctrl", "f")

    for _ in range(1, target_tab):
        pyautogui.press("tab")

    pyautogui.press("enter")
    speak(jarvis_message)


def _simple_chat_fallback(query):
    from datetime import datetime

    text = query.lower()
    if "time" in text:
        return f"The time is {datetime.now().strftime('%I:%M %p')}"
    if "date" in text:
        return f"Today is {datetime.now().strftime('%B %d, %Y')}"
    if "hello" in text or "hi" in text:
        return "Hello Sir, how can I help you?"
    return f"I heard: {query}. Configure HugChat cookies for full chat support."


# Reuse chatbot session across calls so conversation history is preserved
_chatbot_instance = None
_chatbot_conv_id  = None

def chatBot(query):
    global _chatbot_instance, _chatbot_conv_id

    cookie_path = os.path.join(os.path.dirname(__file__), "cookies.json")

    if hugchat is None or not os.path.exists(cookie_path):
        response = _simple_chat_fallback(query)
        speak(response)
        return response

    try:
        user_input = query.lower()

        # Create session once, reuse afterwards
        if _chatbot_instance is None:
            _chatbot_instance = hugchat.ChatBot(cookie_path=cookie_path)
            _chatbot_conv_id  = _chatbot_instance.new_conversation()

        _chatbot_instance.change_conversation(_chatbot_conv_id)
        response = str(_chatbot_instance.chat(user_input))
        speak(response)
        return response
    except Exception as exc:
        print(f"Chat error: {exc}")
        # Reset on error so next call gets a fresh session
        _chatbot_instance = None
        _chatbot_conv_id  = None
        response = _simple_chat_fallback(query)
        speak(response)
        return response


def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    os.system(
        "adb shell am start -a android.intent.action.CALL -d tel:" + mobileNo
    )


def sendMessage(message, mobileNo, name):
    from engine.helper import (
        adbInput,
        goback,
        keyEvent,
        replace_spaces_with_percent_s,
        tapEvents,
    )

    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("Sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    tapEvents(136, 2220)
    tapEvents(819, 2192)
    adbInput(mobileNo)
    tapEvents(601, 574)
    tapEvents(390, 2270)
    adbInput(message)
    tapEvents(957, 1397)
    speak("Message sent successfully to " + name)
