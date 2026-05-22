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
                send_menu(sender, "Categories", "Select service:", [{"id": "kirana", "title": "Kirana"}, {"id": "hotel", "title": "Hotel"}])
            elif sel_id == "kirana":
                send_menu(sender, "Sub-Cat", "Select item:", [{"id": "sabji", "title": "Sabji"}, {"id": "milk", "title": "Milk"}])
        else:
            send_menu(sender, "Welcome", "नमस्कार! NearMe में स्वागत है।", [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}])
    except: pass
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
