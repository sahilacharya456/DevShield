import ast
import math
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import structlog
from typing import Dict, Any, List, Optional
import re

logger = structlog.get_logger("DevShield.Cognitive.DNA")


class DeveloperFingerprinter:
    """
    CognitiveDNA™ — Developer Behavioral Fingerprinting.

    Learns each developer's unique coding style (variable naming, comment density,
    function length, cyclomatic complexity, import patterns, indentation habits)
    and detects when a commit does NOT match their historical style.

    Catches: insider threats, compromised accounts, malicious open-source contributor injections.
    """

    def __init__(self):
        self.developer_profiles: Dict[str, np.ndarray] = {}  # username -> mean feature vector
        self.developer_samples: Dict[str, List[np.ndarray]] = {}  # username -> list of feature vectors
        self.developer_std: Dict[str, np.ndarray] = {}  # username -> std deviation of features
        self.scaler = StandardScaler()
        self.is_calibrated = False

    def _extract_style_features(self, code: str) -> np.ndarray:
        """
        Extract 20 coding style features from a code snippet.
        These form the developer's unique "coding DNA".
        """
        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        total_lines = max(len(non_empty_lines), 1)

        try:
            tree = ast.parse(code)
        except SyntaxError:
            tree = None

        # === Feature Group 1: Naming Style ===
        snake_case_count = len(re.findall(r'\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b', code))
        camel_case_count = len(re.findall(r'\b[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b', code))
        screaming_snake = len(re.findall(r'\b[A-Z][A-Z0-9_]+[A-Z0-9]\b', code))
        naming_ratio = snake_case_count / (camel_case_count + 1)  # >1 = snake_case person

        # === Feature Group 2: Comment Behavior ===
        comment_lines = len(re.findall(r'^\s*#', code, re.MULTILINE))
        inline_comments = len(re.findall(r'[^#]#[^!].+', code))
        docstring_count = code.count('"""') // 2 + code.count("'''") // 2
        comment_density = (comment_lines + inline_comments) / total_lines

        # === Feature Group 3: Code Structure ===
        blank_line_count = len([l for l in lines if not l.strip()])
        blank_line_density = blank_line_count / max(len(lines), 1)

        # Average line length
        avg_line_length = sum(len(l) for l in non_empty_lines) / total_lines

        # Indentation style (tabs vs spaces, depth)
        tab_lines = len([l for l in non_empty_lines if l.startswith("\t")])
        space_lines = len([l for l in non_empty_lines if l.startswith(" ")])
        uses_tabs = 1.0 if tab_lines > space_lines else 0.0

        # Average indentation depth
        indent_depths = []
        for l in non_empty_lines:
            stripped = l.lstrip()
            if stripped:
                indent = len(l) - len(stripped)
                indent_depths.append(indent)
        avg_indent = sum(indent_depths) / max(len(indent_depths), 1)

        # === Feature Group 4: AST-based Features ===
        func_count = 0
        class_count = 0
        func_lengths = []
        one_liner_count = 0
        lambda_count = 0
        list_comp_count = 0

        if tree:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_count += 1
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        func_len = node.end_lineno - node.lineno
                        func_lengths.append(func_len)
                        if func_len <= 1:
                            one_liner_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
                elif isinstance(node, ast.Lambda):
                    lambda_count += 1
                elif isinstance(node, ast.ListComp):
                    list_comp_count += 1

        avg_func_length = sum(func_lengths) / max(len(func_lengths), 1)
        func_density = func_count / total_lines
        lambda_preference = lambda_count / (func_count + 1)
        list_comp_preference = list_comp_count / (func_count + 1)

        # === Feature Group 5: Import Style ===
        from_imports = len(re.findall(r'^from .+ import', code, re.MULTILINE))
        direct_imports = len(re.findall(r'^import ', code, re.MULTILINE))
        from_import_ratio = from_imports / (direct_imports + from_imports + 1)

        # === Feature Group 6: String Style ===
        single_quote = len(re.findall(r"'[^'\n]*'", code))
        double_quote = len(re.findall(r'"[^"\n]*"', code))
        quote_preference = single_quote / (double_quote + 1)  # >1 = single quote person

        features = np.array([
            naming_ratio,                           # 1. snake_case vs camelCase preference
            comment_density,                        # 2. How much they comment
            docstring_count / total_lines,          # 3. Docstring usage
            inline_comments / total_lines,          # 4. Inline comment frequency
            blank_line_density,                     # 5. How much whitespace they use
            avg_line_length,                        # 6. Line length preference
            uses_tabs,                              # 7. Tabs vs spaces
            avg_indent,                             # 8. Average indentation depth
            func_density,                           # 9. Function density (functions per line)
            avg_func_length,                        # 10. Average function length
            one_liner_count / (func_count + 1),    # 11. One-liner preference
            lambda_preference,                      # 12. Lambda usage rate
            list_comp_preference,                   # 13. List comprehension preference
            class_count / total_lines,              # 14. Class density
            from_import_ratio,                      # 15. from X import vs import X preference
            quote_preference,                       # 16. Single vs double quote preference
            screaming_snake / total_lines,          # 17. Constant naming frequency
            (func_count + class_count) / total_lines,          # 18. Code organization density
            avg_func_length / (avg_line_length + 1),           # 19. Verbosity ratio
            (lambda_count + list_comp_count) / (func_count + 1),  # 20. Pythonic-ness
        ], dtype=np.float64)

        return features

    def train_developer(self, developer_id: str, code_samples: List[str]) -> bool:
        """
        Build a behavioral profile for a developer from their historical code.
        Requires at least 3 samples for a meaningful profile.
        """
        if len(code_samples) < 3:
            logger.warning(
                "insufficient_samples",
                developer_id=developer_id,
                count=len(code_samples),
                required=3
            )
            return False

        feature_vectors = []
        for idx, sample in enumerate(code_samples):
            try:
                features = self._extract_style_features(sample)
                feature_vectors.append(features)
            except Exception as e:
                logger.error(
                    "feature_extraction_failed",
                    developer_id=developer_id,
                    sample_index=idx,
                    error=str(e)
                )

        if not feature_vectors:
            return False

        feature_matrix = np.array(feature_vectors)
        self.developer_samples[developer_id] = feature_vectors
        # Profile = mean feature vector (the developer's "average" style)
        self.developer_profiles[developer_id] = np.mean(feature_matrix, axis=0)
        # Store std-dev for anomaly scoring
        self.developer_std[developer_id] = np.std(feature_matrix, axis=0) + 1e-8  # avoid div/0

        logger.info(
            "profile_built",
            developer_id=developer_id,
            sample_count=len(feature_vectors)
        )
        return True

    def verify_author(self, developer_id: str, code: str) -> Dict[str, Any]:
        """
        Verify if a piece of code matches the registered developer's style.
        Returns similarity score and anomaly assessment.
        """
        if developer_id not in self.developer_profiles:
            return {
                "developer_id": developer_id,
                "verified": None,
                "similarity_score": 0,
                "alert": False,
                "severity": "INFO",
                "message": f"No profile registered for '{developer_id}'. Run /cognitive/train first.",
                "feature_breakdown": {}
            }

        current_features = self._extract_style_features(code)
        profile_features = self.developer_profiles[developer_id]
        profile_std = self.developer_std.get(developer_id, np.ones_like(profile_features))

        # Primary metric: cosine similarity
        similarity = cosine_similarity(
            current_features.reshape(1, -1),
            profile_features.reshape(1, -1)
        )[0][0]
        similarity_percent = int(similarity * 100)

        # Secondary metric: z-score based anomaly detection per feature
        z_scores = np.abs((current_features - profile_features) / profile_std)
        high_deviation_features = int(np.sum(z_scores > 2.0))  # features >2σ from mean
        anomaly_pressure = min(40, high_deviation_features * 8)  # bonus penalty for outliers

        # Combined adjusted score
        adjusted_similarity = max(0, similarity_percent - anomaly_pressure)

        # Threshold: below 65% is suspicious
        alert = adjusted_similarity < 65
        severity = "LOW"
        if adjusted_similarity < 40:
            severity = "CRITICAL"
        elif adjusted_similarity < 55:
            severity = "HIGH"
        elif adjusted_similarity < 65:
            severity = "MEDIUM"

        feature_names = [
            "naming_style", "comment_density", "docstring_usage", "inline_comments",
            "blank_line_density", "avg_line_length", "uses_tabs", "avg_indent",
            "func_density", "avg_func_length", "one_liner_pref", "lambda_pref",
            "list_comp_pref", "class_density", "from_import_ratio", "quote_pref",
            "constant_naming", "org_density", "verbosity_ratio", "pythonic_score"
        ]

        feature_breakdown = {}
        for i, name in enumerate(feature_names):
            if i < len(current_features):
                feature_breakdown[name] = {
                    "current": round(float(current_features[i]), 4),
                    "profile_mean": round(float(profile_features[i]), 4),
                    "deviation_sigma": round(float(z_scores[i]), 2),
                    "anomalous": bool(z_scores[i] > 2.0)
                }

        return {
            "developer_id": developer_id,
            "verified": not alert,
            "similarity_score": similarity_percent,
            "adjusted_similarity_score": adjusted_similarity,
            "high_deviation_features": high_deviation_features,
            "alert": alert,
            "severity": severity if alert else "INFO",
            "message": (
                f"⚠️ ALERT: Code style deviates significantly from '{developer_id}' profile "
                f"(Similarity: {similarity_percent}%, Adjusted: {adjusted_similarity}%). "
                f"{high_deviation_features} features exceed 2σ from baseline. "
                f"Possible insider threat or account compromise."
            ) if alert else (
                f"✅ Code style verified. Matches '{developer_id}' profile "
                f"(Similarity: {similarity_percent}%, {high_deviation_features} anomalous features)."
            ),
            "feature_breakdown": feature_breakdown,
            "owasp": "A07:2021-Identification and Authentication Failures"
        }

    def get_profile_summary(self, developer_id: str) -> Dict[str, Any]:
        """Return a summary of a developer's registered style profile."""
        if developer_id not in self.developer_profiles:
            return {"error": f"No profile found for '{developer_id}'"}

        profile = self.developer_profiles[developer_id]
        sample_count = len(self.developer_samples.get(developer_id, []))

        return {
            "developer_id": developer_id,
            "sample_count": sample_count,
            "style_summary": {
                "naming_style": "snake_case" if profile[0] > 1.5 else "camelCase" if profile[0] < 0.5 else "mixed",
                "avg_comment_density": round(float(profile[1]), 3),
                "avg_line_length": round(float(profile[5]), 1),
                "indentation": "tabs" if profile[6] > 0.5 else "spaces",
                "avg_func_length": round(float(profile[9]), 1),
                "pythonic_score": round(float(profile[19]), 3),
            }
        }

    def list_profiles(self) -> List[str]:
        """List all registered developer IDs."""
        return list(self.developer_profiles.keys())

    def remove_profile(self, developer_id: str) -> bool:
        """Remove a developer's profile (e.g., for off-boarding)."""
        removed = False
        for store in [self.developer_profiles, self.developer_samples, self.developer_std]:
            if developer_id in store:
                del store[developer_id]
                removed = True
        if removed:
            logger.info("profile_removed", developer_id=developer_id)
        return removed


# Module-level singleton
developer_fingerprinter = DeveloperFingerprinter()
