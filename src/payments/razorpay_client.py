import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

rzp_key = os.getenv("RAZORPAY_KEY_ID")
rzp_secret = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(rzp_key, rzp_secret)) if rzp_key and rzp_secret else None

def create_payment_link(amount: float, reference_id: str, description: str, customer_name: str, customer_email: str, customer_phone: str) -> dict:
    if not client:
        return {"short_url": f"https://mock-razorpay.com/pay/{reference_id}"}
        
    payment_link_data = {
        "amount": int(amount * 100), 
        "currency": "INR",
        "accept_partial": False,
        "reference_id": reference_id,
        "description": description,
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "contact": customer_phone
        },
        "notify": {
            "sms": True, 
            "email": False 
        },
        "reminder_enable": True,
    }
    
    return client.payment_link.create(payment_link_data)