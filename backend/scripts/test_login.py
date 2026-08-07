import asyncio
import os
import sys
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.models.database import init_db

async def main():
    await init_db()
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", data={
            "username": "testuser2@devshield.ai",
            "password": "admin123"
        })
        print(response.status_code)
        print(response.json())

if __name__ == "__main__":
    asyncio.run(main())
