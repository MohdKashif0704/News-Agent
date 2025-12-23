from langchain.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware 
from langgraph.checkpoint.memory import InMemorySaver 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from services.news_tool import get_news, send_msg
from services.media_tool import video_generator
from dotenv import load_dotenv
import os 
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0, 
    api_key=GEMINI_API_KEY
    )
PROMPT=""" You are a research agent that helps users gather information on various topics using available tools and then send that gathered information through a Telegram bot for approval.
"""
PROMPT2="""
You are a research agent that helps users gather information or news on various topics using available tools and generate videos for the fetched news summary of 5 seconds.
"""
tools=[get_news, video_generator]
agent =create_agent(
    model=llm,
    tools=tools,
    system_prompt=PROMPT2,
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={
            "send_msg":
            {
                "video_generator":["approve", "reject"]
            }
        }
    )
    ],
    checkpointer=InMemorySaver()
)
query="Generate a video for the latest news on medical"
config = {"configurable": {"thread_id": "thread_1"}} 
result = agent.invoke({"messages": [{"role": "user", "content": query}]},config=config)
print(result["messages"][-1].content)