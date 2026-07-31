import urllib.request
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.ml.vuln_classifier import VulnClassifier

def fetch_payloads(url: str, limit=500):
    try:
        print(f"Fetching from {url}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            lines = content.splitlines()
            payloads = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
            return payloads[:limit]
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

def main():
    print("--- Starting Robust ML Model Training ---")
    
    # 1. Gather Payloads from open intelligence lists
    sqli_payloads = fetch_payloads("https://raw.githubusercontent.com/payloadbox/sql-injection-payload-list/master/Intruder/exploit/1_SQLi_CMDi_Fuzzing.txt", 1000)
    xss_payloads = fetch_payloads("https://raw.githubusercontent.com/payloadbox/xss-payload-list/master/Intruder/xss-payload-list.txt", 1000)
    cmd_payloads = fetch_payloads("https://raw.githubusercontent.com/payloadbox/command-injection-payload-list/master/payloads.txt", 1000)
    
    if not sqli_payloads:
        sqli_payloads = ["' OR 1=1--", "UNION SELECT * FROM users", "'; DROP TABLE users--"]
    if not xss_payloads:
        xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]
    if not cmd_payloads:
        cmd_payloads = ["; cat /etc/passwd", "| ping -c 5 127.0.0.1", "`id`"]

    print(f"Gathered {len(sqli_payloads)} SQLi, {len(xss_payloads)} XSS, {len(cmd_payloads)} CMDi payloads.")

    # 2. Synthesize Code Snippets mapping payloads to vulnerability contexts
    X = []
    y = []

    # Synthesize SQLi
    for p in sqli_payloads:
        X.append(f'query = f"SELECT * FROM data WHERE user = \'{p}\'"\ncursor.execute(query)')
        y.append("sql_injection")
    
    # Synthesize XSS
    for p in xss_payloads:
        X.append(f'return "<h1>Hello " + request.get("name", "{p}") + "</h1>"')
        y.append("xss")

    # Synthesize CMDi
    for p in cmd_payloads:
        X.append(f'import os\nos.system("ping " + "{p}")')
        y.append("command_injection")

    # Synthesize Hardcoded Secrets
    secrets = [
        "password = 'super_secret_admin_pw123'",
        "API_KEY = 'sk_live_1234567890abcdef'",
        "token = 'ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ'",
        "db_secret = 'P@ssw0rd!'"
    ] * 50
    for s in secrets:
        X.append(f"def connect_db():\n    {s}\n    return True")
        y.append("hardcoded_secrets")

    # Synthesize Benign / Safe Code
    safe_snippets = [
        "def add(a, b): return a + b",
        "import math\nprint(math.pi)",
        "name = 'John'\nprint(f'Hello {name}')",
        "class User:\n    def __init__(self, name):\n        self.name = name",
        "for i in range(10):\n    print(i)",
        "query = 'SELECT * FROM users WHERE id = %s'\ncursor.execute(query, (user_id,))"
    ] * 200
    
    for s in safe_snippets:
        X.append(s)
        y.append("safe")

    print(f"Total synthetic dataset size: {len(X)} samples.")

    # 3. Train the Model
    clf = VulnClassifier()
    print("Training the GradientBoostingClassifier on the gathered dataset...")
    clf.train(X, y)
    print("Training complete! Model saved to ~/.devshield/classifier.pkl")

if __name__ == "__main__":
    main()
