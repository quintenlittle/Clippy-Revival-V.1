import requests

from .base import ModelBackend


class AnthropicBackend(ModelBackend):
    """Calls the Anthropic API. Needs an API key from https://console.anthropic.com
    Check the console for the current model name string if this default goes stale."""

    name = "anthropic"

    def __init__(self, api_key, model="claude-sonnet-4-6"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt, context=""):
        full_prompt = f"Context from the active window:\n{context}\n\nUser: {prompt}" if context else prompt
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": full_prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        ).strip()
