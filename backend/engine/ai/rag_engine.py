import structlog
import faiss
import numpy as np
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

logger = structlog.get_logger("DevShield.RAG")

DEVSHIELD_DIR = Path.home() / ".devshield"
DEVSHIELD_DIR.mkdir(exist_ok=True)
FAISS_INDEX_PATH = DEVSHIELD_DIR / "vectors.index"
DOC_MAP_PATH = DEVSHIELD_DIR / "doc_map.json"

class RAGEngine:
    """
    True Retrieval-Augmented Generation engine.
    Uses SentenceTransformer for dense embeddings and FAISS for fast similarity search.
    """
    def __init__(self):
        self._encoder = None
        self.dimension = 384
        self.dimension = 384
        
        # Load or create FAISS index
        if FAISS_INDEX_PATH.exists():
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            
        # In-memory mapping from FAISS ID -> document data (In production, use PostgreSQL pgvector)
        self.doc_map: Dict[int, Dict[str, Any]] = {}
        self.current_id = self.index.ntotal
        
        self._load_doc_map()

    def _load_doc_map(self):
        import json
        if DOC_MAP_PATH.exists():
            try:
                with open(DOC_MAP_PATH, "r") as f:
                    data = json.load(f)
                    self.doc_map = {int(k): v for k, v in data.items()}
            except Exception as e:
                logger.error(f"Failed to load doc map: {e}")

    def _save_doc_map(self):
        import json
        try:
            with open(DOC_MAP_PATH, "w") as f:
                json.dump(self.doc_map, f)
        except Exception as e:
            logger.error(f"Failed to save doc map: {e}")

    @property
    def encoder(self):
        if self._encoder is None:
            logger.info("Loading SentenceTransformer model locally (may take a moment)...")
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=str(DEVSHIELD_DIR / "models"))
        return self._encoder

    def add_document(self, content: str, metadata: dict) -> int:
        """
        Embeds content and adds it to the FAISS index.
        """
        vec = self.encoder.encode([content])
        # L2 normalize for cosine similarity behavior
        faiss.normalize_L2(vec)
        
        self.index.add(vec)
        
        doc_id = self.current_id
        self.doc_map[doc_id] = {
            "content": content,
            "metadata": metadata
        }
        self.current_id += 1
        
        # Persist
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        self._save_doc_map()
        
        return doc_id

    def retrieve_similar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the most semantically similar documents.
        """
        if self.index.ntotal == 0:
            return []
            
        vec = self.encoder.encode([query])
        faiss.normalize_L2(vec)
        
        distances, indices = self.index.search(vec, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.doc_map:
                results.append({
                    "score": float(distances[0][i]),
                    "content": self.doc_map[idx]["content"],
                    "metadata": self.doc_map[idx]["metadata"]
                })
        return results

    def get_context_for_fix(self, vulnerability_desc: str) -> str:
        """
        Retrieves past successful fixes for similar vulnerabilities to guide the LLM.
        """
        similar = self.retrieve_similar(vulnerability_desc, top_k=2)
        if not similar:
            return ""
            
        context = "Here are past successful fixes for similar vulnerabilities:\n\n"
        for i, s in enumerate(similar):
            context += f"Example {i+1}:\n"
            context += f"Vulnerability: {s['metadata'].get('title', 'Unknown')}\n"
            context += f"Fix Pattern:\n```\n{s['content']}\n```\n\n"
            
        return context
