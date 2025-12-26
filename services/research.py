from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from services.news_tool import get_news, send_msg,request_video_approval,send_final_output
from services.media_tool import video_generator
from dotenv import load_dotenv
from langgraph.types import Command
from langchain_core.messages import AIMessage
import os
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, ToolMessage

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

import json

def save_interrupt(thread_id, interrupt_id):
    with open("interrupts.json", "w") as f:
        json.dump({thread_id: interrupt_id}, f)

def load_interrupt(thread_id):
    try:
        with open("interrupts.json") as f:
            data = json.load(f)
            return data.get(thread_id)
    except FileNotFoundError:
        return None



INTERRUPT_STORE = {}


llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
)

agent = create_agent(
    model=llm,
    tools=[get_news, video_generator,send_msg,request_video_approval,send_final_output],
    system_prompt="""
    You are an autonomous research agent.
    STRICT FLOW (DO NOT CHANGE ORDER):
    1. Fetch latest tech news
    2. Summarize the news in EXACTLY 2 lines
    3. Call send_msg with the summary
    4. Call request_video_approval with the summary
    5. ONLY AFTER approval, call video_generator
    6. Ouput should be send to telegram :write a short, user-friendly confirmation message. Mention the video link naturally and keep it concise.

    Do NOT skip tool usage.
    """,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "request_video_approval": {
                    "allowed_decisions": ["approve", "reject"]
                }
            }
        )
    ],
    checkpointer=InMemorySaver(),
)

def run_until_interrupt(thread_id: str):
    """
    Runs agent until HITL interrupt.
    Sends summary to Telegram and stores interrupt ID.
    """
    latest_summary = ""

    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": "Generate a 2-line tech news summary and then create a video for it"}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode=["messages","updates"],
    ):
        # print("STREAM:", mode, chunk)

        if mode == "messages":
            token, _ = chunk
            if isinstance(token, AIMessage) and token.content:
                latest_summary = token.content   
        if mode == "updates" and "__interrupt__" in chunk:
            interrupt = chunk["__interrupt__"][0]
            save_interrupt(thread_id, interrupt.id) 
            return True

    return False



def resume_agent(thread_id: str, decision: str):
    interrupt_id = load_interrupt(thread_id)

    if not interrupt_id:
        print("No interrupt to resume")
        return
    messages = []


    for mode, chunk in agent.stream(
        Command(
            resume={
                interrupt_id: {
                    "decisions": [{"type": decision}]
                }
            }
        ),
        config={"configurable": {"thread_id": thread_id}},
        stream_mode=["messages", "updates"],
    ):
     
        if mode == "messages":
            msg, _ = chunk
            messages.append(msg)

    
            

    
