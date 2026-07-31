import json
import logging
from typing import Dict, List, Any
try:
    import spacy
except ImportError:
    spacy = None

logger = logging.getLogger("DevShield.DatasetBuilder")

class NLPFeatureExtractor:
    """Uses spaCy to extract sentiments and intents from raw JSONL interactions."""
    def __init__(self):
        self.nlp = None
        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. NLP features will be disabled.")

    def extract_features(self, feedback_text: str) -> Dict[str, Any]:
        features = {
            "negative_sentiment": False,
            "complexity": 0.0,
            "intents": [],
            "keywords": []
        }
        
        if not self.nlp or not feedback_text:
            return features
            
        doc = self.nlp(feedback_text.lower())
        
        # 1. Negative Sentiment & Intent Matching
        negative_words = {"wrong", "bad", "error", "fail", "incorrect", "false", "stupid", "hate", "bug"}
        for token in doc:
            if token.lemma_ in negative_words:
                features["negative_sentiment"] = True
                
            # Extract domain-specific keywords (Nouns/Proper Nouns)
            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
                features["keywords"].append(token.lemma_)
                
        # 2. Complexity (Noun Chunks indicate detailed architectural feedback)
        features["complexity"] = len(list(doc.noun_chunks)) / (len(doc) + 1)
        
        return features

class DatasetBuilder:
    @staticmethod
    def build_from_jsonl(filepath: str) -> tuple[List[List[float]], List[int]]:
        """Parses JSONL into X (features) and Y (labels) for classifier training."""
        X, Y = [], []
        extractor = NLPFeatureExtractor()
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        text = record.get("user_comment", "")
                        is_fp = record.get("is_false_positive", False)
                        
                        # NLP Vectorization
                        feats = extractor.extract_features(text)
                        
                        # Flatten to numerical array [has_negative_sentiment, complexity, keyword_count]
                        feature_vector = [
                            1.0 if feats["negative_sentiment"] else 0.0,
                            feats["complexity"],
                            len(feats["keywords"])
                        ]
                        
                        X.append(feature_vector)
                        Y.append(1 if is_fp else 0)
                    except Exception:
                        continue
        except FileNotFoundError:
            pass
            
        return X, Y
