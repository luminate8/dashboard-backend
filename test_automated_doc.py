"""
Automated Document Agent Test - No user input required
"""
import asyncio
import httpx
import tempfile
import os

async def test_doc_agent():
    print("=" * 80)
    print("📂 AUTOMATED DOCUMENT AGENT TEST")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # Check server health
    print("\n🔍 Checking server...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{base_url}/health", timeout=5)
            print(f"✅ Server is running: {resp.json()}")
        except Exception as e:
            print(f"❌ Server not running. Start it with: uvicorn main:app --reload")
            return
    
    # 1. Create session
    print("\n1️⃣  Creating session...")
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/api/session", json={
            "ideal_person": "Document Analyst",
            "favourite_celebrity": "Researcher"
        })
        session_id = resp.json()["id"]
        print(f"✅ Session: {session_id}")
    
    # 2. Create test document
    print("\n2️⃣  Creating test document...")
    test_content = """
    Project Luminate Overview
    
    Project Luminate is an AI-powered persona chat system that allows users to interact
    with AI agents that mimic the communication style of celebrities and public figures.
    
    Key Features:
    - Uses LangGraph for agent orchestration
    - Stores data in Neon DB (PostgreSQL)
    - Fetches real tweets to train persona models
    - Powered by Hugging Face LLM (Qwen/Qwen2.5-72B-Instruct)
    
    Technical Stack:
    - Backend: FastAPI + Python
    - Database: Neon DB
    - AI Framework: LangGraph
    - LLM: Hugging Face Router
    """
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_path = f.name
    
    print(f"✅ Test file created: {temp_path}")
    
    # 3. Upload document
    print("\n3️⃣  Uploading document...")
    async with httpx.AsyncClient() as client:
        with open(temp_path, "rb") as f:
            files = {"file": ("test_doc.txt", f)}
            data = {"session_id": session_id}
            resp = await client.post(f"{base_url}/api/documents/upload", data=data, files=files, timeout=30)
            
            if resp.status_code != 200:
                print(f"❌ Upload failed: {resp.text}")
                os.unlink(temp_path)
                return
            print(f"✅ {resp.json()['message']}")
    
    os.unlink(temp_path)
    
    # 4. Test questions
    questions = [
        "What is Project Luminate?",
        "What database does it use?",
        "Which LLM model powers the system?"
    ]
    
    print("\n4️⃣  Testing document Q&A...")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        for i, question in enumerate(questions, 1):
            print(f"\n❓ Question {i}: {question}")
            print("⏳ Processing...")
            
            try:
                resp = await client.post(f"{base_url}/api/doc-chat", json={
                    "session_id": session_id,
                    "message": question
                }, timeout=60)
                
                result = resp.json()
                print(f"\n🤖 Response:")
                print("-" * 40)
                print(result["response"])
                print("-" * 40)
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_doc_agent())
