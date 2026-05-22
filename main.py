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
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']
        
        # 1. यदि यूजर ने बटन क्लिक किया
        if 'interactive' in msg:
            sel_id = msg['interactive']['list_reply']['id']
            
            # [cite_start]कैटेगरी लिस्ट (रिपोर्ट के अनुसार) [cite: 20-33]
            if sel_id == "main_menu":
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                    "type": "list", "header": {"type": "text", "text": "NearMe Categories"},
                    "body": {"text": "सेवा चुनें:"},
                    "action": {"button": "Menu", "sections": [
                        {"title": "सेवाएं", "rows": [
                            {"id": "cat_home", "title": "निर्माण/होम"},
                            {"id": "cat_auto", "title": "ऑटोमोबाइल"},
                            {"id": "cat_food", "title": "खाद्य/आतिथ्य"},
                            {"id": "cat_retail", "title": "दैनिक जरूरतें"},
                            {"id": "cat_health", "title": "स्वास्थ्य/शिक्षा"},
                            {"id": "cat_prof", "title": "प्रोफेशनल"}
                        ]}
                    ]}
                }})
            
            # सब-कैटेगरी लॉजिक (उदा: दैनिक जरूरतें -> किराना)
            elif sel_id == "cat_retail":
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                    "type": "list", "header": {"type": "text", "text": "दैनिक जरूरतें"},
                    "body": {"text": "सब-कैटेगरी चुनें:"},
                    "action": {"button": "Select", "sections": [{"title": "Items", "rows": [{"id": "final_req", "title": "किराना"}, {"id": "final_req", "title": "इलेक्ट्रॉनिक्स"}]}]}
                }})
                
            elif sel_id == "final_req":
                send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "text": {"body": "अपनी मांग (Requirement) लिखें:"}})

        # 2. डिफॉल्ट स्वागत संदेश
        else:
            send_msg(sender, {"messaging_product": "whatsapp", "to": sender, "type": "interactive", "interactive": {
                "type": "list", "header": {"type": "text", "text": "Welcome"},
                "body": {"text": "NearMe में स्वागत है, अपना विकल्प चुनें:"},
                "action": {"button": "Start", "sections": [{"title": "Role", "rows": [{"id": "main_menu", "title": "Buyer"}, {"id": "main_menu", "title": "Seller"}]}]}
            }})
    except: pass
    return "OK", 200

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
    
