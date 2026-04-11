"""
DevShield AI — Reusable UI Components
Streamlit helper functions for consistent rendering across all pages.
"""

import streamlit as st


# ─── Severity Badge ────────────────────────────────────────────────────────────

def severity_badge(level: str) -> str:
    """Return an HTML severity badge string."""
    clean = level.upper().strip()
    label = clean
    return f'<span class="badge badge-{clean}">{label}</span>'


# ─── OWASP Tag ─────────────────────────────────────────────────────────────────

def owasp_tag(owasp_id: str, owasp_name: str = "") -> str:
    """Return an HTML OWASP category tag."""
    text = owasp_id or "Unclassified"
    if owasp_name:
        text += f" — {owasp_name}"
    return f'<span class="owasp-tag">🔒 {text}</span>'


# ─── Confidence Bar ────────────────────────────────────────────────────────────

def confidence_bar(score: int, max_score: int = 10) -> str:
    """Return an HTML confidence bar. score is 1–10."""
    pct = min(100, int((score / max_score) * 100))
    color = (
        "#30d158" if pct >= 70
        else "#ffd60a" if pct >= 40
        else "#ff2d55"
    )
    fill_style = f'background: linear-gradient(90deg, {color}, {color}cc);'
    return (
        f'<div style="font-size:0.78rem;color:#8b949e;margin-bottom:2px;">'
        f'Confidence: <b style="color:{color}">{pct}%</b></div>'
        f'<div class="conf-wrap"><div class="conf-fill" style="width:{pct}%;{fill_style}"></div></div>'
    )


# ─── Stat Card ─────────────────────────────────────────────────────────────────

def stat_card(value: str, label: str) -> str:
    return (
        f'<div class="stat-card">'
        f'<span class="stat-value">{value}</span>'
        f'<span class="stat-label">{label}</span>'
        f'</div>'
    )


# ─── Score Ring ────────────────────────────────────────────────────────────────

def score_display(score: int, grade: str) -> str:
    """HTML circular-style security score display."""
    grade_colors = {
        "A": "#30d158", "B": "#00b4ff",
        "C": "#ffd60a", "D": "#ff6b00", "F": "#ff2d55",
    }
    color = grade_colors.get(grade, "#8b949e")
    return (
        f'<div style="text-align:center; padding: 12px;">'
        f'<div style="font-size:3.5rem; font-weight:800; color:{color}; '
        f'text-shadow: 0 0 20px {color}80; line-height:1;">{score}</div>'
        f'<div style="font-size:0.75rem; color:#8b949e; text-transform:uppercase; '
        f'letter-spacing:1px; margin-top:4px;">/ 100</div>'
        f'<div style="font-size:2.2rem; font-weight:800; color:{color}; margin-top:4px;">'
        f'Grade {grade}</div>'
        f'</div>'
    )


# ─── Vulnerability Card ────────────────────────────────────────────────────────

def vulnerability_card(vuln: dict, index: int) -> None:
    """Render a fully expanded vulnerability card in Streamlit."""
    sev = vuln.get("severity", "INFO")
    name = vuln.get("name", "Unknown")
    line = vuln.get("line", "?")
    desc = vuln.get("description", "")
    owasp_id = vuln.get("owasp_id", "")
    owasp_name = vuln.get("owasp_name", "")
    poc = vuln.get("poc", "")
    fix = vuln.get("fix_suggestion", "")
    fix_code = vuln.get("fixed_code_snippet", "")
    conf = vuln.get("confidence", 0.0)
    conf_pct = int(conf * 100) if conf <= 1.0 else int(conf * 10)

    header = (
        f"{severity_badge(sev)} &nbsp; "
        f"<b>{name}</b> &nbsp; "
        f'<span style="color:#8b949e; font-size:0.8rem;">Line {line}</span> &nbsp; '
        f"{owasp_tag(owasp_id, owasp_name)}"
    )

    with st.expander(f"[{sev}] {name}  —  Line {line}", expanded=(sev == "CRITICAL")):
        st.markdown(header, unsafe_allow_html=True)
        st.markdown(confidence_bar(conf_pct, 100), unsafe_allow_html=True)
        st.markdown("---")

        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("**📋 Description**")
            st.markdown(f"> {desc}")
            if fix:
                st.markdown("**🔧 Recommended Fix**")
                st.info(fix)

        with col2:
            if owasp_id:
                owasp_url = vuln.get("owasp_url", "https://owasp.org/Top10/")
                st.markdown(
                    f"**📖 OWASP Reference**\n\n"
                    f"[{owasp_id} — {owasp_name}]({owasp_url})"
                )

        if poc:
            st.markdown("**⚠️ Proof of Concept** *(educational — defensive context only)*")
            st.code(poc, language="text")

        if fix_code:
            st.markdown("**✅ Fixed Code Snippet**")
            st.code(fix_code)


# ─── Page Header ───────────────────────────────────────────────────────────────

def page_header(icon: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="slide-up">'
        f'<h1 style="margin-bottom:4px;">{icon} {title}</h1>'
        f'<p style="color:#8b949e; margin-top:0; font-size:0.92rem;">{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.divider()


# ─── Sidebar Branding ──────────────────────────────────────────────────────────

def sidebar_brand(version: str, owner: str) -> None:
    st.sidebar.markdown(
        f'<div class="sidebar-brand">'
        f'<div class="sidebar-brand-title logo-pulse">🛡️ DevShield AI</div>'
        f'<div class="sidebar-brand-sub">v{version} &nbsp;·&nbsp; {owner}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.divider()


# ─── Empty State ───────────────────────────────────────────────────────────────

def empty_state(icon: str, message: str, hint: str = "") -> None:
    st.markdown(
        f'<div style="text-align:center; padding:60px 20px;">'
        f'<div style="font-size:3rem; margin-bottom:12px;">{icon}</div>'
        f'<div style="color:#8b949e; font-size:1rem;">{message}</div>'
        f'<div style="color:#484f58; font-size:0.82rem; margin-top:6px;">{hint}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─── Session State Helpers ─────────────────────────────────────────────────────

def init_state(key: str, default):
    """Initialize a session state key if not already set."""
    if key not in st.session_state:
        st.session_state[key] = default
