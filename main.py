import os
from flask import Flask, request
import requests

app = Flask(__name__)

# -----------------------------------
# WHATSAPP API CONFIG
# -----------------------------------

PHONE_ID = "1060745180462931"

TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

VERIFY_TOKEN = "my_secret_token_123"

# -----------------------------------
# USER SESSIONS
# -----------------------------------

user_sessions = {}

# -----------------------------------
# CATEGORY DATA
# -----------------------------------

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
    },
    "personal": {
        "title": "व्यक्तिगत",
        "subs": ["सैलून"]
    },
    "agriculture": {
        "title": "कृषि",
        "subs": ["बीज"]
    }
}

# -----------------------------------
# SEND MESSAGE FUNCTION
# -----------------------------------

def send_msg(payload):

    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

# -----------------------------------
# WEBHOOK VERIFY
# -----------------------------------

@app.route("/webhook", methods=["GET"])

def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

    return "Verification failed", 403

# -----------------------------------
# MAIN WEBHOOK
# -----------------------------------

@app.route("/webhook", methods=["POST"])

def webhook():

    data = request.get_json()

    try:

        if "entry" in data:

            msg = data["entry"][0]["changes"][0]["value"].get("messages", [{}])[0]

            sender = msg.get("from")

            if not sender:
                return "OK", 200

            # -----------------------------------
            # START MESSAGE
            # -----------------------------------

            if "text" in msg:

                text = msg["text"]["body"].lower()

                if text in ["hi", "hello", "start"]:

                    user_sessions[sender] = {
                        "step": "role"
                    }

                    send_msg({
                        "messaging_product": "whatsapp",
                        "to": sender,
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {
                                "text":
                                "नमस्ते 🙏\n\nNear Me Marketplace में आपका स्वागत है।\n\nकृपया अपना रोल चुनें:"
                            },
                            "action": {
                                "buttons": [
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
                            }
                        }
                    })

            # -----------------------------------
            # ROLE SELECT
            # -----------------------------------

            elif "interactive" in msg and \
            "button_reply" in msg["interactive"]:

                reply_id = msg["interactive"]["button_reply"]["id"]

                session = user_sessions.get(sender, {})

                # CUSTOMER / SELLER

                if session.get("step") == "role":

                    session["role"] = reply_id

                    # CUSTOMER FLOW

                    if reply_id == "customer":

                        session["step"] = "distance"

                        send_msg({
                            "messaging_product": "whatsapp",
                            "to": sender,
                            "type": "text",
                            "text": {
                                "body":
                                "कृपया दूरी दर्ज करें।\n\nउदाहरण: 5 KM"
                            }
                        })

                    # SELLER FLOW

                    else:

                        session["step"] = "shop_name"

                        send_msg({
                            "messaging_product": "whatsapp",
                            "to": sender,
                            "type": "text",
                            "text": {
                                "body":
                                "कृपया दुकान का नाम दर्ज करें"
                            }
                        })

            # -----------------------------------
            # CUSTOMER DISTANCE
            # -----------------------------------

            elif "text" in msg and \
            user_sessions.get(sender, {}).get("step") == "distance":

                user_sessions[sender]["distance"] = msg["text"]["body"]

                user_sessions[sender]["step"] = "location"

                send_msg({
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "text",
                    "text": {
                        "body":
                        "कृपया अपनी लोकेशन Share करें"
                    }
                })

            # -----------------------------------
            # SELLER SHOP NAME
            # -----------------------------------

            elif "text" in msg and \
            user_sessions.get(sender, {}).get("step") == "shop_name":

                user_sessions[sender]["shop_name"] = msg["text"]["body"]

                user_sessions[sender]["step"] = "category"

                rows = []

                for key, val in categories.items():

                    rows.append({
                        "id": key,
                        "title": val["title"]
                    })

                send_msg({
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {
                            "type": "text",
                            "text": "श्रेणियाँ"
                        },
                        "body": {
                            "text": "कृपया श्रेणी चुनें"
                        },
                        "action": {
                            "button": "श्रेणी चुनें",
                            "sections": [
                                {
                                    "title": "Near Me Marketplace",
                                    "rows": rows
                                }
                            ]
                        }
                    }
                })

            # -----------------------------------
            # LOCATION RECEIVED
            # -----------------------------------

            elif "location" in msg and \
            user_sessions.get(sender, {}).get("step") == "location":

                user_sessions[sender]["location"] = msg["location"]

                user_sessions[sender]["step"] = "category"

                rows = []

                for key, val in categories.items():

                    rows.append({
                        "id": key,
                        "title": val["title"]
                    })

                send_msg({
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {
                            "type": "text",
                            "text": "श्रेणियाँ"
                        },
                        "body": {
                            "text": "कृपया श्रेणी चुनें"
                        },
                        "action": {
                            "button": "श्रेणी चुनें",
                            "sections": [
                                {
                                    "title": "Near Me Marketplace",
                                    "rows": rows
                                }
                            ]
                        }
                    }
                })

            # -----------------------------------
            # CATEGORY SELECT
            # -----------------------------------

            elif "interactive" in msg and \
            "list_reply" in msg["interactive"]:

                selected = msg["interactive"]["list_reply"]["id"]

                session = user_sessions.get(sender, {})

                # CATEGORY

                if session.get("step") == "category":

                    session["category"] = selected

                    session["step"] = "subcategory"

                    buttons = []

                    for sub in categories[selected]["subs"]:

                        buttons.append({
                            "type": "reply",
                            "reply": {
                                "id": sub,
                                "title": sub[:20]
                            }
                        })

                    send_msg({
                        "messaging_product": "whatsapp",
                        "to": sender,
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {
                                "text":
                                "उप-श्रेणी चुनें"
                            },
                            "action": {
                                "buttons": buttons[:3]
                            }
                        }
                    })

            # -----------------------------------
            # SUBCATEGORY SELECT
            # -----------------------------------

            elif "interactive" in msg and \
            "button_reply" in msg["interactive"] and \
            user_sessions.get(sender, {}).get("step") == "subcategory":

                sub = msg["interactive"]["button_reply"]["id"]

                user_sessions[sender]["subcategory"] = sub

                user_sessions[sender]["step"] = "other"

                send_msg({
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "text",
                    "text": {
                        "body":
                        "यदि अन्य जानकारी देना चाहते हैं तो लिखें"
                    }
                })

            # -----------------------------------
            # OTHER INFO
            # -----------------------------------

            elif "text" in msg and \
            user_sessions.get(sender, {}).get("step") == "other":

                user_sessions[sender]["other"] = msg["text"]["body"]

                user_sessions[sender]["step"] = "whatsapp"

                send_msg({
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "text",
                    "text": {
                        "body":
                        "कृपया अपना WhatsApp नंबर दर्ज करें"
                    }
                })

            # -----------------------------------
            # FINAL SUBMIT
            # -----------------------------------

            elif "text" in msg and \
            user_sessions.get(sender, {}).get("step") == "whatsapp":

                user_sessions[sender]["whatsapp"] = msg["text"]["body"]

                print("USER DATA =", user_sessions[sender])

                send_msg({
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "text",
                    "text": {
                        "body":
                        "धन्यवाद 🙏\n\nआपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है।\n\nहमारी टीम जल्द ही आपसे संपर्क करेगी।"
                    }
                })

                del user_sessions[sender]

    except Exception as e:

        print("ERROR =", e)

    return "OK", 200

# -----------------------------------
# RUN SERVER
# -----------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(host="0.0.0.0", port=port)
