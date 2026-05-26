# app.py

import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Group Chat Bot",
    page_icon="💬",
    layout="wide"
)

# ─── Initialize session state ─────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Admin Panel")
    st.divider()

    # ── Username input here (not in main) ──
    st.subheader("👤 Your Identity")
    username = st.text_input("Username", value="dev1")
    st.divider()

    # ── Add New Q&A ──
    st.subheader("➕ Add Verified Q&A")
    new_question = st.text_input("Question")
    new_answer = st.text_area("Answer", height=80)
    new_category = st.text_input("Category", value="General")
    new_answered_by = st.text_input("Answered By", value="admin")

    if st.button("✅ Add to Knowledge Base"):
        if new_question and new_answer:
            r = requests.post(f"{API_URL}/add-qa", json={
                "question": new_question,
                "answer": new_answer,
                "category": new_category,
                "answered_by": new_answered_by
            })
            if r.status_code == 200:
                st.success("✅ Q&A added successfully!")
            else:
                st.error("❌ Failed to add Q&A.")
        else:
            st.warning("Please fill both question and answer.")

    st.divider()

    if st.button("🔄 Reload Knowledge Base"):
        r = requests.post(f"{API_URL}/reload-kb")
        if r.status_code == 200:
            st.success("✅ Reloaded!")

    st.divider()

    st.subheader("📚 Knowledge Base")
    if st.button("View All Q&A"):
        r = requests.get(f"{API_URL}/knowledge-base")
        if r.status_code == 200:
            for qa in r.json():
                with st.expander(f"Q: {qa['question'][:50]}"):
                    st.markdown(f"**Answer:** {qa['answer']}")
                    st.markdown(f"**Category:** {qa['category']}")
                    st.markdown(f"**Answered By:** {qa['answered_by']}")

    st.divider()

    if st.button("🗑️ Clear Chat UI"):
        st.session_state.chat_messages = []
        st.rerun()

# ─── Main Chat UI ─────────────────────────────────────────────
st.title("💬 Group Chat")
st.caption("Bot automatically answers repeated questions from the knowledge base.")

# ── Display all chat messages ──
for msg in st.session_state.chat_messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        with st.chat_message("user"):
            st.markdown(f"**{msg['username']}:** {content}")
            st.caption(msg.get("timestamp", ""))

    elif role == "bot":
        with st.chat_message("assistant"):
            st.markdown(f"🤖 **Bot:** {content}")
            if msg.get("confidence"):
                st.caption(
                    f"📊 Confidence: {round(msg['confidence'] * 100, 1)}% | "
                    f"✅ Matched: _{msg.get('matched_question', '')}_"
                )

# ── Message input ──
user_message = st.chat_input("Type your message...")

if user_message:
    timestamp = datetime.now().strftime("%H:%M:%S")

    # ✅ Step 1 — Add user message to session state
    st.session_state.chat_messages.append({
        "role": "user",
        "username": username,
        "content": user_message,
        "timestamp": timestamp
    })

    # ✅ Step 2 — Send to API
    try:
        r = requests.post(f"{API_URL}/message", json={
            "username": username,
            "message": user_message
        })
         # ✅ ADD THIS DEBUG LINE
        st.write("🔍 API Response:", r.json())

        if r.status_code == 200:
            result = r.json()

            # ✅ Step 3 — If bot has answer, add to session state
            if result.get("bot_response"):
                st.session_state.chat_messages.append({
                    "role": "bot",
                    "username": "Bot",
                    "content": result["answer"],
                    "confidence": result["confidence"],
                    "matched_question": result["matched_question"],
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the API server is running.")

    # ✅ Step 4 — Rerun AFTER everything is saved to session state
    st.rerun()