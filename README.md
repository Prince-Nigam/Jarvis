# J.A.R.V.I.S — Personal Desktop Voice Assistant

> **Just A Rather Very Intelligent System**
> Control your entire laptop using only your voice — no touch required!

---

## What Is Jarvis?

Jarvis is a Python-based personal voice assistant that lets you **fully control your laptop using voice commands**. Just say **"Wakeup Jarvish"** to activate it, then say **"Jarvish"** followed by any command.

**What it can do:**
- Open apps and websites (WhatsApp, Chrome, YouTube, Instagram, and 200+ more)
- Play any song directly on YouTube
- Control song volume and system volume independently
- Minimize, maximize, snap, and close windows
- Take screenshots
- Type text at the cursor
- Control media playback (play / pause / next / previous)
- Search on Google, YouTube, Wikipedia, Amazon, and more
- Send WhatsApp messages and make calls
- Unlock with face authentication
- **Smart Learning** — Jarvis remembers every website and song you open, so next time it opens instantly

---

## Quick Start — Only 3 Steps

### Step 1 — Install Python
Python 3.10 or higher is required.
Download: https://www.python.org/downloads/

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
pip install pywin32
pip install youtube-search
```

### Step 3 — Run Jarvis
```bash
python run.py
```
Or double-click `run.bat`.

Jarvis will open in your browser at: **http://localhost:8000**

---

## How to Use

### Step 1 — Say the Wake Word
No need to touch your laptop at all:

| Say this | Result |
|----------|--------|
| **"Wakeup Jarvish"** | Jarvis wakes from deep sleep and comes online |
| **"Hey Jarvis"** | Jarvis activates |
| **"Ok Jarvish"** | Jarvis activates |

When activated:
1. A beep sound plays
2. The browser window opens automatically
3. Jarvis says — *"Jarvis online. Say Jarvish to give a command."*

### Step 2 — Give a Command
Say **"Jarvish"** — Jarvis will reply **"Yes Sir, go ahead."**
Then say your command — Jarvis will execute it and tell you what it did.

**Or say it all at once:** `"Jarvish open Chrome"` — no need for two steps.

### Step 3 — Continuous Commands
After each command, Jarvis **stays ready to listen** for the next one.
No need to say "Jarvish" again after every command.

### Step 4 — Put Jarvis to Sleep (optional)
| Say this | Result |
|----------|--------|
| **"Jarvish shutdown"** | Jarvis goes to sleep |
| **"Jarvish bye"** | Jarvis goes to sleep |

> **Auto-Sleep:** If no command is given for 2 minutes, Jarvis automatically goes to sleep.

---

## Full Command Reference

### Open Apps
```
open whatsapp          → Opens WhatsApp Desktop
open chrome            → Opens Google Chrome
open notepad           → Opens Notepad
open calculator        → Opens Calculator
open spotify           → Opens Spotify
open telegram          → Opens Telegram
open vscode            → Opens VS Code
open youtube           → Opens YouTube in browser
open instagram         → Opens Instagram in browser
open gmail             → Opens Gmail in browser
open chatgpt           → Opens ChatGPT in browser
open netflix           → Opens Netflix in browser
open whatsapp web      → Opens WhatsApp Web
```
> 200+ apps and websites are supported out of the box.

### Play a Song on YouTube
```
play believer                        → Plays Believer on YouTube
play arijit singh                    → Plays an Arijit Singh song
open youtube play shape of you       → Plays Shape of You directly
open youtube and play kesariya       → Plays Kesariya directly
play believer on youtube             → Plays Believer
```
> If you say just **"open youtube play the song"** without a name,
> Jarvis will ask — *"Which song Sir? Please tell me the name."*

### Volume Control

**Song / YouTube volume (browser player):**
```
song volume up             → Increase the YouTube player volume
song volume down           → Decrease the YouTube player volume
increase music volume      → Song volume up
decrease music volume      → Song volume down
```

**System / laptop volume:**
```
volume full                → Set system volume to 100%
system volume full         → System volume max
volume up                  → Increase system volume a bit
volume down                → Decrease system volume a bit
volume zero                → Set system volume to zero
mute                       → Mute / Unmute
```

### Open Folders
```
open downloads        → Downloads folder
open documents        → Documents folder
open desktop          → Desktop folder
open pictures         → Pictures folder
open music            → Music folder
open videos           → Videos folder
open c drive          → C:\ drive
open d drive          → D:\ drive
this pc               → File Explorer (This PC)
recycle bin           → Open Recycle Bin
empty recycle bin     → Empty the Recycle Bin
```

### Window Control
```
minimize window       → Minimize the active window
maximize window       → Maximize the active window
close window          → Close the active window
switch window         → Alt+Tab (switch between windows)
show desktop          → Minimize all windows
snap left             → Snap window to the left half
snap right            → Snap window to the right half
full screen           → Toggle fullscreen (F11)
task view             → Show all virtual desktops
split screen          → Tile windows side by side
```

### Keyboard Shortcuts
```
copy                  → Ctrl+C
paste                 → Ctrl+V
cut                   → Ctrl+X
undo                  → Ctrl+Z
redo                  → Ctrl+Y
select all            → Ctrl+A
save file             → Ctrl+S
new tab               → Ctrl+T
close tab             → Ctrl+W
refresh               → F5
go back               → Alt+Left
go forward            → Alt+Right
zoom in               → Ctrl++
zoom out              → Ctrl+-
find on page          → Ctrl+F
new window            → Ctrl+N
press enter           → Enter key
press escape          → Escape key
```

### Media Control
```
play music            → Play / Pause toggle
pause music           → Play / Pause toggle
next song             → Skip to next track
previous song         → Go to previous track
stop music            → Stop media playback
```

### Brightness
```
brightness up              → Increase screen brightness
brightness down            → Decrease screen brightness
set brightness to 70       → Set brightness to exactly 70%
```

### Screenshot
```
take screenshot       → Save a full screenshot to the Desktop
screenshot            → Same as above
snipping tool         → Open Snipping Tool for a partial capture
```

### Type Text
```
type hello world           → Types "hello world" at the cursor
write my name is John      → Types "my name is John" at the cursor
```

### Scroll
```
scroll down           → Scroll the page down
scroll up             → Scroll the page up
scroll to top         → Jump to the top of the page
scroll to bottom      → Jump to the bottom of the page
```

### Search
```
search google for python tutorials      → Search on Google
search youtube for bollywood songs      → Search on YouTube
search wikipedia for machine learning   → Search on Wikipedia
search amazon for headphones            → Search on Amazon
search github for flask                 → Search on GitHub
```

### Browser
```
new tab               → Open a new tab
close tab             → Close current tab
incognito             → Open an Incognito window
developer tools       → Open DevTools (F12)
bookmarks             → Open Bookmarks
history               → Open browsing history
go back               → Navigate back
go forward            → Navigate forward
```

### WhatsApp / Contacts
```
send message to Rahul      → Send a WhatsApp message
phone call to Mom          → Make a phone call
video call to Priya        → Start a video call
```
> To use contacts, add names and numbers in `contacts.csv`.

### System
```
lock screen           → Lock the laptop
sleep                 → Put the laptop to sleep
task manager          → Open Task Manager
open settings         → Open Windows Settings
open run              → Open the Win+R dialog
virtual keyboard      → Open the on-screen keyboard
clipboard             → Open clipboard history (Win+V)
restart               → Restart the system (10 second countdown)
shutdown              → Shut down the system (10 second countdown)
battery status        → Report current battery percentage
ip address            → Report local and public IP address
show wifi             → List saved Wi-Fi networks
```

### Time / Date
```
what time is it       → Tells the current time
what is today's date  → Tells today's date
what day is it        → Tells the day of the week
```

### Smart Learning (Auto Memory)
Jarvis remembers every website and song you open. Next time, just say the name:
```
# First time:
open instagram          → Instagram opens  [LEARN: 'instagram' stored]

