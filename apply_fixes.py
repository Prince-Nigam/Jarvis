"""
apply_fixes.py — command.py ke saare issues fix karo
Run: python apply_fixes.py
"""
import re

with open("engine/command.py", encoding="utf-8") as f:
    src = f.read()

original = src
fixes_applied = []

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — WINDOW MANAGEMENT: response set hai but speak() nahi
# Har window branch mein _spoken = True add karo
# ─────────────────────────────────────────────────────────────────────────────

window_responses = [
    'response = "Window minimized"',
    'response = "Window maximized"',
    'response = "Fullscreen toggled"',
    'response = "Window closed"',
    'response = "Switching window"',
    'response = "Showing desktop"',
    'response = "All windows minimized"',
    'response = "All windows restored"',
    'response = "Other windows minimized"',
    'response = "Snapped to left"',
    'response = "Snapped to right"',
    'response = "Snapped up"',
    'response = "Snapped down"',
    'response = "Task view opened"',
    'response = "Project menu opened"',
    'response = "Window menu opened"',
    'response = "Arranging windows"',
    'response = "Windows explorer restarted"',
    # mouse
    'response = "Left clicked"',
    'response = "Right clicked"',
    'response = "Double clicked"',
    'response = "Middle clicked"',
    'response = "Mouse centered"',
    # media
    'response = "Play/Pause toggled"',
    'response = "Media paused"',
    'response = "Media playing"',
    'response = "Next track"',
    'response = "Previous track"',
    'response = "Media stopped"',
    # text editing
    'response = "Bold applied"',
    'response = "Italic applied"',
    'response = "Underline applied"',
    'response = "Strikethrough applied"',
    'response = "Find and replace opened"',
    'response = "Print dialog opened"',
    'response = "Rename mode"',
    'response = "New document"',
    'response = "Open file dialog"',
    'response = "Hard refresh done"',
    'response = "Tab restored"',
    'response = "All tabs closed"',
    'response = "Next tab"',
    'response = "Previous tab"',
    'response = "Address bar focused"',
    'response = "History opened"',
    'response = "Bookmarks opened"',
    'response = "Downloads opened"',
    'response = "Developer tools opened"',
    'response = "Incognito window opened"',
    'response = "Private window opened"',
    'response = "Bookmark toggled"',
    # print/screen
    'response = "Print screen captured"',
    'response = "Snipping tool activated"',
    'response = "Screenshot saved to Desktop"',
    'response = "Emoji panel opened"',
    'response = "Dictation mode started"',
    'response = "Game bar opened"',
    'response = "Quick link menu opened"',
    'response = "Task manager opened"',
    # keyboard
    'response = "Copied"',
    'response = "Pasted"',
    'response = "Cut"',
    'response = "Undo done"',
    'response = "Redo done"',
    'response = "Selected all"',
    'response = "Saved"',
    'response = "New tab opened"',
    'response = "Tab closed"',
    'response = "Refreshed"',
    'response = "Going back"',
    'response = "Going forward"',
    'response = "Zoomed in"',
    'response = "Zoomed out"',
    'response = "Find opened"',
    'response = "New window opened"',
    'response = "Enter pressed"',
    'response = "Escaped"',
    'response = "Deleted"',
    'response = "Backspace"',
    # scroll
    'response = "Scrolled down"',
    'response = "Scrolled up"',
    'response = "Scrolled left"',
    'response = "Scrolled right"',
    'response = "Scrolled to top"',
    'response = "Scrolled to bottom"',
    # system actions
    'response = "Screen locked"',
    'response = "Signing out"',
    'response = "Going to sleep"',
    'response = "Hibernating system"',
    'response = "Restarting in 10 seconds"',
    'response = "Shutting down in 10 seconds"',
    'response = "Shutdown cancelled"',
    'response = "Opening Task Manager"',
    'response = "Device manager opened"',
    'response = "Disk cleanup opened"',
    'response = "Disk defragmenter opened"',
    'response = "Event viewer opened"',
    'response = "Registry editor opened"',
    'response = "Services opened"',
    'response = "System properties opened"',
    'response = "Sticky notes opened"',
    'response = "Steps recorder opened"',
    'response = "Character map opened"',
    'response = "Narrator started"',
    'response = "WordPad opened"',
    'response = "Display settings opened"',
    'response = "Sound settings opened"',
    'response = "Mouse settings opened"',
    'response = "Network settings opened"',
    'response = "Power settings opened"',
    'response = "Date/Time settings opened"',
    'response = "Firewall settings opened"',
    'response = "Opening Settings"',
    'response = "Run dialog opened"',
    'response = "Search opened"',
    'response = "Notification center opened"',
    'response = "Clipboard history opened"',
    'response = "Virtual keyboard opened"',
    'response = "Magnifier opened"',
    'response = "Brightness increased"',
    'response = "Brightness decreased"',
    # folders
    'response = "Opening Downloads"',
    'response = "Opening Desktop"',
    'response = "Opening Documents"',
    'response = "Opening Pictures"',
    'response = "Opening Music"',
    'response = "Opening Videos"',
    'response = "Opening C Drive"',
    'response = "Opening D Drive"',
    'response = "Opening E Drive"',
    'response = "Opening This PC"',
    'response = "Opening Recycle Bin"',
    'response = "Recycle bin emptied"',
    # file ops
    'response = "Moved to recycle bin"',
    'response = "Item permanently deleted"',
    'response = "File path copied"',
    # cmd/terminal
    'response = "Command prompt opened"',
    'response = "PowerShell opened"',
    'response = "Windows terminal opened"',
    'response = "Temp files cleaned"',
    # search
    'response = "Opening GitHub"',
    'response = "Opening Quora"',
    # type/translate
    'response = "Moved to recycle bin"',
]

