"""Test which HF models are available"""
import asyncio
import httpx
from app.config import HUGGINGFACE_API_KEY, HUGGINGFACE_MODEL

async def test_models():
    models = [
        "meta-llama/Llama-3.2-3B-Instruct",
        "microsoft/Phi-3-mini-4k-instruct",
        "HuggingFaceH4/zephyr-7b-beta",
        "google/gemma-2b-it",
    ]
    
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {"max_new_tokens": 50},
    }
    
    print("Testing HuggingFace models availability...\n")
    
    async with httpx.AsyncClient() as client:
        for model in models:
            url = f"https://api-inference.huggingface.co/models/{model}"
            response = await client.post(url, headers=headers, json=payload, timeout=30)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{status} - {model}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:100]}")

if __name__ == "__main__":
    asyncio.run(test_models())
