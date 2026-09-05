import os
import asyncio
import random
from google import genai
from sqlalchemy.future import select
from sqlalchemy import delete, text
from dotenv import load_dotenv

load_dotenv()
from src.database import AsyncSessionLocal
from src.models.domain import Product

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

BRANDS = ["Lenovo", "Acer", "Dell", "HP", "Apple"]
LAPTOPS = ["Aspire 7", "ThinkPad P16", "Latitude 7430", "EliteBook 840", "MacBook Pro 16"]
EDGE_BOARDS = ["Radxa ZERO 3W with NPU", "Raspberry Pi 5 8GB", "NVIDIA Jetson Orin Nano", "Coral Dev Board"]
SMARTPHONES = ["Enterprise Edition (3D Curved AMOLED, 12GB RAM)", "Pro Series (Flat OLED, 8GB RAM)", "Ultra (Curved AMOLED, 16GB RAM)"]
GPUS = ["NVIDIA RTX 4090", "AMD Radeon PRO W7900", "NVIDIA A100 Tensor Core", "NVIDIA H100 80GB"]

async def main():
    print("Initializing production catalog generation...")
    products_to_create = []
    
    for brand in BRANDS:
        for model in LAPTOPS:
            products_to_create.append((f"{brand} {model} Workstation", random.randint(55000, 185000), random.randint(0, 50)))
    
    for board in EDGE_BOARDS:
        products_to_create.append((f"{board} Edge AI Module", random.randint(3000, 25000), random.randint(10, 200)))
        
    for phone in SMARTPHONES:
        products_to_create.append((f"Corporate Smartphone - {phone}", random.randint(45000, 125000), random.randint(20, 100)))

    for gpu in GPUS:
        products_to_create.append((f"{gpu} Enterprise GPU", random.randint(165000, 2500000), random.randint(2, 15)))

    print(f"Generated {len(products_to_create)} SKUs. Batch-processing embeddings to avoid rate limits...")

    product_names = [p[0] for p in products_to_create]
    batch_size = 20
    all_vectors = []
    
    for i in range(0, len(product_names), batch_size):
        batch = product_names[i:i + batch_size]
        try:
            embed_res = await ai_client.aio.models.embed_content(
                model='gemini-embedding-001',
                contents=batch
            )
            for item in embed_res.embeddings:
                vec = list(item.values)
                if len(vec) > 1536: vec = vec[:1536]
                elif len(vec) < 1536: vec.extend([0.0] * (1536 - len(vec)))
                all_vectors.append(vec)
                
            print(f"Embedded batch {i // batch_size + 1}")
            await asyncio.sleep(2) 
        except Exception as e:
            print(f"Error embedding batch: {e}")
            return

    async with AsyncSessionLocal() as session:
        print("Clearing old mock data and dependent constraints...")
        await session.execute(text("TRUNCATE TABLE products CASCADE;")) 
        
        print("Inserting production SKUs...")
        for i, (name, price, stock) in enumerate(products_to_create):
            new_product = Product(
                name=name,
                base_price=price,
                stock_count=stock,
                embedding=all_vectors[i]
            )
            session.add(new_product)
            
        await session.commit()
        print("Production catalog successfully deployed!")

if __name__ == "__main__":
    asyncio.run(main())