import httpx
import logging
from app.config import HUGGINGFACE_API_KEY

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.api_key = HUGGINGFACE_API_KEY
        self.model_id = "BAAI/bge-small-en-v1.5"
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_id}"

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            logger.error("Hugging Face API key not found.")
            return []

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": texts, "options": {"wait_for_model": True}}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=60)
                if response.status_code != 200:
                    logger.error(f"HF Embedding Error: {response.status_code} - {response.text}")
                    return []
                return response.json()
            except Exception as e:
                logger.error(f"Error calling HF Embedding API: {str(e)}")
                return []

embedding_service = EmbeddingService()
