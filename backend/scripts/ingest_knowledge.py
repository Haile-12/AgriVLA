import os
# Must be set BEFORE torch is imported to prevent Windows OpenMP deadlock
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import logging
import torch

# Double-enforce single-threaded PyTorch
torch.set_num_threads(1)

# Add the backend directory to sys.path so we can import app modules
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from app.knowledge.retrieval import get_rag_retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    data_file = os.path.join(os.path.dirname(__file__), 'knowledge_data.json')
    if not os.path.exists(data_file):
        logger.error(f"Data file not found: {data_file}")
        sys.exit(1)
        
    with open(data_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
        
    logger.info(f"Loaded {len(documents)} documents from {data_file}.")
    
    # Initialize the RAG Retriever (which connects to Qdrant)
    retriever = get_rag_retriever()
    
    logger.info("Starting ingestion...")
    retriever.add_documents(documents)
    logger.info("Ingestion complete!")

if __name__ == "__main__":
    main()
