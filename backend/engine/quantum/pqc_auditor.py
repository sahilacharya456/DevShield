import re
import ast
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger("DevShield.Quantum.PQC")

# NIST PQC Standard replacements (NIST SP 800-227 IPD)
PQC_REPLACEMENTS = {
    "RSA": {
        "replacement": "CRYSTALS-Kyber (ML-KEM) for key encapsulation, CRYSTALS-Dilithium (ML-DSA) for signatures",
        "library": "pqcrypto>=0.1.0 or liboqs-python",
        "migration_code": """# Replace RSA with CRYSTALS-Kyber (NIST PQC KEM)
# pip install liboqs-python
import oqs

# Key Generation
kem = oqs.KeyEncapsulation('Kyber512')
public_key = kem.generate_keypair()

# Encapsulation (sender side)
ciphertext, shared_secret = kem.encap_secret(public_key)

# Decapsulation (receiver side)
shared_secret = kem.decap_secret(ciphertext)"""
    },
    "ECC": {
        "replacement": "CRYSTALS-Dilithium (ML-DSA) for digital signatures",
        "library": "pqcrypto or liboqs-python",
        "migration_code": """# Replace ECDSA with CRYSTALS-Dilithium (NIST ML-DSA)
import oqs

sig = oqs.Signature('Dilithium2')
public_key = sig.generate_keypair()
message = b'message to sign'
signature = sig.sign(message)
valid = sig.verify(message, signature, public_key)"""
    },
    "SHA1": {
        "replacement": "SHA-3 (256/512) — quantum-resistant hash function",
        "library": "hashlib (built-in)",
        "migration_code": """# Replace SHA-1 with SHA-3 (quantum-safe)
import hashlib

# Old (quantum-vulnerable):
# hashlib.sha1(data).hexdigest()

# New (quantum-resistant SHA-3):
hashed = hashlib.sha3_256(data).hexdigest()
# Or for 512-bit security:
hashed = hashlib.sha3_512(data).hexdigest()"""
    },
    "MD5": {
        "replacement": "BLAKE3 or SHA-3-256 for cryptographic hashing",
        "library": "blake3>=0.3.3 or hashlib (built-in)",
        "migration_code": """# Replace MD5 with BLAKE3 (modern, fast, quantum-safe)
# pip install blake3
import blake3
hashed = blake3.blake3(data).hexdigest()

# Or use built-in SHA-3:
import hashlib
hashed = hashlib.sha3_256(data).hexdigest()"""
    },
    "AES-128": {
        "replacement": "AES-256 (128-bit security degrades to 64-bit vs quantum Grover's attack)",
        "library": "cryptography>=42.0.0",
        "migration_code": """# Upgrade from AES-128 to AES-256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Use 256-bit key (32 bytes) instead of 128-bit (16 bytes)
key = os.urandom(32)  # AES-256
nonce = os.urandom(12)
aes = AESGCM(key)
ciphertext = aes.encrypt(nonce, plaintext, None)"""
    },
    "DES": {
        "replacement": "AES-256-GCM (DES has 56-bit key, trivially broken)",
        "library": "cryptography>=42.0.0",
        "migration_code": """# Replace DES with AES-256-GCM
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = os.urandom(32)  # 256-bit AES key
nonce = os.urandom(12)  # 96-bit nonce for GCM
aes = AESGCM(key)
ciphertext = aes.encrypt(nonce, plaintext, associated_data)"""
    },
    "RC4": {
        "replacement": "ChaCha20-Poly1305 for stream cipher use cases",
        "library": "cryptography>=42.0.0",
        "migration_code": """# Replace RC4 with ChaCha20-Poly1305
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os

key = ChaCha20Poly1305.generate_key()
nonce = os.urandom(12)
chacha = ChaCha20Poly1305(key)
ciphertext = chacha.encrypt(nonce, plaintext, None)"""
    },
}

