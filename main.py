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
        
        # 1. Start Step
        if 'text' in msg and msg['text']['body'].lower() in ['hi', 'hello']:
            user_sessions[sender] = {'step': 'welcome'}
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": "NearMe mein swagat hai!"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}]}}})

        # 2. Location Request (Step 2)
        elif 'interactive' in msg and msg['interactive'].get('button_reply', {}).get('id') == "sale_service":
            user_sessions[sender]['step'] = 'location'
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "Apni location bhejein:"}})

        # 3. Handle Category (Step 3)
        elif 'location' in msg:
            user_sessions[sender].update({'step': 'category', 'loc': msg['location']})
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Categories"}, "body": {"text": "Category chunein:"},
                "action": {"button": "Categories", "sections": [{"title": "Select", "rows": [{"id": "cat_1", "title": "1. Construction"}]}]}}})

        # 4. Handle Sub-Category (Step 4)
        elif 'interactive' in msg and 'list_reply' in msg['interactive'] and user_sessions.get(sender, {}).get('step') == 'category':
            cat_id = msg['interactive']['list_reply']['id']
            user_sessions[sender].update({'step': 'subcategory', 'cat': cat_id})
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": "Sub-Category chunein:"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "sub_mason", "title": "Mason"}}]}}})

        # 5. Handle Keywords (Step 5)
        elif 'interactive' in msg and 'button_reply' in msg['interactive'] and user_sessions.get(sender, {}).get('step') == 'subcategory':
            sub_id = msg['interactive']['button_reply']['id']
            user_sessions[sender].update({'step': 'keywords', 'sub': sub_id})
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Keywords"}, "body": {"text": "Keywords chunein:"},
                "action": {"button": "Keywords", "sections": [{"title": "Select", "rows": [{"id": "kw_raj", "title": "Raj Mistri"}]}]}}})

        # 6. Handle Number (Step 6)
        elif 'interactive' in msg and 'list_reply' in msg['interactive'] and user_sessions.get(sender, {}).get('step') == 'keywords':
            user_sessions[sender]['step'] = 'phone'
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "Ab apna WhatsApp Number bhejein:"}})

        # 7. Final Completion
        elif 'text' in msg and user_sessions.get(sender, {}).get('step') == 'phone':
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": "Dhanyavad! Data save ho gaya."}})

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
    
