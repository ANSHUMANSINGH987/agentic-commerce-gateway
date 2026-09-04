import razorpay
from typing import Dict, Any
from src.config import settings

rzp_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment_link(
    amount_inr: float, 
    reference_id: str, 
    description: str, 
    customer_name: str, 
    customer_email: str, 
    customer_phone: str
) -> Dict[str, Any]:
    """
    Generates a standard Razorpay Payment Link.
    Amount is multiplied by 100 because Razorpay expects the smallest currency unit (paise).
    """
    payload = {
        "amount": int(amount_inr * 100), 
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
            "email": True
        },
        "reminder_enable": True
    }
    
    response = rzp_client.payment_link.create(payload)
    return response