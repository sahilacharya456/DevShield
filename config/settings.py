"""
DevShield AI — Global Configuration
All constants, paths, and environment variables loaded here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_root = Path(__file__).parent.parent
load_dotenv(_root / ".env")

# ─── App Identity ────────────────────────────────────────────────────────────
APP_NAME = "DevShield AI"
APP_VERSION = "1.0.0"
APP_OWNER = os.getenv("APP_OWNER", "Sahil")

# ─── LLM Providers ────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# Either 'gemini' or 'groq'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = _root
DATA_DIR = Path.home() / ".devshield"
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "devshield.db"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
EXPORTS_DIR = BASE_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

RULES_DIR = BASE_DIR / "rules"
DEFAULT_RULES_PATH = RULES_DIR / "default_rules.yaml"

# ─── Supported Languages ──────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "React (JSX/TSX)",
    "C++",
    "Java",
    "SQL",
    "Go",
    "Rust",
    "Bash / Shell",
]

# ─── Severity System ──────────────────────────────────────────────────────────
SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFO": 4,
}

SEVERITY_COLORS = {
    "CRITICAL": "#FF2D55",
    "HIGH":     "#FF6B00",
    "MEDIUM":   "#FFD60A",
    "LOW":      "#30D158",
    "INFO":     "#8E8E93",
}

GRADE_COLORS = {
    "A": "#30D158",
    "B": "#00B4FF",
    "C": "#FFD60A",
    "D": "#FF6B00",
    "F": "#FF2D55",
}

# ─── Security Score Thresholds ────────────────────────────────────────────────
def score_to_grade(score: int) -> str:
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 40: return "D"
    return "F"

# ─── Security Limits ─────────────────────────────────────────────────────────
MAX_CODE_LENGTH = 100000  # Max characters allowed for a single scan/generation
TIMEOUT_SECONDS = 30      # Timeout for external API calls and scanners
