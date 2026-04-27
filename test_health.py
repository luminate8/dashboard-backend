import httpx
import asyncio


async def test_health():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("http://localhost:8000/health", timeout=5)
            print("✅ Health Check:", r.json())
            return True
        except Exception as e:
            print("❌ Health check failed:", str(e))
            return False


if __name__ == "__main__":
    result = asyncio.run(test_health())
    exit(0 if result else 1)
