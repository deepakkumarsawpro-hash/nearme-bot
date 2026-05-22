import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Aapka TOKEN aur ID yahan rakhein
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

def send_message(to, payload):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge")
    
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']

        # Agar location share ki
        if 'location' in msg:
            # Report ki Categories (Example ke liye 6 main groups)
            payload = {
                "messaging_product": "whatsapp", "to": sender, "type": "interactive",
                "interactive": {
                    "type": "list", "header": {"type": "text", "text": "NearMe Categories"},
                    "body": {"text": "Apni service chunein:"},
                    "action": {"button": "Categories", "sections": [{
                        "title": "Services",
                        "rows": [
                            {"id": "c1", "title": "Construction"},
                            {"id": "c2", "title": "Automobile"},
                            {"id": "c3", "title": "Food/Hospitality"},
                            {"id": "c4", "title": "Retail/Daily"},
                            {"id": "c5", "title": "Health/Edu"},
                            {"id": "c6", "title": "Professional"}
                        ]
                    }]}
                }
            }
            send_message(sender, payload)
        
        # Agar start message (Hi/Hello)
        else:
            payload = {
                "messaging_product": "whatsapp", "to": sender, "type": "interactive",
                "interactive": {
                    "type": "location_request_message",
                    "body": {"text": "NearMe mein swagat hai! Location share karein taaki hum aapke paas ki services dikha sakein:"}
                }
            }
            send_message(sender, payload)

    except:
        pass
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
