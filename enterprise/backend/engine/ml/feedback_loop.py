import json
import os
import logging
from typing import Dict, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger("DevShield.MLPipeline")

class MLFeedbackPipeline:
    JSONL_PATH = "ml_feedback.jsonl"
    _model = None
    _vectorizer = None

    @classmethod
    def ingest(cls, feedback_req):
        """Ingest feedback and append to JSONL dataset."""
        data = {
            "issue_id": feedback_req.issue_id,
            "is_false_positive": feedback_req.is_false_positive,
            "user_comment": feedback_req.user_comment
        }
        with open(cls.JSONL_PATH, "a") as f:
            f.write(json.dumps(data) + "\n")
            
        logger.info(f"Ingested ML feedback for {feedback_req.issue_id}")
        cls.train()

    @classmethod
    def train(cls):
        """Train Random Forest classifier on historically reported false positives."""
        if not os.path.exists(cls.JSONL_PATH):
            return
            
        X_texts = []
        y_labels = []
        
        with open(cls.JSONL_PATH, "r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    # For a real pipeline, we'd pull the actual vulnerability description and AST text here using the issue_id
                    X_texts.append(record.get("issue_id", ""))
                    y_labels.append(1 if record.get("is_false_positive") else 0)
                except Exception:
                    continue
                    
        if len(X_texts) < 10:
            # Need minimum samples to train effectively
            return
            
        cls._vectorizer = TfidfVectorizer(max_features=1000)
        X_vectors = cls._vectorizer.fit_transform(X_texts).toarray()
        
        cls._model = RandomForestClassifier(n_estimators=50, random_state=42)
        cls._model.fit(X_vectors, y_labels)
        logger.info("ML Classifier retrained successfully on new dataset.")

    @classmethod
    def filter_false_positives(cls, report: Dict) -> Dict:
        """Use trained ML model to filter out predicted false positives from Semgrep/AI results."""
        if cls._model is None or cls._vectorizer is None:
            return report # Pass-through if not trained
            
        filtered_vulns = []
        for vuln in report.get("vulnerabilities", []):
            text_feature = f"{vuln['name']} {vuln['description']} {vuln['source']}"
            vec = cls._vectorizer.transform([text_feature]).toarray()
            is_fp = cls._model.predict(vec)[0]
            
            if not is_fp:
                filtered_vulns.append(vuln)
                
        report["vulnerabilities"] = filtered_vulns
        report["total_issues"] = len(filtered_vulns)
        return report
