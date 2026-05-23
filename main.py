import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Details
PHONE_ID = "1060745180462931"
TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

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
        
        # 1. Welcome Message
        if 'text' in msg and msg['text']['body'].lower() in ['hi', 'hello']:
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": "NearMe mein swagat hai!"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}]}}})
        
        # 2. Location Request
        elif 'interactive' in msg and msg['interactive'].get('button_reply', {}).get('id') == "sale_service":
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "Apna location pin bhejein:"}})
        
        # 3. Location Receive -> Category List
        elif 'location' in msg:
            user_data[sender] = {'loc': msg['location']}
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Categories"}, "body": {"text": "Category chunein:"},
                "action": {"button": "Categories", "sections": [{"title": "Select", "rows": [
                    {"id": "cat_1", "title": "1. Construction"}, {"id": "cat_2", "title": "2. Automotive"},
                    {"id": "cat_3", "title": "3. Food"}, {"id": "cat_4", "title": "4. Retail"},
                    {"id": "cat_5", "title": "5. Healthcare"}, {"id": "cat_6", "title": "6. Personal"},
                    {"id": "cat_7", "title": "7. Agriculture"}]}]}}})
        
        # 4. Handle Number Input
        elif 'text' in msg and msg['text']['body'].isdigit() and len(msg['text']['body']) >= 10:
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "Dhanyavad! Data save ho gaya."}})

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
