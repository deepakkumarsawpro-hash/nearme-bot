import os
import requests
from flask import Flask, request

app = Flask(__name__)

PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

# State storage: {sender_id: {'step': '...', 'category': '...'}}
user_sessions = {}

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
    if request.method == 'GET': return request.args.get("hub.challenge")
    
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']
        
        # 1. Menu Selection Step
        if 'interactive' in msg:
            sel_id = msg['interactive']['list_reply']['id']
            
            if sel_id in ["buyer", "seller"]:
                user_sessions[sender] = {'step': 'location'}
                # Google Maps link bhejna (Ya Location Request button)
                requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages",
                    json={"messaging_product": "whatsapp", "to": sender, "text": {"body": "अपनी लोकेशन शेयर करें या मैप लिंक पर क्लिक करें: https://maps.google.com"}},
                    headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"})
            
            elif sel_id == "cat_1": # Example Category
                user_sessions[sender] = {'step': 'subcat', 'cat': 'kirana'}
                send_menu(sender, "Sub-Category", "सब-कैटेगरी चुनें:", [{"id": "sabji", "title": "सब्जी"}, {"id": "dairy", "title": "डेयरी"}])
            
            elif sel_id == "sabji":
                user_sessions[sender]['step'] = 'final'
                requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages",
                    json={"messaging_product": "whatsapp", "to": sender, "text": {"body": "अपनी मांग (Requirement) यहाँ लिखें:"}},
                    headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"})

        # 2. Location ya Text Input ke baad ka step
        elif 'location' in msg or (sender in user_sessions and user_sessions[sender]['step'] == 'location'):
            user_sessions[sender] = {'step': 'categories'}
            send_menu(sender, "Categories", "15+ सेवाएँ चुनें:", [{"id": "cat_1", "title": "किराना/सब्जी"}, {"id": "cat_2", "title": "होटल/ढाबा"}])
        
        # 3. Default Welcome
        else:
            send_menu(sender, "Welcome", "नमस्कार! NearMe में स्वागत है।", [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}])
    except: pass
    return "OK", 200

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
    
