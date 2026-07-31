import httpx
import asyncio
import structlog
from typing import Dict, Any, List

logger = structlog.get_logger("DevShield.Arsenal.WAF")

# ---------------------------------------------------------------------------
# WAF signature patterns (response header keys / values)
# ---------------------------------------------------------------------------
WAF_SIGNATURES: Dict[str, List[str]] = {
    "Cloudflare":  ["cf-ray", "cloudflare", "__cfduid", "cf-cache-status"],
    "AWS WAF":     ["x-amzn-requestid", "x-amz-cf-id", "x-amz-id"],
    "Akamai":      ["akamai", "x-akamai-transformed", "x-check-cacheable"],
    "Fastly":      ["x-fastly-request-id", "fastly-"],
    "Sucuri":      ["x-sucuri-id", "sucuri"],
    "ModSecurity": ["mod_security", "modsecurity", "noyb"],
    "F5 BIG-IP":   ["bigipserver", "f5", "x-waf-event-info"],
    "Imperva":     ["x-iinfo", "incapsula", "visid_incap"],
    "Barracuda":   ["barra", "bnmobile"],
    "SonicWall":   ["sonicwall"],
}

# URL-encoded attack payloads used to probe for WAF blocking behaviour
SOFT_404_PAYLOADS: List[str] = [
    "/?%27%3E%3Cscript%3Ealert(1)%3C%2Fscript%3E",   # XSS
    "/?id=1%20AND%201%3D1",                            # SQLi
    "/../../../etc/passwd",                             # Path traversal
    "/?cmd=cat%20/etc/passwd",                          # RCE probe
]

# HTTP security headers we audit
SECURITY_HEADERS: Dict[str, str] = {
    "Content-Security-Policy":   "CSP",
    "X-Frame-Options":           "Clickjacking Protection",
    "X-Content-Type-Options":    "MIME Sniff Protection",
    "Strict-Transport-Security": "HSTS",
    "X-XSS-Protection":          "XSS Protection",
    "Referrer-Policy":           "Referrer Policy",
    "Permissions-Policy":        "Permissions Policy",
    "Cross-Origin-Opener-Policy": "COOP",
}


