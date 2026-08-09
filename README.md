# J.A.R.V.I.S — Personal Desktop Voice Assistant

> **Just A Rather Very Intelligent System**  
> Apna laptop sirf awaaz se control karo — bina haath lagaye!

---

## Jarvis kya hai?

Jarvis ek Python-based personal voice assistant hai jo aapko **sirf voice se apna pura laptop control** karne deta hai. Bas **"Wakeup Jarvish"** bolo — aur phir **"Jarvish"** bol ke koi bhi command do.

**Kya kya kar sakta hai:**
- Apps aur websites open karna (WhatsApp, Chrome, YouTube, Instagram, etc.)
- Koi bhi song seedha YouTube pe play karna
- System aur song volume alag alag control karna
- Windows minimize, maximize, snap, close karna
- Screenshots lena
- Text type karna
- Media control (play/pause/next/previous)
- Google, YouTube, Wikipedia search karna
- WhatsApp messages aur calls karna
- Face authentication se unlock karna
- **Smart Learning** — jo bhi website ya song ek baar bologe, Jarvis yaad rakh lega

---

## Quick Start — Sirf 3 Steps

### Step 1 — Python Install karo
Python 3.10 ya usse upar chahiye.  
Download: https://www.python.org/downloads/

### Step 2 — Dependencies Install karo
```bash
pip install -r requirements.txt
```

### Step 3 — Chalu karo
```bash
python run.py
```
Ya `run.bat` double-click karo.

Browser mein Jarvis khulega: **http://localhost:8000**

---

## Kaise Use Karna Hai

### Step 1 — Wake Word Bolo
Kuch bhi chhune ki zaroorat nahi:

| Bologe | Result |
|--------|--------|
| **"Wakeup Jarvish"** | Jarvis deep sleep se online hoga |
| **"Hey Jarvis"** | Jarvis active hoga |
| **"Ok Jarvish"** | Jarvis active hoga |

Activate hone par:
1. Beep sound bajega
2. Browser window apne aap khulegi
3. Jarvis bolega — *"Jarvis online. Jarvish bol ke command do."*

### Step 2 — Command do
**"Jarvish"** bolo — Jarvis bolega **"Haan Sir, boliye."**  
Ab apna command bolo — Jarvis execute karega aur bolega kya kiya.

**Ya seedha bolo:** `"Jarvish open chrome"` — ek hi baar mein.

### Step 3 — Continuous Commands
Ek command ke baad Jarvis **wapas sun ne ke liye ready** rehta hai.  
Dobara "Jarvish" bolne ki zaroorat nahi.

### Step 4 — Sleep karo (optional)
| Bologe | Result |
|--------|--------|
| **"Jarvish shutdown"** | Jarvis so jaayega |
| **"Jarvish bye"** | Jarvis so jaayega |

> **Auto-Sleep:** 2 minute tak koi command nahi di to Jarvis apne aap so jaata hai.

---

## Poori Command List

### Apps Open karo
```
open whatsapp          → WhatsApp Desktop khulegaa
open chrome            → Google Chrome khulega
open notepad           → Notepad khulega
open calculator        → Calculator khulega
open spotify           → Spotify khulega
open telegram          → Telegram khulega
open vscode            → VS Code khulega
open youtube           → YouTube browser mein khulega
open instagram         → Instagram browser mein khulega
open gmail             → Gmail browser mein khulega
open chatgpt           → ChatGPT browser mein khulega
open netflix           → Netflix browser mein khulega
open whatsapp web      → WhatsApp Web khulega
```
> 200+ apps aur websites supported hain.

### YouTube pe Song Play karo
```
play believer                        → YouTube pe believer play karega
play arijit singh                    → Arijit Singh ka song play karega
open youtube play shape of you       → YouTube pe shape of you play karega
open youtube and play kesariya       → Seedha kesariya play karega
play believer on youtube             → Believer play karega
kesariya bajao                       → YouTube pe kesariya play
tere bina chala do                   → Tere Bina play karega
```
> Agar sirf "open youtube play the song" bola to Jarvis poochhe ga —  
> **"Kaunsa song chahiye Sir? Naam batao."**

### Song Volume vs System Volume
```
song volume up          → YouTube/browser pe jo chal raha hai uska volume badhao
song volume down        → YouTube player ka volume kam karo
gaane ki awaaz badhao   → Song ka volume up
gaane ka volume kam karo → Song ka volume down

volume full karo        → Laptop/PC ki system volume 100% kar do
system volume full      → System volume max
volume up               → System volume thoda badhao
volume down             → System volume thoda kam karo
volume zero             → System volume zero
mute                    → Mute/Unmute
```