# Next time:
instagram               → Opens directly, no "open" needed

# Songs too:
play believer           → Plays on YouTube  [LEARN: 'believer' stored]
believer                → Plays directly next time
```
The Activity Log shows `Remembered:` whenever a command runs from memory.

### Chat / AI
Anything not in the command list is handled by the AI chatbot:
```
who are you
tell me a joke
how are you
thank you
what can you do
```

---

## Project Structure

```
Jarvis/
│
├── main.py                  ← Flask server + API endpoints + Event log
├── run.py                   ← Entry point  (python run.py)
├── run.bat                  ← Windows double-click launcher
├── requirements.txt         ← Python dependencies
├── contacts.csv             ← Add your contacts here
├── Database.db              ← SQLite DB (apps, websites, contacts, learned commands)
│
├── engine/
│   ├── command.py           ← Command router + TTS (win32com SAPI5) + Smart Learning
│   ├── features.py          ← Open apps/websites, YouTube play, WhatsApp, ChatBot
│   ├── desktop_control.py   ← Window, keyboard, media, volume, brightness control
│   ├── hotword.py           ← Always-on wake word listener ("Wakeup Jarvish")
│   ├── helper.py            ← Utility functions (YouTube term extraction, etc.)
│   ├── config.py            ← Configuration (assistant name)
│   ├── init_db.py           ← Database setup (sys_command, web_command, learned_commands)
│   ├── system_info.py       ← CPU, RAM, Disk, Battery stats
│   ├── window_manager.py    ← Browser window management
│   ├── authenticator.py     ← Face authentication
│   │
│   └── auth/
│       ├── sample.py        ← Capture face training samples
│       ├── trainer.py       ← Train the face recognition model
│       └── recoganize.py    ← Face recognition logic
│
└── www/                     ← Frontend (HTML / CSS / JS)
    ├── index.html           ← Main Jarvis UI
    ├── main.js              ← Command handling + Activity Log polling
    ├── controller.js        ← Boot sequence, mic button, chat
    ├── style.css            ← Jarvis UI styling
    └── assets/              ← Images, sounds, icons
