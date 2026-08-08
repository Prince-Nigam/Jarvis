import sys
sys.path.insert(0, '.')

from engine.hotword import (
    WAKE_WORDS, SLEEP_WORDS,
    _contains_wake_word, _contains_sleep_word,
    start, stop, is_active, force_activate,
    IDLE_AUTO_SLEEP_SECONDS as AUTO_SLEEP_SECONDS
)

print("=" * 50)
print("  HOTWORD MODULE TEST")
print("=" * 50)

print(f"\nWake words ({len(WAKE_WORDS)}):")
for w in WAKE_WORDS:
    print(f"  - {w}")

print(f"\nSleep words ({len(SLEEP_WORDS)}):")
for w in SLEEP_WORDS:
    print(f"  - {w}")

print(f"\nAuto-sleep after: {AUTO_SLEEP_SECONDS} seconds")

print("\n--- Wake word detection tests ---")
wake_tests = [
    ("wakeup jarvish", True),         # correct wake phrase
    ("wake up jarvish", True),        # spaced variant
    ("wake up jarvis", True),         # jarvis variant
    ("wakeup jarvis", True),          # compact jarvis variant
    ("jarvish", False),               # naam akela — sirf name trigger hai, wake word nahi
    ("hey jarvish", False),           # hey + naam — wake word nahi (no "wakeup" prefix)
    ("open whatsapp", False),         # wake word nahi hai
    ("hello", False),                 # random word
]
all_ok = True
for text, expected in wake_tests:
    result = _contains_wake_word(text)
    status = "OK" if result == expected else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] '{text}' -> {result} (expected {expected})")

print("\n--- Sleep word detection tests ---")
sleep_tests = [
    ("stop", True),
    ("sleep", True),
    ("go to sleep", True),
    ("bye jarvis", True),
    ("jarvish stop", True),
    ("open notepad", False),
]
for text, expected in sleep_tests:
    result = _contains_sleep_word(text)
    status = "OK" if result == expected else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] '{text}' -> {result} (expected {expected})")

print("\n--- is_active() initial state ---")
print(f"  is_active() = {is_active()} (expected False)")
if is_active():
    all_ok = False

print()
if all_ok:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED!")
