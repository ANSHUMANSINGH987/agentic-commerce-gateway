from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.models.domain import Product, PricingRule

async def validate_negotiation(
    session: AsyncSession, 
    product_id: str, 
    requested_qty: int, 
    requested_discount_pct: float
) -> dict:
    """
    Checks stock availability and validates if the AI-proposed discount 
    falls within the strict bounds of our database pricing rules.
    """
    stmt = select(Product).options(selectinload(Product.pricing_rules)).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        return {"status": "REJECTED", "reason": "Product not found."}

    if product.stock_count < requested_qty:
        return {
            "status": "REJECTED", 
            "reason": f"Insufficient stock. Only {product.stock_count} units available."
        }

    applicable_rule = None
    for rule in product.pricing_rules:
        if requested_qty >= rule.min_quantity:
            if applicable_rule is None or rule.max_discount_pct > applicable_rule.max_discount_pct:
                applicable_rule = rule

    max_allowed = float(applicable_rule.max_discount_pct) if applicable_rule else 0.0

    if requested_discount_pct > max_allowed:
        return {
            "status": "COUNTER_OFFER",
            "reason": f"Requested discount of {requested_discount_pct}% exceeds maximum allowance.",
            "max_approved_discount_pct": max_allowed,
            "unit_price_after_discount": float(product.base_price) * (1 - (max_allowed / 100))
        }

   
    final_unit_price = float(product.base_price) * (1 - (requested_discount_pct / 100))
    return {
        "status": "APPROVED",
        "approved_discount_pct": requested_discount_pct,
        "final_unit_price": final_unit_price,
        "total_cost": final_unit_price * requested_qty
    }