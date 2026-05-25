import os
from flask import Flask, request
import requests

app = Flask(__name__)

# =====================================================
# WHATSAPP CONFIG
# =====================================================

PHONE_ID = "YOUR_PHONE_ID"

TOKEN = "YOUR_ACCESS_TOKEN"

VERIFY_TOKEN = "verifytoken"

# =====================================================
# USER SESSIONS
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

def send_message(payload):

    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

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

    send_message(payload)

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

    send_message(payload)

# =====================================================
# SEND LIST
# =====================================================

def send_list(to, rows):

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
                "text": "कृपया श्रेणी चुनें"
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

    send_message(payload)

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
# MAIN WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])

def webhook():

    data = request.get_json()

    try:

        if "entry" in data:

            msg = data["entry"][0]["changes"][0]["value"] \
            .get("messages", [{}])[0]

            sender = msg.get("from")

            if not sender:
                return "OK", 200

            # =====================================================
            # START
            # =====================================================

            if "text" in msg:

                text = msg["text"]["body"].lower()

                # START BOT

                if text in ["hi", "hello", "start"]:

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

            # =====================================================
            # BUTTON REPLY
            # =====================================================

            if "interactive" in msg:

                interactive = msg["interactive"]

                # =====================================================
                # BUTTON CLICK
                # =====================================================

                if interactive["type"] == "button_reply":

                    button_id = interactive["button_reply"]["id"]

                    session = user_sessions.get(sender)

                    # ================================================
                    # ROLE
                    # ================================================

                    if session["step"] == "role":

                        session["role"] = button_id

                        # CUSTOMER

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

                                "📍 आप कितनी दूरी में सेवा चाहते हैं?",

                                buttons
                            )

                        # SELLER

                        else:

                            session["step"] = "shop_name"

                            send_text(

                                sender,

                                "🏪 कृपया दुकान / सेवा का नाम लिखें"
                            )

                        return "OK", 200

                    # ================================================
                    # DISTANCE
                    # ================================================

                    elif session["step"] == "distance":

                        session["distance"] = button_id

                        session["step"] = "location"

                        send_text(

                            sender,

                            "📍 अब अपनी WhatsApp लोकेशन Share करें"
                        )

                        return "OK", 200

                    # ================================================
                    # SUBCATEGORY
                    # ================================================

                    elif session["step"] == "subcategory":

                        session["subcategory"] = button_id

                        send_text(

                            sender,

                            "✅ धन्यवाद!\n\n"
                            "आपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है।"
                        )

                        print(session)

                        del user_sessions[sender]

                        return "OK", 200

                # =====================================================
                # LIST CLICK
                # =====================================================

                elif interactive["type"] == "list_reply":

                    row_id = interactive["list_reply"]["id"]

                    session = user_sessions.get(sender)

                    # CATEGORY

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

                        return "OK", 200

            # =====================================================
            # LOCATION
            # =====================================================

            if "location" in msg:

                session = user_sessions.get(sender)

                # CUSTOMER LOCATION

                if session["step"] == "location":

                    session["location"] = msg["location"]

                    session["step"] = "category"

                    rows = []

                    for key, val in categories.items():

                        rows.append({

                            "id": key,

                            "title": val["title"]
                        })

                    send_list(sender, rows)

                    return "OK", 200

            # =====================================================
            # SELLER SHOP NAME
            # =====================================================

            if "text" in msg:

                session = user_sessions.get(sender)

                if session and session["step"] == "shop_name":

                    session["shop_name"] = msg["text"]["body"]

                    session["step"] = "seller_location"

                    send_text(

                        sender,

                        "📍 अब अपनी दुकान की लोकेशन Share करें"
                    )

                    return "OK", 200

            # =====================================================
            # SELLER LOCATION
            # =====================================================

            if "location" in msg:

                session = user_sessions.get(sender)

                if session and session["step"] == "seller_location":

                    session["location"] = msg["location"]

                    session["step"] = "category"

                    rows = []

                    for key, val in categories.items():

                        rows.append({

                            "id": key,

                            "title": val["title"]
                        })

                    send_list(sender, rows)

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
