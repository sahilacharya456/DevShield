import os
import math
import structlog
import yara
from cryptography.fernet import Fernet
from typing import Dict, Any

logger = structlog.get_logger("DevShield.Aegis")

# Base YARA rules for demonstration in FYP
YARA_RULES = """
rule Suspicious_Script {
    strings:
        $eval = "eval("
        $b64 = "base64_decode"
        $shell = "WScript.Shell"
        $cmd = "cmd.exe"
        $ps = "powershell.exe -w hidden"
    condition:
        2 of them
}
rule EICAR_Test {
    strings:
        $eicar = "X5O!P%@AP[4\\\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    condition:
        $eicar
}
rule Generic_Trojan {
    strings:
        $mz = { 4D 5A } // Windows executable
        $socket = "socket("
        $connect = "connect("
        $createproc = "CreateProcess"
    condition:
        $mz at 0 and all of them
}
"""

class AegisEngine:
    def __init__(self):
        self.rules = yara.compile(source=YARA_RULES)
        self.quarantine_dir = os.path.join("backend", "quarantine_vault")
        os.makedirs(self.quarantine_dir, exist_ok=True)
        # In a real system, this key must be securely managed in a KMS or Vault.
        # For FYP purposes, we use a static derived key to lock the malware.
        self.cipher = Fernet(Fernet.generate_key())

    def calculate_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log2(p_x)
        return entropy

    def quarantine(self, filepath: str) -> str:
        with open(filepath, "rb") as f:
            data = f.read()
            
        encrypted_data = self.cipher.encrypt(data)
        
        filename = os.path.basename(filepath)
        vault_path = os.path.join(self.quarantine_dir, f"{filename}.locked")
        
        with open(vault_path, "wb") as f:
            f.write(encrypted_data)
            
        # Strip all execution and read permissions (000 in octal)
        try:
            os.chmod(vault_path, 0o000)
        except Exception:
            pass # Windows might ignore strict 000, but encryption holds
        
        # Delete original
        os.remove(filepath)
        
        logger.warning(f"Aegis Engine: Malicious file {filename} successfully KILLED and locked in Vault.")
        return vault_path

    async def scan_file(self, filepath: str) -> Dict[str, Any]:
        with open(filepath, "rb") as f:
            data = f.read()
            
        entropy = self.calculate_entropy(data)
        matches = self.rules.match(data=data)
        
        is_malicious = len(matches) > 0 or entropy > 7.5
        
        result = {
            "status": "success",
            "file": os.path.basename(filepath).split('_', 1)[-1] if '_' in os.path.basename(filepath) else os.path.basename(filepath),
            "entropy": round(entropy, 2),
            "is_packed": entropy > 7.5,
            "yara_matches": [m.rule for m in matches],
            "threat_detected": is_malicious,
        }
        
        if is_malicious:
            vault_path = self.quarantine(filepath)
            result["action_taken"] = "KILLED_AND_QUARANTINED"
            result["vault_path"] = vault_path
            result["message"] = "Malware successfully destroyed and isolated."
        else:
            result["action_taken"] = "CLEAN"
            result["message"] = "File is clean."
            os.remove(filepath) # cleanup
            
        return result
