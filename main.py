import os
import requests
from flask import Flask, request

app = Flask(__name__)
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

def send_payload(to, payload):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET': return request.args.get("hub.challenge")
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']
        
        if 'interactive' in msg:
            sel_id = msg['interactive']['list_reply']['id']
            # --- LOCATION KE BAAD CATEGORIES (15 TOTAL) ---
            if sel_id == "buyer":
                send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "location_request_message", "body": {"text": "अपनी लोकेशन शेयर करें:"}}})
            
            # --- 15 CATEGORIES LIST ---
            elif sel_id == "show_cat_1":
                send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Services"}, "body": {"text": "Category चुनें:"}, "action": {"button": "Select", "sections": [{"title": "Part 1", "rows": [{"id": "c1", "title": "Kirana"}, {"id": "c2", "title": "Hotel"}, {"id": "c3", "title": "Repair"}, {"id": "c4", "title": "Auto"}, {"id": "c5", "title": "Education"}, {"id": "c6", "title": "Health"}, {"id": "c7", "title": "Beauty"}, {"id": "c8", "title": "Electronics"}]}]}}})
            elif sel_id == "c1": # Example: Kirana -> Subcategory
                send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Sub-Cat"}, "body": {"text": "Item चुनें:"}, "action": {"button": "Select", "sections": [{"title": "Kirana", "rows": [{"id": "final", "title": "Sabji"}, {"id": "final", "title": "Dairy"}]}]}}})
            
            elif sel_id == "final":
                send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": "अपनी मांग (Requirement) लिखें:"}})

        elif 'location' in msg:
            send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Categories"}, "body": {"text": "सेवाएँ देखें:"}, "action": {"button": "Menu", "sections": [{"title": "Main", "rows": [{"id": "show_cat_1", "title": "15 Categories यहाँ हैं"}]}]}}})
            
        else:
            send_payload(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Welcome"}, "body": {"text": "NearMe में स्वागत है:"}, "action": {"button": "Start", "sections": [{"title": "Role", "rows": [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}]}]}}})
    except: pass
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000)
    
