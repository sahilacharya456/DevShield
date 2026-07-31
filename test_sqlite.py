import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    try:
        engine = create_async_engine("sqlite+aiosqlite:///test.db", echo=True)
        async with engine.begin() as conn:
            print("Successfully connected!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
