"""
DevShield AI — Page 1: Code Generator
Describe a task → Gemini generates production-ready, secure code.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from config.settings import APP_NAME, APP_OWNER, APP_VERSION, SUPPORTED_LANGUAGES
from database.session_manager import create_session_id, init_db, save_session, update_session_flags
from modules.code_generator import generate_code
from ui.components import (
    confidence_bar,
    empty_state,
    init_state,
    page_header,
    sidebar_brand,
)
from ui.styles import get_css
from utils.preference_learner import update_preferences_from_feedback

# ── Setup ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"Generate — {APP_NAME}",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()
st.markdown(get_css(), unsafe_allow_html=True)
sidebar_brand(APP_VERSION, APP_OWNER)

# ── Session State ─────────────────────────────────────────────────────────────
init_state("gen_result", None)
init_state("gen_session_id", None)
init_state("gen_task", "")
init_state("gen_language", "Python")
init_state("gen_rated", False)

page_header("⚡", "Code Generator", "Describe what you want to build — DevShield generates production-ready, secure code.")

# ── Input Panel ───────────────────────────────────────────────────────────────
with st.form("gen_form", clear_on_submit=False):
    task = st.text_area(
        "📝 What do you want to build?",
        placeholder=(
            "e.g. 'A Python REST API endpoint that authenticates users with JWT tokens "
            "and stores their data in PostgreSQL with parameterized queries'"
        ),
        height=120,
        key="task_input",
    )

    col_lang, col_ctx = st.columns([1, 2])
    with col_lang:
        language = st.selectbox("🔤 Language / Framework", SUPPORTED_LANGUAGES, key="lang_select")
    with col_ctx:
        extra = st.text_input(
            "🔧 Additional requirements (optional)",
            placeholder="e.g. 'Use async/await, add rate limiting, Redis caching'",
            key="extra_input",
        )

    use_prefs = st.checkbox("🧠 Apply learned preferences", value=True,
                            help="Inject your past feedback and coding patterns into the prompt")

    submitted = st.form_submit_button("⚡ Generate Secure Code", use_container_width=True)

# ── Generation ────────────────────────────────────────────────────────────────
if submitted and task.strip():
    with st.spinner("🤖 DevShield is generating your code..."):
        result = generate_code(
            task=task.strip(),
            language=language,
            additional_context=extra.strip(),
            use_preferences=use_prefs,
        )

    if result["success"]:
        session_id = create_session_id()
        save_session(
            session_id=session_id,
            task=task.strip(),
            language=language,
            code=result["code"],
            tokens=result["tokens_used"],
            confidence=result["confidence_score"],
        )
        st.session_state.gen_result = result
        st.session_state.gen_session_id = session_id
        st.session_state.gen_task = task.strip()
        st.session_state.gen_language = language
        st.session_state.gen_rated = False
    else:
        st.error(f"❌ Generation failed: {result['error']}")

elif submitted and not task.strip():
    st.warning("⚠️ Please enter a task description.")

# ── Results Panel ─────────────────────────────────────────────────────────────
result = st.session_state.gen_result
if result:
    st.divider()

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Confidence", f"{result['confidence_score']}/10")
    m2.metric("Tokens Used", f"{result['tokens_used']:,}")
    m3.metric("Language", st.session_state.gen_language)
    m4.metric("Session ID", st.session_state.gen_session_id or "—")

    # Confidence bar
    st.markdown(
        confidence_bar(result["confidence_score"], 10),
        unsafe_allow_html=True,
    )
    st.caption(f"💭 {result['confidence_reasoning']}")

    # Security features
    if result.get("key_security_features"):
        feats = "  &nbsp;·&nbsp;  ".join(
            [f"✅ {f}" for f in result["key_security_features"]]
        )
        st.markdown(
            f'<div class="ds-success" style="font-size:0.83rem;">{feats}</div>',
            unsafe_allow_html=True,
        )

    # Dependencies
    if result.get("dependencies"):
        st.markdown(
            f'<div class="ds-info" style="font-size:0.82rem;">'
            f'📦 <b>Dependencies:</b> '
            f'{", ".join([f"<code>{d}</code>" for d in result["dependencies"]])}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Code display
    st.markdown("### 💻 Generated Code")
    st.code(result["code"], language=st.session_state.gen_language.lower().split()[0])

    # Action row
    act1, act2, act3 = st.columns(3)
    with act1:
        if st.button("🔍 Analyze Security", use_container_width=True):
            st.session_state["analyze_code"] = result["code"]
            st.session_state["analyze_language"] = st.session_state.gen_language
            st.session_state["analyze_session_id"] = st.session_state.gen_session_id
            st.switch_page("pages/3_Analyze.py")
    with act2:
        if st.button("📄 Generate Docs", use_container_width=True):
            st.session_state["doc_code"] = result["code"]
            st.session_state["doc_task"] = st.session_state.gen_task
            st.session_state["doc_language"] = st.session_state.gen_language
            st.session_state["doc_session_id"] = st.session_state.gen_session_id
            st.switch_page("pages/2_Document.py")
    with act3:
        st.download_button(
            "⬇️ Download Code",
            data=result["code"],
            file_name=f"devshield_{st.session_state.gen_language.lower().split()[0]}_code.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── Feedback / Rating ──────────────────────────────────────────────────────
    if not st.session_state.gen_rated:
        st.divider()
        st.markdown("### 📊 Rate This Generation")
        st.caption("Your feedback trains DevShield to improve over time.")

        with st.form("rating_form"):
            rc1, rc2 = st.columns([1, 2])
            with rc1:
                rating = st.slider("Star Rating", 1, 5, 4, format="%d ⭐")
            with rc2:
                feedback_text = st.text_input(
                    "Feedback (optional)",
                    placeholder="What was good or what could be improved?",
                )
            submit_rating = st.form_submit_button("💾 Save Feedback", use_container_width=True)

        if submit_rating:
            sid = st.session_state.gen_session_id
            if sid:
                from database.session_manager import update_session_rating
                update_session_rating(sid, rating, feedback_text)
                update_preferences_from_feedback(
                    st.session_state.gen_task,
                    st.session_state.gen_language,
                    rating,
                    feedback_text,
                )
            st.session_state.gen_rated = True
            st.success("✅ Feedback saved! DevShield learned from your rating.")
            st.balloons()
    else:
        st.markdown(
            '<div class="ds-success">✅ Feedback saved. Preferences updated.</div>',
            unsafe_allow_html=True,
        )

else:
    if not submitted:
        empty_state(
            "⚡",
            "Ready to generate code",
            "Fill in the task description above and hit 'Generate Secure Code'",
        )
