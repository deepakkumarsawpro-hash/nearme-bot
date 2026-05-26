# =========================================
# COMPLETE NEAR ME MARKETPLACE BOT
# =========================================

import os
import requests
from flask import Flask, request
import psycopg
import redis
import json
import math

app = Flask(__name__)

# =========================================
# DATABASE CONNECTION
# =========================================

def get_db_connection():
    return psycopg.connect(os.getenv('DATABASE_URL'))

def get_redis():
    return redis.from_url(os.getenv('REDIS_URL'))

# =========================================
# WHATSAPP CONFIG
# =========================================

PHONE_ID = "1060745180462931"

TOKEN = "YOUR_PERMANENT_TOKEN"

VERIFY_TOKEN = "my_secret_token_123"

# =========================================
# CATEGORY DATA
# =========================================

categories = {

    "construction": {
        "title": "Construction",
        "subs": {
            "Mason": "नींव, प्लास्टर",
            "Architect": "नक्शा",
            "Plumber": "पाइप लीकेज",
            "Electrician": "वायरिंग",
            "Carpenter": "फर्नीचर",
            "Paint": "पेंटिंग"
        }
    },

    "automotive": {
        "title": "Automotive",
        "subs": {
            "Mechanic": "इंजन रिपेयर",
            "Denting": "डेंट हटाना",
            "Spare Parts": "पार्ट्स",
            "Washing": "फोम वॉश"
        }
    },

    "food": {
        "title": "Food",
        "subs": {
            "Restaurant": "वेज",
            "Tiffin": "होम मेड",
            "Fast Food": "बर्गर",
            "Bakery": "केक"
        }
    }
}

# =========================================
# HELPER FUNCTIONS
# =========================================

def format_phone(phone):

    phone = str(phone).replace("+", "").replace(" ", "")

    if len(phone) == 10:
        return "91" + phone

    return phone

def haversine_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dLon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# =========================================
# SEND FUNCTIONS
# =========================================

def send(payload):

    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

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
                "text": "📂 Category चुनें"
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

# =========================================
# MATCH SELLERS
# =========================================

