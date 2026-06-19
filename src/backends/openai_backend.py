import requests

from .base import ModelBackend


class OpenAIBackend(ModelBackend):
    """Calls the OpenAI API. Needs an API key from https://platform.openai.com/api-keys
    Use this same backend for GPT models or Codex-family models -- just change
    `model` in config.json to whatever model string your account has access to."""

    name = "openai"

    def __init__(self, api_key, model="gpt-4o"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt, context=""):
        full_prompt = f"Context from the active window:\n{context}\n\nUser: {prompt}" if context else prompt
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": full_prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
