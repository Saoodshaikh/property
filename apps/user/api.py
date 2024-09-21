import requests

def send_otp_to_aadhar(aadhar_number):
    # Example URL for UIDAI  OTP API
    api_url = "https://uidai.gov.in/api/auth/send-otp" # Hypothetical endpoint

    # Example headers (this should include valid authentication headers like API token, Client ID)
    headers = {
        'Authorization': 'a98900sdf0912hgdk@123',
        'content_type': 'application/json'
    }

    # Payload with Aadar card
    payload = {
        'aadhar_number': aadhar_number
    }

    # Make the request to send the OTP
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        return True, 'Otp Send succesfully'
    
    else:
        return False, response.json().get('error', 'Error sending OTP')