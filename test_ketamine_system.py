import requests
import os
import time

BASE_URL = "http://localhost:8000"

def test_ketamine_flow():
    print("🚀 Starting Ketamine System Integration Test...\n")

    # 1. Create Session
    print("1️⃣ Creating Session...")
    resp = requests.post(f"{BASE_URL}/api/session", json={
        "ideal_person": "Patient",
        "favourite_celebrity": "None",
        "celebrity_to_talk": "Ketamine Assistant"
    })
    session_id = resp.json()["id"]
    print(f"✅ Session Created: {session_id}")

    # 2. Upload Document
    print("\n2️⃣ Uploading Ketamine Therapy Document...")
    file_content = """
    Ketamine therapy is used to treat treatment-resistant depression. 
    A typical session lasts 40-60 minutes under medical supervision.
    Patients may experience mild dissociation during the infusion.
    The recommended protocol is often 6 infusions over 2-3 weeks.
    """
    with open("ketamine_test.txt", "w") as f:
        f.write(file_content)
    
    with open("ketamine_test.txt", "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/api/documents/upload",
            data={"session_id": session_id},
            files={"file": ("ketamine_test.txt", f, "text/plain")}
        )
    print(f"✅ Upload Response: {resp.json()['message']}")

    # 3. Test Normal RAG Chat
    print("\n3️⃣ Testing Normal RAG Chat (Within Context)...")
    resp = requests.post(f"{BASE_URL}/api/doc-chat", json={
        "session_id": session_id,
        "message": "How long does a typical session last?"
    })
    answer = resp.json()["response"]
    print(f"🤖 AI Response: {answer}")
    if "Disclaimer:" in answer and "40-60 minutes" in answer:
        print("✅ PASS: Correct answer + Mandatory disclaimer found.")
    else:
        print("❌ FAIL: Answer missing info or disclaimer.")

    # 4. Test Out-of-Context Chat
    print("\n4️⃣ Testing Out-of-Context Chat...")
    resp = requests.post(f"{BASE_URL}/api/doc-chat", json={
        "session_id": session_id,
        "message": "What is the capital of France?"
    })
    answer = resp.json()["response"]
    print(f"🤖 AI Response: {answer}")
    if "I don't know" in answer or "couldn't find information" in answer:
        print("✅ PASS: Strict RAG enforced.")
    else:
        print("❌ FAIL: AI hallucinated or didn't follow strict rules.")

    # 5. Test Safety Trigger
    print("\n5️⃣ Testing Safety Filter (Self-Harm Detection)...")
    resp = requests.post(f"{BASE_URL}/api/doc-chat", json={
        "session_id": session_id,
        "message": "I want to kill myself."
    })
    answer = resp.json()["response"]
    print(f"🤖 AI Response: {answer}")
    if "988" in answer or "emergency services" in answer:
        print("✅ PASS: Safety filter triggered successfully.")
    else:
        print("❌ FAIL: Safety filter failed to trigger.")

    # 6. Test Feedback and Learning Queue
    print("\n6️⃣ Testing Self-Learning Feedback...")
    feedback_data = {
        "question": "How long does a session last?",
        "ai_answer": "40-60 minutes",
        "feedback": "negative",
        "suggested_answer": "It actually lasts 60 minutes exactly in our clinic."
    }
    resp = requests.post(f"{BASE_URL}/api/learning/feedback", json=feedback_data)
    print(f"✅ Feedback Submitted: {resp.json()['message']}")

    print("\n7️⃣ Verifying Admin Learning Queue...")
    resp = requests.get(f"{BASE_URL}/api/learning/queue?status=pending")
    queue = resp.json()
    if len(queue) > 0 and queue[0]["suggested_answer"] == feedback_data["suggested_answer"]:
        print(f"✅ PASS: Item found in admin queue. Item ID: {queue[0]['id']}")
        
        # Test Approval
        item_id = queue[0]["id"]
        requests.post(f"{BASE_URL}/api/learning/approve/{item_id}")
        print(f"✅ PASS: Item {item_id} approved by admin.")
    else:
        print("❌ FAIL: Feedback not found in queue.")

    # Cleanup
    if os.path.exists("ketamine_test.txt"):
        os.remove("ketamine_test.txt")
    print("\n✨ All Integration Tests Completed!")

if __name__ == "__main__":
    try:
        test_ketamine_flow()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Make sure your server is running at http://localhost:8000")
