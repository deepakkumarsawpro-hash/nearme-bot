from flask import Flask, request
import requests

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
    if 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        sender = message['from']
                        text = message.get('text', {}).get('body', '').lower()
                        send_whatsapp_message(sender, text)
    return "OK", 200

def send_whatsapp_message(to, text):
    # Logic: Categories handle karna
    if "hi" in text or "hello" in text:
        reply_body = "Welcome to NearMe! Choose category:\n1. Construction\n2. Automobile\n3. Food"
    elif "construction" in text:
        reply_body = "Construction services: [Link1], [Link2]"
    else:
        reply_body = "Please reply with 'Hi' to see categories."

    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": reply_body}}
    
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(port=5000)
