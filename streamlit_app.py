import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="🌙", layout="wide", page_title="LunaChat")
from lunachat.storage import save_system_prompts, load_system_prompts


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


icon("🌙")

st.subheader("LunaChat", divider="rainbow", anchor=False)


# Functions
def update_system():
    system_dict = {"role": "system", "content": st.session_state.system_input}
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append(system_dict)
    else:
        if st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0] = system_dict
        else:
            st.session_state.messages.insert(0, system_dict)


def reset_messages():
    st.session_state.messages = []


# Initialize state variables
if "system_prompt_dict" not in st.session_state:
    st.session_state.system_prompt_dict = (
        load_system_prompts()
    )  # Load dict from file storage to only read data when needed.

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "system_input" not in st.session_state:
    st.session_state.system_input = st.session_state.system_prompt_dict["default"]

# Define model details
models = {
    # "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {
        "name": "Mixtral-8x7b-Instruct-v0.1",
        "tokens": 32768,
        "developer": "Mistral",
    },
}

with st.expander("System Prompt (Optional)"):
    st.text_area(
        "System Prompt",
        label_visibility="hidden",
        help="Enter pre-chat instructions for the model here.",
        key="system_input",
    )

    submit_system = st.button(
        "Set System Prompt",
        on_click=update_system,
    )

# DEBUG
with st.popover("DEBUG"):
    st.write(st.session_state.messages)

# Layout for model selection and max_tokens slider
col1, col2 = st.columns([10, 1])

with col1:
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=0,  # Default to llama3 70b
    )

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    update_system()
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

with col2:
    # Adjust max_tokens input dynamically based on the selected model
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=max_tokens_range,
        value=min(32768, max_tokens_range),
        step=1024,
        help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}",
    )


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    avatar = "🤖" if message["role"] == "assistant" else "👩‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👩‍💻"):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True,
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response}
        )
