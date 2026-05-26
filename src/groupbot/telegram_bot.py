# src/groupbot/telegram_bot.py

import httpx
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes


BOT_TOKEN = "8991642915:AAFEnoUaxU5vt5txaeskxiT1P48xnRMwzWc"
NGROK_URL = "https://prepaid-mobster-coming.ngrok-free.dev"
API_URL = "http://localhost:8000"

bot = Bot(token=BOT_TOKEN)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles every message in the Telegram group.
    Sends to FastAPI → checks similarity → replies if match found.
    """
    if not update.message or not update.message.text:
        return

    message = update.message.text
    username = update.message.from_user.username or \
               update.message.from_user.first_name or "unknown"
    chat_id = update.message.chat_id

    print(f"📨 Telegram [{username}]: {message}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{API_URL}/message",
                json={
                    "username": username,
                    "message": message
                }
            )
            result = r.json()

        # ✅ If bot has verified answer — reply in group
        if result.get("bot_response"):
            answer = result["answer"]
            confidence = round(result["confidence"] * 100, 1)
            matched = result["matched_question"]

            reply = (
                f"🤖 *Bot Answer:*\n\n"
                f"{answer}\n\n"
                f"📊 Confidence: `{confidence}%`\n"
                f"✅ Matched: _{matched}_"
            )

            await context.bot.send_message(
                chat_id=chat_id,
                text=reply,
                parse_mode="Markdown"
            )
            print(f"✅ Bot replied with confidence {confidence}%")

        else:
            print(f"🔇 Bot silent — {result.get('message')}")

    except Exception as e:
        print(f"❌ Error in handle_message: {e}")


async def set_webhook():
    """Sets Telegram webhook to ngrok URL."""
    webhook_url = f"{NGROK_URL}/webhook/{BOT_TOKEN}"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        print(f"✅ Webhook set: {r.json()}")


def create_bot_app():
    """Creates and returns the Telegram bot application."""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    return app