"""
Reads text out of whatever window currently has focus.

Primary method: Windows UI Automation (the `uiautomation` package) walks the
focused window's accessibility tree and pulls Name/Value text out of it.
This works well for most native Win32, WPF, UWP, and browser apps.

Fallback: clipboard contents, for apps whose accessibility tree is empty or
unsupported (some games, canvas-rendered apps, etc).

Note: OCR (screenshot -> text) is NOT included in this v1 to keep setup
simple (it needs a separate Tesseract binary install). See README for how
to add it later if an app gives you nothing useful through either method.
"""
import pyperclip

try:
    import uiautomation as auto
except Exception:
    auto = None


def get_active_window_text(max_depth=6, max_elements=400):
    if auto is None:
        return ""
    try:
        focused = auto.GetFocusedControl()
        if focused is None:
            return ""
        top = focused.GetTopLevelControl() or focused

        texts = []
        seen = set()

        def walk(control, depth):
            if depth > max_depth or len(texts) >= max_elements:
                return
            try:
                name = control.Name
                if name and name.strip() and name not in seen:
                    seen.add(name)
                    texts.append(name.strip())
            except Exception:
                pass
            try:
                value_pattern = control.GetValuePattern()
                if value_pattern:
                    val = value_pattern.Value
                    if val and val.strip() and val not in seen:
                        seen.add(val)
                        texts.append(val.strip())
            except Exception:
                pass
            try:
                for child in control.GetChildren():
                    walk(child, depth + 1)
            except Exception:
                pass

        walk(top, 0)
        return "\n".join(texts)
    except Exception:
        return ""


def get_clipboard_text():
    try:
        return pyperclip.paste() or ""
    except Exception:
        return ""


def capture_context():
    """Best-effort capture: try the accessibility tree first, fall back to clipboard."""
    text = get_active_window_text()
    if not text.strip():
        text = get_clipboard_text()
    # keep prompts/requests reasonable -- trim very long captures
    return text[:8000]