count = 0
for rline in window_responses:
    # Only add _spoken = True if it's not already there on the next line
    pattern = re.compile(
        r'(' + re.escape(rline) + r')(?!\s*\n\s*_spoken\s*=\s*True)',
        re.MULTILINE
    )
    new_line = rline + '\n            _spoken = True'
    if rline in src and '_spoken = True' not in src[src.find(rline):src.find(rline)+60]:
        src = src.replace(rline, new_line, 1)
        count += 1

fixes_applied.append(f"Issue 1+2: Added _spoken=True to {count} response lines")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3 — 'chalao' CONFLICT
# "kholo/chalao" branch mein "chalao" YouTube commands steal karta hai
# Fix: "chalao" ko is branch se hata do — YouTube branch already handle karta hai
# ─────────────────────────────────────────────────────────────────────────────

old_kholo = 'elif "kholo" in query or "chalao" in query or "shuru karo" in query or "start karo" in query:'
new_kholo = 'elif "kholo" in query or "shuru karo" in query or "start karo" in query:'
if old_kholo in src:
    src = src.replace(old_kholo, new_kholo, 1)
    fixes_applied.append("Issue 3: Removed 'chalao' from kholo branch — YouTube won't be stolen")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4 — Duplicate YouTube play comment block
# ─────────────────────────────────────────────────────────────────────────────
dup_comment = """        # ══════════════════════════════════════════════════════════
        #  YOUTUBE PLAY (check before generic "open")
        # ══════════════════════════════════════════════════════════

        # ══════════════════════════════════════════════════════════
        #  YOUTUBE PLAY — MUST be BEFORE generic "open" branch"""

fixed_comment = """        # ══════════════════════════════════════════════════════════
        #  YOUTUBE PLAY — MUST be BEFORE generic "open" branch"""

if dup_comment in src:
    src = src.replace(dup_comment, fixed_comment, 1)
    fixes_applied.append("Issue 4: Removed duplicate YouTube comment block")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 5 — "stop"/"pause" branch too broad