```

---

## Configuration

### Add Contacts
Edit `contacts.csv`:
```csv
name,mobile_no,email
Rahul,9876543210,rahul@gmail.com
Mom,8765432109,
```

### Add a Custom App or Website
In `Database.db` or directly in `engine/init_db.py`:
```python
# Add a web command
("my website", "https://www.mywebsite.com"),

# Add a desktop app (sys_command table)
# name: "my app",  path: "C:\\Path\\To\\App.exe"
```

### Change the Assistant Name
In `engine/config.py`:
```python
ASSISTANT_NAME = "jarvis"   # change this
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web server (backend) |
| `flask-cors` | API CORS support |
| `pywin32` | TTS via Windows SAPI5 (primary voice engine) |
| `pyttsx3` | TTS fallback |
| `SpeechRecognition` | Microphone voice recognition |
| `PyAudio` | Microphone input |
| `pyautogui` | Desktop automation |
| `psutil` | CPU / RAM / Battery stats |
| `opencv-contrib-python` | Face authentication |
| `Pillow` | Image processing |
| `pygame` | Sound effects |
| `youtube-search` | YouTube video search and direct play |
| `requests` | HTTP requests |
| `edge-tts` | Neural TTS voice (optional) |

---

## Troubleshooting

### "Wakeup Jarvish" is not being heard
- Check your microphone: Windows Settings → Sound → Input
- An internet connection is required (Google Speech Recognition)
- Speak clearly and slightly slower than normal

### Song is not playing on YouTube
```bash
pip install youtube-search
```
Then restart the server: `python run.py`

### Jarvis has no voice (silent)
```bash
pip install pywin32
```
- Windows SAPI5 voices must be installed (they are by default on Windows 10/11)
- Make sure speakers or headphones are connected

### Import errors on startup
```bash
pip install -r requirements.txt
pip install pywin32 youtube-search
```

### Activity Log is not updating
- Refresh the browser at `http://localhost:8000`
- Make sure the server is running (`python run.py`)

---

## Face Authentication Setup

```bash
# Step 1 — Capture face training samples
python engine/auth/sample.py

# Step 2 — Train the face model
python engine/auth/trainer.py

# Step 3 — Jarvis will automatically verify your face on startup
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Core logic | Python 3.10+ |
| Backend API | Flask |
| Frontend UI | HTML / CSS / JavaScript |
| Database | SQLite |
| Voice input | Google Speech Recognition |
| Voice output | win32com SAPI5 (Windows native) |
| Desktop control | PyAutoGUI |
| Window management | Win32 API |
| YouTube playback | youtube-search library |
| Face authentication | OpenCV |

---

*Jarvis — your personal AI assistant*
