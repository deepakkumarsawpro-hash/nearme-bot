import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Details
VERIFY_TOKEN = "my_secret_token_123"
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN: return request.args.get("hub.challenge")
        return "Failed", 403

    data = request.get_json()
    if data and 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        sender = message['from']
                        text = "hi"
                        if 'text' in message: text = message['text']['body'].lower()
                        elif 'interactive' in message: text = message['interactive']['button_reply']['id'].lower()
                        elif 'location' in message: text = "user_location_received"
                        send_response(sender, text)
    return "OK", 200

def send_response(to, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = None

    # STEP 1: Main Category (List)
    if "user_location_received" in text:
        payload = {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "list", "header": {"type": "text", "text": "Categories"}, "body": {"text": "Chuniye:"},
            "action": {"button": "Categories", "sections": [{"title": "Select One", "rows": [
                {"id": "cat1", "title": "1. Construction"}, {"id": "cat2", "title": "2. Automotive"},
                {"id": "cat3", "title": "3. Food"}, {"id": "cat4", "title": "4. Retail"},
                {"id": "cat5", "title": "5. Healthcare"}, {"id": "cat6", "title": "6. Personal"}, {"id": "cat7", "title": "7. Agriculture"}
            ]}]}}}

    # STEP 2: Sub-Category (Buttons) - Example for cat1
    elif text == "cat1":
        payload = {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "button", "body": {"text": "Sub-Category chunein:"},
            "action": {"buttons": [{"type": "reply", "reply": {"id": "sub_mason", "title": "Mason"}}, {"type": "reply", "reply": {"id": "sub_plumber", "title": "Plumber"}}]}}}
            
    # STEP 3: Keywords + Open Text Prompt
    elif text.startswith("sub_"):
        payload = {"messaging_product": "whatsapp", "to": to, "type": "text", 
                   "text": {"body": "Keywords: Raj Mistri, Building. \n\nAb apna specific kaam type karke bhejein (Open Text):"}}

    # Handling Open Text Input
    elif "hi" not in text and "sale_service" not in text and "cat" not in text and "sub_" not in text:
        payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Request received: " + text + ". Hum aapko jaldi contact karenge!"}}

    if payload: requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
