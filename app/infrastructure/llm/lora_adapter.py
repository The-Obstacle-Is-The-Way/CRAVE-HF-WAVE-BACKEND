# File: app/infrastructure/llm/lora_adapter.py

import logging
import os
from typing import Tuple, Dict, List, Optional
import threading
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel  # <--- NOTE: Import from peft
from app.config.settings import settings
from app.infrastructure.llm.llama2_adapter import Llama2Adapter

logger = logging.getLogger(__name__)

class LoRAAdapterManager:
    """
    Manager for LoRA adapters to use with the Llama 2 base model (CPU-only).
    """
    
    _base_model = None
    _base_tokenizer = None
    _adapter_cache = {}
    _model_lock = threading.RLock()
    
    @classmethod
    def load_base_model(cls) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """
        Load or retrieve the base CPU-only Llama 2 model/tokenizer from Llama2Adapter.
        """
        with cls._model_lock:
            if cls._base_model is None or cls._base_tokenizer is None:
                logger.info("Loading base Llama 2 model (CPU) ...")
                start_time = time.time()
                base_model, base_tokenizer = Llama2Adapter.load_base_model()
                cls._base_model = base_model
                cls._base_tokenizer = base_tokenizer
                logger.info(f"Base model loaded in {time.time() - start_time:.2f}s")
            return cls._base_model, cls._base_tokenizer

    @classmethod
    def load_adapter(cls, adapter_path: str) -> PeftModel:
        """
        Load a LoRA adapter from a local path or a HF repo (CPU-only).
        """
        with cls._model_lock:
            if adapter_path in cls._adapter_cache:
                logger.info(f"Using cached adapter: {adapter_path}")
                return cls._adapter_cache[adapter_path]
            
            logger.info(f"Loading LoRA adapter (CPU) from: {adapter_path}")
            start_time = time.time()
            try:
                base_model, _ = cls.load_base_model()
                adapter_model = PeftModel.from_pretrained(
                    base_model,
                    adapter_path,
                    torch_dtype=torch.float32,
                    device_map="cpu",  # <--- We can explicitly force CPU here
                    use_auth_token=settings.HF_AUTH_TOKEN
                )
                cls._adapter_cache[adapter_path] = adapter_model
                logger.info(f"Adapter loaded in {time.time() - start_time:.2f}s")
                return adapter_model
            except Exception as e:
                logger.error(f"Error loading LoRA adapter: {str(e)}")
                logger.warning("Falling back to base model")
                return cls._base_model

    @classmethod
    def generate_text_with_adapter(
        cls, 
        adapter_path: str, 
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 50,
        repetition_penalty: float = 1.1
    ) -> str:
        """
        Generate text using a specific LoRA adapter (CPU).
        """
        try:
            adapter_model = cls.load_adapter(adapter_path)
            _, tokenizer = cls.load_base_model()

            inputs = tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                generated_ids = adapter_model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repetition_penalty=repetition_penalty,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            output_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            # Optionally strip out the prompt
            if output_text.startswith(prompt):
                output_text = output_text[len(prompt):].strip()

            return output_text
        except Exception as e:
            logger.error(f"Error generating text with LoRA adapter: {str(e)}")
            logger.warning("Falling back to base model for text generation")
            return Llama2Adapter.generate_text(prompt)

    @classmethod
    def clear_adapter_cache(cls) -> None:
        """Clear the adapter cache to free up memory (if needed)."""
        with cls._model_lock:
            cls._adapter_cache.clear()
            # No-op if CPU only, but won't hurt:
            torch.cuda.empty_cache()
            logger.info("Adapter cache cleared")

    @classmethod
    def list_available_personas(cls) -> List[str]:
        """Return the persona keys from settings."""
        return list(settings.LORA_PERSONAS.keys())