import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Forecast Friend")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a concise assistant."}
    ]


if "text_input" not in st.session_state:
    st.session_state.text_input = ""
    st.session_state.last_text_input = ""


def submit():
    st.session_state.text_input = st.session_state.widget
    st.session_state.widget = ""


def generate_response(input_text):
    response = client.generate_text(input_text)
    return response


# Display chat history
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Add user input from text box
if st.session_state.text_input != st.session_state.last_text_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": st.session_state.text_input})
    # Display user message
    with st.chat_message("user"):
        st.markdown(st.session_state.text_input)
    # Generate response using full chat history
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            temperature=0.9,
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response)
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.last_text_input = st.session_state.text_input

text_box_content = st.text_input("You:", key="widget", on_change=submit)