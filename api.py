# api.py

import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from telegram import Update

from src.groupbot.vectorstore.faiss_store import QAVectorStore
from src.groupbot.storage.chat_storage import (
    initialize_csv_files,
    save_message,
    save_pending_question,
    get_last_pending_question,
    mark_question_answered,
    save_qa_pair,
    get_chat_history,
    get_qa_pairs,
    get_pending_questions
)
from src.groupbot.telegram_bot import create_bot_app, set_webhook, BOT_TOKEN


# ─── Constants ────────────────────────────────────────────────
QA_CSV_PATH = "data/verified_qa.csv"
SIMILARITY_THRESHOLD = 0.55

# ─── Initialize ───────────────────────────────────────────────
app = FastAPI(title="Group Bot API", version="1.0.0")
initialize_csv_files()
qa_store = QAVectorStore()
telegram_app = create_bot_app()


# ─── Request Models ───────────────────────────────────────────
class MessageRequest(BaseModel):
    username: str
    message: str


class QAPairRequest(BaseModel):
    question: str
    answer: str
    category: str = "General"
    answered_by: str = "user"


# ─── Startup ──────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    if os.path.exists(QA_CSV_PATH):
        try:
            qa_store.build_from_csv(QA_CSV_PATH)
            print("✅ Knowledge base loaded.")
        except Exception as e:
            print(f"⚠️ Knowledge base empty: {e}")

    await set_webhook()
    await telegram_app.initialize()
    print("✅ Telegram bot initialized.")


# ─── Routes ───────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "✅ Group Bot API is running"}


@app.post(f"/webhook/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """Receives messages from Telegram."""
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"status": "error", "detail": str(e)}


@app.post("/message")
async def receive_message(request: MessageRequest):
    """
    Core logic:
    1. Is it a question?
       YES → search KB
             found → reply
             not found → save as pending question
    2. Is it an answer?
       YES → check if pending question exists
             YES → save Q&A pair to KB automatically
    """
    username = request.username
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # ✅ Detect if message is a question
    is_question = message.strip().endswith("?") or \
                  any(message.lower().startswith(w) for w in [
                      "what", "how", "why", "when", "where",
                      "who", "which", "can", "could", "is",
                      "are", "do", "does", "may", "should",
                      "tell", "explain", "give", "show", "help",
                      "i want", "i need", "please", "kindly"
                  ])

    # ✅ Save message to chat history
    message_id = save_message(
        username=username,
        message=message,
        is_question=is_question,
        is_answered=False
    )

    print(f"📝 is_question={is_question} | message={message}")

    # ─── QUESTION FLOW ────────────────────────────────────────
    if is_question:

        # ✅ Search KB for similar verified answer
        if qa_store.is_ready():
            result = qa_store.search(message, threshold=SIMILARITY_THRESHOLD)
            print(f"🔍 found={result['found']} | "
                  f"confidence={result['confidence']} | "
                  f"matched={result['matched_question']}")

            if result["found"]:
                return {
                    "bot_response": True,
                    "answer": result["answer"],
                    "confidence": result["confidence"],
                    "matched_question": result["matched_question"],
                    "category": result["category"],
                    "answered_by": result["answered_by"],
                    "message": f"🤖 Bot: {result['answer']}"
                }

        # ✅ No answer found — save as pending question
        save_pending_question(
            message_id=message_id,
            username=username,
            question=message
        )
        print(f"💾 Saved pending question: {message}")

        return {
            "bot_response": False,
            "answer": None,
            "confidence": None,
            "matched_question": None,
            "message": "✅ Question saved. Waiting for human answer."
        }

    # ─── ANSWER FLOW ──────────────────────────────────────────
    else:
        # ✅ Check if there is a pending question to match
        pending = get_last_pending_question()

        if pending:
            question = pending["question"]
            answer = message
            asked_by = pending["username"]

            print(f"💡 Auto-detected Q&A pair!")
            print(f"   Q [{asked_by}]: {question}")
            print(f"   A [{username}]: {answer}")

            # ✅ Save to verified_qa.csv
            saved = save_qa_pair(
                question=question,
                answer=answer,
                category="Auto-Detected",
                answered_by=username
            )

            # ✅ Add to FAISS in real-time
            if saved and qa_store.is_ready():
                qa_store.add_new_qa(
                    question=question,
                    answer=answer,
                    category="Auto-Detected",
                    answered_by=username
                )
                print(f"✅ Q&A added to knowledge base!")
            elif not qa_store.is_ready():
                # ✅ Build fresh if first Q&A
                qa_store.build_from_csv(QA_CSV_PATH)

            # ✅ Mark question as answered
            mark_question_answered(pending["message_id"])

        return {
            "bot_response": False,
            "answer": None,
            "confidence": None,
            "matched_question": None,
            "message": "✅ Message saved."
        }


@app.post("/add-qa")
async def add_qa_pair(request: QAPairRequest):
    """Manually adds a verified Q&A pair."""
    try:
        saved = save_qa_pair(
            question=request.question,
            answer=request.answer,
            category=request.category,
            answered_by=request.answered_by
        )

        if qa_store.is_ready():
            qa_store.add_new_qa(
                question=request.question,
                answer=request.answer,
                category=request.category,
                answered_by=request.answered_by
            )
        else:
            qa_store.build_from_csv(QA_CSV_PATH)

        return {
            "status": "✅ Q&A pair added successfully.",
            "question": request.question,
            "answer": request.answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat-history")
async def get_history(limit: int = 50):
    df = get_chat_history(limit=limit)
    return df.to_dict(orient="records")


@app.get("/knowledge-base")
async def get_knowledge_base():
    df = get_qa_pairs()
    return df.to_dict(orient="records")


@app.get("/pending-questions")
async def get_pending():
    """Returns all pending unanswered questions."""
    df = get_pending_questions()
    return df.to_dict(orient="records")


@app.post("/reload-kb")
async def reload_knowledge_base():
    try:
        qa_store.build_from_csv(QA_CSV_PATH)
        return {"status": "✅ Knowledge base reloaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))