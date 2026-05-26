# test_level1.py

from src.groupbot.storage.chat_storage import (
    initialize_csv_files,
    save_message,
    save_qa_pair,
    get_chat_history,
    get_qa_pairs
)

# Initialize
initialize_csv_files()

# Save some messages
save_message("dev1", "What is the issue in production level?", is_question=True)
save_message("dev2", "There are some bugs in the server.", is_answered=True)
save_message("dev3", "How do I deploy to production?", is_question=True)
save_message("dev4", "Use the CI/CD pipeline via GitHub Actions.")

# Save Q&A pairs
save_qa_pair(
    question="What is the issue in production level?",
    answer="There are some bugs in the server.",
    category="Production",
    answered_by="dev2"
)

save_qa_pair(
    question="How do I deploy to production?",
    answer="Use the CI/CD pipeline via GitHub Actions.",
    category="DevOps",
    answered_by="dev4"
)

# Verify
print("=== Chat History ===")
print(get_chat_history())

print("\n=== Verified Q&A Pairs ===")
print(get_qa_pairs())