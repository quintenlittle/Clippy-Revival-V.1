import requests

from .base import ModelBackend


class OllamaBackend(ModelBackend):
    """Talks to a locally running Ollama server. No API key needed.
    Install Ollama from https://ollama.com, then e.g. `ollama pull dolphin-mistral`."""

    name = "ollama"

    def __init__(self, model="dolphin-mistral", host="http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, prompt, context=""):
        full_prompt = f"Context from the active window:\n{context}\n\nUser: {prompt}" if context else prompt
        resp = requests.post(
            f"{self.host}/api/generate",
            json={"model": self.model, "prompt": full_prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
