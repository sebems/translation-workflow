from llm_util import model_name
from google import genai
import streamlit as st

st.set_page_config(layout="wide")

workflow_page = st.Page("workflow.py", title="Translation workflow")

def landing():
    st.title("Translation Utilities")

    st.page_link(workflow_page, label="Translation Workflow")


# Manually specify the sidebar

st.sidebar.write(f"Translation Utilities\n\ninspired by [Ken Arnold](https://kenarnold.org/)\n\nModel: {model_name}")

page = st.navigation([
    #st.Page(landing, title="Home", icon="🏠"),
    workflow_page,
])
page.run()
