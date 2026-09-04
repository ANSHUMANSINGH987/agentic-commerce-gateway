import asyncio
import uuid
from decimal import Decimal
from sqlalchemy.future import select
from src.database import AsyncSessionLocal
from src.models.domain import Product, PricingRule

# Dummy 1536-dimensional vectors for text-embedding-3-small
def mock_vector(seed_val: float):
    vec = [0.0] * 1536
    vec[0] = seed_val
    return vec

async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        if result.scalars().first():
            print("Data already seeded.")
            return

        print("Seeding inventory and pricing rules...")
        
        # Product 1: High-end GPU
        gpu = Product(
            name="NVIDIA RTX 4090",
            description="Flagship graphics card for AI workloads and extreme gaming.",
            base_price=Decimal("165000.00"),
            stock_count=5,
            embedding=mock_vector(0.9) 
        )
        
        # Product 2: Dev Laptop
        laptop = Product(
            name="ThinkPad P16 Gen 2",
            description="Mobile workstation with 64GB RAM for heavy software compilation.",
            base_price=Decimal("210000.00"),
            stock_count=12,
            embedding=mock_vector(0.5)
        )
        
        session.add_all([gpu, laptop])
        await session.flush() 

        # Strict rules: 5% max discount on GPU if they buy 2+, 12% on laptop for 5+
        rule1 = PricingRule(product_id=gpu.id, min_quantity=2, max_discount_pct=Decimal("5.00"))
        rule2 = PricingRule(product_id=laptop.id, min_quantity=5, max_discount_pct=Decimal("12.00"))
        
        session.add_all([rule1, rule2])
        await session.commit()
        print("Inventory locked and loaded.")

if __name__ == "__main__":
    asyncio.run(seed())