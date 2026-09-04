import asyncio
import json
from fastmcp import FastMCP
from sqlalchemy.future import select
from src.database import AsyncSessionLocal
from src.models.domain import Product, AuditLog
from src.engine.rules import validate_negotiation
from src.payments.razorpay_client import create_payment_link
import uuid

mcp = FastMCP(name="AgenticCommerceGateway")

@mcp.tool()
async def search_inventory(query: str, limit: int = 5) -> str:
    """
    Search the merchant's catalog. 
    Use this to find products, verify stock, and get base prices before negotiating.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Product).filter(Product.name.ilike(f"%{query}%")).limit(limit)
        result = await session.execute(stmt)
        products = result.scalars().all()
        
        if not products:
            return "No matching products found in stock."
            
        catalog = [
            {
                "id": str(p.id), 
                "name": p.name, 
                "price": float(p.base_price), 
                "stock": p.stock_count
            } for p in products
        ]
        return json.dumps(catalog, indent=2)

@mcp.tool()
async def negotiate_price(product_id: str, requested_qty: int, proposed_discount_pct: float) -> str:
    """
    Propose a bulk discount on an item.
    The rule engine will mathematically reject illegal discounts.
    """
    async with AsyncSessionLocal() as session:
        result = await validate_negotiation(session, product_id, requested_qty, proposed_discount_pct)
        
        audit = AuditLog(
            transaction_id=uuid.uuid4(),
            agent_action="NEGOTIATION_ATTEMPT",
            details={"product_id": product_id, "qty": requested_qty, "requested_discount": proposed_discount_pct},
            rule_status=result["status"]
        )
        session.add(audit)
        await session.commit()
        
        return json.dumps(result, indent=2)

@mcp.tool()
async def generate_checkout(product_id: str, quantity: int, final_unit_price: float, customer_email: str, customer_phone: str) -> str:
    """
    Generate a real Razorpay payment link once negotiations are complete.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Product).where(Product.id == uuid.UUID(product_id))
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            return "Transaction failed: Product not found."

        total_amount = final_unit_price * quantity
        description = f"Order for {quantity}x {product.name}"
        
        try:
            rzp_response = create_payment_link(
                amount_inr=total_amount,
                reference_id=str(uuid.uuid4()),
                description=description,
                customer_name="AI Buyer Client",
                customer_email=customer_email,
                customer_phone=customer_phone
            )
            
            audit = AuditLog(
                transaction_id=uuid.uuid4(),
                agent_action="PAYMENT_LINK_CREATED",
                details={"amount": total_amount, "link": rzp_response.get("short_url")},
                rule_status="APPROVED"
            )
            session.add(audit)
            await session.commit()
            
            return f"Success! Payment link generated: {rzp_response.get('short_url')}"
        except Exception as e:
            return f"Payment generation failed: {str(e)}"

if __name__ == "__main__":
    mcp.run()