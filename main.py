import os
import requests
from flask import Flask, request, render_template_string
import psycopg
import redis
import json
import math
from datetime import datetime

app = Flask(__name__)

# =====================================================
# DATABASE + REDIS CONNECTION
# =====================================================
def get_db_connection():
    conn = psycopg.connect(os.getenv('DATABASE_URL'))
    return conn

def get_redis():
    return redis.from_url(os.getenv('REDIS_URL'))

# =====================================================
# HELPER: FORMAT PHONE NUMBER
# =====================================================
def format_phone(phone):
    phone = str(phone).replace(" ", "").replace("+", "").replace("-", "")
    if len(phone) == 10 and phone.isdigit():
        return "91" + phone
    if len(phone) == 12 and phone.startswith("91"):
        return phone
    return phone

# =====================================================
# HELPER: CALCULATE DISTANCE
# =====================================================
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

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
    "construction": {"title": "Construction", "subs": {"Mason": "नींव, ईंट जुड़ाई, प्लास्टर, टाइल्स", "Architect": "नक्शा, इंटीरियर डिजाइन, 3D व्यू", "Plumber": "पाइप लीकेज, मोटर, टैप फिटिंग", "Electrician": "वायरिंग, शॉर्ट-सर्किट, इनवर्टर, बोर्ड रिपेयर", "Carpenter": "दरवाजा, खिड़की, बेड/अलमारी फर्नीचर", "Paint & Hardware": "वॉल पुट्टी, पेंटिंग, हार्डवेयर सामान"}},
    "automotive": {"title": "Automotive", "subs": {"Mechanic": "इंजन रिपेयर, सर्विसिंग, ब्रेक, क्लच", "Denting/Painting": "डेंट हटाना, पेंटिंग, पॉलिशिंग", "Spare Parts": "ओरिजिनल पार्ट्स, लुब्रिकेंट्स", "Washing": "फोम वॉश, इंटरनल क्लीनिंग, वैक्सिंग", "Batteries": "बैटरी बदलना, चार्जिंग"}},
    "food": {"title": "Food", "subs": {"Restaurants": "वेज, नॉन-वेज, थाली, पार्सल", "Tiffin": "मंथली मेस, होम मेड खाना", "Fast Food": "पिज्जा, बर्गर, मोमोज, चाउमीन", "Sweets/Bakery": "केक, मिठाई", "Catering": "शादी/पार्टी ऑर्डर", "Grocery": "दैनिक राशन सामग्री"}},
    "retail": {"title": "Retail", "subs": {"Clothing": "मेंस, वुमेंस, किड्स वियर", "Electronics": "टीवी, फ्रिज, वाशिंग मशीन", "Pharmacy": "दवाइयां, स्वास्थ्य सप्लीमेंट", "Footwear": "जूते, चप्पल", "Stationery": "कॉपी, किताब, ऑफिस सामान", "Mobile/Laptop": "स्क्रीन रिपेयर, बैटरी, चार्जर"}},
    "healthcare": {"title": "Healthcare", "subs": {"Doctor": "जनरल फिजिशियन, स्पेशलिस्ट", "Clinic": "क्लिनिक सेवाएं", "Diagnostic Lab": "ब्लड टेस्ट, एक्स-रे", "Medical Store": "दवाइयां", "Physiotherapy": "फिजियोथेरेपी सेवाएं", "Ambulance": "24/7 इमरजेंसी"}},
    "personal": {"title": "Personal Services", "subs": {"Salon": "हेयर कट, फेशियल", "Laundry": "ड्राई क्लीनिंग, प्रेस", "Tailoring": "सिलाई सेवाएं", "Cleaning": "सोफा/कारपेट क्लीनिंग", "Pest Control": "दीमक, कॉकरोच", "Courier": "डिलीवरी सेवाएं"}},
    "agriculture": {"title": "Agriculture", "subs": {"Seeds/Fertilizer": "बीज, खाद, कीटनाशक", "Farm Equipment": "थ्रेशर, कल्टीवेटर", "Tractor Service": "इंजन, टायर रिपेयर", "Irrigation": "पंप सेट, पाइप", "Veterinary": "पशु चिकित्सा"}}
}

