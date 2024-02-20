import json
import streamlit as st
from openai import OpenAI

from src.tools import fred_series_search

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Forecast Friend")

MAX_TOOL_CALLS = 10
GPT_MODEL = "gpt-3.5-turbo"
DEBUG = False

tools = [
    {
        "type": "function",
        "function": {
            "name": "fred_series_search",
            "description": "Get economic data series that match keywords and frequency specifications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "Space-separated terms to search for in series titles, units, frequencies and tags.",
                    },
                    "frequency": {
                        "type": "string",
                        "description": 'Optional frequency filter of the data, e.g. "Monthly", "Annual", "Daily"',
                    },
                },
                "required": ["search_text"],
            },
        },
    },
]


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a an assistent that helps the user find economic data for analysis. You ask the user \
            what they require economic data for and use the provided tools to find the series that be matches their \
            needs. Aim to find around 5 matching series, no more than 10. If the tools return many matches, either \
            refine the search to return fewer results, or choose the most relevant matches from the returned results \
            yourself. When you have found the matches, present them in a markdown table with the following columns: \
            Title, ID, Frequency, Last Updated.",
        },
        {
            "role": "assistant",
            "content": "Hello. What kind of economic data do you require? Currently I have access to the FRED database.",
        },
    ]


# Display chat history
for message in st.session_state.messages[1:]:
    # Add conditions to catch function input and output
    if (message["role"] != "function") and (message["content"][:8] != "Function"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages,
        tools=tools,
        stream=False,
    )

    # Check for and handle tool calls
    if response.choices[0].message.tool_calls:
        with st.spinner("Querying data sources, please wait..."):
            for i in range(MAX_TOOL_CALLS):
                if DEBUG:
                    st.write(f"Tool call {i + 1} of maximum {MAX_TOOL_CALLS}")
                tool_call = response.choices[0].message.tool_calls[0]
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": str(tool_call.function),
                    }
                )
                if DEBUG:
                    with st.chat_message(st.session_state.messages[-1]["role"]):
                        st.markdown(st.session_state.messages[-1]["content"])

                if tool_call.function.name == "fred_series_search":
                    function_arguments = json.loads(tool_call.function.arguments)
                    function_response = fred_series_search(**function_arguments)
                else:
                    function_response = f"Unknown tool call: {tool_call.function.name}"

                st.session_state.messages.append(
                    {
                        "role": "function",
                        "content": function_response,
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                    }
                )
                if DEBUG:
                    with st.chat_message(st.session_state.messages[-1]["role"]):
                        st.markdown(st.session_state.messages[-1]["content"])

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages,
                    tools=tools,
                    stream=False,
                )
                if response.choices[0].message.tool_calls is None:
                    if DEBUG:
                        st.write("No more tool calls.")
                    break

            else:
                st.write("Maximum number of tool calls reached.")

    st.session_state.messages.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )
    with st.chat_message(st.session_state.messages[-1]["role"]):
        st.markdown(st.session_state.messages[-1]["content"])