### Folders Open karo
```
open downloads    → Downloads folder
open documents    → Documents folder
open desktop      → Desktop folder
open pictures     → Pictures folder
open music        → Music folder
open videos       → Videos folder
open c drive      → C:\ drive
open d drive      → D:\ drive
this pc           → File Explorer
recycle bin       → Recycle Bin
empty recycle bin → Recycle Bin empty karo
```

### Window Control
```
minimize window       → Window minimize karo
maximize window       → Window maximize karo
close window          → Window band karo
switch window         → Alt+Tab (windows switch)
show desktop          → Sab windows minimize karo
snap left             → Window ko left side snap karo
snap right            → Window ko right side snap karo
full screen           → F11 fullscreen
task view             → Sabhi virtual desktops dikhao
split screen          → Windows arrange karo
```

### Keyboard Shortcuts
```
copy              → Ctrl+C
paste             → Ctrl+V
cut               → Ctrl+X
undo              → Ctrl+Z
redo              → Ctrl+Y
select all        → Ctrl+A
save file         → Ctrl+S
new tab           → Ctrl+T
close tab         → Ctrl+W
refresh           → F5
go back           → Alt+Left
go forward        → Alt+Right
zoom in           → Ctrl++
zoom out          → Ctrl+-
find on page      → Ctrl+F
new window        → Ctrl+N
press enter       → Enter
press escape      → Escape
```

### Media Control
```
play music        → Play/Pause toggle
pause music       → Play/Pause toggle
next song         → Agla song
previous song     → Pichla song
stop music        → Media stop
```

### Brightness
```
brightness up           → Screen bright karo
brightness down         → Screen dim karo
set brightness to 70    → Brightness 70% set karo
```

### Screenshot
```
take screenshot    → Desktop pe screenshot save karo
screenshot         → Same
snipping tool      → Snipping tool kholo (partial screenshot)
```

### Text Type karo
```
type hello world       → "hello world" cursor pe type karega
write my name is John  → "my name is John" type karega
```

### Scroll
```
scroll down       → Page neeche scroll karo
scroll up         → Page upar scroll karo
scroll to top     → Page ke shuru mein jao
scroll to bottom  → Page ke end mein jao
```

### Search
```
search google for python tutorials     → Google pe search
search youtube for bollywood songs     → YouTube pe search
search wikipedia for machine learning  → Wikipedia pe search
search amazon for headphones           → Amazon pe search
```

### Browser Shortcuts
```
new tab              → Naya tab kholo
close tab            → Tab band karo
incognito            → Incognito window kholo
developer tools      → Dev tools kholo
bookmarks            → Bookmarks kholo
history              → History kholo
go back              → Peeche jao
go forward           → Aage jao
```

### WhatsApp / Contacts
```
send message to Rahul    → WhatsApp message bhejo
phone call to Mom        → Phone call karo
video call to Priya      → Video call karo
```
> Contacts add karne ke liye `contacts.csv` mein naam aur number daalo.

### System
```
lock screen       → Laptop lock karo
sleep             → Sleep mode
task manager      → Task Manager kholo
open settings     → Windows Settings
open run          → Win+R dialog
virtual keyboard  → On-screen keyboard
clipboard         → Clipboard history (Win+V)
restart           → System restart (10 sec mein)
shutdown          → System shutdown (10 sec mein)
battery status    → Battery percentage batao
ip address        → IP address batao
show wifi         → Saved WiFi networks list
```

### Time / Date
```
time batao         → Abhi ka time batao
date batao         → Aaj ki date batao
aaj kaun sa din    → Aaj ka din batao
```

### Smart Learning (Auto Memory)
Jarvis jo websites aur songs aap ek baar kholo, yaad rakh leta hai:
```
# Pehli baar:
open instagram        → Instagram khulega  [LEARN: 'instagram' store hua]

# Doosri baar:
instagram             → Seedha open hoga (bina "open" ke bhi)

# Songs bhi:
play believer         → YouTube pe play  [LEARN: 'believer' store hua]
believer              → Seedha play (agle baar)
```
Activity Log mein `Remembered:` dikhega jab memory se execute ho.

### Chat / AI
Jo command list mein nahi hai, woh AI chatbot handle karta hai:
```
who are you
tell me a joke
how are you
thank you
kya kar sakte ho
```

---

## Project Structure

