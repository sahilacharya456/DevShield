# Contributing to DevShield AI X

Thank you for your interest in contributing! DevShield AI X is a professional DevSecOps platform and we hold contributions to a high standard.

## 🔒 Ethical Boundaries (MUST READ)

All contributions **must** remain strictly defensive and ethical. We will reject any pull request that:
- Adds offensive exploitation capabilities (e.g., CVE exploits, attack automation, credential theft).
- Bypasses the AI safety guardrails in the system prompts.
- Enables scanning of unauthorized targets.

## How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/DevShield-AI-X.git
cd DevShield-AI-X
```

### 2. Set Up Your Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create a Feature Branch
```bash
git checkout -b feat/my-new-feature
```

### 4. Make Your Changes
- Follow the existing code style (snake_case for Python, descriptive names).
- All new scanners go in `modules/`. All new UI pages go in `pages/`.
- All new database tables must have an `init_*_db()` function called from `app.py`.
- Avoid hardcoding API keys or paths — use `config/settings.py`.

### 5. Test Your Changes
```bash
streamlit run app.py
```
Manually navigate through the affected pages and verify functionality.

### 6. Submit a Pull Request
- Describe what your change does and **why**.
- Reference any relevant issues.
- Ensure you have not broken existing functionality.

## Code Style
- Python: PEP 8 compliant.
- Docstrings on all public functions.
- Type hints encouraged.

## Questions?
Open a GitHub Discussion or an Issue tagged `[question]`.
