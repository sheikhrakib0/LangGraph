import streamlit as st
from chatbot_backend import chatbot, ChatState
from langchain_core.messages import HumanMessage
st.title("Chatbot with LangGraph and Google Gemini")

# check persistence configuration
Config = {"configurable": {
    "thread_id": "thread_001"}}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# laoding previous messages from session state
for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

# taking a user input
user_input = st.chat_input("Type here")

if user_input:
    # displaying user message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    # preparing initial state for chatbot
    initial_state = ChatState(messages=[HumanMessage(content=user_input)])
    #result = chatbot.invoke(initial_state, config=Config)
    #bot_response = result["messages"][-1]
    
    
    
    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(initial_state, config=Config, stream_mode="messages")
        )
    
    # adding response to session state
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})