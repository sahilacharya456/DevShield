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

<img width="1915" height="972" alt="Screenshot 2026-07-31 224247" src="https://github.com/user-attachments/assets/375833d0-6a6c-4b9d-8710-dd8e668f8575" />
<img width="1919" height="964" alt="Screenshot 2026-07-31 224306" src="https://github.com/user-attachments/assets/518cf3bd-e0a7-442f-919e-17578ee01b32" />
<img width="1918" height="966" alt="Screenshot 2026-07-31 224320" src="https://github.com/user-attachments/assets/e0e789a9-f8eb-4c05-94fc-280f53687325" />
<img width="1918" height="969" alt="Screenshot 2026-07-31 224333" src="https://github.com/user-attachments/assets/f61cadb8-1b61-4050-b29b-237ad21d297e" />
<img width="1919" height="898" alt="Screenshot 2026-07-31 224349" src="https://github.com/user-attachments/assets/2897e6c4-7f82-4d34-a0e4-b4352a8ae27d" />
<img width="1919" height="898" alt="Screenshot 2026-07-31 224406" src="https://github.com/user-attachments/assets/5dffe6ed-93a8-4973-9781-a05cbbf27c02" />
<img width="1919" height="904" alt="Screenshot 2026-07-31 224437" src="https://github.com/user-attachments/assets/d6d23a89-90ee-473c-b2c5-4b354e340558" />
<img width="1919" height="976" alt="Screenshot 2026-07-31 224450" src="https://github.com/user-attachments/assets/53dfe1fa-3747-4427-8758-53650ecc2338" />
<img width="1919" height="964" alt="Screenshot 2026-07-31 224647" src="https://github.com/user-attachments/assets/91907520-714b-4861-89d0-df684395d471" />
<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/shield.svg" width="100" height="100" alt="DevShield AI X"/>
