import os
import requests
from flask import Flask, request

app = Flask(__name__)

PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

def send_menu(to, title, body, rows):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "interactive",
        "interactive": {
            "type": "list", "header": {"type": "text", "text": title},
            "body": {"text": body}, "action": {"button": "Menu", "sections": [{"rows": rows}]}
        }
    }
    requests.post(url, json=payload, headers=headers)

def send_location_request(to):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "interactive",
        "interactive": {"type": "location_request_message", "body": {"text": "अपनी लोकेशन शेयर करें:"}}
    }
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"})

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge")
    
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']
        
        if 'interactive' in msg:
            sel_id = msg['interactive']['list_reply']['id']
            if sel_id == "buyer":
                send_location_request(sender)
            elif sel_id == "cat_kirana":
                send_menu(sender, "Kirana", "Service chunein:", [{"id": "sabji", "title": "Sabji"}, {"id": "dairy", "title": "Dairy"}])
        elif 'location' in msg:
            # 15 Categories ko 2 list mein baant diya
            send_menu(sender, "Categories", "15+ सेवाएँ (Part 1):", [{"id": "cat_kirana", "title": "Kirana"}, {"id": "cat_hotel", "title": "Hotel"}, {"id": "cat_repair", "title": "Repair"}])
        else:
            send_menu(sender, "Welcome", "NearMe mein swagat hai:", [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}])
    except: pass
    return "OK", 200

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
    
