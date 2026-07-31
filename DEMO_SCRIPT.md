# DevShield AI X — Presentation & Viva Demo Script
## Optimised for University Final Year Project / Client Demo

---

## 🎯 Total Demo Time: ~20 Minutes

---

## 📌 OPENING (2 min)
**Say:**
> "DevShield AI X is an AI-powered DevSecOps platform that I built to automate the work of a Security Architect, a SOC Analyst, and a Compliance Officer — all within a single tool. Let me walk you through it."

**Action:** Open the app. Point to the dark glassmorphic dashboard.

---

## 1. LOGIN & RBAC (1 min)
**Action:** Log in as `Admin`.
**Say:**
> "The system uses JWT-based role authentication. There are two roles: Admin — who has full system visibility — and Developer, who only sees their own projects. This is a real-world RBAC model."

---

## 2. COMMAND CENTER DASHBOARD (2 min)
**Action:** Show the home dashboard.
**Say:**
> "The command center gives a real-time Risk Trend graph and Asset Distribution chart across all registered projects. Every security event is logged. We can see total generations, security scans, average risk score, and ML readiness."

---

## 3. PROJECTS & FULL SCAN (3 min)
**Action:** Navigate to `Projects`. Create a new project or select an existing one. Run a full scan.
**Say:**
> "This is where repositories are registered. The multi-engine scanner runs in parallel: SAST using Bandit and custom AI heuristics, SCA for dependency CVEs, Secrets Detection using high-entropy analysis, Docker misconfiguration checks, and CI/CD pipeline auditing — all in one click."

**Point to the scan results:** Highlight severity breakdown (Critical, High, Medium) and the Security Score.

---

## 4. AI AUTO-FIX STUDIO (2 min)
**Action:** Navigate to `Auto-Fix Studio`. Select a HIGH severity vulnerability. Click "Generate Fix".
**Say:**
> "This is one of my flagship features. The AI generates a context-aware patch, explains why the original code was vulnerable, and rates its own confidence. The developer can accept or reject the fix — it's not just a suggestion, it's an intelligent code rewrite."

---

## 5. COMPLIANCE CENTER (1 min)
**Action:** Navigate to `Compliance Center`. Show the OWASP / NIST score breakdown.
**Say:**
> "DevShield automatically maps every detected vulnerability to industry compliance frameworks: OWASP Top 10, NIST 800-53, and GDPR. This transforms our scan into a formal audit report that a real client or auditor would understand."

---

## 6. API SECURITY LAB (2 min)
**Action:** Navigate to `API Security Lab`. In Tab 1, enter `https://httpbin.org` and scan.
**Say:**
> "This DAST module scans live API endpoints. It checks for 7 critical HTTP security headers, detects CORS wildcard misconfigurations — a very common web API flaw — and includes hardened SSRF protection so the tool itself cannot be weaponised to scan internal networks."

**Action:** Go to Tab 2. Paste a JWT token from jwt.io.
**Say:**
> "The JWT Analyzer decodes any token without requiring the secret key and immediately flags critical issues like the 'none' algorithm attack — a real CVE class."

---

## 7. AI THREAT MODEL STUDIO (2 min)
**Action:** Navigate to `Threat Model Studio`. Fill in fields: Name=`Auth Service`, Backend=`FastAPI`, Auth=`JWT`.
**Say:**
> "This is where DevShield truly shifts security left. Instead of finding vulnerabilities after they're shipped, this generates a formal STRIDE Threat Model *before* code is written. The AI acts as a Principal Security Architect, analysing the architecture and generating one threat per STRIDE category."

**Show generated output. Point to the severity matrix.**

---

## 8. PROFESSIONAL REPORTS CENTER (1 min)
**Action:** Navigate to `Reports Center`. Click "Generate AI Executive Summary", then generate Markdown report.
**Say:**
> "The reports center lets me export everything as a professional Markdown deliverable, or as SARIF format which can be uploaded directly to GitHub Advanced Security. I also have a Virtual CISO AI that translates technical findings into business language for management."

---

## 9. SOC ASSISTANT COPILOT (2 min)
**Action:** Navigate to `SOC Assistant`. Select a project. Click "🔥 What should I fix first?"
**Say:**
> "The SOC Assistant is a context-aware DevSecOps copilot. It reads the live scan findings from the database and gives tailored, prioritised advice — not generic answers. Watch how it knows exactly which vulnerability in which file is the most critical."

---

## 🔚 CLOSING (1 min)
**Say:**
> "In summary, DevShield AI X provides real enterprise-grade security automation:
> - 7 parallel scanning engines
> - AI-powered remediation and threat modelling  
> - Compliance mapping, API DAST, and professional reporting
> - All in a single, self-hosted, privacy-first platform
>
> The architecture is already being migrated to a decoupled Next.js + FastAPI stack for scalability. Thank you."

---

## ❓ ANTICIPATED QUESTIONS

**Q: How does the AI know about my specific code?**
> "It doesn't store anything. The code snippet is passed as context in a single API call to Gemini/Groq and the result is returned locally."

**Q: Is this production-ready?**
> "The Streamlit prototype is portfolio-ready. I have scaffolded a full Next.js + FastAPI migration with PostgreSQL and Redis for a production SaaS deployment."

**Q: What makes this different from just using Bandit or Snyk?**
> "Those are single-purpose tools. DevShield integrates 7 engines, adds LLM-powered remediation, maps to compliance frameworks, generates business-readable reports, and includes architectural threat modelling — features that normally require 4–5 separate commercial products."
