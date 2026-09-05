import os
import json
import uuid
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.future import select
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

from src.database import AsyncSessionLocal
from src.models.domain import Product, AuditLog
from src.engine.rules import validate_negotiation
from src.payments.razorpay_client import create_payment_link

app = FastAPI(title="Agentic Commerce Gateway API")
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

async def search_inventory_tool(query: str, limit: int = 5) -> str:
    """Search the merchant's catalog for products, stock levels, and base prices."""
    async with AsyncSessionLocal() as session:
        stmt = select(Product).filter(Product.name.ilike(f"%{query}%")).limit(limit)
        result = await session.execute(stmt)
        products = result.scalars().all()
        if not products:
            return "No matching products found."
        catalog = [{"id": str(p.id), "name": p.name, "price": float(p.base_price), "stock": p.stock_count} for p in products]
        return json.dumps(catalog)

async def negotiate_price_tool(product_id: str, requested_qty: int, proposed_discount_pct: float) -> str:
    """Propose a bulk discount on an item. The system will strictly evaluate the math."""
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
        return json.dumps(result)

async def generate_checkout_tool(product_id: str, quantity: int, final_unit_price: float, customer_email: str, customer_phone: str) -> str:
    """Generate a real Razorpay payment link once a price is approved."""
    async with AsyncSessionLocal() as session:
        stmt = select(Product).where(Product.id == uuid.UUID(product_id))
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            return "Transaction failed: Product not found."

        total_amount = final_unit_price * quantity
        description = f"Order for {quantity}x {product.name}"
        
        try:
            rzp_response = create_payment_link(total_amount, str(uuid.uuid4()), description, "AI Buyer Client", customer_email, customer_phone)
            audit = AuditLog(
                transaction_id=uuid.uuid4(),
                agent_action="PAYMENT_LINK_CREATED",
                details={"amount": total_amount, "link": rzp_response.get("short_url")},
                rule_status="APPROVED"
            )
            session.add(audit)
            await session.commit()
            return f"Payment link generated: {rzp_response.get('short_url')}"
        except Exception as e:
            return f"Payment generation failed: {str(e)}"

tool_map = {
    "search_inventory_tool": search_inventory_tool,
    "negotiate_price_tool": negotiate_price_tool,
    "generate_checkout_tool": generate_checkout_tool
}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    contents = [types.Content(role=m.role, parts=[types.Part.from_text(text=m.content)]) for m in req.messages]
    
    sys_instruct = "You are an AI sales agent for a merchant. Use tools to check stock, negotiate prices, and generate payment links. Never invent prices or URLs. You must use the tools."
    
    response = await ai_client.aio.models.generate_content(
        model='gemini-3.6-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct,
            tools=[search_inventory_tool, negotiate_price_tool, generate_checkout_tool],
            temperature=0.2
        )
    )

    if response.function_calls:
        for fc in response.function_calls:
            func = tool_map.get(fc.name)
            if func:
                tool_result = await func(**fc.args)
                
                contents.append(response.candidates[0].content)
                contents.append(
                    types.Content(role="user", parts=[
                        types.Part.from_function_response(name=fc.name, response={"result": tool_result})
                    ])
                )
                
                final_response = await ai_client.aio.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(tools=[search_inventory_tool, negotiate_price_tool, generate_checkout_tool])
                )
                return {"reply": final_response.text}

    return {"reply": response.text}

@app.get("/api/audit")
async def get_audit_logs():
    async with AsyncSessionLocal() as session:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(20)
        result = await session.execute(stmt)
        logs = result.scalars().all()
        return [{"id": str(log.id), "action": log.agent_action, "status": log.rule_status, "details": log.details, "time": log.created_at.isoformat()} for log in logs]

@app.get("/api/inventory")
async def get_inventory():
    async with AsyncSessionLocal() as session:
        stmt = select(Product).order_by(Product.name)
        result = await session.execute(stmt)
        products = result.scalars().all()
        return [{"id": str(p.id), "name": p.name, "price": float(p.base_price), "stock": p.stock_count} for p in products]