import os
from flask import Flask, request
import requests

app = Flask(__name__)

# =====================================================
# WHATSAPP CONFIG
# =====================================================

PHONE_ID = "YOUR_PHONE_NUMBER_ID"

TOKEN = "YOUR_PERMANENT_TOKEN"

VERIFY_TOKEN = "nearmeverify"

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
        "subs": [
            "मिस्त्री",
            "प्लंबर"
        ]
    },

    "auto": {
        "title": "ऑटो",
        "subs": [
            "मैकेनिक"
        ]
    },

    "food": {
        "title": "भोजन",
        "subs": [
            "रेस्टोरेंट"
        ]
    },

    "retail": {
        "title": "खुदरा",
        "subs": [
            "किराना"
        ]
    },

    "health": {
        "title": "स्वास्थ्य",
        "subs": [
            "डॉक्टर"
        ]
    },

    "personal": {
        "title": "व्यक्तिगत",
        "subs": [
            "सैलून"
        ]
    },

    "agriculture": {
        "title": "कृषि",
        "subs": [
            "बीज"
        ]
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

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    print(response.text)

# =====================================================
# SIMPLE TEXT
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
# BUTTON MESSAGE
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
# LIST MESSAGE
# =====================================================

def send_list(to, body_text, rows):

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
                "text": body_text
            },

            "footer": {
                "text": "कृपया विकल्प चुनें"
            },

            "action": {
                "button": "Open List",

                "sections": [
                    {
                        "title": "Available Options",
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

    if mode and token:

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

            changes = data["entry"][0]["changes"][0]

            value = changes["value"]

            messages = value.get("messages")

            if not messages:
                return "OK", 200

            msg = messages[0]

            sender = msg["from"]

            # =====================================================
            # START BOT
            # =====================================================

            if "text" in msg:

                text = msg["text"]["body"].lower()

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
            # BUTTON CLICK
            # =====================================================

            if "interactive" in msg:

                interactive = msg["interactive"]

                # =====================================================
                # BUTTON REPLY
                # =====================================================

                if interactive["type"] == "button_reply":

                    button_id = interactive["button_reply"]["id"]

                    session = user_sessions.get(sender, {})

                    # =====================================================
                    # ROLE SELECT
                    # =====================================================

                    if session.get("step") == "role":

                        session["role"] = button_id

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

                            "📍 कृपया दूरी चुनें:",

                            buttons
                        )

                        return "OK", 200

                    # =====================================================
                    # DISTANCE SELECT
                    # =====================================================

                    elif session.get("step") == "distance":

                        session["distance"] = button_id

                        session["step"] = "location"

                        send_text(

                            sender,

                            "📍 अब WhatsApp से अपनी लोकेशन Share करें"
                        )

                        return "OK", 200

                    # =====================================================
                    # SUBCATEGORY SELECT
                    # =====================================================

                    elif session.get("step") == "subcategory":

                        session["subcategory"] = button_id

                        session["step"] = "confirm"

                        buttons = [

                            {
                                "type": "reply",
                                "reply": {
                                    "id": "submit",
                                    "title": "Submit"
                                }
                            },

                            {
                                "type": "reply",
                                "reply": {
                                    "id": "restart",
                                    "title": "Restart"
                                }
                            }
                        ]

                        send_buttons(

                            sender,

                            "✅ जानकारी पूरी हो गई।\n\n"
                            "Submit करने के लिए नीचे क्लिक करें।",

                            buttons
                        )

                        return "OK", 200

                    # =====================================================
                    # FINAL SUBMIT
                    # =====================================================

                    elif session.get("step") == "confirm":

                        if button_id == "submit":

                            print("FINAL USER DATA =")
                            print(session)

                            send_text(

                                sender,

                                "🎉 धन्यवाद!\n\n"
                                "आपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है।\n\n"
                                "हमारी टीम जल्द ही आपसे संपर्क करेगी।"
                            )

                            del user_sessions[sender]

                        else:

                            del user_sessions[sender]

                            send_text(
                                sender,
                                "♻️ Restart हो गया।\n\nHi भेजें।"
                            )

                        return "OK", 200

                # =====================================================
                # LIST REPLY
                # =====================================================

                elif interactive["type"] == "list_reply":

                    row_id = interactive["list_reply"]["id"]

                    session = user_sessions.get(sender, {})

                    # =====================================================
                    # CATEGORY SELECT
                    # =====================================================

                    if session.get("step") == "category":

                        session["category"] = row_id

                        session["step"] = "subcategory"

                        subcategories = categories[row_id]["subs"]

                        buttons = []

                        for sub in subcategories:

                            buttons.append({

                                "type": "reply",

                                "reply": {
                                    "id": sub,
                                    "title": sub[:20]
                                }
                            })

                        send_buttons(

                            sender,

                            "🛠 उप-श्रेणी चुनें:",

                            buttons[:3]
                        )

                        return "OK", 200

            # =====================================================
            # LOCATION RECEIVED
            # =====================================================

            if "location" in msg:

                session = user_sessions.get(sender, {})

                if session.get("step") == "location":

                    session["location"] = msg["location"]

                    session["step"] = "category"

                    rows = []

                    for key, val in categories.items():

                        rows.append({

                            "id": key,

                            "title": val["title"],

                            "description": "Click to select"
                        })

                    send_list(

                        sender,

                        "📂 कृपया श्रेणी चुनें:",

                        rows
                    )

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
# RUN SERVER
# =====================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
