from celery import shared_task
from django.utils import timezone
from .models import UserKYC
from .api import send_otp_to_aadhar
import requests

@shared_task
def send_otp_task(user_kyc_id, aadhar_number):
    otp_sent , message = send_otp_to_aadhar(aadhar_number)
    if otp_sent:
        user_kyc = UserKYC.objects.get(id=user_kyc_id)
        user_kyc.generate_otp()
        return True, "OTP send successfully"
    return False, message

@shared_task
def verify_aadhar_otp_task(aadhar_number, entered_otp):

    api_url = "https://uidai.gov.in/api/auth/verify-otp"

    headers = {
        'Authorization': "a98900sdf0912hgdk@123",
        'content_type': 'application/json'
    }

    payload = {
        'aadhar_number': aadhar_number,
        'entered_otp': entered_otp
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code==200:
        return True, 'OTP Verifiaction succesfully'
    else:
        return False, response.json().get('error', 'OTP verifiaction failed')

