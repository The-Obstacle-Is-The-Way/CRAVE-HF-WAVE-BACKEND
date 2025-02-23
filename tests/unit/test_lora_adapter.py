# tests/unit/test_lora_adapter.py
import pytest
from unittest.mock import patch, MagicMock
from app.infrastructure.llm.lora_adapter import LoRAAdapterManager

@pytest.mark.unit
@patch("app.infrastructure.llm.lora_adapter.Llama2Adapter.load_base_model")
@patch("peft.PeftModel.from_pretrained")
def test_lora_generation(mock_peft_from_pretrained, mock_load_base):
    # Mock the base model
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_load_base.return_value = (mock_model, mock_tokenizer)

    # Mock the LoRA model
    mock_lora_model = MagicMock()
    mock_peft_from_pretrained.return_value = mock_lora_model

    # Setup return from model.generate
    mock_lora_model.generate.return_value = ["token_ids"]
    mock_tokenizer.decode.return_value = "mocked output"

    # Now call the generate_text_with_adapter
    adapter_path = "some/path/or/hub"
    prompt = "Test prompt"
    result = LoRAAdapterManager.generate_text_with_adapter(adapter_path, prompt)
    
    assert result == "mocked output"
    mock_peft_from_pretrained.assert_called_once()
    mock_lora_model.generate.assert_called_once()
