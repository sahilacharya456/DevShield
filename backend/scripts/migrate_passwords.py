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
    print("Migrating passwords to SHA256 + bcrypt...")
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"Updating user {user.username}...")
            # We don't know the plain text password, so we reset them to standard ones
            if user.username == 'admin':
                user.hashed_password = get_password_hash("admin123")
            elif user.username == 'testuser2':
                user.hashed_password = get_password_hash("testpassword2")
            else:
                user.hashed_password = get_password_hash("password123")
        await db.commit()
        print("Passwords updated successfully.")
        break

if __name__ == "__main__":
    asyncio.run(main())
