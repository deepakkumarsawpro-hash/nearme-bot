import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Aapke credentials
VERIFY_TOKEN = "my_secret_token_123" 
PHONE_NUMBER_ID = "1190419820813262"
ACCESS_TOKEN = "EAAMEDcGznz0BRpQd1elkurZAqtkH7ksFYX4fOJr3SJZAbxZAgWANWdG03eydQYkl5v53KGnuHxbrwVnqcvyrWNMYHuyJZAsaBJ1JZCNRoHxl0A00BJamqHU4yQszp6x4TBIyRRsQUCtIxL1604mSufsQo1rdHszltEOiBRyv7GVj0KXfs82YYrfwYvifXOAfwJQZDZD"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Message processing
        try:
            # WhatsApp data structure se message nikaalna
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                message = data['entry'][0]['changes'][0]['value']['messages'][0]
                sender_id = message['from']
                text = message['text']['body']
                
                # Auto-reply function call
                send_reply(sender_id, f"Namaste! Mujhe aapka message mila: '{text}'")
        except Exception as e:
            print(f"Error: {e}")
            
        return "OK", 200

def send_reply(to, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message_text}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Reply Status: {response.status_code}") # Log mein check karne ke liye

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
