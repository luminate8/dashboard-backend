"""Test HuggingFace LLM directly"""
import asyncio
from app.services.llm_service import HuggingFaceLLM

async def test_llm():
    llm = HuggingFaceLLM()
    
    messages = [
        {"role": "system", "content": "You are Elon Musk. Respond in his style."},
        {"role": "user", "content": "What do you think about AI?"}
    ]
    
    print("Testing HuggingFace LLM...")
    print(f"Model: {llm.model}")
    print(f"API Key set: {bool(llm.api_key)}")
    print()
    
    response = await llm.generate(messages)
    print(f"\nResponse: {response}")

if __name__ == "__main__":
    asyncio.run(test_llm())
