import os
from flask import Flask, request
import requests

app = Flask(__name__)

PHONE_NUMBER_ID = "1060745180462931"
ACCESS_TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"
VERIFY_TOKEN = "my_secret_token_123"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN: return request.args.get("hub.challenge")
        return "Failed", 403
    
    data = request.get_json()
    if 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    msg = value['messages'][0]
                    sender = msg['from']
                    text = ""
                    if 'text' in msg: text = msg['text']['body'].lower()
                    elif 'interactive' in msg:
                        # LIST aur BUTTON dono handle karne ke liye
                        if 'button_reply' in msg['interactive']: text = msg['interactive']['button_reply']['id'].lower()
                        elif 'list_reply' in msg['interactive']: text = msg['interactive']['list_reply']['id'].lower()
                    elif 'location' in msg: text = "step_location_received"
                    
                    process_step(sender, text)
    return "OK", 200

def send_msg(to, payload):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

def process_step(to, text):
    # Step 0: Welcome
    if "hi" in text or "hello" in text:
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "button", "body": {"text": "Namaste! NearMe mein swagat hai. Aap kya hain?"},
            "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}, {"type": "reply", "reply": {"id": "customer", "title": "ग्राहक"}}]}}})

    # Step 1: Location
    elif text == "sale_service":
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Great! Pin icon par click karke apni location share karein."}})

    # Step 2: Main Categories (List)
    elif text == "step_location_received":
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "list", "header": {"type": "text", "text": "Main Categories"}, "body": {"text": "Location mil gayi! Category chunein:"},
            "action": {"button": "Categories", "sections": [{"title": "Select One", "rows": [
                {"id": "cat_1", "title": "1. Construction"}, {"id": "cat_2", "title": "2. Automotive"},
                {"id": "cat_3", "title": "3. Food"}, {"id": "cat_4", "title": "4. Retail"},
                {"id": "cat_5", "title": "5. Healthcare"}, {"id": "cat_6", "title": "6. Personal"}, {"id": "cat_7", "title": "7. Agriculture"}]}]}}})

    # Step 3: Sub-Categories (Buttons) - Example for Cat 1 (Construction)
    elif text == "cat_1":
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "button", "body": {"text": "Construction Sub-Category:"},
            "action": {"buttons": [{"type": "reply", "reply": {"id": "sub_mason", "title": "Mason"}}, {"type": "reply", "reply": {"id": "sub_plumber", "title": "Plumber"}}]}}})

    # Step 4: Keywords & Open Text
    elif text.startswith("sub_"):
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Keywords: Raj Mistri, Building, Cement. \n\nAb apna specific kaam type karke bhejein:"}})

    # Final Step: Handle Open Text
    elif len(text) > 3 and not text.startswith(("cat_", "sub_", "step_")):
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Aapki request: '" + text + "' mil gayi hai. Hum aapko jald contact karenge!"}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def process_step(to, text):
    # Step 0: Welcome
    if "hi" in text or "hello" in text:
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "button", "body": {"text": "Namaste! NearMe mein swagat hai. Aap kya hain?"},
            "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}, {"type": "reply", "reply": {"id": "customer", "title": "ग्राहक"}}]}}})

    # Step 1: Location & Categories
    elif text == "sale_service":
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Great! Pin icon par click karke location share karein."}})
    
    elif text == "step_location_received":
        # (Yahan wahi 7 Main Categories wali list rahegi jo pichle code mein thi)
        pass 

    # Step 2: Sub-Category select hone par Keywords dikhana
    elif text == "sub_mason": # Example: Mason select hua
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "list", "header": {"type": "text", "text": "Keywords Chunein"}, "body": {"text": "Mason ke liye keywords chunein:"},
            "action": {"button": "Keywords", "sections": [{"title": "Keywords", "rows": [
                {"id": "kw_raj", "title": "Raj Mistri"}, {"id": "kw_cement", "title": "Cement Work"}]}]}}})

    # Step 3: Keywords select hone par WhatsApp Number maangna
    elif text.startswith("kw_"):
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Keywords select ho gaye! \n\nAb apna WhatsApp Number type karke bhejein jahan hum aapse contact kar sakein:"}})

    # Step 4: Final Step (Number capture)
    elif len(text) >= 10 and text.isdigit() and not text.startswith(("cat_", "sub_", "kw_")):
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Dhanyavad! Apka number " + text + " save ho gaya hai. Hum jald aapse sampark karenge."}})
        
