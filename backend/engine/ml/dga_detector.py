import re
import math
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import structlog
from typing import List, Dict, Any
import asyncio
from backend.ai.gemini_handler import GeminiHandler

logger = structlog.get_logger("DevShield.ML.DGA")

class DGADetector:
    """
    True ML model for Domain Generation Algorithm (DGA) detection.
    Extracts URLs/Domains from code and uses a Random Forest classifier
    based on lexical features (entropy, vowel ratio, length, etc.) to 
    detect malicious Command & Control (C2) servers.
    """
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False
        self.gemini = GeminiHandler()
        
    def _shannon_entropy(self, s: str) -> float:
        p, lns = {}, float(len(s))
        for c in s: p[c] = p.get(c, 0) + 1
        return -sum(count/lns * math.log2(count/lns) for count in p.values())

    def _extract_features(self, domain: str) -> np.ndarray:
        """
        Extract lexical features from a domain name.
        """
        domain = domain.lower().split('.')[0] # Analyze the core domain
        if not domain:
            return np.zeros((1, 5))
            
        length = len(domain)
        entropy = self._shannon_entropy(domain)
        vowels = sum(1 for c in domain if c in 'aeiou')
        vowel_ratio = vowels / length if length > 0 else 0
        digits = sum(1 for c in domain if c.isdigit())
        digit_ratio = digits / length if length > 0 else 0
        consonants = length - vowels - digits
        consonant_ratio = consonants / length if length > 0 else 0
        
        return np.array([[length, entropy, vowel_ratio, digit_ratio, consonant_ratio]])

    def train(self):
        """
        Train the Random Forest on a mock dataset of benign (Alexa top) and malicious (DGA) domains.
        In a production system, this would load a massive pre-trained model.
        """
        # Benign examples (Google, Microsoft, Github, etc.)
        benign = ["google", "microsoft", "github", "apple", "amazon", "netflix", "linkedin"]
        # Malicious DGA examples (random alphanumeric gibberish)
        malicious = ["xkhjqoeb", "12984sjdfk", "zxcvbnmasdf", "qweoirutu", "laksjdfhgb", "njk123b4k2"]
        
        X = []
        y = []
        
        for d in benign:
            X.append(self._extract_features(d)[0])
            y.append(0) # 0 = Benign
            
        for d in malicious:
            X.append(self._extract_features(d)[0])
            y.append(1) # 1 = Malicious
            
        if len(X) > 0:
            self.model.fit(np.array(X), np.array(y))
            self.is_trained = True
            logger.info("DGA Detector trained successfully.")

    async def detect(self, code: str) -> List[Dict[str, Any]]:
        """
        Finds URLs in code and classifies them as benign or malicious using AI or Fallback ML.
        """
        findings = []
        urls = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)', code)
        domains_to_check = set(urls)
        
        # Filter out local IPs
        filtered_domains = [d for d in domains_to_check if not (d in ["localhost", "127.0.0.1"] or d.startswith("192.168.") or d.startswith("10."))]
        
        if not filtered_domains:
            return findings

        if self.gemini.model:
            prompt = f"Analyze these domains for DGA (Domain Generation Algorithm) characteristics. Return ONLY a JSON list of objects with 'domain', 'is_dga' (boolean), and 'confidence' (0-100).\nDomains: {filtered_domains}"
            try:
                response_text, _ = await self.gemini.generate_response(prompt)
                import json
                cleaned = response_text.replace('```json', '').replace('```', '').strip()
                results = json.loads(cleaned)
                for res in results:
                    if res.get("is_dga") and res.get("confidence", 0) > 70:
                        findings.append({
                            "title": "Malicious DGA Domain Detected (AI)",
                            "severity": "CRITICAL",
                            "confidence": res.get("confidence"),
                            "line": 1,
                            "description": f"AI Engine classified '{res.get('domain')}' as a potential C2 server (DGA).",
                            "cwe": "CWE-918",
                            "owasp": "A10:2021-SSRF"
                        })
                return findings
            except Exception as e:
                logger.error(f"Gemini API fallback for DGA failed: {e}")
        
        # Fallback to local ML model
        if not self.is_trained:
            self.train()
            
        for domain in filtered_domains:
            features = self._extract_features(domain)
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # If classified as Malicious (1) with >70% probability
            if prediction == 1 and probabilities[1] > 0.70:
                findings.append({
                    "title": "Malicious DGA Domain Detected",
                    "severity": "CRITICAL",
                    "confidence": int(probabilities[1] * 100),
                    "line": 1,
                    "description": f"The ML engine classified the domain '{domain}' as a potential Command & Control (C2) server generated by a Domain Generation Algorithm (DGA).",
                    "cwe": "CWE-918",
                    "owasp": "A10:2021-SSRF"
                })
                
        return findings

# Singleton
dga_detector = DGADetector()
