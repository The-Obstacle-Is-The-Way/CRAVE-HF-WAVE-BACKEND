# crave_trinity_backend/app/infrastructure/llm/llama2_adapter.py

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.config.settings import Settings

settings = Settings()

class Llama2Adapter:
    """
    Loads the base Llama 2 model from Hugging Face (ex: 'meta-llama/Llama-2-13b-hf').
    In real scenarios, you'd handle GPU vs. CPU, 8-bit quantization, etc.
    """
    _model = None
    _tokenizer = None

    @classmethod
    def load_base_model(cls):
        """
        Loads or returns a cached reference to the Llama 2 model & tokenizer.
        """
        if cls._model is not None and cls._tokenizer is not None:
            return cls._model, cls._tokenizer

        model_name = settings.LLAMA2_MODEL_NAME  # e.g. "meta-llama/Llama-2-13b-hf"
        cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
        cls._model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"  # this automatically places model layers on available GPUs
        )

        cls._model.eval()  # set to eval mode

        return cls._model, cls._tokenizer

    @classmethod
    def generate_text(cls, prompt: str, max_new_tokens=128, temperature=0.7) -> str:
        """
        Simple utility to do inference using the base model (no LoRA).
        """
        model, tokenizer = cls.load_base_model()
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
