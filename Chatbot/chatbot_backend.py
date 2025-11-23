# necessary imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, BaseMessage
from typing import Annotated, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

# environment variables
load_dotenv()

# initialize LLM
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature=0.7)

# defining state
class ChatState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages()]

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

# define persistence
checkpoint = InMemorySaver()
chatbot = graph.compile(checkpointer=checkpoint)

# chatbot check for invokation
#Config = {"configurable": {
#    "thread_id": "thread_001"}
#}

#initial_state = ChatState(messages=[HumanMessage(content=input("You: "))])
#generator = chatbot.stream(initial_state, config=Config, #stream_mode="messages")

#for message_chunk, metadata in generator:
#    print(message_chunk.content, end="", flush=True)
#print("Bot:", result["messages"][-1].content)