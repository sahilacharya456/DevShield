import os
import joblib
import logging
from sklearn.ensemble import RandomForestClassifier
from engine.ml.dataset_builder import DatasetBuilder

logger = logging.getLogger("DevShield.ContinuousTraining")

class ContinuousTrainingPipeline:
    JSONL_PATH = "ml_feedback.jsonl"
    MODEL_PATH = "vulnerability_classifier.pkl"
    BATCH_SIZE_THRESHOLD = 500  # Train after 500 interactions

    interaction_count = 0

    @classmethod
    def ingest_and_train(cls, interaction_data: dict):
        # 1. Store interaction
        import json
        with open(cls.JSONL_PATH, "a") as f:
            f.write(json.dumps(interaction_data) + "\n")
            
        cls.interaction_count += 1
        
        # 2. Continuous Learning Loop
        if cls.interaction_count >= cls.BATCH_SIZE_THRESHOLD:
            logger.info(f"Threshold of {cls.BATCH_SIZE_THRESHOLD} reached. Retraining Scikit-Learn models.")
            cls.train_model()
            cls.interaction_count = 0  # Reset

    @classmethod
    def train_model(cls):
        """Train Vulnerability Classifier (scikit-learn) and Save Weights"""
        X, Y = DatasetBuilder.build_from_jsonl(cls.JSONL_PATH)
        
        if not X or len(X) == 0 or len(Y) < 10:
            logger.warning("Dataset too small or invalid for reliable training. Need at least 10 entries.")
            return
            
        # Random Forest for False Positive Classification
        clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        clf.fit(X, Y)
        
        # Save model weights persistently
        joblib.dump(clf, cls.MODEL_PATH)
        logger.info(f"Model successfully saved to {cls.MODEL_PATH}. Inference endpoint updated.")
