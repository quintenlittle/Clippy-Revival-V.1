"""
Path helpers that work both when running from source (python src/main.py)
and when running as a PyInstaller-frozen .exe.
"""
import os
import sys


def get_base_dir():
    """Directory for writable/persistent files (config.json, clippy.log).

    - Frozen (.exe) mode: the folder containing the .exe, so settings
      survive next to wherever you put Clippy.exe (e.g. the startup folder).
    - Source mode: the project root (parent of src/).
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative_path):
    """Path for bundled, read-only resources (assets/avatar.png, etc).

    - Frozen mode: PyInstaller's extraction directory (sys._MEIPASS).
    - Source mode: the project root.
    """
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)