# Regex patterns for vulnerable crypto usage
VULN_PATTERNS = [
    {
        "pattern": re.compile(r'(?:RSA|rsa)[\.\s_](?:generate|create|new|encrypt|decrypt|sign|verify|import)', re.IGNORECASE),
        "algo": "RSA",
        "severity": "CRITICAL",
        "title": "RSA Cryptography (Quantum-Vulnerable)",
        "cwe": "CWE-327",
        "description": "RSA will be broken by Shor's algorithm on quantum computers. NIST deprecated RSA for post-quantum security."
    },
    {
        "pattern": re.compile(r'(?:ECDSA|ECDH|EC|ECC|elliptic|secp256|P-256|P-384|P-521|prime256)', re.IGNORECASE),
        "algo": "ECC",
        "severity": "CRITICAL",
        "title": "Elliptic Curve Cryptography (Quantum-Vulnerable)",
        "cwe": "CWE-327",
        "description": "All ECC algorithms are broken by Shor's algorithm on quantum computers."
    },
    {
        "pattern": re.compile(r'(?:sha1|sha-1|hashlib\.sha1|SHA1|SHA-1)', re.IGNORECASE),
        "algo": "SHA1",
        "severity": "HIGH",
        "title": "SHA-1 Hash (Cryptographically Broken)",
        "cwe": "CWE-328",
        "description": "SHA-1 is collision-prone and provides only ~80-bit quantum security. NIST officially deprecated in 2011."
    },
    {
        "pattern": re.compile(r'(?:md5|hashlib\.md5|MD5)', re.IGNORECASE),
        "algo": "MD5",
        "severity": "CRITICAL",
        "title": "MD5 Hash (Cryptographically Broken)",
        "cwe": "CWE-328",
        "description": "MD5 is fully broken. Collision attacks are trivial. Never use for security purposes."
    },
    {
        "pattern": re.compile(r'AES[\.\-_]?128|AES\([\"\']?(?:128|16)[\"\']?', re.IGNORECASE),
        "algo": "AES-128",
        "severity": "HIGH",
        "title": "AES-128 (Weak Against Quantum Grover's Algorithm)",
        "cwe": "CWE-326",
        "description": "Grover's algorithm halves the effective key length. AES-128 provides only 64-bit quantum security. Use AES-256."
    },
    {
        "pattern": re.compile(r'(?:\bDES\b|3DES|TripleDES|des3|Cipher\.new.*DES)', re.IGNORECASE),
        "algo": "DES",
        "severity": "CRITICAL",
        "title": "DES/3DES Cipher (Deprecated)",
        "cwe": "CWE-327",
        "description": "DES is trivially broken (56-bit key). 3DES is deprecated by NIST (SP 800-131Ar2)."
    },
    {
        "pattern": re.compile(r'(?:\bRC4\b|ARC4|ARCFOUR)', re.IGNORECASE),
        "algo": "RC4",
        "severity": "CRITICAL",
        "title": "RC4 Stream Cipher (Cryptographically Broken)",
        "cwe": "CWE-327",
        "description": "RC4 has multiple known biases and is fully broken. Prohibited by RFC 7465."
    },
]


