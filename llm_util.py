import streamlit as st

model_name = "claude-3-7-sonnet-latest"

def stream_llm_response(prompt, max_tokens=5000, temperature=0.7, **kwargs):
    # FIXME: rename the argument to `messages`, or allow prompt= or messages=
    if isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = prompt
    stream = st.session_state.client.messages.stream(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs
    )
    with stream as text_stream:                    
        for chunk in text_stream:
            if chunk.type == 'text':
                yield chunk.text

def get_and_show_llm_response(prompt: str, key: str, step_name: str, editable: bool = True, show: bool = True, **kwargs) -> str:
    # strip indentation from prompt
    from textwrap import dedent
    prompt = dedent(prompt)
    if 'system' in kwargs:
        kwargs['system'] = dedent(kwargs['system'])

    result = st.session_state.get(key, None)
    redo = st.button("Redo " + step_name, help="Prompt: " + prompt)
    container = st.empty()
    if result is None or redo or st.session_state.get(key + "_prompt") != prompt:
        response = stream_llm_response(prompt, **kwargs)
        result = container.write_stream(response)
        assert isinstance(result, str)
        st.session_state[key] = result
        st.session_state[key + "_prompt"] = prompt
    container.empty()
    if show:
        with container, st.container():
            # We need another container because st.empty() only allows one element
            if editable and st.checkbox(f"Edit {step_name}", key=key + "_edit"):
                result = st.text_area(step_name, result, height=200, key=key)
            else:
                st.markdown(result)
    return result or ""
