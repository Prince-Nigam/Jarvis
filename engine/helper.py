import os
import re
import time


def extract_yt_term(command):
    """
    Extract song/video name from YouTube play command.
    Handles multiple patterns:
      "play X on youtube"
      "play X"
      "X on youtube"
    """
    if not command:
        return None

    # Pattern 1: "play X on youtube"
    match = re.search(r'play\s+(.*?)\s+on\s+youtube', command, re.IGNORECASE)
    if match and match.group(1).strip():
        return match.group(1).strip()

    # Pattern 2: "play X" (no "on youtube")
    match = re.search(r'^play\s+(.+)$', command.strip(), re.IGNORECASE)
    if match and match.group(1).strip():
        return match.group(1).strip()

    # Pattern 3: remove "on youtube" and return rest
    cleaned = re.sub(r'\s*on\s+youtube\s*', '', command, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s*youtube\s*', '', cleaned, flags=re.IGNORECASE).strip()
    if cleaned:
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