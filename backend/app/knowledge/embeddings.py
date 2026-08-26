import logging
from typing import List

logger = logging.getLogger(__name__)

# Model: BAAI/bge-base-en-v1.5 (768-dim, semantic, high-quality)
FASTEMBED_MODEL = "BAAI/bge-base-en-v1.5"


class EmbeddingService:
    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            from fastembed import TextEmbedding
            logger.info(f"Loading FastEmbed model: {FASTEMBED_MODEL}")
            self._model = TextEmbedding(model_name=FASTEMBED_MODEL)
            logger.info("FastEmbed model loaded successfully.")

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        result = list(self._model.embed([text]))
        return result[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        results = list(self._model.embed(texts))
        return [r.tolist() for r in results]


embedding_service = EmbeddingService()
