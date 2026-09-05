import os
import asyncio
from google import genai
from sqlalchemy.future import select
from dotenv import load_dotenv

load_dotenv()

from src.database import AsyncSessionLocal
from src.models.domain import Product

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def main():
    print("Backfilling product embeddings...")
    async with AsyncSessionLocal() as session:
        stmt = select(Product)
        result = await session.execute(stmt)
        products = result.scalars().all()
        
        for p in products:
            print(f"Generating vector for: {p.name}")
            embed_res = await ai_client.aio.models.embed_content(
                model='gemini-embedding-001',
                contents=p.name
            )
            vec = list(embed_res.embeddings[0].values)
            
            if len(vec) > 1536:
                vec = vec[:1536]
            elif len(vec) < 1536:
                vec.extend([0.0] * (1536 - len(vec)))
                
            p.embedding = vec
            
        await session.commit()
        print("Successfully updated all embeddings!")

if __name__ == "__main__":
    asyncio.run(main())