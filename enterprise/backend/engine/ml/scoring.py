import logging
from typing import Dict, List

logger = logging.getLogger("DevShield.ScoringEngine")

class ConfidenceScorer:
    """Blends static, ML, and LLM signals to create a 0-100 reliability score."""
    
    @staticmethod
    def calculate_score(llm_confidence: int, static_findings: List[Dict], ml_false_positives: int) -> int:
        """
        llm_confidence: 0-10 reported by Gemini/Groq
        static_findings: list of vulnerabilities caught by Semgrep
        ml_false_positives: number of issues flagged as false positives by ML
        """
        
        # Base score from LLM (0-100)
        score = llm_confidence * 10
        
        # Penalty for high severity static findings
        static_penalty = 0
        for vuln in static_findings:
            sev = vuln.get("severity", "LOW").upper()
            if sev == "CRITICAL":
                static_penalty += 20
            elif sev == "HIGH":
                static_penalty += 10
            elif sev == "MEDIUM":
                static_penalty += 5
                
        # Bonus for ML filtering correctly
        ml_bonus = ml_false_positives * 5
        
        final_score = score - static_penalty + ml_bonus
        
        # Constrain 0 to 100
        return max(0, min(100, final_score))
