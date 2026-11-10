import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.main import app

async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("Testing /health with ASGITransport...")
        res = await client.get("/health")
        print("Response:", res.status_code, res.json())

if __name__ == "__main__":
    asyncio.run(main())
