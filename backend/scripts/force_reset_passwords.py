import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models.database import get_db
from backend.models.orm import User
from backend.security.auth import get_password_hash
from sqlalchemy.future import select

async def main():
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"Updating user: {user.username} ({user.email}) | Role: {user.role}")
            user.hashed_password = get_password_hash("admin123")
        await db.commit()
        print("All passwords updated to admin123.")
        break

if __name__ == "__main__":
    asyncio.run(main())
