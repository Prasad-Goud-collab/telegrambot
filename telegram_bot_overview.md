# Telegram Group Chat Bot — Auto Q&A Detection

A production-grade intelligent Telegram Group Bot that **automatically tracks real-time conversations**, detects Q&A pairs, builds a knowledge base, and answers repeated questions instantly — so no one has to scroll through hundreds of messages again.

---

##  Problem It Solves

> In large developer or community group chats, the same questions get asked repeatedly.  
> Nobody wants to scroll through hundreds of messages to find the answer.  
> This bot tracks all conversations, learns from them, and answers repeated questions automatically.

```
Day 1:
dev1: "what is the prod issue?"        ← question asked
dev2: "there are bugs in the server"   ← answered by someone

Day 2:
dev3: "may i know the prod issue?"     ← different wording, same question
🤖 Bot: "there are bugs in the server" ← bot answers instantly!
        📊 Confidence: 92%
```

---

##  Features

| Feature | Description |
|---|---|
|  Auto Q&A Detection | Automatically detects questions and answers from group chat |
|  Real-time Tracking | Every message tracked and stored instantly |
|  Semantic Search | Matches questions even with different wording |
|  Confidence Score | Shows how confident the bot is about each answer |
|  Smart Silence | Bot stays silent when no verified answer exists |
|  Auto Knowledge Base | Builds and updates KB from real conversations |
|  Admin Dashboard | Streamlit UI to manage knowledge base |
|  Real-time Updates | New Q&A pairs added without restarting |

---

##  Architecture

```
Telegram Group Message
        ↓
Telegram Bot API (webhook)
        ↓
ngrok (public URL tunnel)
        ↓
FastAPI Backend
        ↓
┌─────────────────────────────────────┐
│  Is it a question?                  │
│     YES → Search FAISS KB           │
│           Found → Bot replies       │
│           Not found → Save pending  │
│     NO  → Is there a pending Q?     │
│           YES → Save Q&A pair       │
│           NO  → Save message only   │
└─────────────────────────────────────┘
        ↓
FAISS Vectorstore (auto-updated)
        ↓
CSV Storage (persistent)
        ↓
Bot replies in Telegram group
```

---

##  Tech Stack

```
FastAPI          — Backend API + webhook receiver
FAISS            — Vector similarity search
HuggingFace      — Sentence embeddings (all-MiniLM-L6-v2)
Telegram Bot API — Group chat integration
python-telegram-bot — Telegram bot framework
ngrok            — Public URL tunnel for webhook
Streamlit        — Admin dashboard UI
Pandas           — CSV data management
Python           — Core language
```

---

##  Project Structure

```
project1/
│
├── app.py                              — Streamlit admin UI
├── api.py                              — FastAPI backend
├── ngrok.exe                           — Public URL tunnel
│
├── data/
│   ├── verified_qa.csv                 — Auto-saved Q&A pairs
│   ├── chat_history.csv                — All group messages
│   └── pending_questions.csv           — Unanswered questions
│
└── src/
    └── groupbot/
        ├── storage/
        │   └── chat_storage.py         — CSV read/write logic
        ├── vectorstore/
        │   └── faiss_store.py          — FAISS build + search
        ├── graph/
        │   └── graph_builder.py        — LangGraph orchestration
        ├── nodes/                      — Processing nodes
        └── telegram_bot.py            — Telegram bot handler
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/telegram-group-chat-bot.git
cd telegram-group-chat-bot
```

### 2. Install dependencies
```bash
pip install fastapi uvicorn python-telegram-bot httpx
pip install faiss-cpu sentence-transformers langchain-huggingface
pip install langchain-community pandas streamlit
```

### 3. Create Telegram Bot
```
1. Open Telegram → search @BotFather
2. Send: /newbot
3. Give name and username (must end with _bot)
4. Copy the bot token
```

### 4. Setup ngrok
```bash
# Download ngrok from https://ngrok.com/download
.\ngrok config add-authtoken YOUR_AUTH_TOKEN
.\ngrok http 8000
# Copy the public URL: https://abc123.ngrok-free.dev
```

