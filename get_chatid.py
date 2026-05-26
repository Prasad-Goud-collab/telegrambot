# get_chatid.py

import httpx
import asyncio

BOT_TOKEN = "8991642915:AAFEnoUaxU5vt5txaeskxiT1P48xnRMwzWc"

async def get_chat_id():
    async with httpx.AsyncClient() as client:

        # Step 1 — Delete webhook temporarily
        r1 = await client.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        )
        print("Webhook deleted:", r1.json())

        # Step 2 — Get updates
        print("\nSend a message in your Telegram group NOW...")
        print("Waiting 10 seconds...")
        await asyncio.sleep(10)

        r2 = await client.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        )
        data = r2.json()
        print("\nFull response:", data)

        # Step 3 — Extract chat_id
        if data.get("result"):
            for update in data["result"]:
                message = update.get("message", {})
                chat = message.get("chat", {})
                print(f"\n✅ Chat ID: {chat.get('id')}")
                print(f"✅ Chat Title: {chat.get('title')}")
                print(f"✅ Chat Type: {chat.get('type')}")
        else:
            print("❌ No messages found. Send a message in group and try again.")

asyncio.run(get_chat_id())