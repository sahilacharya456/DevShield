"""
DevShield AI — Page 4: Session History
Browse all past sessions, view code & analyses, compare versions,
and export history for fine-tuning.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from config.settings import APP_NAME, APP_OWNER, APP_VERSION
from database.session_manager import (
    export_history_csv,
    get_security_analysis,
    get_session,
    get_session_history,
    get_stats,
    init_db,
)
from ui.components import empty_state, page_header, score_display, severity_badge, sidebar_brand
from ui.styles import get_css

# ── Setup ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"History — {APP_NAME}",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()
st.markdown(get_css(), unsafe_allow_html=True)
sidebar_brand(APP_VERSION, APP_OWNER)

page_header(
    "📜",
    "Session History",
    "Browse every code generation and security scan. Compare versions over time.",
)

# ── Stats bar ─────────────────────────────────────────────────────────────────
stats = get_stats()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sessions", stats["total_sessions"])
m2.metric("Total Scans", stats["total_analyses"])
m3.metric("Avg Rating", f"{stats['avg_rating']:.1f} / 5.0")
m4.metric("Avg Security Score", f"{stats['avg_security_score']:.0f} / 100")

st.divider()

# ── Filter + Export Controls ──────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
with ctrl1:
    search = st.text_input("🔍 Search sessions", placeholder="Filter by task, language...")
with ctrl2:
    lang_filter = st.selectbox(
        "Language filter",
        ["All"] + ["Python", "JavaScript", "TypeScript", "C++", "Java", "SQL", "Go", "Rust"],
    )
with ctrl3:
    limit = st.selectbox("Show", [10, 25, 50, 100], index=0)

# Export button
exp_col, _ = st.columns([1, 3])
with exp_col:
    if st.button("⬇️ Export History CSV"):
        from config.settings import EXPORTS_DIR
        csv_path = EXPORTS_DIR / "devshield_history.csv"
        export_history_csv(str(csv_path))
        with open(csv_path, "rb") as f:
            st.download_button(
                "📥 Download history.csv",
                data=f.read(),
                file_name="devshield_history.csv",
                mime="text/csv",
            )

# ── Session List ──────────────────────────────────────────────────────────────
history = get_session_history(limit=limit)

# Apply filters
if search:
    search_lower = search.lower()
    history = [
        h for h in history
        if search_lower in (h.get("task", "") or "").lower()
        or search_lower in (h.get("language", "") or "").lower()
        or search_lower in (h.get("id", "") or "").lower()
    ]

if lang_filter != "All":
    history = [h for h in history if h.get("language", "") == lang_filter]

if not history:
    empty_state("📜", "No sessions found", "Try adjusting your filters or generate some code first")
else:
    st.markdown(f"**{len(history)} session(s) found**")
    st.markdown("---")

    for session in history:
        task_short = (session.get("task") or "Untitled")[:60]
        ts = (session.get("timestamp") or "")[:16].replace("T", " ")
        lang = session.get("language", "—")
        rating = session.get("user_rating")
        analyzed = bool(session.get("analyzed"))
        doc_gen = bool(session.get("doc_generated"))
        confidence = session.get("confidence", 0)
        sid = session.get("id", "")

        stars = "★" * (rating or 0) + "☆" * (5 - (rating or 0)) if rating else "Not rated"
        conf_pct = confidence * 10 if confidence else 0

        with st.expander(
            f"[{lang}] {task_short}  —  {ts}",
            expanded=False,
        ):
            info_c1, info_c2, info_c3 = st.columns(3)
            info_c1.markdown(f"**Session ID:** `{sid}`")
            info_c2.markdown(f"**Rating:** {stars}")
            info_c3.markdown(f"**Confidence:** {confidence}/10")

            badges = []
            if analyzed:
                badges.append("🔍 Analyzed")
            if doc_gen:
                badges.append("📄 Docs Generated")
            if badges:
                st.markdown("  &nbsp;·&nbsp;  ".join(badges))

            feedback = session.get("user_feedback", "")
            if feedback:
                st.markdown(f'<div class="ds-info">💬 <b>Your feedback:</b> {feedback}</div>', unsafe_allow_html=True)

            tab_code, tab_analysis = st.tabs(["💻 Code", "🔍 Security Analysis"])

            with tab_code:
                code = session.get("code", "")
                if code:
                    st.code(code, language=lang.lower().split()[0])
                    action1, action2 = st.columns(2)
                    with action1:
                        if st.button("🔍 Re-Analyze", key=f"reanalyze_{sid}"):
                            st.session_state["analyze_code"] = code
                            st.session_state["analyze_language"] = lang
                            st.session_state["analyze_session_id"] = sid
                            st.switch_page("pages/3_Analyze.py")
                    with action2:
                        if st.button("📄 Re-Document", key=f"redoc_{sid}"):
                            st.session_state["doc_code"] = code
                            st.session_state["doc_task"] = session.get("task", "")
                            st.session_state["doc_language"] = lang
                            st.session_state["doc_session_id"] = sid
                            st.switch_page("pages/2_Document.py")
                else:
                    st.caption("No code stored for this session.")

            with tab_analysis:
                analysis = get_security_analysis(sid)
                if analysis:
                    sc1, sc2 = st.columns([1, 3])
                    with sc1:
                        st.markdown(
                            score_display(analysis["overall_score"], analysis["grade"]),
                            unsafe_allow_html=True,
                        )
                    with sc2:
                        st.markdown(f"**Summary:** {analysis.get('summary', '')}")
                        sc = analysis.get("severity_counts", {})
                        sev_cols = st.columns(5)
                        for i, (sev, clr) in enumerate([("CRITICAL", "#ff2d55"), ("HIGH", "#ff6b00"),
                                                         ("MEDIUM", "#ffd60a"), ("LOW", "#30d158"), ("INFO", "#636366")]):
                            sev_cols[i].markdown(
                                f'<div style="text-align:center;">'
                                f'<div style="font-size:1.4rem; font-weight:800; color:{clr};">{sc.get(sev, 0)}</div>'
                                f'<div style="font-size:0.65rem; color:#8b949e; text-transform:uppercase;">{sev}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                    vulns = analysis.get("vulnerabilities", [])
                    if vulns:
                        st.markdown(f"**{len(vulns)} vulnerabilities found:**")
                        for v in vulns[:10]:
                            st.markdown(
                                f"{severity_badge(v.get('severity', 'INFO'))} "
                                f"**{v.get('name', 'Unknown')}** — Line {v.get('line', '?')} — "
                                f"`{v.get('owasp_id', 'N/A')}`",
                                unsafe_allow_html=True,
                            )
                        if len(vulns) > 10:
                            st.caption(f"...and {len(vulns) - 10} more. Re-analyze to see full report.")

                    if analysis.get("fixed_code"):
                        st.markdown("**✅ Fixed code is available:**")
                        st.download_button(
                            "⬇️ Download Fixed Code",
                            data=analysis["fixed_code"],
                            file_name=f"devshield_fixed_{sid}.txt",
                            mime="text/plain",
                            key=f"dl_fixed_{sid}",
                        )
                else:
                    st.caption("No security analysis found for this session.")
                    if st.button("🔍 Run Analysis Now", key=f"analyze_now_{sid}"):
                        code = session.get("code", "")
                        if code:
                            st.session_state["analyze_code"] = code
                            st.session_state["analyze_language"] = lang
                            st.session_state["analyze_session_id"] = sid
                            st.switch_page("pages/3_Analyze.py")
