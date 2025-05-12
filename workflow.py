from baml_client import b
import streamlit as st
from llm_util import removeMarkdownTag, get_context_prompt, removeFinalTag
import time

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

CONTEXT = get_context_prompt(target_lang=target_lang, source_lang=source_lang, extra_context=extra_context)


############################################################
#                   ANALYSIS
############################################################

st.header("Phase 1: Analysis", divider=True)

ANALYSIS_REDO_BTN = st.button("Redo " + "Analysis")
ANALYSIS_STATUS = st.status("Analyzing prompt..")

with ANALYSIS_STATUS:
    _analysis = b.GetAnalysis(context=CONTEXT, source_lang=source_lang, target_lang=target_lang, source_text=source_text)
    _analysis = removeMarkdownTag(_analysis)
    st.write("Analysis Complete")

    if ANALYSIS_REDO_BTN:
        _analysis = st.empty()
        _analysis = b.GetAnalysis(context=CONTEXT, source_lang=source_lang, target_lang=target_lang, source_text=source_text)
        time.sleep(2)
        _analysis = removeMarkdownTag(_analysis)

st.markdown(_analysis)

############################################################
#                   LITERAL TRANSLATION
############################################################

st.header("Phase 2: Literal Translation", divider=True)

st.subheader(f"{target_lang} Translation")

LITERAL_REDO_BTN = st.button("Redo " + "Literal Translation")
LITERAL_STATUS = st.status("Literal Translation...")

with LITERAL_STATUS:
    _literal_translation = b.GetLiteralTranslate(context=CONTEXT, prompt=source_text, source_lang=source_lang, target_lang=target_lang, is_song=False)
    _literal_translation = removeMarkdownTag(_literal_translation)

    if LITERAL_REDO_BTN:
        _literal_translation = st.empty()
        _literal_translation = b.GetLiteralTranslate(context=CONTEXT, prompt=source_text, source_lang=source_lang, target_lang=target_lang, is_song=False)
        time.sleep(2)
        _literal_translation = removeMarkdownTag(_literal_translation)

st.markdown(_literal_translation)

############################################################
#                   CLARITY
############################################################

st.header("Phase 3: Clarity", divider=True)

CLARITY_REDO_BTN = st.button("Redo " + "Clarity")
CLARITY_STATUS = st.status("Generating clarity analysis...")

with CLARITY_STATUS:
    _clarified_translation = b.GetClarity(context=CONTEXT, prompt=source_text, target_lang=target_lang, literal_translation=_literal_translation, analysis=_analysis)
    _clarified_translation = removeMarkdownTag(_clarified_translation)

    if CLARITY_REDO_BTN:
        _clarified_translation = st.empty()
        _clarified_translation = b.GetClarity(context=CONTEXT, prompt=source_text, target_lang=target_lang, literal_translation=_literal_translation, analysis=_analysis)
        time.sleep(2)
        _clarified_translation = removeMarkdownTag(_clarified_translation)

st.markdown(_clarified_translation)

############################################################
#                   BACKTRANSLATION
############################################################

st.header("Phase 4: Backtranslation", divider=True)

BACKTRANSLATE_REDO_BTN = st.button("Redo " + "Backtranslation")
BACKTRANSLATE_STATUS = st.status("Generating backtranslation...")

# show the original text next to the backtranslation
cols = st.columns(2)
with cols[0]:
    st.subheader("Original Text")
    st.text(source_text)
with cols[1]:
    with BACKTRANSLATE_STATUS:
        _backtranslation = b.GetBackTranslation(context=CONTEXT, source_lang=source_lang, clarified_translation=_clarified_translation)
        _backtranslation = removeMarkdownTag(_backtranslation)

        if BACKTRANSLATE_REDO_BTN:
            _backtranslation = st.empty()
            _backtranslation = b.GetBackTranslation(context=CONTEXT, source_lang=source_lang, clarified_translation=_clarified_translation)
            time.sleep(2)
            _backtranslation = removeMarkdownTag(_backtranslation)

    st.markdown(_backtranslation)

############################################################
#                   FINAL REVIEW
############################################################

st.header("Phase 5: Final Review", divider=True)

REVIEW_REDO_BTN = st.button("Redo " + "Review")
REVIEW_STATUS = st.status("Generating review...")

with REVIEW_STATUS:
    _final_review = b.GetReview(
        context=CONTEXT,
        target_lang=target_lang,
        source_text=source_text,
        clarified_translation=_clarified_translation,
        backtranslation=_backtranslation,
        syllabification="")

    _final_review = removeMarkdownTag(_final_review)

    if REVIEW_REDO_BTN:
        _final_review = st.empty()

        _final_review = b.GetReview(
        context=CONTEXT,
        target_lang=target_lang,
        source_text=source_text,
        clarified_translation=_clarified_translation,
        backtranslation=_backtranslation,
        syllabification="")

        time.sleep(2)
        _final_review = removeMarkdownTag(_final_review)

st.markdown(_final_review)

############################################################
#                   FINAL TRANSLATION
############################################################

st.header("Phase 6: Final Translation", divider=True)

FINAL_REDO_BTN = st.button("Redo " + "Final Translation")
FINAL_STATUS = st.status("Generating final translation...")

with FINAL_STATUS:
    _final_translation = b.GetFinalTranslation(
        context=CONTEXT,
        target_lang=target_lang,
        source_text=source_text,
        analysis=_analysis,
        clarified_translation=_clarified_translation,
        final_review=_final_review,
        item_type="text")

    _final_translation = removeMarkdownTag(_final_translation)
    _final_translation = removeFinalTag(_final_translation)

    if FINAL_REDO_BTN:
        _final_translation = st.empty()

        _final_translation = b.GetFinalTranslation(
        context=CONTEXT,
        target_lang=target_lang,
        source_text=source_text,
        analysis=_analysis,
        clarified_translation=_clarified_translation,
        final_review=_final_review,
        item_type="text")

        time.sleep(2)
        _final_translation = removeMarkdownTag(_final_translation)
        _final_translation = removeFinalTag(_final_translation)

# original text side-by-side with final translation

cols = st.columns(2)
with cols[0]:
    st.subheader("Original Text")
    st.text(source_text)

with cols[1]:
    tabs = st.tabs(["Easy to read", "Easy to copy-paste"])
    tabs[0].text(_final_translation)
    with tabs[1]:
        st.write("Click the Copy button in the top-right corner to copy the text.")
        st.code(_final_translation)