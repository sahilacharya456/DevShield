import os
import joblib
import logging
from engine.ml.dataset_builder import NLPFeatureExtractor

logger = logging.getLogger("DevShield.MLInference")

class InferenceEngine:
    MODEL_PATH = "vulnerability_classifier.pkl"
    _model = None
    _extractor = NLPFeatureExtractor()

    @classmethod
    def _load_model(cls):
        if cls._model is None and os.path.exists(cls.MODEL_PATH):
            try:
                cls._model = joblib.load(cls.MODEL_PATH)
            except Exception as e:
                logger.error(f"Failed to load ML weights: {e}")

    @classmethod
    def is_false_positive(cls, vulnerability_description: str) -> bool:
        """Inference loop using trained models to filter vulnerabilties natively."""
        cls._load_model()
        
        if cls._model is None:
            return False  # Pass through if no model trained yet
            
        # Extract numerical features matching training shape
        feats = cls._extractor.extract_features(vulnerability_description)
        feature_vector = [[
            1.0 if feats["negative_sentiment"] else 0.0,
            feats["complexity"],
            len(feats["keywords"])
        ]]
        
        prediction = cls._model.predict(feature_vector)
        return bool(prediction[0] == 1)
