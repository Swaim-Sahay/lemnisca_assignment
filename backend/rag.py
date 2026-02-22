import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from pathlib import Path

import backend.config as config

class DocumentStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None

    def chunk_text(self, text: str, doc_name: str, page_num: int) -> List[Dict[str, Any]]:
        """Splits text into overlapping chunks."""
        text = text.replace('\n', ' ').replace('\r', ' ')
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + config.CHUNK_SIZE, text_len)
            chunk_content = text[start:end]
            chunks.append({
                "document": doc_name,
                "page": page_num,
                "content": chunk_content
            })
            start += config.CHUNK_SIZE - config.CHUNK_OVERLAP
            
        return chunks

    def ingest_directory(self, docs_dir: Path):
        """Reads all PDFs in a directory, chunks them, and generates embeddings."""
        print(f"Ingesting documents from {docs_dir}...")
        all_chunks = []
        
        pdf_files = list(docs_dir.glob("*.pdf"))
        if not pdf_files:
            print("No PDF files found.")
            return

        for pdf_path in pdf_files:
            try:
                reader = PdfReader(pdf_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        page_chunks = self.chunk_text(text, pdf_path.name, i + 1)
                        all_chunks.extend(page_chunks)
            except Exception as e:
                print(f"Error reading {pdf_path.name}: {e}")

        self.chunks = all_chunks
        print(f"Total chunks created: {len(self.chunks)}")
        
        print("Generating embeddings...")
        texts = [chunk["content"] for chunk in self.chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        self.embeddings = np.array(embeddings)
        print("Embeddings generated.")

    def save(self, filepath: Path):
        """Saves chunks and embeddings to disk."""
        with open(filepath, "wb") as f:
            pickle.dump({"chunks": self.chunks, "embeddings": self.embeddings}, f)
        print(f"Vector store saved to {filepath}")

    def load(self, filepath: Path):
        """Loads chunks and embeddings from disk."""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.embeddings = data["embeddings"]
        print(f"Vector store loaded from {filepath}. Total chunks: {len(self.chunks)}")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant chunks for a given query."""
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        query_embedding = self.embedding_model.encode(query)
        
        # Calculate cosine similarity: dot product of normalized vectors
        # all-MiniLM-L6-v2 embeddings are not normalized by default, so we normalize
        norm_q = np.linalg.norm(query_embedding)
        norm_e = np.linalg.norm(self.embeddings, axis=1)
        
        if norm_q == 0:
            return []
            
        similarities = np.dot(self.embeddings, query_embedding) / (norm_e * norm_q)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            # We enforce a small threshold to avoid totally irrelevant chunks
            score = float(similarities[idx])
            if score > 0.2:
                chunk_data = self.chunks[idx].copy()
                chunk_data["relevance_score"] = score
                results.append(chunk_data)
                
        return results

if __name__ == "__main__":
    store = DocumentStore()
    store.ingest_directory(config.DOCS_DIR)
    store.save(config.VECTOR_STORE_PATH)

