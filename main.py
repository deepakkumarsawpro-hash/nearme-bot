import os
import requests

from flask import Flask, request

app = Flask(__name__)

# =====================================================
# CONFIG
# =====================================================

PHONE_ID = "1060745180462931"

TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

VERIFY_TOKEN = "my_secret_token_123"

# =====================================================
# SESSION STORAGE
# =====================================================

user_sessions = {}

# =====================================================
# CATEGORY DATA
# =====================================================

categories = {

    "construction": {
        "title": "निर्माण",
        "subs": ["मिस्त्री", "प्लंबर"]
    },

    "auto": {
        "title": "ऑटो",
        "subs": ["मैकेनिक"]
    },

    "food": {
        "title": "भोजन",
        "subs": ["रेस्टोरेंट"]
    },

    "retail": {
        "title": "खुदरा",
        "subs": ["किराना"]
    },

    "health": {
        "title": "स्वास्थ्य",
        "subs": ["डॉक्टर"]
    }
}

# =====================================================
# SEND MESSAGE
# =====================================================

def send(payload):

    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    print(response.text)

# =====================================================
# SEND TEXT
# =====================================================

def send_text(to, text):

    payload = {

        "messaging_product": "whatsapp",

        "to": to,

        "type": "text",

        "text": {
            "body": text
        }
    }

    send(payload)

# =====================================================
# SEND BUTTONS
# =====================================================

def send_buttons(to, text, buttons):

    payload = {

        "messaging_product": "whatsapp",

        "to": to,

        "type": "interactive",

        "interactive": {

            "type": "button",

            "body": {
                "text": text
            },

            "action": {
                "buttons": buttons
            }
        }
    }

    send(payload)

# =====================================================
# SEND LIST
# =====================================================

def send_list(to):

    rows = []

    for key, value in categories.items():

        rows.append({

            "id": key,

            "title": value["title"]

        })

    payload = {

        "messaging_product": "whatsapp",

        "to": to,

        "type": "interactive",

        "interactive": {

            "type": "list",

            "header": {
                "type": "text",
                "text": "Near Me Marketplace"
            },

            "body": {
                "text": "📂 कृपया श्रेणी चुनें"
            },

            "action": {

                "button": "श्रेणियाँ",

                "sections": [

                    {
                        "title": "Available Categories",
                        "rows": rows
                    }
                ]
            }
        }
    }

    send(payload)

# =====================================================
# VERIFY WEBHOOK
# =====================================================

@app.route("/webhook", methods=["GET"])

def verify():

    mode = request.args.get("hub.mode")

    token = request.args.get("hub.verify_token")

    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        return challenge, 200

    return "Verification failed", 403

# =====================================================
# WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])

def webhook():

    try:

        data = request.get_json()

        print(data)

        if "entry" not in data:
            return "OK", 200

        changes = data["entry"][0]["changes"][0]

        value = changes["value"]

        messages = value.get("messages")

        if not messages:
            return "OK", 200

        msg = messages[0]

        sender = msg.get("from")

        if not sender:
            return "OK", 200

        # =================================================
        # AUTO START
        # =================================================

        if sender not in user_sessions:

            user_sessions[sender] = {
                "step": "role"
            }

            buttons = [

                {
                    "type": "reply",

                    "reply": {
                        "id": "customer",
                        "title": "ग्राहक"
                    }
                },

                {
                    "type": "reply",

                    "reply": {
                        "id": "seller",
                        "title": "सेवा प्रदाता"
                    }
                }
            ]

            send_buttons(

                sender,

                "🙏 नमस्ते\n\n"
                "Near Me Marketplace में आपका स्वागत है।\n\n"
                "कृपया अपना रोल चुनें:",

                buttons
            )

            return "OK", 200

        session = user_sessions[sender]

        # =================================================
        # BUTTON REPLY
        # =================================================

        if "interactive" in msg:

            interactive = msg["interactive"]

            # =============================================
            # BUTTON
            # =============================================

            if interactive["type"] == "button_reply":

                button_id = interactive["button_reply"]["id"]

                # ROLE

                if session["step"] == "role":

                    session["role"] = button_id

                    # CUSTOMER FLOW

                    if button_id == "customer":

                        session["step"] = "distance"

                        buttons = [

                            {
                                "type": "reply",

                                "reply": {
                                    "id": "1_km",
                                    "title": "1 KM"
                                }
                            },

                            {
                                "type": "reply",

                                "reply": {
                                    "id": "5_km",
                                    "title": "5 KM"
                                }
                            },

                            {
                                "type": "reply",

                                "reply": {
                                    "id": "10_km",
                                    "title": "10 KM"
                                }
                            }
                        ]

                        send_buttons(

                            sender,

                            "📍 कितनी दूरी में सेवा चाहिए?",

                            buttons
                        )

                    # SELLER FLOW

                    else:

                        session["step"] = "shop_name"

                        send_text(

                            sender,

                            "🏪 कृपया दुकान / सेवा का नाम लिखें"
                        )

                # DISTANCE

                elif session["step"] == "distance":

                    session["distance"] = button_id

                    session["step"] = "location"

                    send_text(

                        sender,

                        "📍 अब अपनी लोकेशन Share करें"
                    )

                # SUBCATEGORY

                elif session["step"] == "subcategory":

                    session["subcategory"] = button_id

                    session["step"] = "whatsapp"

                    send_text(

                        sender,

                        "📱 अपना WhatsApp नंबर लिखें"
                    )

            # =============================================
            # LIST
            # =============================================

            elif interactive["type"] == "list_reply":

                row_id = interactive["list_reply"]["id"]

                if session["step"] == "category":

                    session["category"] = row_id

                    session["step"] = "subcategory"

                    subs = categories[row_id]["subs"]

                    buttons = []

                    for sub in subs:

                        buttons.append({

                            "type": "reply",

                            "reply": {
                                "id": sub,
                                "title": sub
                            }
                        })

                    send_buttons(

                        sender,

                        "🛠 उप-श्रेणी चुनें",

                        buttons[:3]
                    )

        # =================================================
        # LOCATION
        # =================================================

        elif "location" in msg:

            # CUSTOMER LOCATION

            if session["step"] == "location":

                session["location"] = msg["location"]

                session["step"] = "category"

                send_list(sender)

            # SELLER LOCATION

            elif session["step"] == "seller_location":

                session["location"] = msg["location"]

                session["step"] = "category"

                send_list(sender)

        # =================================================
        # TEXT MESSAGE
        # =================================================

        elif "text" in msg:

            text = msg["text"]["body"]

            # SELLER SHOP NAME

            if session["step"] == "shop_name":

                session["shop_name"] = text

                session["step"] = "seller_location"

                send_text(

                    sender,

                    "📍 अब दुकान की लोकेशन Share करें"
                )

            # WHATSAPP NUMBER

            elif session["step"] == "whatsapp":

                session["whatsapp"] = text

                print("FINAL DATA =")
                print(session)

                send_text(

                    sender,

                    "✅ धन्यवाद 🙏\n\n"
                    "आपकी जानकारी सफलतापूर्वक दर्ज हो गई है।"
                )

                del user_sessions[sender]

        return "OK", 200

    except Exception as e:

        print("ERROR =", e)

        return "OK", 200

# =====================================================
# HOME
# =====================================================

@app.route("/")

def home():

    return "Near Me Marketplace Bot Running"

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
