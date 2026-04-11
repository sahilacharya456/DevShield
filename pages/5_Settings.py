"""
DevShield AI — Page 5: Settings
Manage custom security rules, view learned preferences,
API configuration, and fine-tuning status.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from config.settings import APP_NAME, APP_OWNER, APP_VERSION, GEMINI_API_KEY, GEMINI_MODEL
from database.session_manager import (
    add_custom_rule,
    delete_custom_rule,
    get_custom_rules_db,
    init_db,
)
from ui.components import empty_state, page_header, sidebar_brand
from ui.styles import get_css
from utils.preference_learner import get_readiness_for_fine_tuning, load_preferences

# ── Setup ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"Settings — {APP_NAME}",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()
st.markdown(get_css(), unsafe_allow_html=True)
sidebar_brand(APP_VERSION, APP_OWNER)

page_header("⚙️", "Settings", "Configure DevShield AI: custom rules, preferences, API, and fine-tuning.")

tabs = st.tabs(["🛡️ Custom Rules", "🧠 Learned Preferences", "🔑 API Config", "🎯 Fine-Tuning"])

# ── Tab 1: Custom Rules ───────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("### 🛡️ Custom Security Rules")
    st.markdown(
        '<div class="ds-info">'
        'Define your own security rules on top of the 20 built-in defaults. '
        'Rules use Python regex patterns and are applied to every scan.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Add Rule Form
    st.markdown("#### ➕ Add New Rule")
    with st.form("add_rule_form"):
        r1, r2 = st.columns(2)
        with r1:
            rule_name = st.text_input("Rule Name", placeholder="e.g. Hardcoded DB Password")
            rule_pattern = st.text_input(
                "Regex Pattern",
                placeholder=r'(?i)db_password\s*=\s*["\'][^"\']+["\']',
            )
        with r2:
            rule_severity = st.selectbox("Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"])
            rule_owasp = st.selectbox(
                "OWASP Category",
                [
                    "A01:2021 — Broken Access Control",
                    "A02:2021 — Cryptographic Failures",
                    "A03:2021 — Injection",
                    "A04:2021 — Insecure Design",
                    "A05:2021 — Security Misconfiguration",
                    "A06:2021 — Vulnerable Components",
                    "A07:2021 — Auth Failures",
                    "A08:2021 — Integrity Failures",
                    "A09:2021 — Logging Failures",
                    "A10:2021 — SSRF",
                ],
            )
        rule_desc = st.text_area(
            "Description",
            placeholder="Explain why this pattern is dangerous and how to fix it...",
            height=80,
        )
        add_submitted = st.form_submit_button("➕ Add Rule", use_container_width=True)

    if add_submitted:
        if rule_name and rule_pattern:
            owasp_id = rule_owasp.split(" — ")[0]
            add_custom_rule(
                name=rule_name,
                pattern=rule_pattern,
                severity=rule_severity,
                owasp_id=owasp_id,
                description=rule_desc,
            )
            st.success(f"✅ Rule '{rule_name}' added!")
            st.rerun()
        else:
            st.warning("⚠️ Name and pattern are required.")

    st.divider()

    # Existing rules
    st.markdown("#### 📋 Active Custom Rules")
    db_rules = get_custom_rules_db()

    if db_rules:
        for rule in db_rules:
            sev_colors = {
                "CRITICAL": "#ff2d55", "HIGH": "#ff6b00",
                "MEDIUM": "#ffd60a", "LOW": "#30d158", "INFO": "#636366",
            }
            clr = sev_colors.get(rule["severity"], "#8b949e")
            with st.expander(
                f"[{rule['severity']}] {rule['name']}  —  {rule['owasp_id']}",
                expanded=False,
            ):
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**Pattern:** `{rule['pattern']}`")
                    st.markdown(f"**Description:** {rule['description'] or '—'}")
                    st.markdown(f"**OWASP:** `{rule['owasp_id']}`")
                    st.markdown(f"**Added:** {(rule.get('created_at') or '')[:16]}")
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_rule_{rule['id']}"):
                        delete_custom_rule(rule["id"])
                        st.success("Rule deleted.")
                        st.rerun()
    else:
        empty_state("🛡️", "No custom rules yet", "Add your first rule above")

    # Default rules info
    st.divider()
    st.markdown("#### 📋 Built-in Default Rules (20 rules, always active)")
    st.markdown(
        '<div class="ds-info">'
        'These 20 rules are always applied and cannot be deleted:<br>'
        '🔐 Hardcoded password/API key/token/private key<br>'
        '🔐 MD5, SHA-1, weak random usage<br>'
        '💉 SQL injection, eval(), exec(), os.system(), shell=True<br>'
        '📦 Unsafe pickle.loads(), yaml.load()<br>'
        '⚙️ Debug mode, TODO security comments<br>'
        '📊 Logging sensitive data, raw exception exposure'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Tab 2: Learned Preferences ─────────────────────────────────────────────────
with tabs[1]:
    st.markdown("### 🧠 Self-Improvement Model")
    prefs = load_preferences()

    ft = get_readiness_for_fine_tuning()
    st.progress(ft["progress_pct"] / 100, text=f"Fine-tuning progress: {ft['progress_pct']}%")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Interactions", ft["total_interactions"])
    c2.metric("Milestone", "500 interactions")
    c3.metric("Remaining", ft["remaining"])

    if ft["ready"]:
        st.markdown(
            '<div class="ds-success">✅ <b>Fine-tuning milestone reached!</b> '
            'Export your feedback data to train a custom model.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="ds-info">🔄 Keep using DevShield to reach the 500-interaction milestone '
            f'and unlock custom model fine-tuning.</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Language preferences
    if prefs.get("preferred_languages"):
        st.markdown("#### 🌐 Language Usage")
        langs = prefs["preferred_languages"]
        sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
        for lang, count in sorted_langs:
            pct = min(100, int((count / max(langs.values())) * 100))
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
                f'<div style="width:100px; color:#e6edf3; font-size:0.85rem;">{lang}</div>'
                f'<div style="flex:1; background:rgba(255,255,255,0.08); border-radius:100px; height:6px;">'
                f'<div style="width:{pct}%; height:100%; background:linear-gradient(90deg,#00ff88,#00b4ff); '
                f'border-radius:100px;"></div></div>'
                f'<div style="width:30px; color:#8b949e; font-size:0.8rem;">{count}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Security priorities
    if prefs.get("security_priorities"):
        st.divider()
        st.markdown("#### 🔐 Learned Security Priorities")
        priorities = list(dict.fromkeys(prefs["security_priorities"]))[:15]
        tags = "  ".join(
            [f'<span class="owasp-tag">{p}</span>' for p in priorities]
        )
        st.markdown(tags, unsafe_allow_html=True)

    # Coding patterns
    if prefs.get("coding_patterns"):
        st.divider()
        st.markdown(f"#### ⭐ Top-Rated Sessions ({len(prefs['coding_patterns'])} patterns learned)")
        for pat in prefs["coding_patterns"][-5:]:
            ts = (pat.get("timestamp") or "")[:10]
            st.markdown(
                f'<div class="ds-card" style="padding:10px 16px; font-size:0.83rem;">'
                f'"{pat.get("task", "")[:80]}" — <code>{pat.get("language", "")}</code> — ⭐{pat.get("rating", "?")} — {ts}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Reset preferences
    st.divider()
    if st.button("🗑️ Reset All Learned Preferences", type="secondary"):
        from config.settings import PREFERENCES_FILE
        if PREFERENCES_FILE.exists():
            PREFERENCES_FILE.unlink()
        st.success("Preferences reset to defaults.")
        st.rerun()

# ── Tab 3: API Config ─────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### 🔑 API Configuration")

    api_status = bool(GEMINI_API_KEY)
    if api_status:
        masked = GEMINI_API_KEY[:6] + "•" * 20 + GEMINI_API_KEY[-4:]
        st.markdown(
            f'<div class="ds-success">✅ <b>Gemini API Key loaded</b><br>'
            f'<code style="font-size:0.85rem;">{masked}</code></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="ds-danger">❌ <b>GEMINI_API_KEY not set!</b><br>'
            'Create a <code>.env</code> file in your DevShield folder.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f"**Active Model:** `{GEMINI_MODEL}`")
    st.markdown(
        '<div class="ds-info">'
        '💡 To change the model, update <code>GEMINI_MODEL</code> in your <code>.env</code> file.<br>'
        'Options: <code>gemini-2.0-flash</code> (fast) | <code>gemini-1.5-pro</code> (thorough)'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("#### 📄 .env Setup Guide")
    st.code(
        "# Create this file at: c:\\Users\\sahil\\Desktop\\DevShield\\.env\n"
        "GEMINI_API_KEY=your_key_here\n"
        "GEMINI_MODEL=gemini-2.0-flash\n"
        "APP_OWNER=Sahil",
        language="bash",
    )
    st.markdown(
        "Get a free Gemini API key at → "
        "[aistudio.google.com](https://aistudio.google.com/app/apikey)"
    )

    st.divider()
    st.markdown("#### 📂 Data Locations")
    from config.settings import DATA_DIR, EXPORTS_DIR, DB_FILE, FEEDBACK_FILE

    st.markdown(
        f'<div class="ds-card">'
        f'<b>Database:</b> <code>{DB_FILE}</code><br>'
        f'<b>Exports:</b> <code>{EXPORTS_DIR}</code><br>'
        f'<b>Feedback JSONL:</b> <code>{FEEDBACK_FILE}</code>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Tab 4: Fine-Tuning ─────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### 🎯 Fine-Tuning Pipeline")
    st.markdown(
        '<div class="ds-info">'
        'After 500+ interactions, you can export your feedback data and fine-tune '
        'a smaller, specialized model that learns your exact coding style, '
        'security priorities, and preferences.'
        '</div>',
        unsafe_allow_html=True,
    )

    ft = get_readiness_for_fine_tuning()
    st.progress(ft["progress_pct"] / 100)
    st.markdown(f"**{ft['total_interactions']} / 500 interactions recorded**")

    st.divider()
    st.markdown("#### 📊 Phase Roadmap")
    phases = [
        ("Phase 1 — Gemini Powered", "Active", "#00ff88",
         "DevShield uses Gemini API for all generation and analysis. Every interaction is logged."),
        ("Phase 2 — Fine-Tuning", "After 500 interactions", "#ffd60a",
         "Export your feedback JSONL and fine-tune a smaller, faster, specialized model."),
        ("Phase 3 — Your Own Model", "Ongoing", "#00b4ff",
         "The fine-tuned model runs locally. Every new project makes it smarter."),
    ]
    for title, status, clr, desc in phases:
        st.markdown(
            f'<div class="ds-card" style="border-left: 3px solid {clr}; padding:14px 20px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<b style="font-size:0.95rem;">{title}</b>'
            f'<span style="color:{clr}; font-size:0.75rem; font-weight:600;">{status}</span>'
            f'</div>'
            f'<div style="color:#8b949e; font-size:0.83rem; margin-top:6px;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("#### ⬇️ Export Fine-Tuning Data")
    if ft["total_interactions"] >= 10:
        if st.button("📥 Export Feedback JSONL", use_container_width=True):
            from config.settings import FEEDBACK_FILE
            if FEEDBACK_FILE.exists():
                with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                    data = f.read()
                st.download_button(
                    "⬇️ Download feedback.jsonl",
                    data=data,
                    file_name="devshield_feedback.jsonl",
                    mime="application/jsonlines",
                    use_container_width=True,
                )
                st.success(f"✅ {ft['total_interactions']} interaction records ready for fine-tuning.")
            else:
                st.warning("No feedback data file found yet.")
    else:
        st.markdown(
            '<div class="ds-warn">'
            f'⚠️ Export requires at least 10 interactions. Currently: {ft["total_interactions"]}.'
            '</div>',
            unsafe_allow_html=True,
        )
