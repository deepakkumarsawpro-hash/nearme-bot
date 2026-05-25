import os
from flask import Flask, request
import requests

app = Flask(__name__)

PHONE_ID = "1060745180462931"
TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

# User session data store
user_sessions = {}

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
        entry = data['entry'][0]
        msg = entry['changes'][0]['value'].get('messages', [{}])[0]
        sender = msg.get('from')
        
        # [span_5](start_span)STEP 1: Welcome Message (Buttons)[span_5](end_span)
        if 'text' in msg and msg['text']['body'].lower() in ['hi', 'hello']:
            user_sessions[sender] = {'step': 'role'}
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": "नमस्ते! Near Me Marketplace में आपका स्वागत है। कृपया अपना रोल चुनें:"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "role_cust", "title": "ग्राहक"}}, 
                                     {"type": "reply", "reply": {"id": "role_prov", "title": "सेवा प्रदाता"}}]}}})

        # [span_6](start_span)[span_7](start_span)STEP 2: Data Collection Flow[span_6](end_span)[span_7](end_span)
        elif 'interactive' in msg and 'button_reply' in msg['interactive']:
            role = msg['interactive']['button_reply']['id']
            user_sessions[sender] = {'step': 'location', 'role': role}
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "कृपया अपनी लोकेशन शेयर करें (Pin location):"}})

        elif 'location' in msg and user_sessions.get(sender, {}).get('step') == 'location':
            user_sessions[sender]['step'] = 'category'
            # [span_8](start_span)List menu for categories[span_8](end_span)
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "श्रेणी"}, "body": {"text": "अपनी श्रेणी चुनें:"},
                "action": {"button": "श्रेणी", "sections": [{"title": "Near Me Categories", "rows": [
                    {"id": "cat_construction", "title": "1. निर्माण"}, {"id": "cat_auto", "title": "2. ऑटो"},
                    {"id": "cat_food", "title": "3. भोजन"}, {"id": "cat_retail", "title": "4. खुदरा"}]}]}}})

        # [span_9](start_span)[span_10](start_span)Final Step: WhatsApp Number[span_9](end_span)[span_10](end_span)
        elif 'interactive' in msg and 'list_reply' in msg['interactive']:
            user_sessions[sender]['step'] = 'final'
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "अपना WhatsApp नंबर लिखें:"}})

        elif 'text' in msg and user_sessions.get(sender, {}).get('step') == 'final':
            # [span_11](start_span)[span_12](start_span)STEP 3: Confirmation[span_11](end_span)[span_12](end_span)
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {
                "body": "धन्यवाद! आपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है। हमारी टीम जल्द ही आपसे संपर्क करेगी।"}})
    
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
