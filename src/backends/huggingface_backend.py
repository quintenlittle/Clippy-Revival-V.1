from .base import ModelBackend


class HuggingFaceBackend(ModelBackend):
    """Runs a HuggingFace model locally instead of through Ollama.
    Heavier than Ollama: needs `transformers` + `torch` installed separately
    (NOT in requirements.txt by default -- see README "Optional: HuggingFace backend").
    Imports are deferred to __init__ so the rest of the app works fine without
    these packages installed if you never select this backend."""

    name = "huggingface"

    def __init__(self, model_id="microsoft/Phi-3-mini-4k-instruct", device="cuda"):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.float16, device_map=device
        )

    def generate(self, prompt, context=""):
        full_prompt = f"Context from the active window:\n{context}\n\nUser: {prompt}" if context else prompt
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.model.device)
        with self.torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=512)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return text[len(full_prompt):].strip()
