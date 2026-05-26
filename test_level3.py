# test_level3.py

import requests

BASE_URL = "http://localhost:8000"

print("=== Test 1: API Health Check ===")
r = requests.get(f"{BASE_URL}/")
print(r.json())
print()

print("=== Test 2: Send Non-Question Message ===")
r = requests.post(f"{BASE_URL}/message", json={
    "username": "dev1",
    "message": "Good morning everyone!"
})
print(r.json())
print()

print("=== Test 3: Send Question — Exact Match ===")
r = requests.post(f"{BASE_URL}/message", json={
    "username": "dev2",
    "message": "What is the issue in production level?"
})
print(r.json())
print()

print("=== Test 4: Send Question — Different Wording ===")
r = requests.post(f"{BASE_URL}/message", json={
    "username": "dev3",
    "message": "may i know what is the issue in the production level?"
})
print(r.json())
print()

print("=== Test 5: Send Question — No Match ===")
r = requests.post(f"{BASE_URL}/message", json={
    "username": "dev4",
    "message": "What is the best pizza topping?"
})
print(r.json())
print()

print("=== Test 6: Add New Q&A Pair ===")
r = requests.post(f"{BASE_URL}/add-qa", json={
    "question": "How do I rollback a deployment?",
    "answer": "Run git revert and redeploy via CI/CD pipeline.",
    "category": "DevOps",
    "answered_by": "dev5"
})
print(r.json())
print()

print("=== Test 7: Search Newly Added Q&A ===")
r = requests.post(f"{BASE_URL}/message", json={
    "username": "dev6",
    "message": "how can i rollback my deployment?"
})
print(r.json())
print()

print("=== Test 8: Get Chat History ===")
r = requests.get(f"{BASE_URL}/chat-history?limit=5")
for msg in r.json():
    print(f"{msg['username']}: {msg['message']}")
print()

print("=== Test 9: Get Knowledge Base ===")
r = requests.get(f"{BASE_URL}/knowledge-base")
for qa in r.json():
    print(f"Q: {qa['question']}")
    print(f"A: {qa['answer']}")
    print()