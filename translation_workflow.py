"""Translation Workflow

This script implements a 6-phase workflow for high-quality text/song translation:

1. Analysis Phase
   - Analyzes theological concepts, cultural references, metaphors, and translation challenges
   - For songs: additionally analyzes poetic devices and syllable stress patterns

2. Literal Translation Phase
   - Creates a word-for-word translation
   - Provides alternative translations for key terms and ambiguous passages
   - Includes explanations and backtranslations for alternatives

3. Clarity Phase
   - Adapts the literal translation for clarity and natural language flow
   - For songs: considers meter and rhyme scheme
   - Provides alternative phrasings in brackets

4. Backtranslation Phase
   - Translates the clarified version back to the original language
   - Helps identify potential meaning shifts or errors

5. Review Phase
   - Evaluates accuracy, theological preservation, and cultural appropriateness
   - Provides specific improvement recommendations
   - For songs: additionally evaluates singability

6. Final Translation Phase
   - Produces the final translation incorporating all previous feedback
   - Displays results side-by-side with the original
   - Allows for iterative improvement cycles

The workflow is implemented as a Streamlit web application with interactive forms
and step-by-step progression through each phase.
"""

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


with st.form("input_form"):
    source_lang = st.text_input("Source Language", "English")
    lang = st.text_input("Target Language", "French")
    is_song = st.checkbox("Is this a song?")
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
#
# Prompts
#

def get_context_prompt(*, lang: str, source_text: str, is_song: bool) -> str:
    if is_song:
        base = f"""For context, we are translating a worship song from {source_lang} to {lang}, aiming for theological accuracy, simple and clear language, singability to the original tune, and cultural sensitivity.

This step is one part of a multi-step process to translate the song. Do only what is asked in each step.
"""
    else:
        base = f"""For context, we are translating a text from {source_lang} to {lang}, aiming for accuracy, simplicity, and clarity.

This step is one part of a multi-step process to translate the text. Do only what is asked in each step.
"""
        
    if extra_context:
        return f"{base}\n\nThe following extra context was provided by the user. Please use it only if it is helpful. <extra_context>\n{extra_context}</extra_context>\n"
    return base

def get_analysis_prompt(*, lang: str, source_text: str, is_song: bool) -> str:
    context = get_context_prompt(lang=lang, source_text=source_text, is_song=is_song)

    analysis_components = [
        f"Theological concepts and terminology, including any specific references to scripture or doctrine. For each concept or reference, describe it in {source_lang} and {lang}, including a complete quote in {lang} if applicable.",
        "Cultural references",
        "Key metaphors and imagery",
        "Potential translation challenges"
    ]
    if is_song:
        analysis_components.append("Poetic devices (rhyme scheme, meter, alliteration)")

    return f"""{context}

Please provide a detailed analysis of the source text to help guide the translation process.

<source_text>
{source_text}
<source_text>

Provide a detailed analysis of the following aspects:
{'\n'.join('{}. {}'.format(i + 1, comp) for i, comp in enumerate(analysis_components))}

Use bullet points to organize your analysis.

{'Also, for each line in a representative sample of each section of the song (verse, chorus, bridge, etc.), show the stressed and unstressed syllables. For example, "a-MA-zing GRACE, how SWEET the SOUND"; "He who is MIGHTy has DONE a great THING".' if is_song else ''}

Place the results of your analysis inside <analysis> tags.
"""

def get_literal_translation_prompt(*, lang: str, source_text: str, is_song: bool) -> str:
    context = get_context_prompt(lang=lang, source_text=source_text, is_song=is_song)
    item_type = "lyrics" if is_song else "text"
    return f"""{context}

Provide a literal, word-for-word translation of the following {item_type} into {lang}:

<source_text>
{source_text}
</source_text>

After each line or paragraph, provide alternative translations for key terms, ambiguous passages, and any challenging passages. Use square brackets to indicate alternatives. Include brief explanations and backtranslations of any alternative translations so that even a non-native speaker could understand what the choice means.

{'If a stanza has a heading (like Chorus 2 or Bridge), include it in the output *without translation*.' if is_song else ''} If a line is blank, include a blank line in the output.

Place your translation inside <literal_translation> tags.
"""

def get_clarity_prompt(*, lang: str, source_text: str, is_song: bool, literal_translation, analysis) -> str:
    context = get_context_prompt(lang=lang, source_text=source_text, is_song=is_song)
    item_type = "song" if is_song else "text"
    target_characteristics = "singable, poetic" if is_song else "clear, simple"

    return f"""{context}

Adapt this literal translation into {target_characteristics} {lang}, emphasizing clarity while retaining a reasonable amount of the original meaning.

If a stanza has a heading (like Chorus 2 or Bridge), include it in the output *without translation*. Likewise, if a line is blank, include a blank line in the output.

If applicable, write an alternative translation after a phrase or line in square brackets. For example, "Amazing grace, how sweet the sound [Stunning grace, how it moves my ear]". Don't include backtranslations at this point.

If there are no reasonable alternatives, simply leave the line as is.

<original>
{source_text}
</original>

<analysis>
{analysis}
</analysis>

<literal_translation>
{literal_translation}
</literal_translation>

Place your resulting translation inside <clear_translation> </clear_translation> tags.

{'Then, inside <syllabification> </syllabification> tags, repeat the entire translation but writing STRESSED and unstressed syllables as was done in the analysis above.' if is_song else ''}

"""