class PQCAuditor:
    """
    QuantumVault™ — Post-Quantum Cryptography Auditor.
    Scans codebases for quantum-vulnerable cryptographic operations
    and provides NIST PQC-compliant migration guidance.
    """

    def audit(self, code: str, filename: str = "code.py") -> Dict[str, Any]:
        """
        Comprehensive PQC audit of provided code.
        Returns findings with NIST PQC migration guidance.
        """
        findings = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for vuln_pattern in VULN_PATTERNS:
                if vuln_pattern["pattern"].search(line):
                    pqc_info = PQC_REPLACEMENTS.get(vuln_pattern["algo"], {})
                    findings.append({
                        "title": vuln_pattern["title"],
                        "severity": vuln_pattern["severity"],
                        "line": line_num,
                        "code_snippet": line.strip(),
                        "description": vuln_pattern["description"],
                        "cwe": vuln_pattern["cwe"],
                        "quantum_threat": (
                            "Shor's Algorithm"
                            if vuln_pattern["algo"] in ["RSA", "ECC"]
                            else "Grover's Algorithm"
                        ),
                        "nist_replacement": pqc_info.get("replacement", ""),
                        "migration_library": pqc_info.get("library", ""),
                        "migration_code": pqc_info.get("migration_code", ""),
                        "owasp": "A02:2021-Cryptographic Failures"
                    })

        # Keep all line-specific findings (each match is valuable for precise remediation)
        quantum_score = max(0, 100 - (len(findings) * 15))
        quantum_readiness = (
            "READY" if quantum_score >= 80
            else "AT_RISK" if quantum_score >= 50
            else "VULNERABLE"
        )

        critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in findings if f["severity"] == "HIGH")

        return {
            "filename": filename,
            "total_findings": len(findings),
            "critical_findings": critical_count,
            "high_findings": high_count,
            "quantum_score": quantum_score,
            "quantum_readiness": quantum_readiness,
            "findings": findings,
            "summary": (
                f"Found {len(findings)} quantum-vulnerable cryptographic operations "
                f"({critical_count} CRITICAL, {high_count} HIGH). "
                f"Quantum Score: {quantum_score}/100. "
                f"Readiness: {quantum_readiness}."
            )
        }

    def audit_ast(self, code: str, filename: str = "code.py") -> Dict[str, Any]:
        """
        Deep AST-based audit for Python code.
        Extracts import nodes, function calls, and attribute access
        to detect crypto library usage with higher precision.
        """
        ast_findings = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.warning(f"AST parse failed for {filename}: {e}. Falling back to regex audit.")
            return self.audit(code, filename)

        aliases: Dict[str, str] = {}

        def add_finding(algo: str, line: int, snippet: str, method: str):
            if not algo or algo not in PQC_REPLACEMENTS:
                return
            pqc_info = PQC_REPLACEMENTS[algo]
            severity = next((p["severity"] for p in VULN_PATTERNS if p["algo"] == algo), "HIGH")
            title = next((p["title"] for p in VULN_PATTERNS if p["algo"] == algo), f"{algo} Cryptography Detected")
            description = next((p["description"] for p in VULN_PATTERNS if p["algo"] == algo), f"Detected quantum-vulnerable {algo} usage.")
            cwe = next((p["cwe"] for p in VULN_PATTERNS if p["algo"] == algo), "CWE-327")
            ast_findings.append({
                "title": title if method == "call" else f"{algo} Import Detected (AST)",
                "severity": severity,
                "line": line,
                "code_snippet": snippet,
                "description": description if method == "call" else f"Direct import of quantum-vulnerable {algo} library.",
                "cwe": cwe,
                "quantum_threat": "Shor's Algorithm" if algo in ["RSA", "ECC"] else "Grover's Algorithm",
                "nist_replacement": pqc_info.get("replacement", ""),
                "migration_library": pqc_info.get("library", ""),
                "migration_code": pqc_info.get("migration_code", ""),
                "owasp": "A02:2021-Cryptographic Failures",
                "detection_method": f"AST-{method}"
            })

        # Walk AST looking for crypto-related imports and calls.
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    bound_name = alias.asname or alias.name.split(".")[0]
                    aliases[bound_name] = alias.name
                    algo = self._classify_name(alias.name)
                    if algo:
                        add_finding(algo, node.lineno, f"import {alias.name}", "import")

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    bound_name = alias.asname or alias.name
                    aliases[bound_name] = full_name
                    algo = self._classify_name(full_name)
                    if algo:
                        add_finding(algo, node.lineno, f"from {module} import {alias.name}", "import")

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_name = self._call_name(node.func, aliases)
            algo = self._classify_name(call_name)
            if algo:
                add_finding(algo, getattr(node, "lineno", 1), call_name, "call")
                continue

            # AES-128 detection from common 16-byte key slicing/length patterns.
            if "AES.new" in call_name or "AESGCM" in call_name:
                for arg in node.args:
                    if isinstance(arg, ast.Subscript) and isinstance(arg.slice, ast.Slice):
                        upper = arg.slice.upper
                        if isinstance(upper, ast.Constant) and upper.value == 16:
                            add_finding("AES-128", getattr(node, "lineno", 1), call_name, "call")
                    elif isinstance(arg, ast.Call) and self._call_name(arg.func, aliases).endswith("urandom"):
                        if arg.args and isinstance(arg.args[0], ast.Constant) and arg.args[0].value == 16:
                            add_finding("AES-128", getattr(node, "lineno", 1), call_name, "call")

        # Merge with regex findings (deduplicated by line)
        regex_result = self.audit(code, filename)
        seen_keys = {(f["line"], f["title"]) for f in ast_findings}
        for finding in regex_result["findings"]:
            if (finding["line"], finding["title"]) not in seen_keys:
                finding["detection_method"] = "regex"
                ast_findings.append(finding)

        total = len(ast_findings)
        quantum_score = max(0, 100 - (total * 15))
        quantum_readiness = (
            "READY" if quantum_score >= 80
            else "AT_RISK" if quantum_score >= 50
            else "VULNERABLE"
        )

        return {
            "filename": filename,
            "total_findings": total,
            "quantum_score": quantum_score,
            "quantum_readiness": quantum_readiness,
            "findings": ast_findings,
            "summary": (
                f"AST+Regex scan: {total} quantum-vulnerable operations found. "
                f"Quantum Score: {quantum_score}/100."
            )
        }

    def _classify_module(self, module: str) -> str:
        """Map a Python module name to a crypto algorithm category."""
        return self._classify_name(module)

    def _classify_name(self, name: str) -> str:
        """Map an import/call name to a crypto algorithm category."""
        name_lower = (name or "").lower()
        if "hashlib.md5" in name_lower or name_lower.endswith(".md5") or name_lower == "md5":
            return "MD5"
        if "hashlib.sha1" in name_lower or name_lower.endswith(".sha1") or "sha-1" in name_lower:
            return "SHA1"
        if "crypto.publickey.rsa" in name_lower or name_lower in {"rsa", "rsa.generate_private_key"} or ".rsa" in name_lower:
            return "RSA"
        if any(token in name_lower for token in ["ecdsa", "ecdh", "elliptic", "secp", "prime256", "cryptography.hazmat.primitives.asymmetric.ec"]):
            return "ECC"
        if "crypto.cipher.des3" in name_lower or "tripledes" in name_lower or "3des" in name_lower:
            return "DES"
        if "crypto.cipher.des" in name_lower or name_lower.endswith(".des") or ".des." in name_lower:
            return "DES"
        if "arc4" in name_lower or "rc4" in name_lower:
            return "RC4"
        if "rsa" in name_lower:
            return "RSA"
        if "ecdsa" in name_lower or "ecc" in name_lower or "elliptic" in name_lower:
            return "ECC"
        if "des" in name_lower:
            return "DES"
        if "rc4" in name_lower or "arc4" in name_lower:
            return "RC4"
        if "md5" in name_lower:
            return "MD5"
        return ""

    def _call_name(self, node: ast.AST, aliases: Dict[str, str]) -> str:
        if isinstance(node, ast.Name):
            return aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            parent = self._call_name(node.value, aliases)
            return f"{parent}.{node.attr}" if parent else node.attr
        if isinstance(node, ast.Call):
            return self._call_name(node.func, aliases)
        return ""


# Module-level singleton
pqc_auditor = PQCAuditor()
