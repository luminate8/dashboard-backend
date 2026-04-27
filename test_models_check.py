"""
Test script: checks which LLM and embedding models work with the current HF API key.
Run: python test_models_check.py
"""
import asyncio
import httpx

HF_API_KEY = "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"
CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
EMBED_BASE = "https://router.huggingface.co/hf-inference/models"

CHAT_MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",           # currently used
    "mistralai/Mistral-7B-Instruct-v0.3",   # requested
    "mistralai/Mistral-Nemo-Instruct-2407",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "meta-llama/Llama-3.2-3B-Instruct",
]

EMBED_MODELS = [
    "BAAI/bge-small-en-v1.5",              # currently used
    "sentence-transformers/all-MiniLM-L6-v2",
]

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}


async def test_chat(model: str):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say hello in one word."}],
        "max_tokens": 20,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(CHAT_URL, headers=HEADERS, json=payload, timeout=30)
    if r.status_code == 200:
        answer = r.json()["choices"][0]["message"]["content"].strip()
        print(f"  [OK]   {model} -> '{answer}'")
    else:
        err = r.json().get("error", {})
        msg = err.get("message", r.text[:100]) if isinstance(err, dict) else str(err)[:100]
        print(f"  [FAIL] {model} -> {msg}")


async def test_embed(model: str):
    url = f"{EMBED_BASE}/{model}"
    payload = {"inputs": ["hello world"], "options": {"wait_for_model": True}}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=HEADERS, json=payload, timeout=30)
    if r.status_code == 200:
        vec = r.json()
        dim = len(vec[0]) if isinstance(vec[0], list) else len(vec)
        print(f"  [OK]   {model} -> embedding dim={dim}")
    else:
        print(f"  [FAIL] {model} -> {r.text[:120]}")


async def main():
    print("=== Chat / LLM Models ===")
    for m in CHAT_MODELS:
        await test_chat(m)

    print("\n=== Embedding Models ===")
    for m in EMBED_MODELS:
        await test_embed(m)


if __name__ == "__main__":
    asyncio.run(main())
