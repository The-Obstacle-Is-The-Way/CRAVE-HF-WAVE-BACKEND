# crave_trinity_backend/app/infrastructure/llm/lora_adapter.py

import torch
from peft import PeftModel
from app.config.settings import Settings
from .llama2_adapter import Llama2Adapter

settings = Settings()

class LoRAAdapterManager:
    """
    Manages loading LoRA adapters (fine-tuned for different craving personas).
    We can dynamically load/unload or keep them in memory, depending on usage.
    """

    loaded_adapters = {}  # cache: { adapter_name: PeftModel(...) }

    @classmethod
    def load_lora_adapter(cls, adapter_path: str):
        """
        Loads a LoRA adapter on top of the base Llama 2 model.
        adapter_path might be a local folder or HF Hub reference.
        """
        if adapter_path in cls.loaded_adapters:
            return cls.loaded_adapters[adapter_path]

        base_model, tokenizer = Llama2Adapter.load_base_model()
        # Wrap the base model with the LoRA weights
        lora_model = PeftModel.from_pretrained(
            base_model,
            adapter_path,
            torch_dtype=torch.float16,
        )
        lora_model.eval()

        cls.loaded_adapters[adapter_path] = lora_model
        return lora_model

    @classmethod
    def generate_text_with_adapter(
        cls, 
        adapter_path: str, 
        prompt: str, 
        max_new_tokens=128, 
        temperature=0.7
    ) -> str:
        """
        Use the specified LoRA adapter to generate text. 
        The base model + adapter is used in forward pass.
        """
        lora_model = cls.load_lora_adapter(adapter_path)
        tokenizer = Llama2Adapter._tokenizer  # from the base adapter cache

        inputs = tokenizer(prompt, return_tensors="pt").to(lora_model.device)
        with torch.no_grad():
            outputs = lora_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
