import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Config
PHONE_ID = "1060745180462931"
TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

# Backend Data Storage
user_data = {}

def send_msg(to, payload):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge") if request.args.get("hub.verify_token") == "my_secret_token_123" else "Error"
    
    data = request.get_json()
    if 'entry' in data:
        msg = data['entry'][0]['changes'][0]['value'].get('messages', [{}])[0]
        sender = msg.get('from')
        
        # Logic Flow
        if 'text' in msg or 'interactive' in msg:
            text = msg['text']['body'].lower() if 'text' in msg else msg['interactive'].get('button_reply', {}).get('id', '')
            
            # 1. Welcome
            if text in ['hi', 'hello']:
                user_data[sender] = {'step': 1}
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                    "type": "button", "body": {"text": "Namaste! NearMe mein swagat hai. Aap kya hain?"},
                    "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}, {"type": "reply", "reply": {"id": "customer", "title": "ग्राहक"}}]}}})
            
            # 2. Form Start
            elif text == "sale_service":
                user_data[sender]['step'] = 2
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "NearMe Form:\n1. Location: कृपया अपना लोकेशन पिन भेजें।"}})
            
            # 3. Handle Number
            elif sender in user_data and user_data[sender].get('step') == 3 and text.isdigit():
                user_data[sender]['phone'] = text
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": f"Dhanyavad! Aapka data save ho gaya hai. Hum {text} par sampark karenge."}})
                # Yahan aap apna logic daal sakte hain jo backend se match karega.
                print(f"SAVED DATA: {user_data[sender]}")

        # Handle Location
        elif 'location' in msg:
            if sender in user_data:
                user_data[sender]['loc'] = msg['location']
                user_data[sender]['step'] = 3
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "Location mil gayi! \n\nAb apna WhatsApp Number type karein:"}})
    
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
    
