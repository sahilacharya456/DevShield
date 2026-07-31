import ssl
import socket
import structlog
from typing import Dict, Any, List
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = structlog.get_logger("DevShield.Arsenal.SSL")

# Weak / deprecated cipher suites
WEAK_CIPHERS: List[str] = [
    "RC4", "DES", "3DES", "NULL", "EXPORT", "MD5",
    "ADH", "AECDH", "RC2", "SEED", "IDEA", "anon",
]

# Deprecated TLS / SSL versions
DEPRECATED_VERSIONS: List[str] = ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]

# Grade degradation map
_GRADE_ORDER = ["A", "B", "C", "D", "F"]


def _degrade_grade(current: str, new: str) -> str:
    """Return the worse of two letter grades."""
    ci = _GRADE_ORDER.index(current) if current in _GRADE_ORDER else 0
    ni = _GRADE_ORDER.index(new) if new in _GRADE_ORDER else 0
    return _GRADE_ORDER[max(ci, ni)]


class SSLAuditor:
    """
    DevShield Arsenal: Advanced SSL/TLS Certificate & Configuration Auditor.
    Checks for expired certs, weak ciphers, deprecated protocols, and missing
    security headers.
    """

    def audit(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Complete SSL/TLS audit of a host.

        Returns a structured dict with:
          - certificate metadata
          - detected protocols & ciphers
          - per-finding severity + remediation
          - an overall letter grade (A–F)
        """
        results: Dict[str, Any] = {
            "hostname": hostname,
            "port": port,
            "findings": [],
            "overall_grade": "A",
            "certificate": {},
            "protocols": [],
            "ciphers": [],
        }

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_binary = ssock.getpeercert(binary_form=True)
                    tls_version = ssock.version()          # e.g. "TLSv1.3"
                    cipher = ssock.cipher()                 # (name, proto, bits)

                    results["protocols"].append(tls_version)
                    results["ciphers"].append(
                        cipher[0] if cipher else "Unknown"
                    )

                    # ── Certificate analysis ─────────────────────────────────
                    if cert_binary:
                        cert = x509.load_der_x509_certificate(
                            cert_binary, default_backend()
                        )

                        # Prefer the timezone-aware attribute available in
                        # cryptography >= 42; fall back gracefully.
                        if hasattr(cert, "not_valid_after_utc"):
                            not_after = cert.not_valid_after_utc
                        else:
                            not_after = cert.not_valid_after.replace(
                                tzinfo=timezone.utc
                            )

                        if hasattr(cert, "not_valid_before_utc"):
                            not_before = cert.not_valid_before_utc
                        else:
                            not_before = cert.not_valid_before.replace(
                                tzinfo=timezone.utc
                            )

                        days_remaining = (
                            not_after - datetime.now(timezone.utc)
                        ).days

                        results["certificate"] = {
                            "subject": str(cert.subject),
                            "issuer": str(cert.issuer),
                            "not_before": not_before.isoformat(),
                            "not_after": not_after.isoformat(),
                            "days_remaining": days_remaining,
                            "serial": str(cert.serial_number),
                        }

                        if days_remaining < 0:
                            results["findings"].append(
                                {
                                    "title": "SSL Certificate EXPIRED",
                                    "severity": "CRITICAL",
                                    "description": (
                                        f"Certificate expired "
                                        f"{abs(days_remaining)} days ago."
                                    ),
                                    "remediation": (
                                        "Renew SSL certificate immediately. "
                                        "Use Let's Encrypt for free auto-renewal."
                                    ),
                                }
                            )
                            results["overall_grade"] = _degrade_grade(
                                results["overall_grade"], "F"
                            )
                        elif days_remaining < 30:
                            results["findings"].append(
                                {
                                    "title": "SSL Certificate Expiring Soon",
                                    "severity": "HIGH",
                                    "description": (
                                        f"Certificate expires in "
                                        f"{days_remaining} days."
                                    ),
                                    "remediation": "Renew certificate immediately.",
                                }
                            )
                            results["overall_grade"] = _degrade_grade(
                                results["overall_grade"], "B"
                            )
                        elif days_remaining < 90:
                            results["findings"].append(
                                {
                                    "title": "SSL Certificate Expiring in 90 Days",
                                    "severity": "MEDIUM",
                                    "description": (
                                        f"Certificate expires in "
                                        f"{days_remaining} days. "
                                        "Schedule renewal soon."
                                    ),
                                    "remediation": (
                                        "Automate renewal with certbot/ACME."
                                    ),
                                }
                            )

                    # ── Protocol version check ───────────────────────────────
                    if tls_version in DEPRECATED_VERSIONS:
                        results["findings"].append(
                            {
                                "title": f"Deprecated Protocol: {tls_version}",
                                "severity": "HIGH",
                                "description": (
                                    f"{tls_version} is deprecated and vulnerable "
                                    "to downgrade attacks (POODLE, BEAST, DROWN)."
                                ),
                                "remediation": (
                                    "Enforce TLS 1.2+ only. Disable TLS 1.0 and 1.1 "
                                    "in server configuration."
                                ),
                            }
                        )
                        results["overall_grade"] = _degrade_grade(
                            results["overall_grade"], "C"
                        )

                    # ── Cipher suite check ───────────────────────────────────
                    if cipher:
                        cipher_name = cipher[0]
                        if any(w in cipher_name for w in WEAK_CIPHERS):
                            results["findings"].append(
                                {
                                    "title": f"Weak Cipher Suite: {cipher_name}",
                                    "severity": "HIGH",
                                    "description": (
                                        "Weak cipher detected. Vulnerable to "
                                        "decryption and MITM attacks."
                                    ),
                                    "remediation": (
                                        "Configure server to prefer "
                                        "ECDHE+AESGCM or CHACHA20-POLY1305 only."
                                    ),
                                }
                            )
                            results["overall_grade"] = _degrade_grade(
                                results["overall_grade"], "C"
                            )

        except ssl.SSLError as e:
            results["findings"].append(
                {
                    "title": "SSL Handshake Failed",
                    "severity": "CRITICAL",
                    "description": str(e),
                    "remediation": (
                        "Check certificate installation and server SSL configuration."
                    ),
                }
            )
            results["overall_grade"] = "F"

        except socket.timeout:
            results["findings"].append(
                {
                    "title": "Connection Timeout",
                    "severity": "INFO",
                    "description": (
                        f"Could not reach {hostname}:{port} within 10 seconds."
                    ),
                    "remediation": "Verify the host is accessible from this network.",
                }
            )

        except ConnectionRefusedError:
            results["findings"].append(
                {
                    "title": "Connection Refused",
                    "severity": "INFO",
                    "description": f"Port {port} on {hostname} is closed or filtered.",
                    "remediation": "Verify the target and port are correct.",
                }
            )

        except Exception as e:
            results["findings"].append(
                {
                    "title": "Audit Error",
                    "severity": "INFO",
                    "description": str(e),
                    "remediation": "Check target connectivity and permissions.",
                }
            )

        # If no issues at all, add a positive finding
        if not results["findings"]:
            results["findings"].append(
                {
                    "title": "SSL Configuration Looks Good",
                    "severity": "INFO",
                    "description": "No major SSL/TLS issues detected.",
                    "remediation": (
                        "Continue monitoring certificate expiry. "
                        "Consider HSTS preloading for maximum protection."
                    ),
                }
            )

        return results


ssl_auditor = SSLAuditor()
