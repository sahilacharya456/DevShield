import asyncio
from backend.engine.sast.tree_sitter_analyzer import run_sast
from backend.engine.sca.osv_scanner import run_sca
from backend.engine.container.docker_scanner import run_container_scan

class SecurityAgent:
    """
    Orchestrates the new true security engines (Tree-Sitter AST, OSV API, Docker AST).
    """
    def __init__(self):
        pass

    async def analyze(self, code: str, filename: str = "app.py") -> dict:
        findings = []
        
        # 1. Run SAST (Tree-sitter AST)
        if filename.endswith(".py"):
            sast_findings = run_sast(code, language="python")
            findings.extend(sast_findings)
            
        # 2. Run SCA (OSV API)
        if filename == "requirements.txt" or filename == "package.json":
            sca_findings = await run_sca(code)
            findings.extend(sca_findings)
            
        # 3. Run Container Scan (Dockerfile AST)
        if "Dockerfile" in filename:
            container_findings = run_container_scan(code)
            findings.extend(container_findings)
            
        # 4. ML Anomaly Detection (Zero-day / Obfuscation)
        from backend.engine.ml.anomaly_detector import anomaly_detector
        if not anomaly_detector.is_trained and filename.endswith(".py"):
            # Auto-train on the first few snippets (simplified for demo)
            anomaly_detector.train([
                "def hello(): print('world')", 
                "class A: pass", 
                "import os\nprint(os.getcwd())",
                "x = [i for i in range(10)]",
                "def test(): return 1+1",
                "from typing import List\ndef f(x: List[int]) -> int: return sum(x)",
                "import json\njson.dumps({'a': 1})",
                "import requests\nr = requests.get('http://google.com')",
                "def main(): pass",
                "if __name__ == '__main__': main()",
                "class Config:\n    DEBUG = False\n    SECRET_KEY = 'abc'",
                "def validate(email):\n    import re\n    return re.match(r'[^@]+@[^@]+', email)",
                "from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef index():\n    return 'hello'",
            ])
            
        if anomaly_detector.is_trained:
            anomaly = anomaly_detector.detect(code)
            if anomaly:
                findings.append(anomaly)
                
        # 5. ML DGA (Domain Generation Algorithm) Detection
        from backend.engine.ml.dga_detector import dga_detector
        dga_findings = await dga_detector.detect(code)
        findings.extend(dga_findings)
        
        # 6. Deep Neural Network (Secret Entropy Classification)
        from backend.engine.ml.secret_neural_net import secret_neural_net
        secret_findings = secret_neural_net.detect(code)
        findings.extend(secret_findings)

        # Calculate dynamic score
        score = 100
        priorities = []
        for v in findings:
            sev = v.get('severity', 'INFO')
            if sev == 'CRITICAL': 
                score -= 20
                priorities.append(v['title'])
            elif sev == 'HIGH': 
                score -= 10
            elif sev == 'MEDIUM': 
                score -= 5
            elif sev == 'LOW': 
                score -= 2
                
        score = max(0, score)
        
        return {
            "overall_score": score,
            "vulnerabilities": findings,
            "remediation_priorities": list(set(priorities))
        }
