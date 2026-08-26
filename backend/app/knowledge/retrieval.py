import uuid
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from app.config.settings import settings
from app.knowledge.embeddings import embedding_service

logger = logging.getLogger(__name__)

COLLECTION_NAME = "agricultural_knowledge"
EMBEDDING_DIM = 768  # multi-qa-mpnet-base-dot-v1 produces 768-dim vectors

class RAGRetriever:
    def __init__(self):
        # By default, storing in a local directory based on settings
        # In production, change settings.VECTOR_STORE_URL to http://qdrant:6333
        if settings.VECTOR_STORE_URL.startswith("http"):
            self.client = QdrantClient(url=settings.VECTOR_STORE_URL, check_compatibility=False)
        else:
            self.client = QdrantClient(path=settings.VECTOR_STORE_URL)
        
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if COLLECTION_NAME in collection_names:
                # Verify the dimension matches; if not, recreate
                info = self.client.get_collection(COLLECTION_NAME)
                existing_dim = info.config.params.vectors.size
                if existing_dim != EMBEDDING_DIM:
                    logger.warning(
                        f"Collection dimension mismatch ({existing_dim} != {EMBEDDING_DIM}). "
                        "Recreating collection..."
                    )
                    self.client.delete_collection(COLLECTION_NAME)
                    collection_names.remove(COLLECTION_NAME)

            if COLLECTION_NAME not in collection_names:
                logger.info(f"Creating Qdrant collection: {COLLECTION_NAME} (dim={EMBEDDING_DIM})")
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=rest_models.VectorParams(
                        size=EMBEDDING_DIM,
                        distance=rest_models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        documents must be a list of dicts with 'content' and 'metadata'.
        """
        if not documents:
            return

        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        vectors = embedding_service.embed_batch(texts)
        points = []
        
        for idx, (vector, text, metadata) in enumerate(zip(vectors, texts, metadatas)):
            point_id = str(uuid.uuid4())
            payload = {"content": text, **metadata}
            
            points.append(rest_models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Ingested {len(points)} documents into {COLLECTION_NAME}.")

    def retrieve(self, query: str, top_k: int = 3, filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieves relevant documents. Optionally accepts a filter dictionary for metadata filtering.
        """
        query_vector = embedding_service.embed_text(query)
        
        qdrant_filter = None
        if filter_conditions:
            # Simple exact match filter builder for MVP
            must_clauses = [
                rest_models.FieldCondition(key=k, match=rest_models.MatchValue(value=v))
                for k, v in filter_conditions.items()
            ]
            qdrant_filter = rest_models.Filter(must=must_clauses)
            
        search_result = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=top_k
        ).points
        
        results = []
        for hit in search_result:
            results.append({
                "id": hit.id,
                "content": hit.payload.get("content", ""),
                "metadata": {k: v for k, v in hit.payload.items() if k != "content"},
                "score": hit.score
            })
            
        return results

rag_retriever: Optional[RAGRetriever] = None

def init_rag_retriever():
    global rag_retriever
    if rag_retriever is None:
        rag_retriever = RAGRetriever()

def get_rag_retriever() -> RAGRetriever:
    global rag_retriever
    if rag_retriever is None:
        init_rag_retriever()
    return rag_retriever
