# test_webhook.py
# test_webhook.py

import httpx
import asyncio

BOT_TOKEN = "8991642915:AAFEnoUaxU5vt5txaeskxiT1P48xnRMwzWc"
NGROK_URL = "https://prepaid-mobster-coming.ngrok-free.dev"

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:

        print("=== Test: Real Group Chat ID ===")
        fake_update = {
            "update_id": 123456799,
            "message": {
                "message_id": 10,
                "from": {
                    "id": 123456,
                    "is_bot": False,
                    "first_name": "Komara",
                    "username": "komara_prasad"
                },
                "chat": {
                    "id": -1003521471260,       # ✅ your real group chat_id
                    "title": "Dev Team Chat",
                    "type": "supergroup"        # ✅ supergroup
                },
                "date": 1234567890,
                "text": "What is the issue in production level?"
            }
        }

        webhook_url = f"{NGROK_URL}/webhook/{BOT_TOKEN}"
        r = await client.post(webhook_url, json=fake_update)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")

asyncio.run(test())