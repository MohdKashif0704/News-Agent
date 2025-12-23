from fastapi import FastAPI, Request
import os 
from dotenv import load_dotenv

load_dotenv()

app=FastAPI()
@app.post("/telegram/webhook")
async def telegram_webhook(req:Request):
    data = await req.json()

    if "callback_query" in data:
        callback = data["callback_query"]["data"]

        if callback.startswith("approve") or callback.startswith("reject"):
            story_id = callback.split(":")[0]
            print(story_id)
        
        

    
