import os
import requests
from flask import Flask, request

app = Flask(__name__)
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

# State storage: {sender: step}
user_sessions = {}

def send_payload(to, payload):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']
        
        # 1. Location Received
        if 'location' in msg:
            user_sessions[sender] = 'category'
            send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Select Service"}, "body": {"text": "15+ Categories:"},
                "action": {"button": "Menu", "sections": [{"title": "List", "rows": [{"id": "kirana", "title": "Kirana"}, {"id": "hotel", "title": "Hotel"}]}]}
            }})

        # 2. Interactive (Buyer/Seller/Category/Subcat)
        elif 'interactive' in msg:
            sel_id = msg['interactive']['list_reply']['id']
            
            if sel_id == "buyer":
                send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                    "type": "location_request_message", "body": {"text": "अपनी लोकेशन शेयर करें:"}
                }})
            elif sel_id == "kirana":
                user_sessions[sender] = 'final'
                send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": "अपनी मांग (Requirement) लिखें:"}})
        
        # 3. Final Text Input
        elif 'text' in msg and user_sessions.get(sender) == 'final':
            send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": "धन्यवाद! आपका आर्डर दर्ज हो गया है।"}})
            user_sessions[sender] = 'start'
        
        # 4. Welcome (Fallback)
        else:
            send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Welcome"}, "body": {"text": "NearMe में स्वागत है, कौन हैं आप?"},
                "action": {"button": "Start", "sections": [{"rows": [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}]}]}
            }})
    except: pass
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000)
    
