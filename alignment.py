import streamlit as st
from llm_util import get_and_show_llm_response

# wide page
st.set_page_config(layout="wide")

# Initialize Anthropic client
if 'client' not in st.session_state:
    from anthropic import Anthropic
    st.session_state.client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


st.subheader("Original Text")
english_text = st.text_area("Enter the English version with formatting:", height=300)

st.subheader("Translations")
translations = st.text_area("Enter the available translations:", height=300)

# Construct the prompts
SYSTEM_PROMPT = """You are an expert at aligning song translations while preserving formatting for slides. 
For each English line, provide the corresponding translated text that conveys the same meaning, 
trying to match the line breaks as much as possible.

Guidelines:
1. Keep all stanza headings (like 'Verse 1') and blank lines exactly as they appear in the original, without translating them.
2. If a translated line contains multiple original ideas, split it to match the original line breaks
3. If multiple translated lines express one original line, combine them
4. If there's no translation for a line, use the original in italics
5. For stage directions like '(Repeat)', translate them appropriately
6. Feel free to break up translated lines in unnatural places to maintain alignment - 
   we care more about matching the original structure than preserving natural line breaks
7. Output *only* the translated text, not the original.
"""

BACKTRANSLATION_PROMPT = """You are an expert at providing literal translations. Please provide a word-for-word 
backtranslation of the following French text into English. Your goal is to help the reader understand the exact 
meaning of each French line, even if the result is not elegant English.

Guidelines:
1. Keep all stanza headings and formatting exactly as they appear
2. Maintain all blank lines
3. For each French line, provide the most literal possible English translation
4. If a word has multiple possible meanings, include them in [brackets]
5. If a line is already in English and italicized, keep it unchanged
6. For stage directions like '*(Répéter)*', translate them but keep the formatting
7. Use [lit: ...] to add literal meaning clarification where helpful
"""


# Add a button to process the texts
if english_text and translations:
    if not english_text or not translations:
        st.error("Please enter both the original text and translations")
    else:
        # Create tabs for different views
        col1, col2, col3 = st.columns(3)
        try:
            with col1:
                # First API call for alignment
                alignment_prompt = f"""Please align these translations with the original text:

Original text:
{english_text}

Available translations:
{translations}

Output the aligned version using the guidelines above."""
                aligned_text = get_and_show_llm_response(
                    alignment_prompt,
                    "alignment",
                    "Alignment",
                    editable=False,
                    system=SYSTEM_PROMPT
                )

                st.code(aligned_text)
                
            with col2:
                # Second API call for backtranslation
                backtranslation_prompt = f"""Please provide a literal backtranslation of this French text:

{aligned_text}"""
                backtranslation = get_and_show_llm_response(
                    backtranslation_prompt,
                    "backtranslation",
                    "Backtranslation",
                    editable=False,
                    system=BACKTRANSLATION_PROMPT
                )

            with col3:
                st.subheader("Original Text")
                st.text("Here is the original text:")
                st.text(english_text)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Add helpful instructions in the sidebar
with st.sidebar:
    st.markdown("""
    ### How to use this app:
    
    1. Enter your Anthropic API key
    2. Paste the original text with all formatting
    3. Paste the available translations
    4. Click "Align Translations"
    5. Review the results in the tabs:
       - Aligned Translation: The formatted French version
       - Backtranslation: Word-for-word English translation
       - Side by Side: Compare both versions
    6. Download any version you need
    
    ### Format Requirements:
    
    - Include all stanza headings (e.g., "Verse 1")
    - Keep blank lines for slide breaks
    - Include any stage directions like "(Repeat)"
    
    ### Tips:
    
    - The alignment prioritizes matching the original structure
    - Lines may be split or combined as needed
    - Missing translations will be shown in italics
    - Stage directions will be translated
    - The backtranslation is intentionally literal to help spot
      any meaning differences
    """)
