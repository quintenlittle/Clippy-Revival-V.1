"""
Sets an API key in your local config.json interactively. The key is typed
with hidden input (like a sudo password prompt) and written straight to
config.json on disk -- it never goes anywhere else.
"""
import getpass
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from config import load_config, save_config  # noqa: E402

BACKENDS = {
    "1": "anthropic",
    "2": "openai",
    "3": "gemini",
}


def main():
    print("Which backend's API key do you want to set?")
    print("  1) Anthropic (Claude)")
    print("  2) OpenAI (GPT / Codex)")
    print("  3) Gemini")
    choice = input("Enter 1, 2, or 3: ").strip()
    backend = BACKENDS.get(choice)
    if not backend:
        print("Not a valid choice -- exiting, nothing changed.")
        return

    key = getpass.getpass(f"Paste your {backend} API key (hidden, won't echo to screen): ").strip()
    if not key:
        print("No key entered -- exiting, nothing changed.")
        return

    cfg = load_config()
    cfg[backend]["api_key"] = key

    make_active = input(f"Make '{backend}' the active backend now? [Y/n]: ").strip().lower()
    if make_active in ("", "y", "yes"):
        cfg["active_backend"] = backend

    save_config(cfg)
    print(f"\nSaved. {backend}.api_key updated in config.json.")
    if cfg["active_backend"] == backend:
        print(f"active_backend is now '{backend}'.")
    else:
        print(f"active_backend is still '{cfg['active_backend']}' -- edit config.json if you want to switch.")


if __name__ == "__main__":
    main()