class WAFDetector:
    """
    DevShield Arsenal: Web Application Firewall (WAF) Detection Engine.
    Fingerprints WAF presence and type using header analysis and payload probing.
    Also audits the presence of HTTP security headers.
    """

    async def detect(self, target_url: str) -> Dict[str, Any]:
        """
        Detect WAF presence/type and audit HTTP security headers.

        Returns a structured dict with:
          - waf_detected, waf_type, waf_confidence
          - security_headers that are present
          - per-finding severity + remediation
          - response_codes for each probe payload
        """
        results: Dict[str, Any] = {
            "target": target_url,
            "waf_detected": False,
            "waf_type": "None",
            "waf_confidence": 0,
            "response_codes": {},
            "security_headers": {},
            "findings": [],
        }

        async with httpx.AsyncClient(
            verify=False,
            timeout=15,
            follow_redirects=True,
        ) as client:
            try:
                # ── 1. Baseline request ──────────────────────────────────────
                resp = await client.get(
                    target_url,
                    headers={"User-Agent": "Mozilla/5.0 DevShield-WAF-Detector/2.0"},
                )
                resp_headers_lower = {
                    k.lower(): v for k, v in resp.headers.items()
                }
                all_header_text = " ".join(resp_headers_lower.values()).lower()

                # ── 2. Security header audit ─────────────────────────────────
                for header, label in SECURITY_HEADERS.items():
                    header_lower = header.lower()
                    if header_lower in resp_headers_lower:
                        results["security_headers"][label] = resp_headers_lower[
                            header_lower
                        ]
                    else:
                        results["findings"].append(
                            {
                                "title": f"Missing Security Header: {header}",
                                "severity": "MEDIUM",
                                "description": (
                                    f"The {label} header is not present in "
                                    "HTTP responses."
                                ),
                                "remediation": (
                                    f"Add the '{header}' header to all HTTP "
                                    "responses in your web server / reverse proxy config."
                                ),
                            }
                        )

                # ── 3. WAF header fingerprinting ─────────────────────────────
                detected_waf: str | None = None
                for waf_name, signatures in WAF_SIGNATURES.items():
                    matches = sum(
                        1 for sig in signatures if sig.lower() in all_header_text
                    )
                    if matches > 0:
                        confidence = min(100, matches * 35)
                        if detected_waf is None or confidence > results["waf_confidence"]:
                            detected_waf = waf_name
                            results["waf_detected"] = True
                            results["waf_type"] = waf_name
                            results["waf_confidence"] = confidence
                            logger.info(
                                "WAF fingerprinted",
                                waf=waf_name,
                                confidence=confidence,
                            )

                if detected_waf:
                    results["findings"].append(
                        {
                            "title": f"WAF Detected: {detected_waf}",
                            "severity": "INFO",
                            "description": (
                                f"{detected_waf} Web Application Firewall "
                                f"detected (confidence: {results['waf_confidence']}%)."
                            ),
                            "remediation": (
                                "WAF is present — verify rules cover the full "
                                "OWASP Top 10 and enable logging/alerting."
                            ),
                        }
                    )

                # ── 4. Payload probing ───────────────────────────────────────
                blocked_count = 0
                probe_tasks = [
                    self._probe(client, target_url, payload)
                    for payload in SOFT_404_PAYLOADS
                ]
                probe_results = await asyncio.gather(
                    *probe_tasks, return_exceptions=True
                )
                for payload, code in zip(SOFT_404_PAYLOADS, probe_results):
                    if isinstance(code, Exception):
                        continue
                    results["response_codes"][payload] = code
                    if code in [403, 406, 429, 503]:
                        blocked_count += 1

                # If header fingerprinting missed it, fall back to block-rate
                if blocked_count >= 2 and not results["waf_detected"]:
                    results["waf_detected"] = True
                    results["waf_type"] = "Unknown WAF"
                    results["waf_confidence"] = min(100, blocked_count * 25)
                    results["findings"].append(
                        {
                            "title": "WAF Detected (Behavioural)",
                            "severity": "INFO",
                            "description": (
                                f"{blocked_count}/{len(SOFT_404_PAYLOADS)} "
                                "attack payloads were blocked (403/406/429/503). "
                                "WAF type could not be fingerprinted from headers."
                            ),
                            "remediation": (
                                "WAF present — verify rule coverage and update "
                                "WAF signatures regularly."
                            ),
                        }
                    )

                # ── 5. No WAF finding ────────────────────────────────────────
                if not results["waf_detected"]:
                    results["findings"].append(
                        {
                            "title": "No WAF Detected",
                            "severity": "HIGH",
                            "description": (
                                "No Web Application Firewall was detected. "
                                "The application appears to be directly exposed."
                            ),
                            "remediation": (
                                "Deploy a WAF (Cloudflare, AWS WAF, ModSecurity) "
                                "to protect against OWASP Top 10 attacks."
                            ),
                        }
                    )

            except httpx.ConnectError as e:
                results["findings"].append(
                    {
                        "title": "Connection Failed",
                        "severity": "INFO",
                        "description": f"Could not connect to {target_url}: {e}",
                        "remediation": "Verify the target URL is correct and reachable.",
                    }
                )
            except httpx.TimeoutException:
                results["findings"].append(
                    {
                        "title": "Request Timed Out",
                        "severity": "INFO",
                        "description": f"Request to {target_url} timed out after 15 s.",
                        "remediation": "Check network connectivity to the target.",
                    }
                )
            except Exception as e:
                results["findings"].append(
                    {
                        "title": "WAF Detection Error",
                        "severity": "INFO",
                        "description": str(e),
                        "remediation": "Check target accessibility and retry.",
                    }
                )

        return results

    # ── helpers ────────────────────────────────────────────────────────────
    @staticmethod
    async def _probe(
        client: httpx.AsyncClient, base_url: str, payload: str
    ) -> int:
        """Fire a single probe request and return the HTTP status code."""
        probe_url = base_url.rstrip("/") + payload
        try:
            resp = await client.get(probe_url)
            return resp.status_code
        except Exception:
            return -1


waf_detector = WAFDetector()
