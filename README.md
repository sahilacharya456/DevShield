<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/shield.svg" width="100" height="100" alt="DevShield AI X"/>
  <h1>DevShield AI X</h1>
  <p><strong>The Next-Generation Enterprise DevSecOps Platform</strong></p>
  <p>Powered by Isolation Forests, DGA ML Detectors, and True RAG Auto-Fixing.</p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](#)
  [![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)](#)
  [![Security](https://img.shields.io/badge/Security-A%2B-success)](#)
</div>

<br />

## 🚀 Overview
**DevShield AI X** is a production-grade DevSecOps platform designed to natively integrate offensive security capabilities, static code analysis (SAST), and Machine Learning (ML) driven anomaly detection directly into modern developer workflows.

Built with a lightning-fast **FastAPI** backend and an ultra-premium **Next.js** frontend, DevShield provides unparalleled visibility into threat models, supply chain vulnerabilities, and active network risks.

## ✨ Key Features
- **Native SAST Engine**: Tree-sitter AST parsing tracks exact data flow from sources to dangerous sinks, identifying Logic Bombs and injection vulnerabilities.
- **Zero-Day ML Detection**: Utilizes Scikit-Learn Isolation Forests to automatically flag heavily obfuscated payloads and DGA (Domain Generation Algorithm) endpoints.
- **FAISS RAG Auto-Fixing**: Employs SentenceTransformers to encode past security fixes, dynamically guiding Large Language Models (LLMs) to generate strict JSON vulnerability patches.
- **Kali Arsenal Hub (15 Integrated Tools)**: Fully integrated Async WebSocket execution of industry-standard tools (Nmap, SQLMap, ZAP, Gobuster, Nikto, Shodan, etc.) through a stunning terminal UI.
- **JWT & Role-Based Access Control**: Fully secured REST endpoints via FastAPI Security dependencies.

## 🛠️ Architecture Stack
- **Frontend**: Next.js 15 (App Router), React, TailwindCSS, Framer Motion, TypeScript
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (Async), Uvicorn, Celery
- **Database**: SQLite (Async) natively supporting advanced relational mapping
- **AI/ML Layer**: Scikit-Learn, FAISS, SentenceTransformers, Gemini Pro (Generative AI)

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/DevShield.git
cd DevShield
```

### 2. Start the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env      # Add your API keys!
python -m uvicorn main:app --reload
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000` to access the DevShield AI X God-Mode Dashboard.

## 🛡️ Arsenal Toolkit Integrations
The `Arsenal` module dynamically interfaces with native CLI tools and API services to stream real-time results via WebSockets:
1. PortGrabber (Python-Native)
2. SSL Auditor
3. WAF Detector
4. Nmap
5. SQLMap
6. DNSRecon
7. Gobuster
8. theHarvester
9. Hydra
10. Nikto
11. Shodan
12. Sublist3r
13. WhatWeb
14. OWASP ZAP
15. Hash Analyzer

*Disclaimer: DevShield AI X Offensive modules are strictly for authorized testing on owned infrastructure. Unauthorized scanning is illegal.*

---

<div align="center">
  Built with ❤️ for the DevSecOps Community.
</div>