# =====================================================
# SEND FUNCTION
# =====================================================

def send(payload):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Send Error: {e}")

def send_text(to, text):
    send({"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}})

def send_image(to, image_id, caption):
    send({"messaging_product": "whatsapp", "to": to, "type": "image", "image": {"id": image_id, "caption": caption}})

def send_buttons(to, text, buttons):
    send({"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {"type": "button", "body": {"text": text}, "action": {"buttons": buttons}}})

def send_category_list(to):
    rows = [{"id": key, "title": value["title"]} for key, value in categories.items()]
    send({"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Near Me Marketplace"}, "body": {"text": "📂 कृपया Category चुनें"}, "action": {"button": "Open Categories", "sections": [{"title": "Categories", "rows": rows}]}}})

# =====================================================
# AUTO MATCHING FUNCTION - LIMIT 10 SELLERS
# =====================================================
def find_and_notify_sellers(customer_data, customer_lead_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cust_lat = customer_data["location"]["latitude"]
        cust_lon = customer_data["location"]["longitude"]
        cust_category = customer_data["category"]
        cust_subcategory = customer_data["subcategory"]
        max_distance = int(customer_data["distance"].split()[0])
        req_text = customer_data.get("requirement_text") or customer_data.get("requirement_caption", "No text")
        cust_phone = customer_data.get("whatsapp", "Not provided")
        req_image_id = customer_data.get("requirement_image")

        # DB se matching sellers nikalo
        cur.execute("""
            SELECT phone, data FROM leads
            WHERE data->>'role' = 'seller'
            AND data->>'category' = %s
            AND data->>'subcategory' = %s
            ORDER BY created_at DESC
        """, (cust_category, cust_subcategory))

        sellers = cur.fetchall()
        matched_sellers = []

        # Distance calculate karke sort karo
        for seller_phone, seller_data_json in sellers:
            seller_data = seller_data_json
            seller_lat = seller_data["location"]["latitude"]
            seller_lon = seller_data["location"]["longitude"]
            distance = haversine_distance(cust_lat, cust_lon, seller_lat, seller_lon)

            if distance <= max_distance:
                matched_sellers.append({
                    "phone": seller_phone,
                    "data": seller_data,
                    "distance": distance
                })

        # Distance ke hisaab se sort karo aur top 10 lo
        matched_sellers.sort(key=lambda x: x["distance"])
        matched_sellers = matched_sellers[:10] # LIMIT 10 SELLERS

        for seller in matched_sellers:
            seller_phone_formatted = format_phone(seller["phone"])
            shop_name = seller["data"].get("shop_name", "Seller")
            distance = seller["distance"]

            # Seller ko message + Interested button bhejo
            msg = f"🔔 *New Customer Lead* 🔔\n\n👤 *Customer*: +{cust_phone}\n📍 *Distance*: {distance:.1f} KM away\n🏪 *Shop*: {shop_name}\n📂 *Category*: {categories[cust_category]['title']} > {cust_subcategory}\n📝 *Requirement*: {req_text}\n\n*Lead ID*: {customer_lead_id}"

            buttons = [
                {"type": "reply", "reply": {"id": f"interested_{customer_lead_id}", "title": "✅ Interested"}}
            ]

            if req_image_id:
                send_image(seller_phone_formatted, req_image_id, msg)
                send_buttons(seller_phone_formatted, "Kya aap is customer se connect karna chahte hain?", buttons)
            else:
                send_buttons(seller_phone_formatted, msg, buttons)

        cur.close()
        conn.close()
        return len(matched_sellers)

    except Exception as e:
        print(f"Matching Error: {e}")
        return 0

# =====================================================
# ADMIN DASHBOARD
# =====================================================
@app.route("/admin")
def admin():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, phone, data, created_at FROM leads ORDER BY created_at DESC LIMIT 100")
        leads = cur.fetchall()
        cur.close()
        conn.close()

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Near Me Marketplace - Admin</title>
            <style>
                body { font-family: Arial; margin: 20px; background: #f5f5f5; }
                h1 { color: #333; }
                table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #4CAF50; color: white; }
                tr:hover { background: #f1f1f1; }
               .badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; }
               .customer { background: #2196F3; }
               .seller { background: #FF9800; }
            </style>
        </head>
        <body>
            <h1>📊 Near Me Marketplace - Leads Dashboard</h1>
            <p>Total Leads: {{ leads|length }}</p>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Role</th>
                    <th>Phone</th>
                    <th>Category</th>
                    <th>Location</th>
                    <th>Requirement</th>
                    <th>Date</th>
                </tr>
                {% for lead in leads %}
                <tr>
                    <td>{{ lead[0] }}</td>
                    <td><span class="badge {{ lead[2]['role'] }}">{{ lead[2]['role'].title() }}</span></td>
                    <td>+{{ lead[1] }}</td>
                    <td>{{ lead[2].get('category', '-') }} > {{ lead[2].get('subcategory', '-') }}</td>
                    <td>{{ lead[2]['location']['latitude'] }}, {{ lead[2]['location']['longitude'] }}</td>
                    <td>{{ lead[2].get('requirement_text', lead[2].get('requirement_caption', '-'))[:50] }}...</td>
                    <td>{{ lead[3].strftime('%d-%m-%Y %H:%M') }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html_template, leads=leads)
    except Exception as e:
        return f"Error: {e}"

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
        r = get_redis()
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
            return "OK", 200

        msg = data["entry"][0]["changes"][0]["value"].get("messages", [{}])[0]
        sender = msg.get("from")
        if not sender:
            return "OK", 200

        r = get_redis()
        session_data = r.get(f"session:{sender}")

        if not session_data:
            session = {"step": "role"}
            r.set(f"session:{sender}", json.dumps(session))
            buttons = [{"type": "reply", "reply": {"id": "customer", "title": "Customer"}}, {"type": "reply", "reply": {"id": "seller", "title": "Seller"}}]
            send_buttons(sender, "🙏 Welcome to Near Me Marketplace\n\nकृपया अपना रोल चुनें:", buttons)
            return "OK", 200

        session = json.loads(session_data)

        if "text" in msg and session["step"] == "role":
            buttons = [{"type": "reply", "reply": {"id": "customer", "title": "Customer"}}, {"type": "reply", "reply": {"id": "seller", "title": "Seller"}}]
            send_buttons(sender, "🙏 Welcome to Near Me Marketplace\n\nकृपया अपना रोल चुनें:", buttons)
            return "OK", 200

        if "interactive" in msg:
            interactive = msg["interactive"]
            if interactive["type"] == "button_reply":
                button_id = interactive["button_reply"]["id"]

                # SELLER INTERESTED BUTTON
                if button_id.startswith("interested_"):
                    lead_id = button_id.split("_")[1]
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT phone, data FROM leads WHERE id = %s", (lead_id,))
                    result = cur.fetchone()
                    cur.close()
                    conn.close()

                    if result:
                        customer_phone, customer_data = result
                        seller_data = json.loads(session_data) if session_data else {}
                        seller_shop = seller_data.get("shop_name", "Ek Seller")

                        # Customer ko notify karo
                        send_text(format_phone(customer_phone), f"🎉 Good News!\n\n*{seller_shop}* aapki requirement me interested hai.\n\nSeller aapse jaldi contact karega: +{sender}")
                        # Seller ko confirm karo
                        send_text(sender, "✅ Done! Customer ko aapka contact bhej diya gaya hai. Jaldi call karke deal close karein.")
                    return "OK", 200

                if session["step"] == "role":
                    session["role"] = button_id
                    if button_id == "customer":
                        session["step"] = "distance"
                        buttons = [{"type": "reply", "reply": {"id": "1 KM", "title": "1 KM"}}, {"type": "reply", "reply": {"id": "5 KM", "title": "5 KM"}}, {"type": "reply", "reply": {"id": "10 KM", "title": "10 KM"}}]
                        send_buttons(sender, "📍 कितनी दूरी में सेवा चाहिए?", buttons)
                    else:
                        session["step"] = "shop_name"
                        send_text(sender, "🏪 अपनी दुकान / सेवा का नाम लिखें")

                elif session["step"] == "distance":
                    session["distance"] = button_id
                    session["step"] = "location"
                    send_text(sender, "📍 अब अपनी लोकेशन Share करें")

                elif session["step"] == "subcategory":
                    session["subcategory"] = button_id
                    session["step"] = "requirement"
                    send_text(sender, "📝 अपनी पूरी जरूरत / requirement लिखें\n\nया संबंधित फोटो भेजें।\n\n✅ Text लिख सकते हैं\n✅ Photo भेज सकते हैं\n✅ Photo + Text दोनों भेज सकते हैं")

            elif interactive["type"] == "list_reply":
                row_id = interactive["list_reply"]["id"]
                if session["step"] == "category":
                    session["category"] = row_id
                    session["step"] = "subcategory"
                    buttons = []
                    subs = categories[row_id]["subs"]
                    for sub, keyword in subs.items():
                        buttons.append({"type": "reply", "reply": {"id": sub, "title": sub[:20]}})
                    send_buttons(sender, "🛠 Sub Category चुनें", buttons[:3])

        elif "location" in msg:
            if session["step"] == "location":
                session["location"] = msg["location"]
                session["step"] = "category"
                send_category_list(sender)
            elif session["step"] == "seller_location":
                session["location"] = msg["location"]
                session["step"] = "category"
                send_category_list(sender)

        elif "text" in msg:
            text = msg["text"]["body"]
            if session["step"] == "shop_name":
                session["shop_name"] = text
                session["step"] = "seller_location"
                send_text(sender, "📍 अब दुकान की लोकेशन Share करें")

            elif session["step"] == "requirement":
                session["requirement_text"] = text
                session["step"] = "whatsapp"
                send_text(sender, "📱 अब अपना WhatsApp नंबर लिखें")

            elif session["step"] == "whatsapp":
                session["whatsapp"] = format_phone(text)
                print("FINAL USER DATA =", session)

                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("CREATE TABLE IF NOT EXISTS leads (id SERIAL PRIMARY KEY, phone VARCHAR(20), data JSONB, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    cur.execute("INSERT INTO leads (phone, data) VALUES (%s, %s) RETURNING id", (sender, json.dumps(session)))
                    lead_id = cur.fetchone()[0]
                    conn.commit()
                    cur.close()
                    conn.close()

                    if session["role"] == "customer":
                        matched = find_and_notify_sellers(session, lead_id)
                        send_text(sender, f"✅ धन्यवाद 🙏\n\nआपकी जानकारी सफलतापूर्वक दर्ज हो गई है।\n\n📢 {matched} नजदीकी दुकानदारों को आपकी requirement भेज दी गई है।\n\n*Lead ID: {lead_id}*\n\nJab koi seller interested hoga to aapko turant notification milega.")
                    else:
                        send_text(sender, "✅ धन्यवाद 🙏\n\nआपकी दुकान सफलतापूर्वक रजिस्टर हो गई है।\n\nAb aapke area ke Customer ki requirement seedhe aapke WhatsApp par aayegi 'Interested' button ke saath.")

                except Exception as db_error:
                    print(f"DB Save Error: {db_error}")
                    send_text(sender, "⚠️ कुछ Error आ गया। कृपया फिर से try करें।")

                r.delete(f"session:{sender}")
                return "OK", 200

        elif "image" in msg:
            if session["step"] == "requirement":
                session["requirement_image"] = msg["image"]["id"]
                if "caption" in msg["image"]:
                    session["requirement_caption"] = msg["image"]["caption"]
                session["step"] = "whatsapp"
                send_text(sender, "🖼 आपकी फोटो / requirement प्राप्त हो गई।\n\n📱 अब अपना WhatsApp नंबर लिखें")

        r.set(f"session:{sender}", json.dumps(session))
        return "OK", 200

    except Exception as e:
        print("ERROR =", e)
        return "OK", 200

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return "Near Me Marketplace Bot Running ✅"

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
