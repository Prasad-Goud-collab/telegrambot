# test_level2.py

from src.groupbot.vectorstore.faiss_store import QAVectorStore

# Build vectorstore
store = QAVectorStore()
store.build_from_csv("data/verified_qa.csv")

print("\n=== Semantic Search Tests ===\n")

# Test 1 — exact same question
q1 = "What is the issue in production level?"
r1 = store.search(q1)
print(f"Q: {q1}")
print(f"Found: {r1['found']}")
print(f"Answer: {r1['answer']}")
print(f"Confidence: {r1['confidence']}")
print(f"Matched: {r1['matched_question']}")
print()

# Test 2 — different wording, same meaning
q2 = "may i know what is the issue in the production level?"
r2 = store.search(q2)
print(f"Q: {q2}")
print(f"Found: {r2['found']}")
print(f"Answer: {r2['answer']}")
print(f"Confidence: {r2['confidence']}")
print(f"Matched: {r2['matched_question']}")
print()

# Test 3 — completely unrelated question
q3 = "What is the best pizza topping?"
r3 = store.search(q3)
print(f"Q: {q3}")
print(f"Found: {r3['found']}")
print(f"Answer: {r3['answer']}")
print(f"Confidence: {r3['confidence']}")
print()

# Test 4 — add new Q&A in real-time and search immediately
print("=== Real-time Add Test ===\n")
store.add_new_qa(
    question="Who is responsible for fixing server bugs?",
    answer="The backend team is responsible. Contact @backend-team on Slack.",
    category="Production",
    answered_by="dev5"
)

q4 = "who handles server bug fixes?"
r4 = store.search(q4)
print(f"Q: {q4}")
print(f"Found: {r4['found']}")
print(f"Answer: {r4['answer']}")
print(f"Confidence: {r4['confidence']}")
print(f"Matched: {r4['matched_question']}")