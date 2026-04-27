"""
Dynamic Document Agent test - Upload any file and chat with it.
"""
import asyncio
import httpx
import os
import sys

async def run_dynamic_doc_test():
    print("=" * 80)
    print("📂 LUMINATE AI - DYNAMIC DOCUMENT ANALYST TEST")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # 1. Create session
    print("\n1️⃣  Initializing Analysis Session...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{base_url}/api/session", json={
                "ideal_person": "Document Analyst",
                "favourite_celebrity": "Researcher"
            })
            session_id = resp.json()["id"]
            print(f"✅ Session created: {session_id}")
        except Exception as e:
            print(f"❌ Could not connect to server: {e}")
            return

    # 2. Get File Path
    print("\n2️⃣  Select a Document to Analyze")
    file_path = input("📄 Enter the FULL PATH to a PDF, DOCX, or TXT file: ").strip().replace('"', '')
    
    if not os.path.exists(file_path):
        print(f"❌ File not found at: {file_path}")
        return

    # 3. Upload File
    filename = os.path.basename(file_path)
    print(f"⏳ Uploading and processing '{filename}'...")
    
    async with httpx.AsyncClient() as client:
        try:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f)}
                data = {"session_id": session_id}
                resp = await client.post(f"{base_url}/api/documents/upload", data=data, files=files)
                
                if resp.status_code != 200:
                    print(f"❌ Upload failed: {resp.text}")
                    return
                print(f"✅ {resp.json()['message']}")
        except Exception as e:
            print(f"❌ Error during upload: {e}")
            return

    # 4. Chat Loop
    print("\n" + "="*80)
    print(f"✨ AI is now trained on '{filename}'! Ask anything about it.")
    print("(Type 'exit' to quit)")
    print("="*80)

    async with httpx.AsyncClient() as client:
        while True:
            user_msg = input("\n💬 Your Question: ")
            if user_msg.lower() in ['exit', 'quit']:
                break
                
            print("⏳ AI is analyzing document...")
            try:
                resp = await client.post(f"{base_url}/api/doc-chat", json={
                    "session_id": session_id,
                    "message": user_msg
                }, timeout=60)
                
                result = resp.json()
                print("\n🤖 RESPONSE:")
                print("-" * 40)
                print(result["response"])
                print("-" * 40)
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_dynamic_doc_test())
    except KeyboardInterrupt:
        print("\n👋 Test ended.")
