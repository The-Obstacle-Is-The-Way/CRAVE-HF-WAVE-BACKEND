# File: app/infrastructure/llm/lora_adapter.py
"""
LoRA adapter management for Llama 2 models.

This module provides functionality to load and use LoRA adapters with the base Llama 2 model,
enabling persona-specific fine-tuning without requiring full model retraining.

LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that
adds small trainable matrices to the model's attention mechanism.
"""

import logging
import os
from typing import Tuple, Dict, List, Optional, Union
import threading
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

from app.config.settings import Settings
from app.infrastructure.llm.llama2_adapter import Llama2Adapter

# Set up logging
logger = logging.getLogger(__name__)

# Get settings
settings = Settings()

class LoRAAdapterManager:
    """
    Manager for LoRA adapters to use with the Llama 2 base model.
    
    This class provides functionality for:
    - Loading LoRA adapters from local paths or Hugging Face
    - Dynamically swapping adapters during runtime
    - Managing adapter caching for performance
    - Text generation with specific adapters
    """
    
    # Class-level variables for sharing resources
    _base_model = None
    _base_tokenizer = None
    _adapter_cache = {}  # Cache loaded adapters
    _model_lock = threading.RLock()  # Lock for thread safety
    
    @classmethod
    def load_base_model(cls) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """
        Load the base Llama 2 model and tokenizer.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        with cls._model_lock:
            if cls._base_model is None or cls._base_tokenizer is None:
                logger.info("Loading base Llama 2 model and tokenizer...")
                
                # Start a timer to track loading time
                start_time = time.time()
                
                try:
                    # Configure quantization for memory efficiency
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True
                    )
                    
                    # Use Llama2Adapter's base model path
                    model_path = settings.LLAMA2_MODEL_PATH
                    
                    # Load model with quantization
                    model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        device_map="auto",
                        trust_remote_code=True,
                        quantization_config=quantization_config
                    )
                    
                    # Load tokenizer
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_path,
                        trust_remote_code=True
                    )
                    tokenizer.pad_token = tokenizer.eos_token
                    
                    # Store in class variables
                    cls._base_model = model
                    cls._base_tokenizer = tokenizer
                    
                    logger.info(f"Base model loaded successfully in {time.time() - start_time:.2f} seconds")
                    
                except Exception as e:
                    logger.error(f"Error loading base model: {str(e)}")
                    raise
            
            return cls._base_model, cls._base_tokenizer
            
    @classmethod
    def load_adapter(cls, adapter_path: str) -> PeftModel:
        """
        Load a LoRA adapter from path or HuggingFace.
        
        Args:
            adapter_path: Path to the adapter or HuggingFace model ID
            
        Returns:
            PeftModel with adapter applied
        """
        with cls._model_lock:
            # Check cache first
            if adapter_path in cls._adapter_cache:
                logger.info(f"Using cached adapter: {adapter_path}")
                return cls._adapter_cache[adapter_path]
                
            logger.info(f"Loading LoRA adapter: {adapter_path}")
            start_time = time.time()
            
            try:
                # First load base model
                base_model, _ = cls.load_base_model()
                
                # Load adapter
                adapter_model = PeftModel.from_pretrained(
                    base_model,
                    adapter_path,
                    device_map="auto",
                    torch_dtype=torch.float16
                )
                
                # Cache the loaded adapter
                cls._adapter_cache[adapter_path] = adapter_model
                
                logger.info(f"Adapter loaded successfully in {time.time() - start_time:.2f} seconds")
                return adapter_model
                
            except Exception as e:
                logger.error(f"Error loading adapter: {str(e)}")
                # Fallback to base model
                logger.warning(f"Falling back to base model due to adapter loading error")
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
        Generate text using a specific LoRA adapter.
        
        Args:
            adapter_path: Path to the adapter or HuggingFace model ID
            prompt: Input prompt for text generation
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repetition_penalty: Penalty for repeating tokens
            
        Returns:
            Generated text
        """
        try:
            # Load adapter
            adapter_model = cls.load_adapter(adapter_path)
            
            # Get tokenizer
            _, tokenizer = cls.load_base_model()
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
            
            # Generate text
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
            
            # Decode output
            output_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            
            # Remove the input prompt from the output
            if output_text.startswith(prompt):
                output_text = output_text[len(prompt):].strip()
                
            return output_text
            
        except Exception as e:
            logger.error(f"Error generating text with adapter: {str(e)}")
            # Fallback to base model
            logger.warning("Falling back to base model for text generation")
            return Llama2Adapter.generate_text(prompt)
            
    @classmethod
    def clear_adapter_cache(cls) -> None:
        """Clear the adapter cache to free up memory."""
        with cls._model_lock:
            cls._adapter_cache.clear()
            torch.cuda.empty_cache()
            logger.info("Adapter cache cleared")
            
    @classmethod
    def list_available_personas(cls) -> List[str]:
        """
        List available persona adapters from settings.
        
        Returns:
            List of persona names
        """
        return list(settings.LORA_PERSONAS.keys())