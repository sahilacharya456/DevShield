"""
DevShield AI — Main Dashboard (app.py)
Entry point for the Streamlit application.
Shows stats, score trends, recent sessions, and system status.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.settings import APP_NAME, APP_OWNER, APP_VERSION, GEMINI_API_KEY, GRADE_COLORS
from database.session_manager import get_session_history, get_stats, init_db
from ui.components import empty_state, page_header, sidebar_brand, stat_card
from ui.styles import get_css
from utils.preference_learner import get_readiness_for_fine_tuning

# ── Must be FIRST Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME} — Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
st.markdown(get_css(), unsafe_allow_html=True)
sidebar_brand(APP_VERSION, APP_OWNER)

# ── API Key Gate ──────────────────────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.markdown(
        '<div class="ds-danger">'
        '⚠️ <b>GEMINI_API_KEY is not set.</b> '
        'Create a <code>.env</code> file in the DevShield folder with:<br>'
        '<code>GEMINI_API_KEY=your_key_here</code><br>'
        'Get a free key at <a href="https://aistudio.google.com/app/apikey" target="_blank">aistudio.google.com</a>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Page Header ───────────────────────────────────────────────────────────────
page_header(
    "🏠",
    "Dashboard",
    f"Welcome back, {APP_OWNER}. Your AI-powered secure development platform.",
)

# ── Load Data ─────────────────────────────────────────────────────────────────
stats = get_stats()
ft_status = get_readiness_for_fine_tuning()
history = get_session_history(limit=10)

# ── Top KPI Row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (str(stats["total_sessions"]),   "Total Sessions",      c1),
    (str(stats["total_analyses"]),   "Security Scans",      c2),
    (f"{stats['avg_security_score']:.0f}", "Avg Security Score", c3),
    (f"{stats['avg_rating']:.1f}★",  "Avg Rating",          c4),
    (f"{ft_status['progress_pct']}%","Fine-tune Progress",  c5),
]
for val, label, col in kpis:
    with col:
        st.markdown(stat_card(val, label), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row ────────────────────────────────────────────────────────────────
left, right = st.columns([1.6, 1])

with left:
    st.markdown("### 📈 Security Score Trend")
    trend = stats.get("score_trend", [])
    if trend:
        scores = [t["score"] for t in trend]
        labels = [t["timestamp"][:10] for t in trend]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=labels, y=scores, mode="lines+markers",
            line=dict(color="#00ff88", width=2.5, shape="spline"),
            marker=dict(color="#00ff88", size=7, line=dict(color="#070b14", width=2)),
            fill="tozeroy",
            fillcolor="rgba(0,255,136,0.06)",
            name="Security Score",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b949e", family="Inter"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
                       range=[0, 105]),
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("📊", "No scan data yet", "Run your first security analysis to see trends")

with right:
    st.markdown("### 🌐 Language Distribution")
    top_langs = stats.get("top_languages", [])
    if top_langs:
        langs = [l["language"] for l in top_langs]
        counts = [l["count"] for l in top_langs]
        colors_list = ["#00ff88", "#00b4ff", "#7c3aed", "#ffd60a", "#ff6b00"]
        fig2 = go.Figure(go.Pie(
            labels=langs, values=counts,
            hole=0.6,
            marker=dict(colors=colors_list[:len(langs)],
                        line=dict(color="#070b14", width=3)),
            textfont=dict(color="#e6edf3", family="Inter"),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b949e", family="Inter"),
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(color="#8b949e")),
            showlegend=True,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        empty_state("🌐", "No language data yet", "Generate some code to see distribution")

st.divider()

# ── Self-Improvement Progress ──────────────────────────────────────────────────
st.markdown("### 🧠 AI Self-Improvement Progress")
col_prog, col_info = st.columns([2, 1])
with col_prog:
    pct = ft_status["progress_pct"]
    st.progress(pct / 100)
    if ft_status["ready"]:
        st.markdown(
            '<div class="ds-success">✅ <b>Fine-tuning ready!</b> '
            'You have 500+ interactions. Export your feedback data to train a custom model.</div>',
            unsafe_allow_html=True,
        )
    else:
        remaining = ft_status["remaining"]
        st.markdown(
            f'<div class="ds-info">🔄 <b>{pct}% to fine-tuning milestone.</b> '
            f'{remaining} more interactions needed to unlock custom model training.</div>',
            unsafe_allow_html=True,
        )
with col_info:
    st.metric("Total Interactions", ft_status["total_interactions"])
    st.metric("Milestone Target", "500")

st.divider()

# ── Recent Sessions ──────────────────────────────────────────────────────────
st.markdown("### 🕐 Recent Sessions")
if history:
    for session in history[:8]:
        task_short = (session["task"] or "Untitled")[:55]
        ts = (session["timestamp"] or "")[:16].replace("T", " ")
        lang = session.get("language", "—")
        rating = session.get("user_rating")
        analyzed = bool(session.get("analyzed"))
        doc_gen = bool(session.get("doc_generated"))

        stars = "★" * (rating or 0) + "☆" * (5 - (rating or 0)) if rating else "—"
        analysis_badge = "🔍" if analyzed else "○"
        doc_badge = "📄" if doc_gen else "○"

        st.markdown(
            f'<div class="ds-card" style="display:flex; align-items:center; gap:12px; padding:14px 20px;">'
            f'<div style="flex:1;">'
            f'<span style="font-weight:600; font-size:0.92rem;">{task_short}</span>&nbsp;'
            f'<code style="font-size:0.72rem; background:rgba(0,255,136,0.1); '
            f'color:#00ff88; padding:2px 7px; border-radius:4px;">{lang}</code>'
            f'</div>'
            f'<div style="color:#8b949e; font-size:0.78rem; white-space:nowrap;">'
            f'{analysis_badge} Analyzed &nbsp; {doc_badge} Docs &nbsp; '
            f'<span style="color:#ffd60a;">{stars}</span> &nbsp; {ts}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
else:
    empty_state(
        "🚀",
        "No sessions yet",
        "Head to ⚡ Generate to create your first session",
    )

# ── Quick Nav ─────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### ⚡ Quick Start")
q1, q2, q3 = st.columns(3)
with q1:
    st.markdown(
        '<div class="ds-card" style="text-align:center;">'
        '<div style="font-size:2rem;">⚡</div>'
        '<b>Generate Code</b><br>'
        '<span style="color:#8b949e;font-size:0.82rem;">Describe a task → get production-ready code</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with q2:
    st.markdown(
        '<div class="ds-card" style="text-align:center;">'
        '<div style="font-size:2rem;">🔍</div>'
        '<b>Analyze Security</b><br>'
        '<span style="color:#8b949e;font-size:0.82rem;">Paste code → get OWASP-mapped vulnerability report</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with q3:
    st.markdown(
        '<div class="ds-card" style="text-align:center;">'
        '<div style="font-size:2rem;">📄</div>'
        '<b>Generate Docs</b><br>'
        '<span style="color:#8b949e;font-size:0.82rem;">Auto-produce README, API docs, Word & PDF</span>'
        '</div>',
        unsafe_allow_html=True,
    )
