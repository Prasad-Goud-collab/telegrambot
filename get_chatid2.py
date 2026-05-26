# get_chatid2.py

import requests

BOT_TOKEN = "8991642915:AAFEnoUaxU5vt5txaeskxiT1P48xnRMwzWc"

def get_chat_id():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    r = requests.get(url, params={"offset": -10}, timeout=10)
    data = r.json()
    print("Response:", data)

    if data.get("result"):
        for update in data["result"]:
            message = update.get("message", {})
            chat = message.get("chat", {})
            username = message.get("from", {}).get("username", "")
            text = message.get("text", "")
            print(f"\n✅ Chat ID: {chat.get('id')}")
            print(f"✅ Chat Type: {chat.get('type')}")
            print(f"✅ Username: {username}")
            print(f"✅ Message: {text}")
    else:
        print("❌ No messages found.")

get_chat_id()