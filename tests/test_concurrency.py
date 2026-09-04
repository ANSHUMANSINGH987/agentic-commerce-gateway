import asyncio
import uuid
import pytest
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.database import AsyncSessionLocal, engine
from src.models.domain import Product

@pytest.mark.asyncio
async def test_race_condition():
    """
    Simulates two AI agents trying to buy the exact same product simultaneously.
    Proves that our database locking and constraints prevent overselling.
    """
    product_id = uuid.uuid4()
    async with AsyncSessionLocal() as session:
        test_product = Product(
            id=product_id,
            name="Limited Edition Sneaker",
            base_price=250.00,
            stock_count=1,
            embedding=[0.0] * 1536 
        )
        session.add(test_product)
        await session.commit()

    async def ai_checkout_attempt(worker_name: str):
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(Product).where(Product.id == product_id).with_for_update()
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()

                if not product or product.stock_count < 1:
                    print(f"[{worker_name}] Failed: Out of stock.")
                    return False

                await asyncio.sleep(0.5)

                product.stock_count -= 1
                await session.commit()
                print(f"[{worker_name}] SUCCESS: Bought the item!")
                return True
                
            except IntegrityError:
                await session.rollback()
                print(f"[{worker_name}] Failed: Database Integrity Error (Negative Stock).")
                return False

    results = await asyncio.gather(
        ai_checkout_attempt("Agent Alpha"),
        ai_checkout_attempt("Agent Beta")
    )

    successes = sum(results)
    assert successes == 1, f"Concurrency failure: {successes} agents succeeded instead of 1."
    
    async with AsyncSessionLocal() as session:
        stmt = select(Product).where(Product.id == product_id)
        result = await session.execute(stmt)
        final_product = result.scalar_one()
        assert final_product.stock_count == 0, "Stock count should be exactly zero."

        await session.delete(final_product)
        await session.commit()