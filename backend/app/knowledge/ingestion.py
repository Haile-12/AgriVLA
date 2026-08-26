import json
import logging
import os
from pathlib import Path
from app.knowledge.retrieval import get_rag_retriever

logger = logging.getLogger(__name__)

class KnowledgeIngestionService:
    def __init__(self, data_dir: str = "./data/knowledge/raw"):
        self.data_dir = data_dir
        
    def ingest_all(self):
        """
        Reads JSON files containing agricultural knowledge and ingests them into the vector store.
        Expected format per file:
        [
            {
                "crop": "tomato",
                "condition": "early_blight",
                "content": "Detailed text about treatment...",
                "source": "USDA"
            }
        ]
        """
        path = Path(self.data_dir)
        if not path.exists():
            logger.warning(f"Knowledge data directory {self.data_dir} does not exist. Skipping ingestion.")
            return
            
        total_ingested = 0
        for file_path in path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                documents = []
                for item in data:
                    content = item.pop("content", "")
                    if not content:
                        continue
                        
                    documents.append({
                        "content": content,
                        "metadata": item # Remaining keys become metadata (crop, condition, source)
                    })
                    
                if documents:
                    get_rag_retriever().add_documents(documents)
                    total_ingested += len(documents)
                    
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                
        logger.info(f"Ingestion complete. Added {total_ingested} new chunks.")
