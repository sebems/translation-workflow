from baml_client import b
import streamlit as st
from llm_util import removeMarkdownTag, get_context_prompt

with st.form("input_form"):
    source_lang = st.text_input("Source Language", "English")
    target_lang = st.text_input("Target Language", "French")
    # is_song = st.checkbox("Is this a song?")
    source_text = st.text_area(
        "Original Text",
        key="source_text",
        height=200
    )
    extra_context = st.text_area("Extra Context (optional)", height=200, help="Provide any additional context or instructions that might be helpful for the translation.")
    st.form_submit_button("Start Translation Workflow")

if not source_text:
    st.stop()

st.header("Phase 1: Analysis")

CONTEXT = get_context_prompt(target_lang=target_lang, source_lang=source_lang, extra_context=extra_context)

_analysis = b.GetAnalysis(context=CONTEXT, source_lang=source_lang, target_lang=target_lang, source_text=source_text)
_analysis = removeMarkdownTag(_analysis)

st.markdown(_analysis)

st.header("Phase 2: Literal Translation")

st.subheader(f"{target_lang} Translation")

_literal_translation = b.GetLiteralTranslate(context=CONTEXT, prompt=source_text, source_lang=source_lang, target_lang=target_lang, is_song=False)
_literal_translation = removeMarkdownTag(_literal_translation)

st.markdown(_literal_translation)