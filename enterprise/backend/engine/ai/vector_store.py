import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "faiss_index.bin", meta_path: str = "faiss_meta.json"):
        self.dimension = dimension
        self.index_path = index_path
        self.meta_path = meta_path
        
        # Load local embedding model (e.g., all-MiniLM-L6-v2)
        try:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.encoder = None

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w') as f:
            json.dump(self.metadata, f)

    def add_snippets(self, snippets: list[dict]):
        """Expects format: [{'id': str, 'text': str, 'filename': str}]"""
        if not self.encoder:
            return
            
        texts = [s['text'] for s in snippets]
        embeddings = self.encoder.encode(texts)
        
        faiss.normalize_L2(embeddings)
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(snippets)
        self.save()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.encoder or self.index.ntotal == 0:
            return []
            
        query_vec = self.encoder.encode([query])
        faiss.normalize_L2(query_vec)
        distances, indices = self.index.search(np.array(query_vec).astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                res = self.metadata[idx].copy()
                res["score"] = float(distances[0][i])
                results.append(res)
        return results
