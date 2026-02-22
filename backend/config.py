import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
VECTOR_STORE_PATH = BASE_DIR / "vector_store.pkl"

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding Model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# LLM Models
GROQ_MODEL_SIMPLE = "llama-3.1-8b-instant"
GROQ_MODEL_COMPLEX = "llama-3.3-70b-versatile"
