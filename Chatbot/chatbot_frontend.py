##### importing necessary libraries
import streamlit as st
from chatbot_backend import chatbot, ChatState
from langchain_core.messages import HumanMessage
import uuid

st.title("Chatbot with LangGraph and Google Gemini")

# Utility functions
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_ui():
    
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_msg(thread_id):
    Config = {"configurable": {
    "thread_id": thread_id}}
    response = chatbot.get_state(config=Config)
    print(response.values)
    messages = response.values['messages']
    message_temp = []
    for message in messages:
        #print("called message", message)
        if isinstance(message, HumanMessage):
            role = 'user'
        else:
            role='assistant'
        message_temp.append({'role':role, 'content':message.content})
    st.session_state['message_history'] = message_temp



# **************** Session setup ****************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

add_thread(st.session_state["thread_id"])

# check persistence of thread id in session state
Config = {"configurable": {
    "thread_id": st.session_state["thread_id"]}}

# laoding all messages from session state
for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

# ******************* UI Part *******************

# Side bar
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    st.session_state.message_history.clear()
    reset_ui()
st.sidebar.header("My Conversations")
for thread in st.session_state["chat_threads"]:
    if st.sidebar.button(thread):
        load_msg(thread)



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
