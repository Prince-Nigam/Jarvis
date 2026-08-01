# JARVIS - How to Use

## PC ON hone par AUTO-START
Jarvis already Windows Startup mein add ho gaya hai.
Ab jab bhi PC on karoge, Jarvis background mein automatically start ho jayega.

Agar manually remove karna ho:
```
python install_startup.py uninstall
```

---

## WAKE WORD - "Hey Jarvis"

Jarvis background mein microphone listen karta rahega.
Inme se kuch bhi bolne par Jarvis open ho jayega:

| Bol sako | Result |
|----------|--------|
| **"Hey Jarvis"** | Jarvis opens + listens |
| **"Wake Jarvis"** | Jarvis opens + listens |
| **"Jarvis"** | Jarvis opens + listens |
| **"Ok Jarvis"** | Jarvis opens + listens |

Wake word detect hone par:
1. Do beep sounds sunai denge
2. Browser mein Jarvis khul jayega
3. Jarvis bolega "Yes Sir, how can I help you?"
4. Aap command bol sakte ho

---

## COMMANDS - Kya kya bol sakte ho

### Apps & Websites
```
open youtube
open google
open chrome
open notepad
open calculator
open whatsapp
play <song name> on youtube
```

### System Info
```
what time is it
what is today's date
```

### Smart Commands
```
hello / hi
what is your name
tell me a joke
take screenshot
volume up / volume down / mute
```

### WhatsApp / Calls (contacts.csv mein contact hona chahiye)
```
send message to <name>
phone call to <name>
video call to <name>
```

### General Chat
Kuch bhi pucho jo upar nahi hai — chatbot handle karega.

---

## MANUALLY CHALANA

Double-click `run.bat` — console window ke saath chalega.

Ya terminal mein:
```
python run.py
```

Phir browser mein jao: http://localhost:8000
