import os
import requests
from flask import Flask, request

app = Flask(__name__)
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

def send_msg(to, payload):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET': return request.args.get("hub.challenge")
    data = request.get_json()
    
    try:
        # Message aur sender extract karna
        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])
        
        if messages:
            msg = messages[0]
            sender = msg['from']
            
            # --- AGAR INTERACTIVE MENU CLICK KYA HAI ---
            if 'interactive' in msg:
                sel_id = msg['interactive']['list_reply']['id']
                
                if sel_id == "buyer":
                    # Location Request
                    send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", 
                        "interactive": {"type": "location_request_message", "body": {"text": "अपनी लोकेशन शेयर करें:"}}})
                
                elif sel_id == "kirana":
                    send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": "अपनी मांग (Requirement) यहाँ लिखें:"}})
            
            # --- AGAR LOCATION SHARE KI HAI ---
            elif 'location' in msg:
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                    "type": "list", "header": {"type": "text", "text": "Services"}, "body": {"text": "Categories चुनें:"},
                    "action": {"button": "Menu", "sections": [{"title": "List", "rows": [{"id": "kirana", "title": "Kirana"}, {"id": "hotel", "title": "Hotel"}]}]}
                }})
            
            # --- AGAR NORMAL START/HI HAI (WELCOME) ---
            else:
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                    "type": "list", "header": {"type": "text", "text": "Welcome"}, "body": {"text": "NearMe में स्वागत है, कौन हैं आप?"},
                    "action": {"button": "Start", "sections": [{"title": "Role", "rows": [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}]}]}
                }})
                
    except Exception as e:
        print(f"Error: {e}")
        
    return "OK", 200

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
    
