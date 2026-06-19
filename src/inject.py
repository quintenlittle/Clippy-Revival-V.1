"""
Writes text into whatever window currently has focus, by putting it on the
clipboard and sending Ctrl+V. This is far more reliable across different
apps than simulating individual keystrokes (handles unicode, emoji,
newlines, and doesn't get outrun by the target app's input handling).

Note: this can only paste into windows running at the same privilege level
as Clippy (or lower). To paste into an elevated/admin window, run Clippy
itself as admin too -- this is a Windows security boundary (UIPI), not a
bug in this script.
"""
import time

import keyboard
import pyperclip


def write_text_to_active_app(text, restore_clipboard=True):
    if not text:
        return

    previous = None
    if restore_clipboard:
        try:
            previous = pyperclip.paste()
        except Exception:
            previous = None

    pyperclip.copy(text)
    time.sleep(0.05)
    keyboard.send("ctrl+v")
    time.sleep(0.05)

    if restore_clipboard and previous is not None:
        time.sleep(0.2)
        try:
            pyperclip.copy(previous)
        except Exception:
            pass
