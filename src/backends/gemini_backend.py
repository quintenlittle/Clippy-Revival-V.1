import requests

from .base import ModelBackend


class GeminiBackend(ModelBackend):
    """Calls the Google Gemini API. Needs an API key from https://aistudio.google.com/apikey
    Check Google AI Studio for the current model name string if this default goes stale."""

    name = "gemini"

    def __init__(self, api_key, model="gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt, context=""):
        full_prompt = f"Context from the active window:\n{context}\n\nUser: {prompt}" if context else prompt
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        resp = requests.post(
            url,
            json={"contents": [{"parts": [{"text": full_prompt}]}]},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
