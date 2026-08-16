import pyttsx3
import sys

text = sys.argv[1] if len(sys.argv) > 1 else "Hello Sir can you hear me"
print(f"Speaking: {text}")
try:
    e = pyttsx3.init("sapi5")
    voices = e.getProperty("voices")
    print(f"Voices found: {len(voices)}")
    e.setProperty("voice", voices[0].id)
    e.setProperty("rate", 165)
    e.setProperty("volume", 1.0)
    e.say(text)
    e.runAndWait()
    e.stop()
    print("Done")
except Exception as ex:
    print(f"Error: {ex}")
