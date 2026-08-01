import os

# ── Assistant name ─────────────────────────────────────────────────────────────
ASSISTANT_NAME = "jarvis"

# ── Porcupine hotword detection ────────────────────────────────────────────────
# Get a free key at https://console.picovoice.ai/ and set it as an env variable:
#   Windows:  setx PORCUPINE_ACCESS_KEY "your-key-here"
#   Or add it to a .env file and load with python-dotenv
PORCUPINE_ACCESS_KEY = os.environ.get("PORCUPINE_ACCESS_KEY", "")
