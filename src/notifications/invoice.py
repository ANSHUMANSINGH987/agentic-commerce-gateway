import os
import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

async def send_secure_invoice(customer_email: str, product_name: str, quantity: int, total_amount: float, payment_link: str, transaction_id: str):
    if not resend.api_key:
        print("⚠️ RESEND_API_KEY not set. Skipping email dispatch.")
        return
        
    html_content = f"""
    <div style="font-family: monospace; max-width: 600px; margin: 0 auto; padding: 24px; background-color: #09090b; color: #e4e4e7; border-radius: 12px; border: 1px solid #27272a;">
        <h2 style="color: #10b981; margin-top: 0;">Agentic Commerce Gateway</h2>
        <p style="color: #a1a1aa;">Secure B2B Invoice & Checkout</p>
        <hr style="border: 1px solid #27272a; margin: 24px 0;" />
        
        <table style="width: 100%; text-align: left; border-collapse: collapse;">
            <tr><th style="padding-bottom: 8px; color: #a1a1aa;">Transaction ID</th><td style="padding-bottom: 8px;">{transaction_id}</td></tr>
            <tr><th style="padding-bottom: 8px; color: #a1a1aa;">Item</th><td style="padding-bottom: 8px;">{quantity}x {product_name}</td></tr>
            <tr><th style="padding-bottom: 24px; color: #a1a1aa;">Total Amount</th><td style="padding-bottom: 24px; color: #10b981; font-weight: bold; font-size: 18px;">₹{total_amount:,.2f}</td></tr>
        </table>
        
        <a href="{payment_link}" style="background-color: #10b981; color: #09090b; padding: 14px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; width: 100%; text-align: center; box-sizing: border-box;">
            Complete Secure Payment
        </a>
        <p style="margin-top: 24px; font-size: 12px; color: #71717a; text-align: center;">Powered by Razorpay & Gemini AI</p>
    </div>
    """
    
    try:
        params = {
            "from": "Agentic Gateway <onboarding@resend.dev>",
            "to": [customer_email],
            "subject": f"Action Required: Secure Invoice for {quantity}x {product_name}",
            "html": html_content
        }
        resend.Emails.send(params)
        print(f"📧 Secure invoice successfully dispatched to {customer_email}")
    except Exception as e:
        print(f"❌ Failed to send email invoice: {e}")