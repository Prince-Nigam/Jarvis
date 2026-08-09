import os
import re
import time


def extract_yt_term(command):
    """
    Extract song/video name from YouTube play command.
    Returns clean song name or None.
    """
    if not command:
        return None

    cmd = command.strip()

    # Pattern 1: "play X on youtube"
    m = re.search(r'play\s+(.+?)\s+on\s+youtube', cmd, re.IGNORECASE)
    if m:
        t = m.group(1).strip()
        if t:
            return t

    # Pattern 2: "open youtube and play X" / "open youtube play X"
    m = re.search(r'(?:open\s+)?youtube\s+(?:and\s+)?play\s+(?:the\s+song\s+)?(.+)', cmd, re.IGNORECASE)
    if m:
        t = m.group(1).strip()
        if t:
            return t

    # Pattern 3: "play X" (no youtube mentioned)
    m = re.search(r'^play\s+(.+)$', cmd, re.IGNORECASE)
    if m:
        t = m.group(1).strip()
        # remove trailing "on youtube" if present
        t = re.sub(r'\s+on\s+youtube\s*$', '', t, flags=re.IGNORECASE).strip()
        if t:
            return t

    # Pattern 4: strip all youtube/open/play noise and return what's left
    cleaned = cmd
    for noise in ("open youtube and play", "open youtube play", "on youtube",
                  "youtube pe", "youtube par", "youtube mein", "play on youtube",
                  "youtube", "open", "play the song", "play karo", "the song",
                  "chalao", "chala do", "laga do", "and play", "play"):
        cleaned = re.sub(r'\b' + re.escape(noise) + r'\b', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = ' '.join(cleaned.split()).strip()

    if cleaned and len(cleaned) > 1:
        return cleaned

    return None


def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string



# key events like receive call, stop call, go back
def keyEvent(key_code):
    command =  f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)

# Tap event used to tap anywhere on screen
def tapEvents(x, y):
    command =  f'adb shell input tap {x} {y}'
    os.system(command)
    time.sleep(1)

# Input Event is used to insert text in mobile
def adbInput(message):
    command =  f'adb shell input text "{message}"'
    os.system(command)
    time.sleep(1)

# to go complete back (sends back keyevent 'steps' times)
def goback(steps=4):
    for _ in range(steps):
        keyEvent(4)  # keycode 4 = Android BACK button

# To replace space in string with %s for complete message send
def replace_spaces_with_percent_s(input_string):
    """Replace spaces with %20 for proper URL/ADB encoding."""
    return input_string.replace(' ', '%20')