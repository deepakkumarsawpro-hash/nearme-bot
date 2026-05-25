import os
from flask import Flask, request
import requests

app = Flask(__name__)

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
        
        # 1. Welcome Message
        if 'text' in msg and msg['text']['body'].lower() in ['hi', 'hello']:
            user_sessions[sender] = {'step': 'role'}
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": "नमस्ते! Near Me Marketplace में आपका स्वागत है। कृपया अपना रोल चुनें:"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "role_cust", "title": "ग्राहक"}}, {"type": "reply", "reply": {"id": "role_prov", "title": "सेवा प्रदाता"}}]}}})

        # 2. Distance Input
        elif 'interactive' in msg and 'button_reply' in msg['interactive'] and user_sessions.get(sender, {}).get('step') == 'role':
            user_sessions[sender].update({'step': 'distance', 'role': msg['interactive']['button_reply']['id']})
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "कृपया दूरी (Distance) दर्ज करें:"}})

        # 3. Location Request
        elif 'text' in msg and user_sessions.get(sender, {}).get('step') == 'distance':
            user_sessions[sender].update({'step': 'location', 'dist': msg['text']['body']})
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "कृपया अपनी लोकेशन (Share Location) साझा करें:"}})

        # 4. Category List (Poori list blueprint ke mutabik)
        elif 'location' in msg and user_sessions.get(sender, {}).get('step') == 'location':
            user_sessions[sender]['step'] = 'category'
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "श्रेणियाँ"}, "body": {"text": "अपनी श्रेणी चुनें:"},
                "action": {"button": "श्रेणियाँ", "sections": [{"title": "Near Me Marketplace", "rows": [
                    {"id": "cat_construction", "title": "1. निर्माण"}, {"id": "cat_auto", "title": "2. ऑटो"},
                    {"id": "cat_food", "title": "3. भोजन"}, {"id": "cat_retail", "title": "4. खुदरा"},
                    {"id": "cat_health", "title": "5. स्वास्थ्य"}, {"id": "cat_personal", "title": "6. व्यक्तिगत"},
                    {"id": "cat_agri", "title": "7. कृषि"}]}]}}})

        # 5. Sub-Category & Other (Logic)
        elif 'interactive' in msg and 'list_reply' in msg['interactive'] and user_sessions.get(sender, {}).get('step') == 'category':
            user_sessions[sender].update({'step': 'whatsapp', 'cat': msg['interactive']['list_reply']['id']})
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "अंतिम चरण: अपना WhatsApp नंबर लिखें:"}})

        # 6. Final Submit
        elif 'text' in msg and user_sessions.get(sender, {}).get('step') == 'whatsapp':
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "धन्यवाद! आपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है। हमारी टीम जल्द ही आपसे संपर्क करेगी।"}})
            del user_sessions[sender]

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
