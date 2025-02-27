#llama2_model.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def load_llama2_model(model_name: str):
    """
    Loads the base Llama 2 model in half-precision (fp16) with device_map set to "auto".
    
    Parameters:
      model_name (str): The Hugging Face model identifier for the base Llama 2 model.
      
    Returns:
      model: The loaded model in fp16.
      tokenizer: The associated tokenizer.
    """
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

def load_llama2_with_lora(model_name: str, lora_model_path: str):
    """
    Loads the base Llama 2 model and applies a LoRA adapter.
    
    Parameters:
      model_name (str): The Hugging Face model identifier for the base Llama 2 model.
      lora_model_path (str): The local path or Hugging Face identifier for the LoRA adapter checkpoint.
      
    Returns:
      model: The model with the LoRA adapter applied.
      tokenizer: The associated tokenizer.
    """
    # Load the base model and tokenizer
    model, tokenizer = load_llama2_model(model_name)
    # Apply the LoRA adapter using the peft library
    model = PeftModel.from_pretrained(model, lora_model_path)
    return model, tokenizer

if __name__ == "__main__":
    # Example usage for testing:
    base_model_name = "meta-llama/Llama-2-13b-hf"  # Update with your model name if different
    lora_path = "./lora/llama2_lora"  # Ensure this directory exists and contains your adapter
    model, tokenizer = load_llama2_with_lora(base_model_name, lora_path)
    
    # Run a simple inference test:
    input_text = "Hello, how are you today?"
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=50)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Generated text:", generated_text)
