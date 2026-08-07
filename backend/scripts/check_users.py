import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models.database import get_db
from backend.models.orm import User
from sqlalchemy.future import select

async def main():
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"User: {user.username} ({user.email}) | Role: {user.role}")
        break

if __name__ == "__main__":
    asyncio.run(main())
