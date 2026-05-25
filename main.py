import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Aapki Details
PHONE_ID = "1060745180462931"
TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

user_sessions = {}

def send_msg(to, payload):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    data = request.get_json()
    if 'entry' in data:
        msg = data['entry'][0]['changes'][0]['value'].get('messages', [{}])[0]
        sender = msg.get('from')
        
        # 1. [span_2](start_span)Welcome Message (Button Design)[span_2](end_span)
        if 'text' in msg and msg['text']['body'].lower() in ['hi', 'hello']:
            user_sessions[sender] = {'step': 'role'}
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": "नमस्ते! NearMe में आपका स्वागत है। कृपया अपना रोल चुनें:"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "role_customer", "title": "ग्राहक"}}, 
                                     {"type": "reply", "reply": {"id": "role_provider", "title": "सेवा प्रदाता"}}]}}})

        # 2. [span_3](start_span)Category Selection (List Design)[span_3](end_span)
        elif 'interactive' in msg and msg['interactive'].get('button_reply', {}).get('id', '').startswith('role_'):
            user_sessions[sender]['step'] = 'category'
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "श्रेणी चुनें"}, "body": {"text": "कृपया अपनी श्रेणी चुनें:"},
                "action": {"button": "श्रेणियाँ", "sections": [{"title": "NearMe Categories", "rows": [
                    {"id": "cat_construction", "title": "1. निर्माण (Construction)"},
                    {"id": "cat_auto", "title": "2. ऑटो (Automotive)"},
                    {"id": "cat_food", "title": "3. भोजन (Food)"}]}]}}})

        # 3. [span_4](start_span)Final Confirmation[span_4](end_span)
        elif 'text' in msg and len(msg['text']['body']) >= 10:
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {
                "body": "धन्यवाद! आपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है। हमारी टीम जल्द ही आपसे संपर्क करेगी। चुनने के लिए धन्यवाद!"}})

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
