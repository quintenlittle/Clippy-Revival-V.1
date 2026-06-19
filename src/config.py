"""
Loads/saves config.json (created next to the .exe, or in the project root
when running from source) and builds the active model backend from it.
"""
import json
import os

from paths import get_base_dir

CONFIG_PATH = os.path.join(get_base_dir(), "config.json")

DEFAULT_CONFIG = {
    "active_backend": "ollama",
    "hotkey_toggle": "ctrl+alt+c",
    "hotkey_capture": "ctrl+alt+space",
    "ollama": {
        "model": "dolphin-mistral",
        "host": "http://localhost:11434"
    },
    "anthropic": {
        "api_key": "",
        "model": "claude-sonnet-4-6"
    },
    "openai": {
        "api_key": "",
        "model": "gpt-4o"
    },
    "gemini": {
        "api_key": "",
        "model": "gemini-2.0-flash"
    },
    "huggingface": {
        "model_id": "microsoft/Phi-3-mini-4k-instruct",
        "device": "cuda"
    }
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # backfill any keys missing from an older config.json
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    for key, default_val in DEFAULT_CONFIG.items():
        if isinstance(default_val, dict):
            merged_sub = dict(default_val)
            merged_sub.update(cfg.get(key, {}))
            merged[key] = merged_sub
    return merged


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def get_active_backend(cfg):
    name = cfg.get("active_backend", "ollama")

    if name == "ollama":
        from backends.ollama_backend import OllamaBackend
        c = cfg["ollama"]
        return OllamaBackend(model=c["model"], host=c["host"])

    if name == "anthropic":
        from backends.anthropic_backend import AnthropicBackend
        c = cfg["anthropic"]
        if not c.get("api_key"):
            raise ValueError("anthropic.api_key is empty in config.json")
        return AnthropicBackend(api_key=c["api_key"], model=c["model"])

    if name == "openai":
        from backends.openai_backend import OpenAIBackend
        c = cfg["openai"]
        if not c.get("api_key"):
            raise ValueError("openai.api_key is empty in config.json")
        return OpenAIBackend(api_key=c["api_key"], model=c["model"])

    if name == "gemini":
        from backends.gemini_backend import GeminiBackend
        c = cfg["gemini"]
        if not c.get("api_key"):
            raise ValueError("gemini.api_key is empty in config.json")
        return GeminiBackend(api_key=c["api_key"], model=c["model"])

    if name == "huggingface":
        from backends.huggingface_backend import HuggingFaceBackend
        c = cfg["huggingface"]
        return HuggingFaceBackend(model_id=c["model_id"], device=c["device"])

    raise ValueError(f"Unknown active_backend: {name!r}")
