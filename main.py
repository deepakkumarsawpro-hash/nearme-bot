import os
import requests
from flask import Flask, request

app = Flask(__name__)

# =====================================================
# WHATSAPP CONFIG
# =====================================================

PHONE_ID = "1060745180462931"

TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"

VERIFY_TOKEN = "my_secret_token_123"

# =====================================================
# USER SESSION
# =====================================================

user_sessions = {}

# =====================================================
# FULL CATEGORY DATA
# =====================================================

categories = {

    "construction": {

        "title": "Construction",

        "subs": {

            "Mason":
            "नींव, ईंट जुड़ाई, प्लास्टर, टाइल्स",

            "Architect":
            "नक्शा, इंटीरियर डिजाइन, 3D व्यू",

            "Plumber":
            "पाइप लीकेज, मोटर, टैप फिटिंग",

            "Electrician":
            "वायरिंग, शॉर्ट-सर्किट, इनवर्टर, बोर्ड रिपेयर",

            "Carpenter":
            "दरवाजा, खिड़की, बेड/अलमारी फर्नीचर",

            "Paint & Hardware":
            "वॉल पुट्टी, पेंटिंग, हार्डवेयर सामान"
        }
    },

    "automotive": {

        "title": "Automotive",

        "subs": {

            "Mechanic":
            "इंजन रिपेयर, सर्विसिंग, ब्रेक, क्लच",

            "Denting/Painting":
            "डेंट हटाना, पेंटिंग, पॉलिशिंग",

            "Spare Parts":
            "ओरिजिनल पार्ट्स, लुब्रिकेंट्स",

            "Washing":
            "फोम वॉश, इंटरनल क्लीनिंग, वैक्सिंग",

            "Batteries":
            "बैटरी बदलना, चार्जिंग"
        }
    },

    "food": {

        "title": "Food",

        "subs": {

            "Restaurants":
            "वेज, नॉन-वेज, थाली, पार्सल",

            "Tiffin":
            "मंथली मेस, होम मेड खाना",

            "Fast Food":
            "पिज्जा, बर्गर, मोमोज, चाउमीन",

            "Sweets/Bakery":
            "केक, मिठाई",

            "Catering":
            "शादी/पार्टी ऑर्डर",

            "Grocery":
            "दैनिक राशन सामग्री"
        }
    },

    "retail": {

        "title": "Retail",

        "subs": {

            "Clothing":
            "मेंस, वुमेंस, किड्स वियर",

            "Electronics":
            "टीवी, फ्रिज, वाशिंग मशीन",

            "Pharmacy":
            "दवाइयां, स्वास्थ्य सप्लीमेंट",

            "Footwear":
            "जूते, चप्पल",

            "Stationery":
            "कॉपी, किताब, ऑफिस सामान",

            "Mobile/Laptop":
            "स्क्रीन रिपेयर, बैटरी, चार्जर"
        }
    },

    "healthcare": {

        "title": "Healthcare",

        "subs": {

            "Doctor":
            "जनरल फिजिशियन, स्पेशलिस्ट",

            "Clinic":
            "क्लिनिक सेवाएं",

            "Diagnostic Lab":
            "ब्लड टेस्ट, एक्स-रे",

            "Medical Store":
            "दवाइयां",

            "Physiotherapy":
            "फिजियोथेरेपी सेवाएं",

            "Ambulance":
            "24/7 इमरजेंसी"
        }
    },

    "personal": {

        "title": "Personal Services",

        "subs": {

            "Salon":
            "हेयर कट, फेशियल",

            "Laundry":
            "ड्राई क्लीनिंग, प्रेस",

            "Tailoring":
            "सिलाई सेवाएं",

            "Cleaning":
            "सोफा/कारपेट क्लीनिंग",

            "Pest Control":
            "दीमक, कॉकरोच",

            "Courier":
            "डिलीवरी सेवाएं"
        }
    },

    "agriculture": {

        "title": "Agriculture",

        "subs": {

            "Seeds/Fertilizer":
            "बीज, खाद, कीटनाशक",

            "Farm Equipment":
            "थ्रेशर, कल्टीवेटर",

            "Tractor Service":
            "इंजन, टायर रिपेयर",

            "Irrigation":
            "पंप सेट, पाइप",

            "Veterinary":
            "पशु चिकित्सा"
        }
    }
}

