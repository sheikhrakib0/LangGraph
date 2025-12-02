##### importing necessary libraries
import streamlit as st
from db_chatbot_backend import chatbot, ChatState, get_all_threads, get_thread_config
from langchain_core.messages import HumanMessage
import uuid

st.title("Chatbot with LangGraph and Google Gemini")

# Utility functions
def generate_thread_id(thread_name="New Chat"):
    thread_id = str(uuid.uuid4())
    full_uuid = str(uuid.uuid4())
    thread_name = full_uuid[:5]
    thread = {"thread_id": thread_id, "thread_name": thread_name}
    return thread

def reset_ui():
    st.session_state.message_history.clear()
    thread = generate_thread_id()
    thread_id = thread['thread_id']
    st.session_state["thread_id"] = thread_id
    add_thread(thread)
    st.rerun()

def thread_check(thread):
    for thrd in st.session_state["chat_threads"]:
        if thrd['thread_id'] == thread['thread_id']:
            return True
    return False

def add_thread(thread):
    check = thread_check(thread)
    if check == False:
        st.session_state["chat_threads"].append(thread)

def load_msg(thread_id):
    Config = {"configurable": {
    "thread_id": thread_id}}
    response = chatbot.get_state(config=Config) # type: ignore
    messages = response.values.get('messages',[])
    message_temp = []
    for message in messages:
        #print("called message", message)
        if isinstance(message, HumanMessage):
            role = 'user'
        else:
            role='assistant'
        message_temp.append({'role':role, 'content':message.content})
    st.session_state['message_history'] = message_temp
    st.rerun()



# **************** Session setup ****************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = get_all_threads()


# check persistence of thread id in session state
Config = {"configurable": {
    "thread_id": st.session_state["thread_id"]}}


# ******************* UI Part *******************

# laoding all messages from session state
for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

# Side bar
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    reset_ui()
st.sidebar.header("My Conversations")
for thread in st.session_state["chat_threads"][::-1]:
    button_name = thread['thread_name']
    thread_id = thread['thread_id']
    if st.sidebar.button(button_name):
        st.session_state["thread_id"] = thread_id
        load_msg(thread_id)


# taking a user input
user_input = st.chat_input("Type here")

if user_input:
    # Adding new thread to the session
    if "thread_id" not in st.session_state:
        new_thread_config = get_thread_config(msg=user_input)
        new_thread = new_thread_config['configurable']
        st.session_state["thread_id"] = new_thread["thread_id"]
        # sending full thread dict to chat_threads. 
        # add_thread() should be down to the creation of chat_threads
        add_thread(new_thread)

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
            message_chunk.content for message_chunk, metadata in chatbot.stream(initial_state, config=Config, stream_mode="messages") # type: ignore
        )
    
    # adding response to session state
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