### 5. Update config in `src/groupbot/telegram_bot.py`
```python
BOT_TOKEN = "your_bot_token_here"
NGROK_URL = "https://your-ngrok-url.ngrok-free.dev"
```

### 6. Run the application

**Terminal 1 — FastAPI:**
```bash
uvicorn api:app --port 8000
```

**Terminal 2 — ngrok:**
```bash
.\ngrok http 8000
```

**Terminal 3 — Streamlit:**
```bash
streamlit run app.py
```

---

## 💡 How It Works — Step by Step

### Step 1 — Question Detection
```
Message comes in
      ↓
Check if ends with "?" OR
starts with: what, how, why, when, where,
             who, which, can, could, is,
             are, do, does, may, should...
      ↓
Classified as Question ✅ or Statement ❌
```

### Step 2 — Knowledge Base Search
```
Question detected
      ↓
FAISS semantic search
      ↓
Similarity score calculated
      ↓
Score >= 0.55 → Return verified answer
Score < 0.55  → Save as pending question
```

### Step 3 — Auto Q&A Detection
```
Statement detected
      ↓
Check pending questions
      ↓
Pending question exists?
      YES → Save Q&A pair to CSV + FAISS
      NO  → Save message only
```

### Step 4 — Bot Reply
```
Verified answer found
      ↓
Bot sends reply in group:
 Bot Answer: [answer]
 Confidence: 92%
 Matched: [original question]
```

---

##  Build Levels

```
Level 1 — CSV Storage Layer
   chat_history.csv — tracks all messages
  verified_qa.csv  — stores Q&A pairs
   pending_questions.csv — unanswered questions

Level 2 — FAISS RAG Pipeline
   HuggingFace embeddings
   Semantic similarity search
   Real-time index updates (no rebuild needed)
   Configurable similarity threshold

Level 3 — FastAPI Backend
   POST /message       — receive and process messages
   POST /add-qa        — manually add Q&A pairs
   GET  /chat-history  — view all messages
   GET  /knowledge-base— view all Q&A pairs
   GET  /pending-questions — view unanswered questions
   POST /reload-kb     — reload FAISS from CSV

Level 4 — Streamlit Admin Dashboard
   View all chat messages
   Manually add Q&A pairs
  View entire knowledge base
   Reload knowledge base button

Level 5 — Telegram Integration
   Real-time webhook from Telegram
   Bot reads ALL group messages
   Auto Q&A detection from conversations
   Bot replies with confidence score
   Smart silence when no answer found
```

---

##  Key Highlights

-  Zero manual data entry — bot learns from real conversations
-  Semantic matching — handles different question phrasings
-  Confidence scoring — transparent about answer quality
-  Smart silence — never gives wrong answers
-  Real-time knowledge base updates
-  Persistent storage — survives server restarts
-  Admin dashboard for knowledge base management
-  Production-grade FastAPI + webhook architecture

---

##  Performance

```
Exact same question     → Confidence: 100%
Different wording       → Confidence: 60-95%
Unrelated question      → Bot stays silent ✅
New Q&A auto-detected   → Added in real-time ✅
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/message` | Process group message |
| POST | `/add-qa` | Add verified Q&A pair |
| GET | `/chat-history` | Get recent messages |
| GET | `/knowledge-base` | Get all Q&A pairs |
| GET | `/pending-questions` | Get unanswered questions |
| POST | `/reload-kb` | Reload FAISS from CSV |
| POST | `/webhook/{token}` | Telegram webhook receiver |

---

##  Requirements

```
fastapi
uvicorn
python-telegram-bot
httpx
faiss-cpu
sentence-transformers
langchain-huggingface
langchain-community
pandas
streamlit
```

---

##  Future Improvements

```
⏳ Deploy to cloud (Railway/Render) — remove ngrok dependency
⏳ Multi-platform support (Slack, Discord)
⏳ Analytics dashboard — most asked questions, bot accuracy
⏳ Docker containerization
⏳ Auto-categorization of Q&A pairs
⏳ Admin approval before saving Q&A pairs
```

---

## 🙋 Author

**Komara Prasad**  
AI Engineer | LLM Systems | RAG Pipelines | Agentic AI

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)(www.linkedin.com/in/prasadkpk)]
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/Prasad-Goud-collab)

