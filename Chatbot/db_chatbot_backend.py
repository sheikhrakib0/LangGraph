# necessary imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, BaseMessage
from typing import Annotated, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import uuid

# environment variables
load_dotenv()

# initialize LLM
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature=0.7)

# defining state
class ChatState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages()] # type: ignore

# define chatting function
def chat(state: ChatState):
    messages = state.messages
    response = llm.invoke(messages)
    return {"messages": [response]}

# define the graph
graph = StateGraph(ChatState)
graph.add_node("generate", chat)

# define edges
graph.add_edge(START, "generate")
graph.add_edge("generate", END)

# creating a connector for the database
conn = sqlite3.connect(database="DB/chatbot.db",check_same_thread=False)
conn.execute("""
CREATE TABLE IF NOT EXISTS chat_threads (
    thread_id TEXT PRIMARY KEY,
    thread_name TEXT
    );
""")
conn.commit()

# define persistence
checkpoint = SqliteSaver(conn)


########## Utility functions ###############

def generate_chat_title_from_txt(text:str)-> str:
    text = text.strip()
    if len(text) >= 60:
        text = text[:60] + "..."
    return text

def get_thread_config(msg:str, thread_id=None):
    if thread_id:
        #for existing thread id
        return {
            'configurable': {
                'thread_id': thread_id,
                'thread_name': get_title_from_db(thread_id)
            }
        }
    # new title generation
    new_title = generate_chat_title_from_txt(msg)
    new_thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    save_title_to_db(new_thread_id, new_title)

    return {
        'configurable': {
            'thread_id': new_thread_id,
            'thread_name': new_title
        }
    }

def save_title_to_db(thread_id, new_title):
    conn.execute(
        "INSERT OR REPLACE INTO chat_threads (thread_id, thread_name)  VALUES (?, ?)",
        (thread_id, new_title)
    )
    conn.commit()

def get_title_from_db(thread_id):
    cur = conn.execute(
        "SELECT thread_name FROM chat_threads WHERE thread_id=?",(thread_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None

# returning all the threads available to frontend

def get_all_threads(checkpoint=checkpoint):
    unique_threads = {}

    for entry in checkpoint.list(None):
        cfg = entry.config.get("configurable", {})
        thread_id = cfg.get("thread_id")

        if not thread_id:
            continue  # skip malformed entries

        # Only add if not already added
        if thread_id not in unique_threads:
            thread_name = get_title_from_db(thread_id) or "Untitled Chat"
            unique_threads[thread_id] = {
                "thread_id": thread_id,
                "thread_name": thread_name
            }

    # return the unique thread objects as a list
    return list(unique_threads.values())


######### Final Object #################
chatbot = graph.compile(checkpointer=checkpoint)
 

############# checking purposes  ###############

# chatbot check for invokation
#msg = "What is the capital of Bangladesh? and Area?"
#Config = get_thread_config(msg)

#initial_state = ChatState(messages=[HumanMessage(content="You: What is the capital of Bangladesh? and Area?")])
#response = chatbot.invoke(initial_state, config=Config) #type: ignore
#print(response)

#all_threads = get_all_threads()
#print(all_threads)
