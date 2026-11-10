import re
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = "9232677706:AAHx8h5JIeEyhZpA6nP_5vQn45yCKwHgZkw"
API = f"https://api.telegram.org/bot{TOKEN}"


@app.get("/")
def home():
    return {"status": "Test Bot is live!"}


@app.get("/set")
def set_webhook(req: Request):
    # Deploy के बाद ब्राउज़र में your-app.vercel.app/set खोलें
    url = f"https://{req.headers.get('host')}/api/index"
    r = requests.get(f"{API}/setWebhook", params={"url": url})
    return r.json()


@app.post("/api/index")
async def webhook(req: Request):
    data = await req.json()
    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    user = message.get("from", {})
    user_id = user.get("id")
    name = user.get("first_name", "User")
    text = message.get("text", "")

    # 1. Anti-link
    if re.search(r"(https?://\S+|www\.\S+|\S+\.com\S*)", text):
        requests.post(f"{API}/deleteMessage",
                      json={"chat_id": chat_id, "message_id": message_id})
        requests.post(f"{API}/sendMessage",
                      json={"chat_id": chat_id,
                            "text": f"⚠️ {name}, इस चैट में लिंक भेजना मना है!"})
        return {"ok": True}

    # 2. /start
    if text.startswith("/start"):
        reply = f"👋 नमस्ते {name}!\n\n🆔 आपकी User ID: {user_id}\n🚀 बॉट Vercel पर चल रहा है!"
    else:
        # 3. सामान्य मैसेज
        reply = f"🤖 {name}, आपका मैसेज मिल गया!"

    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": reply})
    return {"ok": True}