# =====================================================
# SEND FUNCTION
# =====================================================

def send(payload):

    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(
        url,
        json=payload,
        headers=headers
    )

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
# SEND CATEGORY LIST
# =====================================================

def send_category_list(to):

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
                "text": "📂 कृपया Category चुनें"
            },

            "action": {

                "button": "Open Categories",

                "sections": [

                    {
                        "title": "Categories",
                        "rows": rows
                    }
                ]
            }
        }
    }

    send(payload)

# =====================================================
# WEBHOOK VERIFY
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

    try:

        data = request.get_json()

        if "entry" not in data:
            return "OK", 200

        msg = data["entry"][0]["changes"][0]["value"] \
        .get("messages", [{}])[0]

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
                        "title": "Customer"
                    }
                },

                {
                    "type": "reply",

                    "reply": {
                        "id": "seller",
                        "title": "Seller"
                    }
                }
            ]

            send_buttons(

                sender,

                "🙏 Welcome to Near Me Marketplace\n\n"
                "कृपया अपना रोल चुनें:",

                buttons
            )

            return "OK", 200

        session = user_sessions[sender]

        # =================================================
        # INTERACTIVE
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

                    if button_id == "customer":

                        session["step"] = "distance"

                        buttons = [

                            {
                                "type": "reply",

                                "reply": {
                                    "id": "1 KM",
                                    "title": "1 KM"
                                }
                            },

                            {
                                "type": "reply",

                                "reply": {
                                    "id": "5 KM",
                                    "title": "5 KM"
                                }
                            },

                            {
                                "type": "reply",

                                "reply": {
                                    "id": "10 KM",
                                    "title": "10 KM"
                                }
                            }
                        ]

                        send_buttons(

                            sender,

                            "📍 कितनी दूरी में सेवा चाहिए?",

                            buttons
                        )

                    else:

                        session["step"] = "shop_name"

                        send_text(

                            sender,

                            "🏪 अपनी दुकान / सेवा का नाम लिखें"
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

                    session["step"] = "requirement"

                    send_text(

                        sender,

                        "📝 अपनी पूरी जरूरत / requirement लिखिए"
                    )

            # =============================================
            # LIST
            # =============================================

            elif interactive["type"] == "list_reply":

                row_id = interactive["list_reply"]["id"]

                # CATEGORY

                if session["step"] == "category":

                    session["category"] = row_id

                    session["step"] = "subcategory"

                    buttons = []

                    subs = categories[row_id]["subs"]

                    for sub, keyword in subs.items():

                        buttons.append({

                            "type": "reply",

                            "reply": {
                                "id": sub,
                                "title": sub[:20]
                            }
                        })

                    send_buttons(

                        sender,

                        "🛠 Sub Category चुनें",

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

                send_category_list(sender)

            # SELLER LOCATION

            elif session["step"] == "seller_location":

                session["location"] = msg["location"]

                session["step"] = "category"

                send_category_list(sender)

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

            # REQUIREMENT TEXT

elif session["step"] == "requirement":

    session["requirement_text"] = text

    session["step"] = "whatsapp"

    send_text(

        sender,

        "📱 अब अपना WhatsApp नंबर लिखें"
    )

# =================================================
# IMAGE MESSAGE
# =================================================

elif "image" in msg:

    if session["step"] == "requirement":

        session["requirement_image"] = \
        msg["image"]["id"]

        # IMAGE CAPTION

        if "caption" in msg["image"]:

            session["requirement_caption"] = \
            msg["image"]["caption"]

        session["step"] = "whatsapp"

        send_text(

            sender,

            "🖼 आपकी फोटो / requirement प्राप्त हो गई।\n\n"
            "📱 अब अपना WhatsApp नंबर लिखें"
        )

            # WHATSAPP

            elif session["step"] == "whatsapp":

                session["whatsapp"] = text

                print("FINAL USER DATA =")
                print(session)

                send_text(

                    sender,

                    "✅ धन्यवाद 🙏\n\n"
                    "आपकी जानकारी सफलतापूर्वक दर्ज हो गई है।\n\n"
                    "हमारी टीम जल्द ही आपसे संपर्क करेगी।"
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
