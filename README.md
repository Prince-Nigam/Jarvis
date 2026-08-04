# 🤖 J.A.R.V.I.S — Personal Desktop Voice Assistant

> **Just A Rather Very Intelligent System**
> Control your laptop using only your voice — no touch required!

---

## 📌 What Is Jarvis?

Jarvis is a Python-based personal voice assistant that lets you
**fully control your laptop using voice commands**. Simply say **"Jarvish"** —
and then give any command, and it will be executed on your computer.

- Open apps (WhatsApp, Chrome, Notepad, etc.)
- Open files and folders
- Control volume and brightness
- Minimize, maximize, and close windows
- Take screenshots
- Type text
- Control media playback (play/pause/next/previous)
- Search on Google or YouTube
- ... and much more

---

## 🚀 Quick Start — Only 3 Steps

### Step 1 — Install Python
Python 3.10 or later is required.
Download: https://www.python.org/downloads/

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run It
```bash
python main.py
```
Or double-click `run.bat`.

The browser window will open with Jarvis at: **http://localhost:8000**

---

## 🎙️ How to Use It

### Step 1 — Say the Wake Word
You can say any of the following words (no need to touch the laptop):

| What you say | Result |
|--------------|--------|
| **"Jarvish"** | Jarvis becomes active |
| **"Hey Jarvis"** | Jarvis becomes active |
| **"Ok Jarvis"** | Jarvis becomes active |
| **"Hello Jarvis"** | Jarvis becomes active |

Once activated:
1. 🔔 A double beep sound will play
2. The Jarvis window will open in the browser
3. Jarvis will say — *"Yes Sir, I am listening"*

### Step 2 — Give a Command
Now say any command you want — Jarvis will execute it.

### Step 3 — Deactivate It (optional)
When you are done:

| What you say | Result |
|--------------|--------|
| **"Stop"** | Jarvis goes to sleep |
| **"Sleep"** | Jarvis goes to sleep |
| **"Bye Jarvis"** | Jarvis goes to sleep |

> **Auto-Sleep:** If no command is given for 30 seconds, Jarvis will automatically go to sleep.

---

## 🗣️ Full Command List

### 📱 Open Apps
```
open whatsapp         → Opens WhatsApp Desktop
open chrome           → Opens Google Chrome
open notepad          → Opens Notepad
open calculator       → Opens Calculator
open spotify          → Opens Spotify
open telegram         → Opens Telegram
open vscode           → Opens VS Code
open youtube          → Opens YouTube in the browser
open instagram        → Opens Instagram in the browser
open gmail            → Opens Gmail in the browser
open chatgpt          → Opens ChatGPT in the browser
open netflix          → Opens Netflix in the browser
```

### 📂 Open Folders
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
recycle bin           → Recycle Bin
empty recycle bin     → Empty the Recycle Bin
```

### 🪟 Window Control
```
minimize window       → Minimize the window
maximize window       → Maximize the window / Full Screen
close window          → Close the window
switch window         → Alt+Tab (switch windows)
show desktop          → Minimize all windows
snap left             → Snap the window to the left side
snap right            → Snap the window to the right side
task view             → Show all virtual desktops
```

### ⌨️ Keyboard Shortcuts
```
copy                  → Ctrl+C
paste                 → Ctrl+V
cut                   → Ctrl+X
undo                  → Ctrl+Z
redo                  → Ctrl+Y
select all            → Ctrl+A
save file             → Ctrl+S
new tab               → Ctrl+T (browser)
close tab             → Ctrl+W (browser)
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

### 🎵 Media Control
```
play music            → Play/Pause toggle
pause music           → Play/Pause toggle
next song             → Next song
previous song         → Previous song
stop music            → Stop media
volume up             → Increase volume
volume down           → Decrease volume
mute                  → Mute/Unmute
```

### 🔆 Brightness
```
brightness up         → Brighten the screen
brightness down       → Dim the screen
set brightness to 70  → Set brightness to 70%
```

### 📸 Screenshot
```
take screenshot       → Save a full-screen screenshot to the Desktop
screenshot            → Same as above
```

### ✍️ Type Text
```
type hello world      → Type "hello world" at the cursor
write my name is John → Type "my name is John" at the cursor
```

### 📜 Scroll
```
scroll down           → Scroll the page down
scroll up             → Scroll the page up
```

### 🔍 Search
```
search google for python tutorials   → Search on Google
search youtube for bollywood songs   → Search on YouTube
play <song> on youtube               → Play directly on YouTube
```

