from baml_client import b
import streamlit as st
from llm_util import removeMarkdownTag, get_context_prompt, removeFinalTag

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

st.header("Phase 3: Clarity")

_clarified_translation = b.GetClarity(context=CONTEXT, prompt=source_text, target_lang=target_lang, literal_translation=_literal_translation, analysis=_analysis)
_clarified_translation = removeMarkdownTag(_clarified_translation)

st.markdown(_clarified_translation)

st.header("Phase 4: Backtranslation")

# show the original text next to the backtranslation
cols = st.columns(2)
with cols[0]:
    st.subheader("Original Text")
    st.text(source_text)
with cols[1]:
    _backtranslation = b.GetBackTranslation(context=CONTEXT, source_lang=source_lang, clarified_translation=_clarified_translation)
    _backtranslation = removeMarkdownTag(_backtranslation)

    st.markdown(_backtranslation)

st.header("Phase 5: Final Review")

_final_review = b.GetReview(
    context=CONTEXT,
    target_lang=target_lang,
    source_text=source_text,
    clarified_translation=_clarified_translation,
    backtranslation=_backtranslation,
    syllabification="")

_final_review = removeMarkdownTag(_final_review)

st.markdown(_final_review)

st.header("Phase 6: Final Translation")

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

def iteratively_improve(translation):
    """Copy the final translation back into 'clarified translation'"""
    key = f"clarified_translation_{target_lang}"
    st.session_state[key] = translation

st.button("Iteratively Improve", on_click=iteratively_improve, args=(_final_translation,))

st.write("## Conversation")

if "messages" not in st.session_state or st.button("Reset Chat"):
    st.session_state.messages = []

with st.chat_message("user"):
    st.write(f"*Context includes original text and final translation above*")
    context_for_llm = f"""<context><source_text>
{source_text}
</source_text>

<translationSoFar>
{_final_translation}
</translationSoFar>
</context>
"""

    with st.expander("Show context for LLM", expanded=False):
        st.text(context_for_llm)

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# # Accept user input
# if prompt := st.chat_input():
#     with st.chat_message("user"):
#         st.markdown(prompt)


#     st.session_state.messages.append({"role": "user", "content": prompt})

#     # Prepend the context to the first user message
#     actual_messages = [
#         {"role": "user", "content": context_for_llm},
#         {"role": "assistant", "content": "Got it."},
#     ] + st.session_state.messages
#     with st.chat_message('assistant'):
#         # This shows the response also
#         response = st.write_stream(stream_llm_response(actual_messages))
#     st.session_state.messages.append({"role": "assistant", "content": response})