# crave_trinity_backend/app/core/services/rag_service.py

from app.infrastructure.vector_db.vector_repository import VectorRepository
from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService
from app.infrastructure.llm.lora_adapter import LoRAAdapterManager
from app.infrastructure.llm.llama2_adapter import Llama2Adapter
from app.config.settings import Settings

settings = Settings()

def generate_personalized_insight(
    user_id: int, 
    query: str, 
    persona: str = None,
    top_k: int = 3
) -> str:
    """
    1) Embeds the user query
    2) Retrieves top-k user craving logs from Pinecone
    3) Assembles a prompt that includes the retrieved context
    4) Either uses the base LLM or a LoRA persona
    5) Returns the model's answer
    """

    # 1) Embed query
    embed_service = OpenAIEmbeddingService()
    query_embedding = embed_service.embed_text(query)

    # 2) Retrieve relevant cravings
    vector_repo = VectorRepository()
    matches = vector_repo.query_cravings(query_embedding, top_k=top_k)

    # 3) Build a context snippet from the matched metadata
    #    For example, we assume each match metadata has "description" or "created_at"
    context_lines = []
    for m in matches:
        desc = m["metadata"].get("description", "")
        timestamp = m["metadata"].get("created_at", "")
        context_lines.append(f"- Craving: {desc} at {timestamp}")

    context_text = "\n".join(context_lines)
    if not context_text:
        context_text = "No relevant craving data found."

    # 4) Build the final prompt
    prompt = f"""You are CRAVE AI, helping user {user_id}.
Relevant user cravings:
{context_text}

User question: {query}

Please provide an insightful, empathetic response.
"""

    # 5) If persona is specified, use LoRA. Otherwise use base model.
    if persona and persona in settings.LORA_PERSONAS:
        adapter_path = settings.LORA_PERSONAS[persona]
        answer = LoRAAdapterManager.generate_text_with_adapter(adapter_path, prompt)
    else:
        answer = Llama2Adapter.generate_text(prompt)

    return answer