### 💬 WhatsApp / Contacts
```
send message to Rahul     → Send a WhatsApp message
phone call to Mom         → Make a phone call
video call to Priya       → Make a video call
```
> To use contacts, add names and numbers in `contacts.csv`.

### 💻 System
```
lock screen           → Lock the laptop
sleep                 → Put the laptop to sleep
task manager          → Open Task Manager
open settings         → Open Windows Settings
open run              → Open the Win+R dialog
virtual keyboard      → Open the on-screen keyboard
clipboard             → Open clipboard history (Win+V)
```

### 🕐 Time / Date
```
what time is it       → Tell the current time
what is today's date  → Tell today's date
```

### 🤖 Chat
Ask any question that is not in the list above — Jarvis will answer using the AI chatbot.
```
who are you
tell me a joke
what is the capital of India
explain machine learning
```

---

## 📁 Project Structure

```
Jarvis/
│
├── main.py                  ← Flask server + API endpoints (Entry Point)
├── run.py                   ← Alternative launcher
├── run.bat                  ← Run by double-clicking (Windows)
├── requirements.txt         ← Python dependencies
├── contacts.csv             ← Add your contacts here
├── jarvis.db                ← SQLite database (apps, websites, contacts)
│
├── engine/
│   ├── command.py           ← Voice command router (all commands are routed here)
│   ├── features.py          ← Open apps/websites, YouTube, WhatsApp, ChatBot
│   ├── desktop_control.py   ← Desktop control (window, keyboard, media, brightness)
│   ├── hotword.py           ← Always-on wake word listener ("Jarvish")
│   ├── authenticator.py     ← Face authentication
│   ├── helper.py            ← Utility functions
│   ├── config.py            ← Configuration (assistant name, keys)
│   ├── init_db.py           ← Database setup
│   ├── system_info.py       ← CPU, RAM, Disk stats
│   ├── window_manager.py    ← Browser window management
│   │
│   └── auth/
│       ├── sample.py        ← Capture face samples
│       ├── trainer.py       ← Train the face model
│       └── recoganize.py    ← Face authentication logic
│
└── www/                     ← Frontend (HTML/CSS/JS)
    └── index.html           ← Main Jarvis UI
```

---

## ⚙️ Configuration

### Add Contacts
Add your contacts to the `contacts.csv` file:
```csv
name,mobile_no,email
Rahul,9876543210,rahul@gmail.com
Mom,8765432109,
```

### Add a New App or Website
In the `jarvis.db` database, or directly in `engine/init_db.py`:
```python
# Add a web command
("mywebsite", "https://www.mywebsite.com"),

# Add a desktop app — in the sys_command table
# name: "my app", path: "C:\\Path\\To\\App.exe"
```

### Change the Assistant Name
In `engine/config.py`:
```python
ASSISTANT_NAME = "jarvis"  # change here
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web server |
| `flask-cors` | API CORS |
| `pyttsx3` | Text-to-Speech (voice output) |
| `SpeechRecognition` | Listen to voice from the microphone |
| `pyautogui` | Desktop automation |
| `pywhatkit` | YouTube, WhatsApp |
| `hugchat` | AI Chatbot |
| `psutil` | System stats (CPU/RAM) |
| `playsound` | Sound effects |

---

## ❓ Troubleshooting

### Jarvis is not hearing "Jarvish"
- Check your microphone (Windows Settings → Sound → Input)
- An internet connection is required (Google Speech Recognition is used)
- Speak more clearly and slightly slower

### WhatsApp does not open
- WhatsApp Desktop must be installed (from the Microsoft Store)
- Or it will automatically open in the browser at web.whatsapp.com

### TTS (voice) is not playing
- Run `pip install pyttsx3`
- Windows SAPI5 voices must be installed

### Import errors are appearing
```bash
pip install -r requirements.txt
```

---

## 👨‍💻 Tech Stack

- **Python 3.10+** — Core logic
- **Flask** — REST API backend
- **HTML / CSS / JavaScript** — Jarvis UI (frontend)
- **SQLite** — Local database (apps, contacts)
- **Google Speech Recognition** — Voice-to-text
- **pyttsx3 / SAPI5** — Text-to-voice
- **PyAutoGUI** — Desktop automation
- **Win32 API** — Window management

---

*Built with ❤️ — Jarvis, your personal AI assistant*