```
Jarvis/
│
├── main.py                  ← Flask server + API endpoints + Event log
├── run.py                   ← Entry point (python run.py)
├── run.bat                  ← Windows double-click launcher
├── requirements.txt         ← Python dependencies
├── contacts.csv             ← Apne contacts yahan add karo
├── Database.db              ← SQLite DB (apps, websites, contacts, learned commands)
│
├── engine/
│   ├── command.py           ← Voice command router + TTS (win32com SAPI5) + Smart Learning
│   ├── features.py          ← Apps/websites open karo, YouTube play, WhatsApp, ChatBot
│   ├── desktop_control.py   ← Window, keyboard, media, volume, brightness control
│   ├── hotword.py           ← Always-on wake word listener ("Wakeup Jarvish")
│   ├── helper.py            ← Utility functions (YouTube term extract, etc.)
│   ├── config.py            ← Configuration (assistant name)
│   ├── init_db.py           ← Database setup (sys_command, web_command, learned_commands)
│   ├── system_info.py       ← CPU, RAM, Disk, Battery stats
│   ├── window_manager.py    ← Browser window management
│   ├── authenticator.py     ← Face authentication
│   │
│   └── auth/
│       ├── sample.py        ← Face samples capture karo
│       ├── trainer.py       ← Face model train karo
│       └── recoganize.py    ← Face recognition logic
│
└── www/                     ← Frontend (HTML/CSS/JS)
    ├── index.html           ← Main Jarvis UI
    ├── main.js              ← Command handling + Activity Log polling
    ├── controller.js        ← Boot sequence, mic button, chat
    ├── style.css            ← Jarvis UI styling
    └── assets/              ← Images, sounds, icons
```

---

## Configuration

### Contacts Add karo
`contacts.csv` mein naam aur number daalo:
```csv
name,mobile_no,email
Rahul,9876543210,rahul@gmail.com
Mom,8765432109,
```

### Naya App ya Website Add karo
`Database.db` mein ya `engine/init_db.py` mein:
```python
# Web command add karo
("meri site", "https://www.merisite.com"),

# Desktop app add karo (sys_command table mein)
# name: "my app", path: "C:\\Path\\To\\App.exe"
```

### Assistant ka Naam Badlo
`engine/config.py` mein:
```python
ASSISTANT_NAME = "jarvis"   # yahan badlo
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web server (backend) |
| `flask-cors` | API CORS support |
| `win32com` (pywin32) | TTS — Windows SAPI5 voice (primary) |
| `pyttsx3` | TTS fallback |
| `SpeechRecognition` | Mic se voice sun na |
| `PyAudio` | Microphone input |
| `pyautogui` | Desktop automation |
| `psutil` | CPU/RAM/Battery stats |
| `opencv-contrib-python` | Face authentication |
| `Pillow` | Image processing |
| `pygame` | Sound effects |
| `youtube-search` | YouTube pe song search aur play |
| `requests` | HTTP requests |
| `edge-tts` | Neural voice TTS (optional) |

### Requirements install karo:
```bash
pip install -r requirements.txt
pip install pywin32
pip install youtube-search
```

---

## Troubleshooting

### "Wakeup Jarvish" kaam nahi kar raha
- Microphone check karo: Windows Settings → Sound → Input
- Internet connection chahiye (Google Speech Recognition use hota hai)
- Thoda saaf aur dheere bolo

### YouTube pe song play nahi ho raha
```bash
pip install youtube-search
```
Phir server restart karo: `python run.py`

### Jarvis bolta nahi (koi awaaz nahi)
- `pywin32` install karo: `pip install pywin32`
- Windows SAPI5 voices installed honi chahiye
- Speaker ya headphone connected hona chahiye

### Import errors aa rahe hain
```bash
pip install -r requirements.txt
pip install pywin32 youtube-search
```

### Activity Log mein kuch nahi dikh raha
- Browser mein `http://localhost:8000` refresh karo
- Server chal raha hona chahiye (`python run.py`)

---

## Face Authentication Setup

```bash
# Step 1: Face samples capture karo
python engine/auth/sample.py

# Step 2: Model train karo
python engine/auth/trainer.py

# Step 3: Jarvis automatically face verify karega startup pe
```

---

## Tech Stack

- **Python 3.10+** — Core logic
- **Flask** — REST API backend
- **HTML / CSS / JavaScript** — Jarvis UI (frontend)
- **SQLite** — Local database (apps, contacts, learned commands)
- **Google Speech Recognition** — Voice to text
- **win32com SAPI5** — Text to voice (Windows native)
- **PyAutoGUI** — Desktop automation
- **Win32 API** — Window management
- **youtube-search** — YouTube video search aur direct play

---

*Jarvis — aapka personal AI assistant*
