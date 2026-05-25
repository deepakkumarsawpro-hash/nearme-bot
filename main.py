import os
import requests
from flask import Flask, request
import psycopg
import redis
import json

app = Flask(__name__)

# =====================================================
# DATABASE + REDIS CONNECTION
# =====================================================
def get_db_connection():
    conn = psycopg.connect(os.getenv('DATABASE_URL'))
    return conn

def get_redis_connection():
    return redis.from_url(os.getenv('REDIS_URL'))

def get_redis():
    return redis.from_url(os.getenv('REDIS_URL'))

# =====================================================
# WHATSAPP CONFIG
# =====================================================

PHONE_ID = "1060745180462931"
TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"
VERIFY_TOKEN = "my_secret_token_123"

# =====================================================
# FULL CATEGORY DATA
# =====================================================

categories = {
    "construction": {
        "title": "Construction",
        "subs": {
            "Mason": "नींव, ईंट जुड़ाई, प्लास्टर, टाइल्स",
            "Architect": "नक्शा, इंटीरियर डिजाइन, 3D व्यू",
            "Plumber": "पाइप लीकेज, मोटर, टैप फिटिंग",
            "Electrician": "वायरिंग, शॉर्ट-सर्किट, इनवर्टर, बोर्ड रिपेयर",
            "Carpenter": "दरवाजा, खिड़की, बेड/अलमारी फर्नीचर",
            "Paint & Hardware": "वॉल पुट्टी, पेंटिंग, हार्डवेयर सामान"
        }
    },
    "automotive": {
        "title": "Automotive",
        "subs": {
            "Mechanic": "इंजन रिपेयर, सर्विसिंग, ब्रेक, क्लच",
            "Denting/Painting": "डेंट हटाना, पेंटिंग, पॉलिशिंग",
            "Spare Parts": "ओरिजिनल पार्ट्स, लुब्रिकेंट्स",
            "Washing": "फोम वॉश, इंटरनल क्लीनिंग, वैक्सिंग",
            "Batteries": "बैटरी बदलना, चार्जिंग"
        }
    },
    "food": {
        "title": "Food",
        "subs": {
            "Restaurants": "वेज, नॉन-वेज, थाली, पार्सल",
            "Tiffin": "मंथली मेस, होम मेड खाना",
            "Fast Food": "पिज्जा, बर्गर, मोमोज, चाउमीन",
            "Sweets/Bakery": "केक, मिठाई",
            "Catering": "शादी/पार्टी ऑर्डर",
            "Grocery": "दैनिक राशन सामग्री"
        }
    },
    "retail": {
        "title": "Retail",
        "subs": {
            "Clothing": "मेंस, वुमेंस, किड्स वियर",
            "Electronics": "टीवी, फ्रिज, वाशिंग मशीन",
            "Pharmacy": "दवाइयां, स्वास्थ्य सप्लीमेंट",
            "Footwear": "जूते, चप्पल",
            "Stationery": "कॉपी, किताब, ऑफिस सामान",
            "Mobile/Laptop": "स्क्रीन रिपेयर, बैटरी, चार्जर"
        }
    },
    "healthcare": {
        "title": "Healthcare",
        "subs": {
            "Doctor": "जनरल फिजिशियन, स्पेशलिस्ट",
            "Clinic": "क्लिनिक सेवाएं",
            "Diagnostic Lab": "ब्लड टेस्ट, एक्स-रे",
            "Medical Store": "दवाइयां",
            "Physiotherapy": "फिजियोथेरेपी सेवाएं",
            "Ambulance": "24/7 इमरजेंसी"
        }
    },
    "personal": {
        "title": "Personal Services",
        "subs": {
            "Salon": "हेयर कट, फेशियल",
            "Laundry": "ड्राई क्लीनिंग, प्रेस",
            "Tailoring": "सिलाई सेवाएं",
            "Cleaning": "सोफा/कारपेट क्लीनिंग",
            "Pest Control": "दीमक, कॉकरोच",
            "Courier": "डिलीवरी सेवाएं"
        }
    },
    "agriculture": {
        "title": "Agriculture",
        "subs": {
            "Seeds/Fertilizer": "बीज, खाद, कीटनाशक",
            "Farm Equipment": "थ्रेशर, कल्टीवेटर",
            "Tractor Service": "इंजन, टायर रिपेयर",
            "Irrigation": "पंप सेट, पाइप",
            "Veterinary": "पशु चिकित्सा"
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
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Send Error: {e}")

# =====================================================
# SEND TEXT
# =====================================================

def send_text(to, text):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
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
            "body": {"text": text},
            "action": {"buttons": buttons}
        }
    }
    send(payload)

# =====================================================
# SEND CATEGORY LIST
# =====================================================

def send_category_list(to):
    rows = []
    for key, value in categories.items():
        rows.append({"id": key, "title": value["title"]})

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "Near Me Marketplace"},
            "body": {"text": "📂 कृपया Category चुनें"},
            "action": {
                "button": "Open Categories",
                "sections": [{"title": "Categories", "rows": rows}]
            }
        }
    }
    send(payload)

# =====================================================
# DB CHECK ROUTE
# =====================================================
@app.route("/db-check")
def db_check():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        cur.close()
        conn.close()

        r = get_redis_connection()
        r.ping()
        return "Database + Redis Connected ✅"
    except Exception as e:
        return f"Connection Failed ❌ {e}"

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
            return
