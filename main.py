import os
import requests
from flask import Flask, request

app = Flask(__name__)
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

user_state = {}

def send_msg(to, payload):
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
            user_state[sender] = 'cat'
            # Pura 15 Categories ka list (Do sections mein)
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Services"}, "body": {"text": "15+ सेवाएँ चुनें:"},
                "action": {"button": "Categories", "sections": [
                    {"title": "Set 1", "rows": [{"id": "kirana", "title": "Kirana"}, {"id": "hotel", "title": "Hotel"}, {"id": "repair", "title": "Repair"}, {"id": "auto", "title": "Auto"}, {"id": "edu", "title": "Education"}]},
                    {"title": "Set 2", "rows": [{"id": "health", "title": "Health"}, {"id": "beauty", "title": "Beauty"}, {"id": "elec", "title": "Electronics"}, {"id": "cloth", "title": "Clothing"}, {"id": "real", "title": "Real Estate"}]}
                ]}
            }})

        # 2. Interactive Logic
        elif 'interactive' in msg:
            sel_id = msg['interactive']['list_reply']['id']
            if sel_id == "buyer":
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "location_request_message", "body": {"text": "अपनी वर्तमान लोकेशन शेयर करें:"}}})
            elif sel_id in ["kirana", "hotel", "repair"]: # Categories
                user_state[sender] = 'final'
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": f"आपने {sel_id} चुना है। अपनी ज़रूरत (Requirement) विस्तार से लिखें:"}})

        # 3. Final Input
        elif 'text' in msg and user_state.get(sender) == 'final':
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": "धन्यवाद! आपकी रिक्वेस्ट दर्ज हो गई है। हमारी टीम जल्द आपसे संपर्क करेगी।"}})
            user_state[sender] = 'start'
            
        else:
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Welcome"}, "body": {"text": "NearMe में स्वागत है, कौन हैं आप?"}, "action": {"button": "Start", "sections": [{"rows": [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}]}]}}})
    except: pass
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000)
    
