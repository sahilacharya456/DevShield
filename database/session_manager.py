"""
DevShield AI — Session Manager
All SQLite CRUD operations for sessions, analyses, and custom rules.
"""

import sqlite3
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import DB_FILE, FEEDBACK_FILE


# ─── Schema Init ─────────────────────────────────────────────────────────────

def init_db():
    """Initialize all database tables on first run."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          TEXT PRIMARY KEY,
            timestamp   TEXT NOT NULL,
            task        TEXT NOT NULL,
            language    TEXT NOT NULL,
            code        TEXT,
            tokens_used INTEGER DEFAULT 0,
            confidence  INTEGER DEFAULT 0,
            user_rating INTEGER,
            user_feedback TEXT,
            doc_generated INTEGER DEFAULT 0,
            analyzed    INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS security_analyses (
            id              TEXT PRIMARY KEY,
            session_id      TEXT NOT NULL,
            code            TEXT,
            vulnerabilities TEXT,
            fixed_code      TEXT,
            overall_score   INTEGER DEFAULT 0,
            grade           TEXT DEFAULT 'F',
            severity_counts TEXT,
            summary         TEXT,
            timestamp       TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS custom_rules (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            pattern     TEXT NOT NULL,
            severity    TEXT DEFAULT 'MEDIUM',
            owasp_id    TEXT DEFAULT '',
            description TEXT DEFAULT '',
            enabled     INTEGER DEFAULT 1,
            created_at  TEXT
        )
    """)

    conn.commit()
    conn.close()


# ─── Session CRUD ─────────────────────────────────────────────────────────────

def create_session_id() -> str:
    return datetime.now().strftime("DS_%Y%m%d_%H%M%S_%f")[:20]


def save_session(
    session_id: str,
    task: str,
    language: str,
    code: str,
    tokens: int = 0,
    confidence: int = 0,
    rating: Optional[int] = None,
    feedback: str = "",
    doc_generated: bool = False,
    analyzed: bool = False,
):
    """Insert or replace a session record."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """INSERT OR REPLACE INTO sessions VALUES
           (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            datetime.now().isoformat(),
            task,
            language,
            code,
            tokens,
            confidence,
            rating,
            feedback,
            int(doc_generated),
            int(analyzed),
        ),
    )
    conn.commit()
    conn.close()

    # Also append to JSONL for future fine-tuning
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "session_id": session_id,
                    "task": task,
                    "language": language,
                    "code": code[:500],  # truncate for file size
                    "rating": rating,
                    "feedback": feedback,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            + "\n"
        )


def update_session_rating(session_id: str, rating: int, feedback: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE sessions SET user_rating=?, user_feedback=? WHERE id=?",
        (rating, feedback, session_id),
    )
    conn.commit()
    conn.close()


def update_session_flags(session_id: str, doc_generated: bool = None, analyzed: bool = None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if doc_generated is not None:
        c.execute("UPDATE sessions SET doc_generated=? WHERE id=?", (int(doc_generated), session_id))
    if analyzed is not None:
        c.execute("UPDATE sessions SET analyzed=? WHERE id=?", (int(analyzed), session_id))
    conn.commit()
    conn.close()


def get_session(session_id: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id=?", (session_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_session_history(limit: int = 50) -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sessions ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM sessions WHERE user_rating IS NOT NULL")
    rated = c.fetchone()[0]

    c.execute("SELECT AVG(user_rating) FROM sessions WHERE user_rating IS NOT NULL")
    avg_rating = c.fetchone()[0] or 0.0

    c.execute("SELECT COUNT(*) FROM security_analyses")
    total_analyses = c.fetchone()[0]

    c.execute("SELECT AVG(overall_score) FROM security_analyses")
    avg_score = c.fetchone()[0] or 0.0

    c.execute("SELECT language, COUNT(*) as cnt FROM sessions GROUP BY language ORDER BY cnt DESC LIMIT 5")
    top_langs = [{"language": r[0], "count": r[1]} for r in c.fetchall()]

    c.execute("SELECT overall_score, timestamp FROM security_analyses ORDER BY timestamp ASC LIMIT 20")
    score_trend = [{"score": r[0], "timestamp": r[1]} for r in c.fetchall()]

    conn.close()

    return {
        "total_sessions": total_sessions,
        "rated_sessions": rated,
        "avg_rating": round(avg_rating, 1),
        "total_analyses": total_analyses,
        "avg_security_score": round(avg_score, 1),
        "top_languages": top_langs,
        "score_trend": score_trend,
    }


# ─── Security Analysis CRUD ───────────────────────────────────────────────────

def save_security_analysis(
    session_id: str,
    code: str,
    vulnerabilities: list,
    fixed_code: str,
    overall_score: int,
    grade: str,
    severity_counts: dict,
    summary: str,
) -> str:
    analysis_id = f"ANAL_{session_id}"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """INSERT OR REPLACE INTO security_analyses VALUES
           (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            analysis_id,
            session_id,
            code,
            json.dumps(vulnerabilities),
            fixed_code,
            overall_score,
            grade,
            json.dumps(severity_counts),
            summary,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return analysis_id


def get_security_analysis(session_id: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM security_analyses WHERE session_id=?", (session_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["vulnerabilities"] = json.loads(result.get("vulnerabilities") or "[]")
    result["severity_counts"] = json.loads(result.get("severity_counts") or "{}")
    return result


# ─── Custom Rules CRUD ────────────────────────────────────────────────────────

def get_custom_rules_db() -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM custom_rules WHERE enabled=1 ORDER BY severity")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_custom_rule(name: str, pattern: str, severity: str, owasp_id: str, description: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO custom_rules (name, pattern, severity, owasp_id, description, enabled, created_at) VALUES (?,?,?,?,?,1,?)",
        (name, pattern, severity, owasp_id, description, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def delete_custom_rule(rule_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM custom_rules WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()


# ─── Export ───────────────────────────────────────────────────────────────────

def export_history_csv(filepath: str):
    sessions = get_session_history(limit=10000)
    if not sessions:
        return
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sessions[0].keys())
        writer.writeheader()
        writer.writerows(sessions)
