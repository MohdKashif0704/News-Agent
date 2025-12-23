from eventregistry import *
import json, os, sys
from langchain.tools import tool
import requests

from dotenv import load_dotenv
load_dotenv()
NEWS_API_KEY = "64ec200e-1a00-467b-91d8-624f3f4ad5c1"
er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)

@tool(name_or_callable="get_news")
def get_news(field:str):
    """ Description : Get or Fetch latest news articles related to a specific field or topic .
        Input : field (str) : The field or topic to search for news articles.
        Output : ans (str) : A JSON-formatted string containing the bodies of the latest news articles related to the specified field.
    """
    q = QueryArticlesIter(
        keywords=field,
        lang="eng",
        dataType=["news"], 
    )
    results = []

    for art in q.execQuery(er, sortBy="date", maxItems=1):
        results.append(art["body"])

    ans = json.dumps(results, indent=4)
    return ans



@tool(name_or_callable="send_msg")
def send_msg(msg:str):
    """Description : Send a news message to a Telegram bot for story approval.
       Input : msg (str) : The message content of news to be sent to the Telegram bot.
       Output : None"""
    

    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN_KEY")
    CHAT_ID = os.getenv("TELEGRAM_BOT_KEY")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": f"STORY CARD\n\nApprove this story?{msg}",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Approve", "callback_data": "approve:story_1"},
                    {"text": " Reject", "callback_data": "reject:story_1"}
                ]
            ]
        }
    }

    requests.post(url, json=payload)

