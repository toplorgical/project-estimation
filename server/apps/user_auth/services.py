
import requests
from django.conf import settings

PAYSTACK_INIT_URL = 'https://api.paystack.co/transaction/initialize'
PAYSTACK_VERIFY_URL = 'https://api.paystack.co/transaction/verify/'

HEADERS = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json"
}

def initialize_payment(email, amount, reference, callback_url):
    data = {
        "email": email,
        "amount": int(amount * 100), 
        "reference": reference,
        "callback_url": callback_url,
    }
    response = requests.post(PAYSTACK_INIT_URL, json=data, headers=HEADERS)
    return response.json()


def verify_payment(reference):
    response = requests.get(f"{PAYSTACK_VERIFY_URL}{reference}", headers=HEADERS)
    return response.json()
