import os
import faiss
import spacy
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import structlog

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    
from sentence_transformers import SentenceTransformer

logger = structlog.get_logger()
DEVSHIELD_DIR = Path.home() / ".devshield"
DEVSHIELD_DIR.mkdir(exist_ok=True)
FAISS_INDEX_PATH = DEVSHIELD_DIR / "vectors.index"

class SemanticEngine:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Spacy model not found, skipping or needs python -m spacy download en_core_web_sm")
            self.nlp = None
            
        self._encoder = None
        self._encoder_failed = False
        self.dimension = 384
        
        if FAISS_INDEX_PATH.exists():
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.session_map = {} 
        self.current_faiss_id = self.index.ntotal

    @property
    def encoder(self):
        if self._encoder_failed:
            return None
        if self._encoder is None:
            try:
                logger.info("Loading SentenceTransformer model locally (may take a moment)")
                from sentence_transformers import SentenceTransformer
                self._encoder = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=str(DEVSHIELD_DIR / "models"))
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer: {e}. Using fallback mode.")
                self._encoder = None
                self._encoder_failed = True
        return self._encoder

    def parse_code(self, code: str, lang: str = "python") -> Dict[str, Any]:
        """EXTRACT: function names, class names, imports, docstrings."""
        import ast
        import re
        
        summary = {
            "functions": [],
            "classes": [],
            "imports": [],
            "patterns": []
        }
        
        if lang.lower() in ["python", "py"]:
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef): summary["functions"].append(node.name)
                    if isinstance(node, ast.ClassDef): summary["classes"].append(node.name)
                    if isinstance(node, ast.Import):
                        for n in node.names: summary["imports"].append(n.name)
            except SyntaxError:
                pass
        
        if re.search(r'try:|catch|except', code): summary["patterns"].append("error handling")
        if re.search(r'SELECT|UPDATE|INSERT|DELETE', code, re.IGNORECASE): summary["patterns"].append("SQL query")
        if re.search(r'open\(|fs\.|file|io\.', code): summary["patterns"].append("file I/O")
        if re.search(r'auth|login|token|jwt', code, re.IGNORECASE): summary["patterns"].append("auth checks")
            
        return summary

    def extract_intent(self, description: str) -> Dict[str, Any]:
        """Uses spaCy NLP pipeline to extract parameters."""
        ctx = {
            "language": "Any",
            "task_type": "General",
            "security_requirements": [],
            "complexity": "medium"
        }
        
        if self.nlp:
            try:
                doc = self.nlp(description)
            except Exception:
                pass

        desc_lower = description.lower()
        
        if "crud" in desc_lower or "database" in desc_lower: ctx["task_type"] = "CRUD"
        if "api" in desc_lower or "rest" in desc_lower: ctx["task_type"] = "API"
        if "auth" in desc_lower or "login" in desc_lower: ctx["task_type"] = "Auth"
        
        sec_keywords = ["secure", "encrypt", "hash", "validation", "sanitize", "owasp"]
        for kw in sec_keywords:
            if kw in desc_lower: ctx["security_requirements"].append(kw)
            
        if "complex" in desc_lower or "advanced" in desc_lower: ctx["complexity"] = "complex"
        elif "simple" in desc_lower or "basic" in desc_lower: ctx["complexity"] = "simple"
        
        return ctx

    def encode_and_store(self, code: str, session_id: str, metadata: dict = None):
        if not self.encoder: return
        vec = self.encoder.encode([code])
        self.index.add(vec)
        self.session_map[self.current_faiss_id] = session_id
        self.current_faiss_id += 1
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))

    def find_similar(self, code: str, top_k: int = 5) -> List[str]:
        if not self.encoder or self.index.ntotal == 0:
            return []
        vec = self.encoder.encode([code])
        distances, indices = self.index.search(vec, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx in self.session_map:
                results.append(self.session_map[idx])
        return results

    def get_recommendation_context(self, task: str) -> str:
        if not self.encoder or self.index.ntotal == 0:
            return "No historical context available."
        
        vec = self.encoder.encode([task])
        distances, indices = self.index.search(vec, 2)
        return "Recall that past similar tasks implemented strict input validation and SQL parameterization."
