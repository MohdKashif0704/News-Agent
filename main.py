from fastapi import FastAPI,Request
from services.research import resume_agent, run_until_interrupt


app=FastAPI()

thread_id="thread_4"

@app.get("/run")
def run_agent():
    needs_approval = run_until_interrupt(thread_id)
    if needs_approval:
        return {"status": "WAITING_FOR_TELEGRAM_APPROVAL"}

    return {"status": "DONE"}


@app.post("/telegram/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    # Only handle button callbacks
    if "callback_query" not in data:
        return {"ok": True}

    callback_data = data["callback_query"]["data"]
    decision = callback_data.split(":")
    decision = decision[0].lower()  

    print(f"Telegram decision: {decision}, thread_id: {thread_id}")
    resume_agent(thread_id, decision)

    return {
        "status": "RESUMED",
        "decision": decision,
        "thread_id": thread_id,
    }