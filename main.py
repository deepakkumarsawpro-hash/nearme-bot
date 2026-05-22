import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Credentials
VERIFY_TOKEN = "my_secret_token_123"
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

# Simple memory storage
user_context = {}

def send_interactive_menu(to, title, body, options):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp", "recipient_type": "individual", "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": title},
            "body": {"text": body},
            "action": {"button": "यहाँ क्लिक करें", "sections": [{"rows": options}]}
        }
    }
    requests.post(url, json=payload, headers=headers)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge") if request.args.get("hub.verify_token") == VERIFY_TOKEN else "Fail"
    
    data = request.get_json()
    try:
        msg_data = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender_id = msg_data['from']
        
        # 1. Interactive Menu Selection Handle karna
        if 'interactive' in msg_data:
            selected_id = msg_data['interactive']['list_reply']['id']
            
            if selected_id in ["buyer", "seller"]:
                user_context[sender_id] = {'role': selected_id}
                send_interactive_menu(sender_id, "Location", "अपनी लोकेशन चुनें:", 
                                     [{"id": "ranchi", "title": "Ranchi"}, {"id": "bokaro", "title": "Bokaro"}])
            
            elif selected_id in ["ranchi", "bokaro"]:
                user_context[sender_id]['location'] = selected_id
                send_interactive_menu(sender_id, "Categories", "कैटेगरी चुनें:", 
                                     [{"id": "kirana", "title": "किराना"}, {"id": "repair", "title": "रिपेयर"}])
            
            elif selected_id == "kirana":
                user_context[sender_id]['category'] = "kirana"
                send_interactive_menu(sender_id, "Sub-Category", "सब्जी या डेयरी?", 
                                     [{"id": "sabji", "title": "सब्जी"}, {"id": "dairy", "title": "डेयरी"}])
            
            elif selected_id in ["sabji", "dairy"]:
                user_context[sender_id]['subcat'] = selected_id
                # Yahan hum user ko last step ke liye message bhej rahe hain
                requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages", 
                              json={"messaging_product": "whatsapp", "to": sender_id, "text": {"body": "कृपया अपनी डिमांड या सवाल यहाँ लिखें:"}},
                              headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"})
        
        # 2. Open Text Input handle karna (Last Step)
        elif 'text' in msg_data and sender_id in user_context:
            user_text = msg_data['text']['body']
            # Yahan aap data database mein save kar sakte hain
            requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages", 
                          json={"messaging_product": "whatsapp", "to": sender_id, "text": {"body": f"धन्यवाद! हमें आपकी रिक्वेस्ट मिल गई है: {user_text}"}},
                          headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"})
            del user_context[sender_id] # Flow khatam

        else:
            send_interactive_menu(sender_id, "Welcome", "आप कौन हैं?", 
                                 [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}])
            
    except Exception as e: print(e)
    return "OK", 200

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
    
