# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | ✅ Actively maintained |
| 1.x     | ⚠️ Critical patches only |

## Reporting a Vulnerability

DevShield AI X is a **defensive** cybersecurity tool. We take the security of the platform itself seriously.

If you discover a security vulnerability within DevShield AI X, please do **NOT** open a public GitHub issue.

Instead, please report it privately:
1. Email the maintainer directly with the subject line: `[SECURITY] DevShield Vulnerability Report`
2. Include a clear description of the vulnerability, steps to reproduce, and your suggested impact assessment.
3. We will acknowledge receipt within 72 hours and provide a timeline for a fix.

## Security Philosophy

DevShield AI X operates under a **strict defensive and ethical** mandate:
- All AI prompts include explicit system-level guardrails to prevent generation of malicious code, exploits, or harmful content.
- Source code submitted for analysis is only transmitted to the configured LLM provider (Groq/Gemini) for the purposes of security review. It is never stored externally.
- The API Security Lab includes SSRF protections to prevent the tool from being used to probe internal network resources.

## Disclosure Policy

We follow Responsible Disclosure. We will:
- Acknowledge your report within 72 hours.
- Provide a fix within 30 days for critical issues, 90 days for others.
- Credit you publicly in the release notes (unless you prefer anonymity).
