"""
DevShield AI — Page 2: Documentation Engine
Takes code (from Generator or pasted) → writes README, API docs, usage examples
→ exports to Word (.docx) and PDF.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from config.settings import APP_NAME, APP_OWNER, APP_VERSION, SUPPORTED_LANGUAGES
from database.session_manager import get_security_analysis, init_db, update_session_flags
from modules.doc_engine import export_to_pdf, export_to_word, generate_documentation
from ui.components import empty_state, init_state, page_header, sidebar_brand
from ui.styles import get_css

# ── Setup ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"Document — {APP_NAME}",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()
st.markdown(get_css(), unsafe_allow_html=True)
sidebar_brand(APP_VERSION, APP_OWNER)

# ── Session State ─────────────────────────────────────────────────────────────
init_state("doc_result", None)
init_state("doc_code", "")
init_state("doc_task", "")
init_state("doc_language", "Python")
init_state("doc_session_id", None)

page_header(
    "📄",
    "Documentation Engine",
    "Paste code or carry it from the Generator — DevShield writes all your docs automatically.",
)

# ── Source Code Input ─────────────────────────────────────────────────────────
st.markdown("### 📥 Source Code")

# Pre-fill from Generator if navigated from there
prefill_code = st.session_state.get("doc_code", "")
prefill_task = st.session_state.get("doc_task", "")
prefill_lang = st.session_state.get("doc_language", "Python")

tabs = st.tabs(["✏️ Paste Code", "📋 From Generator Session"])

with tabs[0]:
    with st.form("doc_form"):
        code_input = st.text_area(
            "Paste your code here",
            value=prefill_code,
            height=200,
            placeholder="Paste any Python, JavaScript, Java, C++, etc. code here...",
        )
        task_input = st.text_input(
            "Task / Project description",
            value=prefill_task,
            placeholder="What does this code do? e.g. 'JWT authentication API'",
        )
        lang_input = st.selectbox(
            "Language",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(prefill_lang) if prefill_lang in SUPPORTED_LANGUAGES else 0,
        )

        include_security = st.checkbox(
            "🔐 Include security report section (if available from a previous scan)",
            value=True,
        )
        submitted = st.form_submit_button("📄 Generate Documentation", use_container_width=True)

with tabs[1]:
    session_id_input = st.text_input(
        "Session ID (from Generate page)",
        value=st.session_state.get("doc_session_id", "") or "",
        placeholder="DS_20250411_182233_1",
    )
    if session_id_input and st.button("📥 Load from Session"):
        from database.session_manager import get_session
        sess = get_session(session_id_input.strip())
        if sess:
            st.session_state.doc_code = sess.get("code", "")
            st.session_state.doc_task = sess.get("task", "")
            st.session_state.doc_language = sess.get("language", "Python")
            st.session_state.doc_session_id = sess["id"]
            st.success(f"✅ Loaded session: {sess['id']}")
            st.rerun()
        else:
            st.error("Session not found.")

# ── Generation ────────────────────────────────────────────────────────────────
code_to_use = code_input if "code_input" in dir() else prefill_code
task_to_use = task_input if "task_input" in dir() else prefill_task
lang_to_use = lang_input if "lang_input" in dir() else prefill_lang

if submitted and code_to_use.strip():
    # Optionally load security report
    sec_report = None
    if include_security and st.session_state.doc_session_id:
        sec_report = get_security_analysis(st.session_state.doc_session_id)

    with st.spinner("📄 Generating documentation..."):
        doc_result = generate_documentation(
            code=code_to_use.strip(),
            task=task_to_use.strip() or "Generated Code",
            language=lang_to_use,
            security_report=sec_report,
        )

    st.session_state.doc_result = doc_result
    st.session_state.doc_code = code_to_use.strip()
    st.session_state.doc_task = task_to_use.strip()
    st.session_state.doc_language = lang_to_use

    if st.session_state.doc_session_id:
        update_session_flags(st.session_state.doc_session_id, doc_generated=True)

elif submitted and not code_to_use.strip():
    st.warning("⚠️ Please paste some code first.")

# ── Results ───────────────────────────────────────────────────────────────────
doc_result = st.session_state.doc_result

if doc_result:
    st.divider()

    if not doc_result.get("success"):
        st.warning(f"⚠️ Documentation generated with warnings: {doc_result.get('error', '')}")

    # ── Tab viewer ──────────────────────────────────────────────────────────
    dt1, dt2, dt3, dt4 = st.tabs(["📋 README", "📚 API Reference", "🚀 Examples", "⬇️ Export"])

    with dt1:
        readme = doc_result.get("readme", "")
        if readme:
            st.markdown(readme)
        else:
            empty_state("📋", "No README generated")

    with dt2:
        fn_docs = doc_result.get("function_docs", [])
        if fn_docs:
            for fn in fn_docs:
                with st.expander(f"🔹 `{fn.get('name', 'Unknown')}`", expanded=False):
                    st.code(fn.get("signature", ""), language="python")
                    st.markdown(f"**Description:** {fn.get('description', '')}")

                    params = fn.get("params", [])
                    if params:
                        st.markdown("**Parameters:**")
                        for p in params:
                            st.markdown(
                                f"- `{p.get('name')}` *({p.get('type', 'Any')})* — {p.get('description', '')}"
                            )

                    if fn.get("returns"):
                        st.markdown(f"**Returns:** {fn['returns']}")

                    raises = fn.get("raises", [])
                    if raises:
                        st.markdown("**Raises:**")
                        for r in raises:
                            st.markdown(f"- `{r}`")

                    if fn.get("example"):
                        st.markdown("**Example:**")
                        st.code(fn["example"])
        else:
            empty_state("📚", "No function documentation generated")

    with dt3:
        examples = doc_result.get("usage_examples", [])
        if examples:
            for i, ex in enumerate(examples, 1):
                st.markdown(f"#### Example {i}: {ex.get('title', '')}")
                st.markdown(ex.get("description", ""))
                st.code(
                    ex.get("code", ""),
                    language=st.session_state.doc_language.lower().split()[0],
                )
                st.divider()
        else:
            empty_state("🚀", "No usage examples generated")

    with dt4:
        st.markdown("### ⬇️ Export Documentation")

        if doc_result.get("security_notes"):
            st.markdown("**🔐 Security Notes:**")
            for note in doc_result["security_notes"]:
                st.markdown(f"- {note}")
            st.divider()

        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.markdown(
                '<div class="ds-card" style="text-align:center;">'
                '<div style="font-size:2rem;">📘</div>'
                '<b>Word Document (.docx)</b><br>'
                '<span style="color:#8b949e;font-size:0.82rem;">Styled with cover page, '
                'code blocks, API reference & security table</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button("📘 Export to Word", use_container_width=True, key="export_word"):
                sec_report = None
                if st.session_state.doc_session_id:
                    sec_report = get_security_analysis(st.session_state.doc_session_id)
                with st.spinner("Generating Word document..."):
                    try:
                        path = export_to_word(
                            doc_data=doc_result,
                            task=st.session_state.doc_task or "DevShield Report",
                            language=st.session_state.doc_language,
                            code=st.session_state.doc_code,
                            security_report=sec_report,
                        )
                        with open(path, "rb") as f:
                            st.download_button(
                                "⬇️ Download .docx",
                                data=f.read(),
                                file_name=Path(path).name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                            )
                        st.success(f"✅ Saved to: `{path}`")
                    except Exception as e:
                        st.error(f"Export failed: {e}")

        with exp_col2:
            st.markdown(
                '<div class="ds-card" style="text-align:center;">'
                '<div style="font-size:2rem;">📕</div>'
                '<b>PDF Report (.pdf)</b><br>'
                '<span style="color:#8b949e;font-size:0.82rem;">Printable PDF with '
                'source code, vulnerability table & project summary</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button("📕 Export to PDF", use_container_width=True, key="export_pdf"):
                sec_report = None
                if st.session_state.doc_session_id:
                    sec_report = get_security_analysis(st.session_state.doc_session_id)
                with st.spinner("Generating PDF..."):
                    try:
                        path = export_to_pdf(
                            doc_data=doc_result,
                            task=st.session_state.doc_task or "DevShield Report",
                            language=st.session_state.doc_language,
                            code=st.session_state.doc_code,
                            security_report=sec_report,
                        )
                        with open(path, "rb") as f:
                            st.download_button(
                                "⬇️ Download .pdf",
                                data=f.read(),
                                file_name=Path(path).name,
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        st.success(f"✅ Saved to: `{path}`")
                    except Exception as e:
                        st.error(f"Export failed: {e}")

        # Raw Markdown download
        st.divider()
        if doc_result.get("readme"):
            st.download_button(
                "⬇️ Download README.md",
                data=doc_result["readme"],
                file_name="README.md",
                mime="text/markdown",
                use_container_width=True,
            )

else:
    if not submitted:
        empty_state(
            "📄",
            "No documentation yet",
            "Paste code above or carry code from the ⚡ Generate page",
        )
