# 🤖 J.A.R.V.I.S — Personal Desktop Voice Assistant

> **Just A Rather Very Intelligent System**
> Apne laptop ko sirf awaaz se control karo — ek bhi touch nahi!

---

## 📌 Kya Hai Jarvis?

Jarvis ek Python-based personal voice assistant hai jo tumhare laptop ko
**poori tarah voice se control karta hai**. Jarvis ko sirf **"Jarvish"** bolo —
aur phir jo bhi command do, woh laptop pe execute ho jaati hai.

- Apps kholna (WhatsApp, Chrome, Notepad, etc.)
- Files/Folders open karna
- Volume, Brightness control
- Window minimize/maximize/close
- Screenshot lena
- Text type karna
- Media control (play/pause/next/previous)
- Google/YouTube pe search karna
- ... aur bahut kuch

---

## 🚀 Quick Start — Sirf 3 Steps

### Step 1 — Python Install karo
Python 3.10 ya upar chahiye.
Download: https://www.python.org/downloads/

### Step 2 — Dependencies Install karo
```bash
pip install -r requirements.txt
```

### Step 3 — Chalao
```bash
python main.py
```
Ya double-click karo `run.bat` pe.

Browser mein Jarvis khul jaayega: **http://localhost:8000**

---

## 🎙️ Kaise Use Karna Hai

### Step 1 — Wake Word bolo
Kuch bhi bolo inme se (laptop touch karne ki zarurat nahi):

| Jo bolo | Result |
|---------|--------|
| **"Jarvish"** | Jarvis active ho jaata hai |
| **"Hey Jarvis"** | Jarvis active ho jaata hai |
| **"Ok Jarvis"** | Jarvis active ho jaata hai |
| **"Hello Jarvis"** | Jarvis active ho jaata hai |

Activate hone par:
1. 🔔 Double beep sound aayegi
2. Browser mein Jarvis window khulegi
3. Jarvis bolega — *"Yes Sir, I am listening"*

### Step 2 — Command do
Ab koi bhi command bolo — Jarvis execute karega.

### Step 3 — Deactivate karo (optional)
Jab kaam ho jaaye:

| Jo bolo | Result |
|---------|--------|
| **"Stop"** | Jarvis so jaata hai |
| **"Sleep"** | Jarvis so jaata hai |
| **"Bye Jarvis"** | Jarvis so jaata hai |

> **Auto-Sleep:** Agar 30 seconds tak koi command nahi di toh Jarvis khud so jaata hai.

---

## 🗣️ Poori Command List

### 📱 Apps Kholna
```
open whatsapp         → WhatsApp Desktop khulega
open chrome           → Google Chrome khulega
open notepad          → Notepad khulega
open calculator       → Calculator khulega
open spotify          → Spotify khulega
open telegram         → Telegram khulega
open vscode           → VS Code khulega
open youtube          → YouTube browser mein khulega
open instagram        → Instagram browser mein khulega
open gmail            → Gmail browser mein khulega
open chatgpt          → ChatGPT browser mein khulega
open netflix          → Netflix browser mein khulega
```

### 📂 Folders Kholna
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
empty recycle bin     → Recycle Bin saaf karo
```

### 🪟 Window Control
```
minimize window       → Window chota karo
maximize window       → Window bada karo / Full Screen
close window          → Window band karo
switch window         → Alt+Tab (windows switch)
show desktop          → Saare windows minimize
snap left             → Window left side pe
snap right            → Window right side pe
task view             → Saare virtual desktops dikhao
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
next song             → Agli song
previous song         → Pichli song
stop music            → Media stop
volume up             → Volume badhao
volume down           → Volume ghato
mute                  → Mute/Unmute
```

### 🔆 Brightness
```
brightness up         → Screen roshan karo
brightness down       → Screen dim karo
set brightness to 70  → 70% brightness
```

### 📸 Screenshot
```
take screenshot       → Full screen screenshot Desktop pe save
screenshot            → Same as above
```

### ✍️ Text Type Karna
```
type hello world      → Cursor pe "hello world" type ho jaayega
write my name is John → "my name is John" type ho jaayega
```

### 📜 Scroll
```
scroll down           → Page neeche
scroll up             → Page upar
```

### 🔍 Search
```
search google for python tutorials   → Google pe search
search youtube for bollywood songs   → YouTube pe search
play <song> on youtube               → YouTube pe directly play
```

### 💬 WhatsApp / Contacts
```
send message to Rahul     → WhatsApp message bhejo
phone call to Mom         → Phone call
video call to Priya       → Video call
```
> Contacts ke liye `contacts.csv` mein naam aur number daalo.

### 💻 System
```
lock screen           → Laptop lock ho jaata hai
sleep                 → Laptop sleep mode
task manager          → Task Manager khulega
open settings         → Windows Settings
open run              → Win+R dialog
virtual keyboard      → On-screen keyboard
clipboard             → Clipboard history (Win+V)
```

### 🕐 Time / Date
```
what time is it       → Current time batayega
what is today's date  → Aaj ki date batayega
```

### 🤖 Chat
Koi bhi sawaal pucho jo upar list mein nahi hai — Jarvis AI chatbot se jawab dega.
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
├── run.bat                  ← Double-click se chalao (Windows)
├── requirements.txt         ← Python dependencies
├── contacts.csv             ← Apne contacts yahan daalo
├── jarvis.db                ← SQLite database (apps, websites, contacts)
│
├── engine/
│   ├── command.py           ← Voice command router (saari commands yahan route hoti hain)
│   ├── features.py          ← App/website open karna, YouTube, WhatsApp, ChatBot
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
│       ├── sample.py        ← Face samples capture karo
│       ├── trainer.py       ← Face model train karo
│       └── recoganize.py    ← Face authentication logic
│
└── www/                     ← Frontend (HTML/CSS/JS)
    └── index.html           ← Main Jarvis UI
```

---

## ⚙️ Configuration

### Contacts Add Karna
`contacts.csv` file mein apne contacts daalo:
```csv
name,mobile_no,email
Rahul,9876543210,rahul@gmail.com
Mom,8765432109,
```

### Nayi App/Website Add Karna
`jarvis.db` database mein ya directly `engine/init_db.py` mein:
```python
# Web command add karna
("mywebsite", "https://www.mywebsite.com"),

# Desktop app add karna — sys_command table mein
# name: "my app", path: "C:\\Path\\To\\App.exe"
```

### Assistant Name Change Karna
`engine/config.py` mein:
```python
ASSISTANT_NAME = "jarvis"  # yahan change karo
```

---

## 📦 Dependencies

| Package | Kaam |
|---------|------|
| `flask` | Web server |
| `flask-cors` | API CORS |
| `pyttsx3` | Text-to-Speech (awaaz) |
| `SpeechRecognition` | Microphone se voice sunna |
| `pyautogui` | Desktop automation |
| `pywhatkit` | YouTube, WhatsApp |
| `hugchat` | AI Chatbot |
| `psutil` | System stats (CPU/RAM) |
| `playsound` | Sound effects |

---

## ❓ Troubleshooting

### Jarvis "Jarvish" nahi sun raha
- Microphone check karo (Windows Settings → Sound → Input)
- Internet connection hona chahiye (Google Speech Recognition use hoti hai)
- Thoda zyada clearly bolo

### WhatsApp open nahi ho raha
- WhatsApp Desktop install hona chahiye (Microsoft Store se)
- Ya browser mein web.whatsapp.com khulega automatically

### TTS (awaaz) nahi aa rahi
- `pip install pyttsx3` run karo
- Windows SAPI5 voices installed honi chahiye

### Import errors aa rahe hain
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
