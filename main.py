from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Aapki details
VERIFY_TOKEN = "my_secret_token_123"
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Failed", 403

    data = request.get_json()
    if data and 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        sender = message['from']
                        text = "hi" # Default
                        
                        if 'text' in message:
                            text = message['text']['body'].lower()
                        elif 'interactive' in message:
                            text = message['interactive']['button_reply']['id'].lower()
                        
                        send_response(sender, text)
    return "OK", 200

def send_response(to, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    
    # Payload hamesha define hona chahiye
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Processing..."}}

    if "hi" in text or "hello" in text:
        payload = {
            "messaging_product": "whatsapp", "to": to, "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Namaste! NearMe mein swagat hai. Aap kya hain?"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}, {"type": "reply", "reply": {"id": "customer", "title": "ग्राहक"}}]}
            }
        }
    elif "sale_service" in text:
        payload = {
            "messaging_product": "whatsapp", "to": to, "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Great! Ab aap apna location share karein."},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "share_loc_now", "title": "Location bhejein"}}]}
            }
        }
    
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    # Railway ke liye port set karna zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
