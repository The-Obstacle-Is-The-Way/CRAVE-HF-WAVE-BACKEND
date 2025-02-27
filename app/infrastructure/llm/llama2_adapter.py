# crave_trinity_backend/app/infrastructure/llm/llama2_adapter.py

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.config.settings import settings

class Llama2Adapter:
    """
    Loads the base Llama 2 model from Hugging Face (e.g., 'meta-llama/Llama-2-7b-chat-hf')
    in CPU-only mode if no GPU is available.
    """
    _model = None
    _tokenizer = None

    @classmethod
    def load_base_model(cls):
        """
        Loads or returns a cached reference to the Llama 2 model & tokenizer (CPU-only).
        """
        if cls._model is not None and cls._tokenizer is not None:
            return cls._model, cls._tokenizer

        model_name = settings.LLAMA2_MODEL_NAME

        # If you have a HF token, set "use_auth_token=settings.HF_AUTH_TOKEN"
        # If your model is truly public, you can omit it.
        cls._tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            use_auth_token=settings.HF_AUTH_TOKEN
        )

        # For CPU only:
        cls._model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,         # On CPU, float16 can cause errors in some ops
            device_map="auto",                 # "auto" → CPU if no GPU
            use_auth_token=settings.HF_AUTH_TOKEN
        )

        cls._model.eval()
        return cls._model, cls._tokenizer

    @classmethod
    def generate_text(cls, prompt: str, max_new_tokens=128, temperature=0.7) -> str:
        """
        Simple utility to do inference using the base model.
        """
        model, tokenizer = cls.load_base_model()
        # On CPU
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)