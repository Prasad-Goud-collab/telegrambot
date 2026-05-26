# src/groupbot/storage/chat_storage.py

import pandas as pd
import os
from datetime import datetime


QA_CSV_PATH = "data/verified_qa.csv"
CHAT_CSV_PATH = "data/chat_history.csv"
PENDING_CSV_PATH = "data/pending_questions.csv"  # ✅ tracks unanswered questions


def initialize_csv_files():
    """Creates CSV files if they don't exist."""

    if not os.path.exists("data"):
        os.makedirs("data")

    # verified_qa.csv
    if not os.path.exists(QA_CSV_PATH):
        df = pd.DataFrame(columns=[
            "question", "answer", "category",
            "timestamp", "answered_by"
        ])
        df.to_csv(QA_CSV_PATH, index=False)

    # chat_history.csv
    if not os.path.exists(CHAT_CSV_PATH):
        df = pd.DataFrame(columns=[
            "message_id", "username", "message",
            "timestamp", "is_question", "is_answered"
        ])
        df.to_csv(CHAT_CSV_PATH, index=False)

    # ✅ pending_questions.csv — tracks unanswered questions
    if not os.path.exists(PENDING_CSV_PATH):
        df = pd.DataFrame(columns=[
            "message_id", "username", "question", "timestamp", "answered"
        ])
        df.to_csv(PENDING_CSV_PATH, index=False)


def save_message(username: str, message: str,
                 is_question: bool = False,
                 is_answered: bool = False) -> int:
    """Saves a chat message to chat_history.csv."""
    df = pd.read_csv(CHAT_CSV_PATH)
    message_id = len(df) + 1

    new_row = {
        "message_id": message_id,
        "username": username,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_question": is_question,
        "is_answered": is_answered
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CHAT_CSV_PATH, index=False)
    return message_id


def save_pending_question(message_id: int, username: str, question: str):
    """
    Saves unanswered question to pending_questions.csv.
    Waits for someone to answer it.
    """
    df = pd.read_csv(PENDING_CSV_PATH)

    new_row = {
        "message_id": message_id,
        "username": username,
        "question": question,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "answered": False
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PENDING_CSV_PATH, index=False)


def get_last_pending_question() -> dict:
    """
    Returns the most recent unanswered question.
    Used to match with incoming answers.
    """
    df = pd.read_csv(PENDING_CSV_PATH)
    unanswered = df[df["answered"] == False]

    if unanswered.empty:
        return None

    last = unanswered.iloc[-1]
    return {
        "message_id": last["message_id"],
        "username": last["username"],
        "question": last["question"],
        "timestamp": last["timestamp"]
    }


def mark_question_answered(message_id: int):
    """Marks a pending question as answered."""
    df = pd.read_csv(PENDING_CSV_PATH)
    df.loc[df["message_id"] == message_id, "answered"] = True
    df.to_csv(PENDING_CSV_PATH, index=False)


def save_qa_pair(question: str, answer: str,
                 category: str = "General",
                 answered_by: str = "user") -> bool:
    """
    Saves a verified Q&A pair to verified_qa.csv.
    Returns True if saved, False if duplicate.
    """
    df = pd.read_csv(QA_CSV_PATH)

    if question in df["question"].values:
        return False

    new_row = {
        "question": question,
        "answer": answer,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "answered_by": answered_by
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(QA_CSV_PATH, index=False)
    return True


def get_chat_history(limit: int = 50) -> pd.DataFrame:
    """Returns recent chat history."""
    df = pd.read_csv(CHAT_CSV_PATH)
    return df.tail(limit)


def get_qa_pairs() -> pd.DataFrame:
    """Returns all verified Q&A pairs."""
    return pd.read_csv(QA_CSV_PATH)


def get_pending_questions() -> pd.DataFrame:
    """Returns all pending questions."""
    return pd.read_csv(PENDING_CSV_PATH)