import asyncio
from sqlalchemy import text
from src.database import engine
from src.models.domain import Base

async def init_db():
    async with engine.begin() as conn:
        print("Creating pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())