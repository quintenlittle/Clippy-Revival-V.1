from abc import ABC, abstractmethod


class ModelBackend(ABC):
    """Every backend (local or cloud) implements this one method.
    Overlay code never needs to know which backend is active."""

    name = "base"

    @abstractmethod
    def generate(self, prompt: str, context: str = "") -> str:
        """Return a text reply given the user's prompt and optional
        captured screen/app context."""
        raise NotImplementedError
