import streamlit as st
from llm_util import get_and_show_llm_response

def extract_text_inside_tags(text: str, tag: str) -> str:
    """Extract text inside a pair of tags.
    
    If there's no such tag, return the whole text.
    """
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start = text.find(start_tag)
    end = text.find(end_tag)
    if start == -1 or end == -1:
        return text
    return text[start + len(start_tag):end].strip()


lang = st.text_input("Target Language", "Spanish")

st.header("Phase 1: Source Text Input and Analysis")

# Source text input
source_text = st.text_area(
    "Original Lyrics",
    height=200
)

if not source_text:
    st.stop()



context = f"""For context, we are translating a worship song from English to {lang}, aiming for theological accuracy, simple and clear language, singability to the original tune, and cultural sensitivity.

This step is one part of a multi-step process to translate the song. Do only what is asked in each step.
"""

analysis_prompt = f"""{context}

Please provide a detailed analysis of the source text to help guide the translation process.

{source_text}

Provide a detailed analysis of:
1. Theological concepts and terminology, including any specific references to scripture or doctrine. For each concept or reference, describe it in English and {lang}, including a complete quote in {lang} if applicable.
2. Poetic devices (rhyme scheme, meter, alliteration)
3. Cultural references
4. Key metaphors and imagery
5. Potential translation challenges

Use bullet points to organize your analysis.

Also, for each line, show the stressed and unstressed syllables. For example, "a-MA-zing GRACE, how SWEET the SOUND"; "He who is MIGHTy has DONE a great THING".

Place the results of your analysis inside <analysis> tags.
"""

analysis = get_and_show_llm_response(analysis_prompt, "source_analysis", "Source Analysis")

st.header("Phase 2: Literal Translation")

st.subheader(f"{lang} Translation")

literal_translation_prompt = f"""{context}

Provide a literal, word-for-word translation of the following lyrics into {lang}:

{source_text}

Include alternate translations for key terms and note any challenging passages.

If a stanza has a heading (like Chorus 2 or Bridge), include it in the output *without translation*. Likewise, if a line is blank, include a blank line in the output.

Place your translation inside <literal_translation> tags.
"""

literal_translation = get_and_show_llm_response(literal_translation_prompt, f"literal_translation_{lang}", f"{lang} Literal Translation")

st.header("Phase 3: Singability and Clarity")
    

adaptation_prompt = f"""{context}

Adapt this literal translation into singable, poetic {lang}, emphasizing clarity while retaining a reasonable amount of the original meaning.

If a stanza has a heading (like Chorus 2 or Bridge), include it in the output *without translation*. Likewise, if a line is blank, include a blank line in the output.

If applicable, write an alternative translation after a line in square brackets. For example, "Amazing grace, how sweet the sound [Stunning grace, how it moves my ear]".
If there are no reasonable alternatives, simply leave the line as is.

<original>
{source_text}
</original>

<analysis>
{extract_text_inside_tags(analysis, "analysis")}
</analysis>

<literal_translation>
{extract_text_inside_tags(literal_translation, "literal_translation")}
</literal_translation>

Consider meter and rhyme scheme.

Place your singable translation inside <singable_translation> tags.
"""

singable_translation = get_and_show_llm_response(adaptation_prompt, f"singable_translation_{lang}", f"{lang} Singable Translation")

st.header("Phase 4: Backtranslation")
backtranslation_prompt = f"""{context}

To verify the translation, we will backtranslate it into the original language. Translate the following literally into English, adding notes as needed in [ ] brackets:

<translation>
{extract_text_inside_tags(singable_translation, "singable_translation")}
</translation>
"""

# show the original lyrics next to the backtranslation
cols = st.columns(2)
with cols[0]:
    st.subheader("Original Lyrics")
    st.text(source_text)
with cols[1]:
    backtranslation = get_and_show_llm_response(backtranslation_prompt, f"backtranslation_{lang}", f"{lang} Backtranslation", editable=False)

st.header("Phase 5: Final Review")
review_prompt = f"""{context}

Please provide a comprehensive review of the translation, considering:
1. Accuracy of meaning
2. Preservation of theological concepts
3. How well it can be sung to the original tune
4. Cultural appropriateness
5. Areas for potential improvement

One or more errors may have been introduced in the translation. Identify and correct it.

Compare:

Original:
{source_text}

Final Translation:
{extract_text_inside_tags(singable_translation, "singable_translation")}

Backtranslation:
{backtranslation}

Rate each aspect on a scale of 1-5 and provide specific recommendations for improvement.
Place your review inside <review> tags.
"""

final_review = get_and_show_llm_response(review_prompt, f"final_review_{lang}", "Final Review", editable=True)

st.header("Phase 6: Final Translation")

final_translation_prompt = f"""{context}

Based on the analysis, translation, backtranslation, and review, provide a final translation of the song lyrics into {lang}.

<original>
{source_text}
</original>

<analysis>
{extract_text_inside_tags(analysis, "analysis")}
</analysis>

<translation>
{extract_text_inside_tags(singable_translation, "singable_translation")}
</translation>

<review>
{extract_text_inside_tags(final_review, "review")}
</review>

Place your final translation inside <final_translation> tags.
"""

final_translation = get_and_show_llm_response(final_translation_prompt, f"final_translation_{lang}", f"{lang} Final Translation")


final_translation_body = extract_text_inside_tags(final_translation, "final_translation")

# original text side-by-side with final translation

cols = st.columns(2)
with cols[0]:
    st.subheader("Original Lyrics")
    st.text(source_text)

with cols[1]:
    tabs = st.tabs(["Easy to read", "Easy to copy-paste"])
    tabs[0].text(final_translation_body)
    with tabs[1]:
        st.write("Click the Copy button in the top-right corner to copy the text.")
        st.code(final_translation_body)

def iteratively_improve():
    """Copy the final translation back into 'singable translation'"""
    key = f"singable_translation_{lang}"
    st.session_state[key] = final_translation_body

st.button("Iteratively Improve", on_click=iteratively_improve)