# "stop" alone catches too many unrelated queries
# Fix: add more specific context check
# ─────────────────────────────────────────────────────────────────────────────

old_stop = '''        elif any(k in query for k in ("stop", "pause", "ruko", "band karo music", "music band karo", "video band karo", "music roko", "video roko")):
            # "stop" / "pause" — youtube/spotify wala jo bhi chal raha ho
            dc.media_play_pause()
            response = "Media paused"'''

new_stop = '''        elif any(k in query for k in ("pause music", "ruko music", "band karo music", "music band karo", "video band karo", "music roko", "video roko", "pause karo", "music pause")) or (any(k in query for k in ("stop", "pause", "ruko")) and any(k in query for k in ("music", "song", "video", "gaana", "youtube", "media", "play"))):
            # "stop/pause" — sirf tab jab music/video context ho
            dc.media_play_pause()
            response = "Media paused"'''

if old_stop in src:
    src = src.replace(old_stop, new_stop, 1)
    fixes_applied.append("Issue 5: Fixed too-broad stop/pause branch — now requires music/video context")

# ─────────────────────────────────────────────────────────────────────────────
# Also fix "type" and "write" branches — _spoken needed
# ─────────────────────────────────────────────────────────────────────────────
for old_t, new_t in [
    ('response = f"Typed: {text_to_type}"\n                    dc.type_text(text_to_type)\n',
     'response = f"Typed: {text_to_type}"\n                    dc.type_text(text_to_type)\n'),
    ('response = f"Folder {nm} created"', 'response = f"Folder {nm} created"\n            _spoken = True'),
    ('response = f"File {nm} created"', 'response = f"File {nm} created"\n            _spoken = True'),
    ('response = "New folder created on Desktop"', 'response = "New folder created on Desktop"\n                _spoken = True'),
    ('response = "New text file created on Desktop"', 'response = "New text file created on Desktop"\n                _spoken = True'),
    ('response = f"Brightness set to {nums[0]}%"', 'response = f"Brightness set to {nums[0]}%"\n                _spoken = True'),
]:
    if old_t in src and '_spoken' not in src[src.find(old_t):src.find(old_t)+80]:
        src = src.replace(old_t, new_t, 1)

# Search responses — add _spoken
for sterm in [
    'response = f"Searching Google for {term}"',
    'response = f"Searching Bing for {term}"',
    'response = f"Searching DuckDuckGo for {term}"',
    'response = f"Searching YouTube for {term}"',
    'response = f"Searching Wikipedia for {term}"',
    'response = f"Searching StackOverflow for {term}"',
    'response = f"Searching Quora for {term}"',
    'response = f"Searching GitHub for {term}"',
    'response = f"Searching Amazon for {term}"',
    'response = f"Searching Flipkart for {term}"',
    'response = f"Searching Maps for {term}"',
    'response = f"Searching Gmail for {term}"',
    'response = f"Searching Google Scholar for {term}"',
]:
    # Add _spoken after first occurrence if not already there
    idx = src.find(sterm)
    if idx != -1 and '_spoken' not in src[idx:idx+60]:
        src = src.replace(sterm, sterm + '\n                _spoken = True', 1)

fixes_applied.append("Bonus: Added _spoken=True to search, folder, file creation responses")

# ─────────────────────────────────────────────────────────────────────────────
# Write back
# ─────────────────────────────────────────────────────────────────────────────
with open("engine/command.py", "w", encoding="utf-8") as f:
    f.write(src)

print("\n✅ Fixes applied:")
for fix in fixes_applied:
    print(f"   • {fix}")

# Verify syntax
import ast
try:
    ast.parse(src)
    print("\n✅ Syntax OK — no errors")
except SyntaxError as e:
    print(f"\n❌ Syntax ERROR: {e}")
    # Restore original
    with open("engine/command.py", "w", encoding="utf-8") as f:
        f.write(original)
    print("   ↩️  Original restored")
