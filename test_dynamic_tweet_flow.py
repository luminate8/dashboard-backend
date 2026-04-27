"""
Dynamic end-to-end test of the backend with user-provided celebrities.
"""
import asyncio
import httpx
import sys

async def run_dynamic_test():
    print("=" * 80)
    print("🌟 LUMINATE AI - DYNAMIC PERSONA TEST")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{base_url}/health")
    except Exception:
        print("❌ ERROR: Backend server is not running on http://localhost:8000")
        print("Please run 'python main.py' in another terminal first.")
        return

    # Get user inputs
    print("\n--- Setup Your Personas ---")
    ideal_person = input("👤 Enter the 'Ideal Person' (e.g., Steve Jobs): ") or "Elon Musk"
    fav_celebrity = input("👤 Enter the 'Favorite Celebrity' (e.g., Taylor Swift): ") or "Lionel Messi"
    
    # Step 1: Create session
    print(f"\n1️⃣  Creating session with {ideal_person} & {fav_celebrity}...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/session",
            json={
                "ideal_person": ideal_person,
                "favourite_celebrity": fav_celebrity
            }
        )
        if response.status_code != 200:
            print(f"❌ Failed to create session: {response.text}")
            return
            
        session = response.json()
        session_id = session["id"]
        print(f"✅ Session created! ID: {session_id}")
    
    # Step 2: Get message
    print("\n--- Chat with AI ---")
    user_message = input(f"💬 Ask a question: ") 
    if not user_message:
        user_message = f"What do you both think about the future of technology?"

    # Step 3: Chat with AI
    print(f"\n2️⃣  Sending message: '{user_message}'")
    print("⏳ Please wait... AI is fetching real tweets and thinking...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "session_id": session_id,
                    "message": user_message
                },
                timeout=180  # 3 minutes timeout for scraping + AI
            )
            
            if response.status_code != 200:
                print(f"❌ Error from server: {response.text}")
                return
                
            result = response.json()
            
            print("\n" + "✨" * 40)
            print("💬 AI RESPONSE:")
            print("-" * 80)
            print(result["response"])
            print("-" * 80)
            print(f"👤 Personas logic based on: {', '.join(result['personas'])}")
            print("✨" * 40)
            
        except httpx.ReadTimeout:
            print("\n❌ TIMEOUT: The scraping/AI generation took too long.")
            print("Try again, or check your API keys.")
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(run_dynamic_test())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user.")
