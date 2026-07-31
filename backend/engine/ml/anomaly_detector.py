import numpy as np
from sklearn.ensemble import IsolationForest
import structlog
from typing import List, Dict, Any
import ast

logger = structlog.get_logger("DevShield.ML.Anomaly")

class CodeAnomalyDetector:
    """
    True ML model for code anomaly detection.
    Uses an Isolation Forest to detect statistical outliers (potential logic bombs, obfuscation, or zero-days)
    based on code structure features extracted from AST.
    """
    def __init__(self):
        # Isolation Forest is excellent for outlier detection without labeled data
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=0.05, # Expecting 5% of code blocks to be highly anomalous
            random_state=42
        )
        self.is_trained = False
        self.feature_history = []

    def _extract_features(self, code: str) -> np.ndarray:
        """
        Extract statistical features from the code using Python's ast module.
        """
        try:
            tree = ast.parse(code)
            
            # Features:
            # 1. Total nodes
            # 2. Max depth
            # 3. Number of variables
            # 4. Number of function calls
            # 5. Number of imports
            # 6. Cyclomatic complexity approximation (num branches/loops)
            
            num_nodes = 0
            num_vars = 0
            num_calls = 0
            num_imports = 0
            num_branches = 0
            
            for node in ast.walk(tree):
                num_nodes += 1
                if isinstance(node, ast.Name):
                    num_vars += 1
                elif isinstance(node, ast.Call):
                    num_calls += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    num_imports += 1
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    num_branches += 1
                    
            # Normalize by length of code to get density
            lines = max(len(code.split('\n')), 1)
            
            features = [
                num_nodes / lines,
                num_vars / lines,
                num_calls / lines,
                num_imports / lines,
                num_branches / lines,
                len(code) / lines
            ]
            return np.array([features])
            
        except Exception:
            # Fallback features if parsing fails (obfuscated code often fails standard parsing)
            return np.array([[100.0, 100.0, 100.0, 0.0, 0.0, 100.0]])

    def train(self, code_samples: List[str]):
        """
        Train the anomaly detector on a baseline of known codebase samples.
        """
        features_list = []
        for sample in code_samples:
            features_list.append(self._extract_features(sample)[0])
            
        if len(features_list) > 10:
            X = np.array(features_list)
            self.model.fit(X)
            self.is_trained = True
            logger.info(f"Anomaly detector trained on {len(features_list)} samples.")

    def detect(self, code: str) -> Dict[str, Any]:
        """
        Evaluate code for anomalies.
        """
        if not self.is_trained:
            # If not trained, train it on some basic heuristics or just return false
            return {"is_anomalous": False, "confidence": 0}
            
        X = self._extract_features(code)
        prediction = self.model.predict(X)[0] # -1 for outlier, 1 for inlier
        score = self.model.decision_function(X)[0] # negative is more anomalous
        
        is_anomalous = (prediction == -1)
        
        # Convert score to a 0-100 anomaly confidence percentage
        # decision_function typically returns values between -0.5 and 0.5
        confidence = min(max(int((abs(score) / 0.5) * 100), 0), 100)
        
        if is_anomalous:
            return {
                "title": "Statistical Code Anomaly Detected",
                "severity": "HIGH",
                "confidence": confidence,
                "line": 1,
                "description": f"This code structure is a statistical outlier compared to the baseline codebase (Anomaly Score: {score:.3f}). This often indicates obfuscation, malicious logic bombs, or backdoors.",
                "cwe": "CWE-506",
                "owasp": "A08:2021-Software and Data Integrity Failures"
            }
        return {}

# Singleton instance
anomaly_detector = CodeAnomalyDetector()
