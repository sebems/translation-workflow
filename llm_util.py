from google.genai import types
from pathlib import Path
import streamlit as st
import logging, re

model_name = "gemini-2.0-flash"

def create_logger(path="logs/info.log"):
    """ Create a logger for the project. """
    logging.basicConfig(
        filename=Path(path),
        filemode="a",
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        # level=logging.INFO
    )
    return logging.getLogger()

LOGGER = create_logger()

def removeMarkdownTag(text: str) -> str:
    """Extract text inside a pair of tags.

    If there's no such tag, return the whole text.
    """
    text = text.replace("```markdown\n", "")
    text = text.replace("\n```", "")
    return text

def removeFinalTag(text: str) -> str:
    text = text.replace("*   **Final Translation:**", "")
    return text

def get_context_prompt(*, target_lang: str, source_lang: str, is_song=False, extra_context) -> str:
    if is_song:
        base = f"""For context, we are translating a worship song from {source_lang} to {target_lang}, aiming for theological accuracy, simple and clear language, singability to the original tune, and cultural sensitivity.

This step is one part of a multi-step process to translate the song. Do only what is asked in each step.
"""
    else:
        base = f"""For context, we are translating a text from {source_lang} to {target_lang}, aiming for accuracy, simplicity, and clarity.

This step is one part of a multi-step process to translate the text. Do only what is asked in each step.
"""

    if extra_context:
        return f"{base}\n\nThe following extra context was provided by the user. Please use it only if it is helpful. <extra_context>\n{extra_context}</extra_context>\n"
    return base