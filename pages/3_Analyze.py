"""
DevShield AI — Page 3: Security Analyzer
Scan any code for vulnerabilities → OWASP-mapped report → Auto-Fix.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from config.settings import APP_NAME, APP_OWNER, APP_VERSION, SEVERITY_COLORS, SUPPORTED_LANGUAGES
from database.session_manager import (
    get_custom_rules_db,
    get_session,
    init_db,
    save_security_analysis,
    update_session_flags,
)
from modules.security_analyzer import auto_fix_code, run_full_analysis
from ui.components import (
    empty_state,
    init_state,
    owasp_tag,
    page_header,
    score_display,
    severity_badge,
    sidebar_brand,
    vulnerability_card,
)
from ui.styles import get_css

# ── Setup ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"Analyze — {APP_NAME}",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()
st.markdown(get_css(), unsafe_allow_html=True)
sidebar_brand(APP_VERSION, APP_OWNER)

# ── Session State ─────────────────────────────────────────────────────────────
init_state("analyze_result", None)
init_state("analyze_code", "")
init_state("analyze_language", "Python")
init_state("analyze_session_id", None)
init_state("fixed_result", None)

page_header(
    "🔍",
    "Security Analyzer",
    "Paste any code → Bandit + Gemini AI + Custom Rules → OWASP-mapped vulnerability report.",
)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("### 📥 Code to Analyze")

prefill_code = st.session_state.get("analyze_code", "")
prefill_lang = st.session_state.get("analyze_language", "Python")

with st.form("analyze_form"):
    code_input = st.text_area(
        "Paste code here",
        value=prefill_code,
        height=200,
        placeholder="Paste any code to scan for vulnerabilities...",
    )
    col_l, col_s = st.columns([1, 2])
    with col_l:
        lang_sel = st.selectbox(
            "Language",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(prefill_lang) if prefill_lang in SUPPORTED_LANGUAGES else 0,
        )
    with col_s:
        session_ref = st.text_input(
            "Link to session (optional)",
            value=st.session_state.get("analyze_session_id", "") or "",
            placeholder="DS_20250411_182233 — links analysis to a Generate session",
        )

    use_custom = st.checkbox("🛡️ Apply custom rules from Settings", value=True)
    submitted = st.form_submit_button("🔍 Run Full Security Analysis", use_container_width=True)

# ── Also allow loading from session ──────────────────────────────────────────
with st.expander("📂 Load code from a saved session"):
    sid_load = st.text_input("Session ID to load", key="sid_load_input")
    if st.button("📥 Load session code"):
        sess = get_session(sid_load.strip()) if sid_load.strip() else None
        if sess:
            st.session_state.analyze_code = sess.get("code", "")
            st.session_state.analyze_language = sess.get("language", "Python")
            st.session_state.analyze_session_id = sess["id"]
            st.success(f"Loaded: {sess['id']}")
            st.rerun()
        else:
            st.error("Session not found.")

# ── Run Analysis ──────────────────────────────────────────────────────────────
code_to_scan = code_input.strip() if "code_input" in dir() else ""
lang_to_scan = lang_sel if "lang_sel" in dir() else "Python"

if submitted and code_to_scan:
    db_rules = get_custom_rules_db() if use_custom else []

    progress_bar = st.progress(0, text="Initializing analysis pipeline...")

    progress_bar.progress(10, text="🔧 Running custom rules...")
    progress_bar.progress(30, text="🐍 Bandit static analysis...")
    with st.spinner("🔍 Running full security analysis (Bandit + Gemini AI)..."):
        result = run_full_analysis(
            code=code_to_scan,
            language=lang_to_scan,
            db_rules=db_rules,
        )

    progress_bar.progress(90, text="📊 Mapping to OWASP Top 10...")

    # Save to DB
    linked_session = (session_ref or st.session_state.get("analyze_session_id", "")).strip()
    if not linked_session:
        from database.session_manager import create_session_id, save_session
        linked_session = create_session_id()
        save_session(
            session_id=linked_session,
            task="[Direct Paste Analysis]",
            language=lang_to_scan,
            code=code_to_scan,
        )

    save_security_analysis(
        session_id=linked_session,
        code=code_to_scan,
        vulnerabilities=result["vulnerabilities"],
        fixed_code="",
        overall_score=result["overall_score"],
        grade=result["grade"],
        severity_counts=result["severity_counts"],
        summary=result["summary"],
    )
    update_session_flags(linked_session, analyzed=True)

    progress_bar.progress(100, text="✅ Analysis complete!")
    st.session_state.analyze_result = result
    st.session_state.analyze_code = code_to_scan
    st.session_state.analyze_language = lang_to_scan
    st.session_state.analyze_session_id = linked_session
    st.session_state.fixed_result = None

elif submitted and not code_to_scan:
    st.warning("⚠️ Please paste some code to analyze.")

# ── Results ───────────────────────────────────────────────────────────────────
result = st.session_state.analyze_result

if result:
    st.divider()

    # ── Score + Summary Row ──────────────────────────────────────────────────
    score_col, summary_col = st.columns([1, 2.5])
    with score_col:
        st.markdown(
            score_display(result["overall_score"], result["grade"]),
            unsafe_allow_html=True,
        )
    with summary_col:
        st.markdown("### 📋 Executive Summary")
        st.markdown(
            f'<div class="ds-info">{result["summary"]}</div>',
            unsafe_allow_html=True,
        )
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Issues", result["total_issues"])
        m2.metric("Gemini Found", result.get("gemini_count", 0))
        m3.metric("Bandit Found", result.get("bandit_count", 0))
        m4.metric("Custom Rules", result.get("custom_rule_count", 0))

    st.divider()

    # ── Severity Chart ───────────────────────────────────────────────────────
    sev_counts = result.get("severity_counts", {})
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    counts = [sev_counts.get(s, 0) for s in severities]
    bar_colors = ["#FF2D55", "#FF6B00", "#FFD60A", "#30D158", "#636366"]

    fig = go.Figure(
        go.Bar(
            x=severities, y=counts,
            marker_color=bar_colors,
            text=counts, textposition="outside",
            textfont=dict(color="#e6edf3", family="Inter", size=14),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e", family="Inter"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Vulnerability List ───────────────────────────────────────────────────
    vulns = result.get("vulnerabilities", [])
    if vulns:
        # Filter controls
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            sev_filter = st.multiselect(
                "Filter by Severity",
                ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                default=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
            )
        with fc2:
            source_filter = st.multiselect(
                "Filter by Source",
                ["Gemini", "Bandit", "CustomRule"],
                default=["Gemini", "Bandit", "CustomRule"],
            )

        filtered = [
            v for v in vulns
            if v.get("severity", "INFO") in sev_filter
            and v.get("source", "Gemini") in source_filter
        ]

        st.markdown(f"### 🚨 Vulnerabilities Found ({len(filtered)} shown)")
        for i, vuln in enumerate(filtered):
            vulnerability_card(vuln, i)

        # ── OWASP Coverage Map ───────────────────────────────────────────────
        st.divider()
        st.markdown("### 🔒 OWASP Top 10 Coverage")
        owasp_counts = {}
        for v in vulns:
            oid = v.get("owasp_id", "Unclassified")
            oname = v.get("owasp_name", "")
            key = f"{oid}"
            owasp_counts[key] = owasp_counts.get(key, {"count": 0, "name": oname})
            owasp_counts[key]["count"] += 1

        if owasp_counts:
            owcols = st.columns(min(len(owasp_counts), 5))
            for i, (oid, data) in enumerate(owasp_counts.items()):
                with owcols[i % 5]:
                    cnt = data["count"]
                    name = data["name"][:18] or "Unclassified"
                    clr = "#ff2d55" if cnt >= 3 else "#ff6b00" if cnt >= 2 else "#ffd60a"
                    st.markdown(
                        f'<div class="ds-card" style="text-align:center; padding:14px;">'
                        f'<div style="font-size:1.5rem; font-weight:800; color:{clr};">{cnt}</div>'
                        f'<div class="owasp-tag">{oid}</div>'
                        f'<div style="font-size:0.7rem; color:#8b949e; margin-top:4px;">{name}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # ── Auto-Fix Button ──────────────────────────────────────────────────
        st.divider()
        fix_col1, fix_col2 = st.columns([2, 1])
        with fix_col1:
            st.markdown("### 🔧 Auto-Fix Engine")
            st.markdown(
                '<div class="ds-warn">'
                '⚡ One click sends all vulnerabilities back through Gemini with patch instructions. '
                'The fixed code replaces every security issue with inline comments on each fix.'
                '</div>',
                unsafe_allow_html=True,
            )
        with fix_col2:
            run_fix = st.button(
                f"🔧 Auto-Fix All {len(vulns)} Issues",
                use_container_width=True,
                type="primary",
            )

        if run_fix:
            with st.spinner("🔧 Applying security patches..."):
                fixed = auto_fix_code(
                    code=st.session_state.analyze_code,
                    language=st.session_state.analyze_language,
                    vulnerabilities=vulns,
                )
            st.session_state.fixed_result = fixed

            # Save fixed code to analysis record
            if st.session_state.analyze_session_id:
                sql_conn = __import__("sqlite3").connect(str(__import__("pathlib").Path.home() / ".devshield" / "devshield.db"))
                sql_conn.execute(
                    "UPDATE security_analyses SET fixed_code=? WHERE session_id=?",
                    (fixed.get("fixed_code", ""), st.session_state.analyze_session_id),
                )
                sql_conn.commit()
                sql_conn.close()

        fixed_result = st.session_state.fixed_result
        if fixed_result:
            if fixed_result["success"]:
                st.success(f"✅ {len(fixed_result.get('fixes_applied', []))} fixes applied!")
            else:
                st.warning("⚠️ Auto-fix completed with warnings.")

            if fixed_result.get("fixes_applied"):
                st.markdown("**Applied Fixes:**")
                for fix in fixed_result["fixes_applied"]:
                    st.markdown(f"- ✅ {fix}")

            if fixed_result.get("remaining_concerns"):
                st.markdown("**Remaining Concerns (manual review needed):**")
                for concern in fixed_result["remaining_concerns"]:
                    st.markdown(f"- ⚠️ {concern}")

            st.markdown("### ✅ Fixed Code")
            st.code(
                fixed_result.get("fixed_code", ""),
                language=st.session_state.analyze_language.lower().split()[0],
            )
            st.download_button(
                "⬇️ Download Fixed Code",
                data=fixed_result.get("fixed_code", ""),
                file_name="devshield_fixed_code.txt",
                mime="text/plain",
                use_container_width=True,
            )

    else:
        st.markdown(
            '<div class="ds-success" style="font-size:1rem; text-align:center; padding:24px;">'
            '🎉 <b>No vulnerabilities found!</b> Your code looks clean.'
            '</div>',
            unsafe_allow_html=True,
        )

else:
    if not submitted:
        empty_state(
            "🔍",
            "Ready to scan",
            "Paste code into the form above and hit 'Run Full Security Analysis'",
        )
