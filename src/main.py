"""
Entry point. PyInstaller targets this file directly.
Wraps startup in a try/except that logs to clippy.log next to the exe,
since --windowed mode has no console to print errors to.
"""
import logging
import os
import sys

from paths import get_base_dir

logging.basicConfig(
    filename=os.path.join(get_base_dir(), "clippy.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def main():
    try:
        from overlay import main as run_overlay
        run_overlay()
    except Exception:
        logging.exception("Fatal error on startup")
        raise


if __name__ == "__main__":
    main()
