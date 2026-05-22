import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "my_secret_token_123" 
PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                message = data['entry'][0]['changes'][0]['value']['messages'][0]
                sender_id = message['from']
                text = message['text']['body'].lower() # Yahan lowercase kiya gaya hai
                
                # --- Custom Reply Logic ---
                if "hi" in text or "hello" in text:
                    reply = "Namaste! Main aapka AI assistant hoon. Main aapki kya madad kar sakta hoon?"
                elif "kaise ho" in text:
                    reply = "Main ek bot hoon, bilkul mast! Aap bataiye?"
                elif "price" in text:
                    reply = "Hamari services ka price 500 rupaye se shuru hota hai."
                else:
                    reply = f"Mujhe aapka message mila: '{text}'. Main abhi seekh raha hoon!"
                
                send_reply(sender_id, reply)
        except Exception as e:
            print(f"Error: {e}")
        return "OK", 200

def send_reply(to, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": message_text}}
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