def get_backtranslation_prompt(*, lang: str, source_text: str, clarified_translation: str) -> str:
    context = get_context_prompt(lang=lang, source_text=source_text, is_song=is_song)
    return f"""{context}

To verify the translation, we will backtranslate it into the original language. Translate the following literally into {source_lang}, adding notes as needed in [ ] brackets:

<translation>
{clarified_translation}
</translation>
"""

def get_review_prompt(*, lang: str, source_text: str, clarified_translation: str, backtranslation: str, is_song: bool, syllabification: str | None) -> str:
    context = get_context_prompt(lang=lang, source_text=source_text, is_song=is_song)
    review_elements = [
        "Accuracy of meaning",
        "Preservation of theological concepts",
        "Cultural appropriateness",
        "Areas for potential improvement"
    ]
    syllabification_prompt = ''
    if is_song:
        review_elements.append("How well it can be sung to the original tune")
        syllabification_prompt = f"""
<syllabification>
{syllabification}
</syllabification>
"""

    return f"""{context}

Please provide a comprehensive review of the translation, considering:
{'\n'.join('{}. {}'.format(i + 1, elem) for i, elem in enumerate(review_elements))}

One or more errors may have been introduced in the translation. Identify and correct them.

Compare:

Original:
{source_text}

Final Translation:
{clarified_translation}

Backtranslation:
{backtranslation}

{syllabification_prompt if is_song else ''}
The analysis should include both strengths and weaknesses. Provide specific recommendations for improvement.
Place your review inside <review> tags.
"""

def get_final_translation_prompt(*, lang: str, source_text: str, analysis: str, clarified_translation: str, final_review: str, is_song: bool) -> str:
    context = get_context_prompt(lang=lang, source_text=source_text, is_song=is_song)
    item_type = "song" if is_song else "text"
    return f"""{context}

Based on the analysis, translation, backtranslation, and review, provide a final translation of the {item_type} into {lang}.

<original>
{source_text}
</original>

<analysis>
{analysis}
</analysis>

<translation>
{clarified_translation}
</translation>

<review>
{final_review}
</review>

Place your final translation inside <final_translation> tags.
"""

# Run it!

analysis_prompt = get_analysis_prompt(lang=lang, source_text=source_text, is_song=is_song)
analysis = get_and_show_llm_response(analysis_prompt, "source_analysis", "Source Analysis")
analysis = extract_text_inside_tags(analysis, "analysis")

st.header("Phase 2: Literal Translation")

st.subheader(f"{lang} Translation")

literal_translation_prompt = get_literal_translation_prompt(lang=lang, source_text=source_text, is_song=is_song)
literal_translation = get_and_show_llm_response(literal_translation_prompt, f"literal_translation_{lang}", f"{lang} Literal Translation")
literal_translation = extract_text_inside_tags(literal_translation, "literal_translation")

st.header("Phase 3: Clarity")

adaptation_prompt = get_clarity_prompt(lang=lang, source_text=source_text, is_song=is_song, literal_translation=literal_translation, analysis=analysis)
clarified_translation_raw = get_and_show_llm_response(adaptation_prompt, f"clarified_translation_{lang}", f"{lang} clarified Translation")
clarified_translation = extract_text_inside_tags(clarified_translation_raw, "clear_translation")
syllabification = extract_text_inside_tags(clarified_translation_raw, "syllabification") if is_song else None

st.header("Phase 4: Backtranslation")

# show the original text next to the backtranslation
cols = st.columns(2)
with cols[0]:
    st.subheader("Original Text")
    st.text(source_text)
with cols[1]:
    backtranslation_prompt = get_backtranslation_prompt(lang=lang, source_text=source_text, clarified_translation=clarified_translation)
    backtranslation = get_and_show_llm_response(backtranslation_prompt, f"backtranslation_{lang}", f"{lang} Backtranslation", editable=False)
    backtranslation = extract_text_inside_tags(backtranslation, "backtranslation")

st.header("Phase 5: Final Review")

review_prompt = get_review_prompt(lang=lang, source_text=source_text, clarified_translation=clarified_translation, backtranslation=backtranslation, is_song=is_song, syllabification=syllabification)
final_review = get_and_show_llm_response(review_prompt, f"final_review_{lang}", "Final Review", editable=True)
final_review = extract_text_inside_tags(final_review, "review")

st.header("Phase 6: Final Translation")

final_translation_prompt = get_final_translation_prompt(lang=lang, source_text=source_text, analysis=analysis, clarified_translation=clarified_translation, final_review=final_review, is_song=is_song)
final_translation = get_and_show_llm_response(final_translation_prompt, f"final_translation_{lang}", f"{lang} Final Translation")
final_translation_body = extract_text_inside_tags(final_translation, "final_translation")

# original text side-by-side with final translation

cols = st.columns(2)
with cols[0]:
    st.subheader("Original Text")
    st.text(source_text)

with cols[1]:
    tabs = st.tabs(["Easy to read", "Easy to copy-paste"])
    tabs[0].text(final_translation_body)
    with tabs[1]:
        st.write("Click the Copy button in the top-right corner to copy the text.")
        st.code(final_translation_body)

def iteratively_improve():
    """Copy the final translation back into 'clarified translation'"""
    key = f"clarified_translation_{lang}"
    st.session_state[key] = final_translation_body

st.button("Iteratively Improve", on_click=iteratively_improve)