def find_matching_sellers(customer_data):

    try:

        conn = get_db_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT phone, data
            FROM leads
            WHERE data->>'role'='seller'

        """)

        sellers = cur.fetchall()

        cur.close()
        conn.close()

        matches = []

        for seller_phone, seller_data in sellers:

            if (
                seller_data.get("category") ==
                customer_data.get("category")

                and

                seller_data.get("subcategory") ==
                customer_data.get("subcategory")
            ):

                distance = haversine_distance(

                    customer_data["location"]["latitude"],
                    customer_data["location"]["longitude"],

                    seller_data["location"]["latitude"],
                    seller_data["location"]["longitude"]
                )

                allowed = int(
                    customer_data["distance"].split()[0]
                )

                if distance <= allowed:

                    matches.append({
                        "phone": seller_phone,
                        "distance": distance
                    })

        return matches[:10]

    except Exception as e:

        print(e)

        return []

# =========================================
# WEBHOOK VERIFY
# =========================================

@app.route("/webhook", methods=["GET"])

def verify():

    mode = request.args.get("hub.mode")

    token = request.args.get("hub.verify_token")

    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        return challenge, 200

    return "Verification failed", 403

# =========================================
# MAIN WEBHOOK
# =========================================

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

        r = get_redis()

        session_data = r.get(f"session:{sender}")

        # =====================================
        # START SESSION
        # =====================================

        if not session_data:

            session = {
                "step": "role"
            }

            r.set(
                f"session:{sender}",
                json.dumps(session)
            )

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

        session = json.loads(session_data)

        # =====================================
        # INTERACTIVE
        # =====================================

        if "interactive" in msg:

            interactive = msg["interactive"]

            # BUTTON REPLY

            if interactive["type"] == "button_reply":

                button_id = \
                interactive["button_reply"]["id"]

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
                            "🏪 दुकान / सेवा का नाम लिखें"
                        )

                # DISTANCE

                elif session["step"] == "distance":

                    session["distance"] = button_id

                    session["step"] = "location"

                    send_text(
                        sender,
                        "📍 अपनी लोकेशन Share करें"
                    )

                # SUBCATEGORY

                elif session["step"] == "subcategory":

                    session["subcategory"] = button_id

                    session["step"] = "requirement"

                    send_text(

                        sender,

                        "📝 Requirement लिखें\n\n"
                        "या फोटो भेजें"
                    )

            # LIST REPLY

            elif interactive["type"] == "list_reply":

                row_id = \
                interactive["list_reply"]["id"]

                if session["step"] == "category":

                    session["category"] = row_id

                    session["step"] = "subcategory"

                    buttons = []

                    subs = categories[row_id]["subs"]

                    for sub in subs:

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

        # =====================================
        # LOCATION
        # =====================================

        elif "location" in msg:

            if session["step"] == "location":

                session["location"] = msg["location"]

                session["step"] = "category"

                send_category_list(sender)

            elif session["step"] == "seller_location":

                session["location"] = msg["location"]

                session["step"] = "category"

                send_category_list(sender)

        # =====================================
        # IMAGE
        # =====================================

        elif "image" in msg:

            if session["step"] == "requirement":

                session["requirement_image"] = \
                msg["image"]["id"]

                session["step"] = "whatsapp"

                send_text(
                    sender,
                    "📱 WhatsApp नंबर लिखें"
                )

        # =====================================
        # TEXT
        # =====================================

        elif "text" in msg:

            text = msg["text"]["body"]

            # SHOP NAME

            if session["step"] == "shop_name":

                session["shop_name"] = text

                session["step"] = "seller_location"

                send_text(
                    sender,
                    "📍 दुकान की लोकेशन Share करें"
                )

            # REQUIREMENT

            elif session["step"] == "requirement":

                session["requirement_text"] = text

                session["step"] = "whatsapp"

                send_text(
                    sender,
                    "📱 WhatsApp नंबर लिखें"
                )

            # FINAL SAVE

            elif session["step"] == "whatsapp":

                session["whatsapp"] = \
                format_phone(text)

                conn = get_db_connection()

                cur = conn.cursor()

                cur.execute("""

                    CREATE TABLE IF NOT EXISTS leads (

                        id SERIAL PRIMARY KEY,

                        phone VARCHAR(20),

                        data JSONB,

                        created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                    )

                """)

                cur.execute("""

                    INSERT INTO leads
                    (phone, data)

                    VALUES (%s, %s)

                """, (

                    sender,

                    json.dumps(session)
                ))

                conn.commit()

                cur.close()

                conn.close()

                # CUSTOMER

                if session["role"] == "customer":

                    matches = \
                    find_matching_sellers(session)

                    for seller in matches:

                        send_text(

                            format_phone(
                                seller["phone"]
                            ),

                            f"🔔 New Customer Lead\n\n"
                            f"📂 {session['category']}\n"
                            f"🛠 {session['subcategory']}\n"
                            f"📍 {seller['distance']:.1f} KM\n\n"
                            f"📝 Requirement:\n"
                            f"{session.get('requirement_text','Photo Sent')}"
                        )

                    send_text(

                        sender,

                        f"✅ {len(matches)} sellers को "
                        f"आपकी requirement भेज दी गई है।"
                    )

                # SELLER

                else:

                    send_text(

                        sender,

                        "✅ Seller Registration Complete"
                    )

                r.delete(f"session:{sender}")

        r.set(
            f"session:{sender}",
            json.dumps(session)
        )

        return "OK", 200

    except Exception as e:

        print("ERROR =", e)

        return "OK", 200

# =========================================
# HOME
# =========================================

@app.route("/")

def home():

    return "Near Me Marketplace Bot Running ✅"

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
