from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# --------------------------
# Categories
# --------------------------

categories = {
    "निर्माण": ["मिस्त्री", "प्लंबर"],
    "ऑटो": ["मैकेनिक"],
    "भोजन": ["रेस्टोरेंट"],
    "खुदरा": ["किराना"],
    "स्वास्थ्य": ["डॉक्टर"],
    "व्यक्तिगत": ["सैलून"],
    "कृषि": ["बीज"]
}

# --------------------------
# Sessions
# --------------------------

sessions = {}

# --------------------------
# Save Data
# --------------------------

def save_data(data):

    file_name = "data.json"

    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            try:
                old = json.load(file)
            except:
                old = []
    else:
        old = []

    old.append(data)

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(old, file, ensure_ascii=False, indent=4)

# --------------------------
# HTML UI
# --------------------------

HTML = '''

<!DOCTYPE html>
<html>
<head>

<title>Near Me Marketplace</title>

<style>

body{
font-family:Arial;
background:#f2f2f2;
padding:20px;
}

.chat{
max-width:500px;
margin:auto;
background:white;
padding:20px;
border-radius:10px;
box-shadow:0px 0px 10px #ccc;
}

.messages{
height:400px;
overflow-y:auto;
border:1px solid #ddd;
padding:10px;
margin-bottom:10px;
}

.user{
text-align:right;
margin:10px;
color:blue;
}

.bot{
text-align:left;
margin:10px;
color:green;
}

input{
width:75%;
padding:10px;
}

button{
padding:10px;
background:#28a745;
color:white;
border:none;
cursor:pointer;
}

</style>

</head>

<body>

<div class="chat">

<h2>Near Me Marketplace</h2>

<div class="messages" id="messages"></div>

<input type="text" id="msg" placeholder="Message लिखें">

<button onclick="send()">Send</button>

</div>

<script>

const user_id = "demo_user";

async function send(){

let input = document.getElementById("msg");

let message = input.value;

if(message == "") return;

let box = document.getElementById("messages");

box.innerHTML += `<div class='user'>${message}</div>`;

input.value = "";

const response = await fetch("/chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
user_id:user_id,
message:message
})

});

const data = await response.json();

box.innerHTML += `<div class='bot'>${data.reply}</div>`;

box.scrollTop = box.scrollHeight;

}

window.onload = async function(){

const response = await fetch("/chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
user_id:user_id,
message:"start"
})

});

const data = await response.json();

document.getElementById("messages").innerHTML +=
`<div class='bot'>${data.reply}</div>`;

}

</script>

</body>
</html>

'''

# --------------------------
# Home
# --------------------------

@app.route("/")
def home():
    return render_template_string(HTML)

# --------------------------
# Chat API
# --------------------------

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    user_id = data["user_id"]
    message = data["message"]

    if user_id not in sessions:
        sessions[user_id] = {
            "step": "welcome"
        }

    session = sessions[user_id]

    # Welcome

    if session["step"] == "welcome":

        session["step"] = "role"

        return jsonify({
            "reply":
            "नमस्ते 🙏\\n\\nNear Me Marketplace में आपका स्वागत है।\\n\\nअपना रोल चुनें:\\n\\n1. Customer\\n2. Seller"
        })

    # Role

    elif session["step"] == "role":

        session["role"] = message

        if message.lower() == "customer":

            session["step"] = "distance"

            return jsonify({
                "reply":"कृपया दूरी दर्ज करें (उदाहरण: 5 KM)"
            })

        elif message.lower() == "seller":

            session["step"] = "shop"

            return jsonify({
                "reply":"दुकान का नाम दर्ज करें"
            })

        else:

            return jsonify({
                "reply":"केवल Customer या Seller लिखें"
            })

    # Customer

    elif session["step"] == "distance":

        session["distance"] = message
        session["step"] = "location"

        return jsonify({
            "reply":"अपनी लोकेशन दर्ज करें"
        })

    elif session["step"] == "location":

        session["location"] = message
        session["step"] = "category"

        cats = "\\n".join(categories.keys())

        return jsonify({
            "reply":f"श्रेणी चुनें:\\n\\n{cats}"
        })

    elif session["step"] == "category":

        if message not in categories:

            return jsonify({
                "reply":"सही श्रेणी चुनें"
            })

        session["category"] = message

        subs = "\\n".join(categories[message])

        session["step"] = "subcategory"

        return jsonify({
            "reply":f"उप-श्रेणी चुनें:\\n\\n{subs}"
        })

    elif session["step"] == "subcategory":

        session["subcategory"] = message
        session["step"] = "other"

        return jsonify({
            "reply":"अन्य जानकारी लिखें"
        })

    elif session["step"] == "other":

        session["other"] = message
        session["step"] = "whatsapp"

        return jsonify({
            "reply":"WhatsApp नंबर दर्ज करें"
        })

    elif session["step"] == "whatsapp":

        session["whatsapp"] = message

        save_data(session)

        sessions.pop(user_id)

        return jsonify({
            "reply":"धन्यवाद 🙏\\n\\nआपकी जानकारी सफलतापूर्वक दर्ज कर ली गई है।"
        })

    # Seller

    elif session["step"] == "shop":

        session["shop_name"] = message
        session["step"] = "seller_category"

        cats = "\\n".join(categories.keys())

        return jsonify({
            "reply":f"श्रेणी चुनें:\\n\\n{cats}"
        })

    elif session["step"] == "seller_category":

        if message not in categories:

            return jsonify({
                "reply":"सही श्रेणी चुनें"
            })

        session["category"] = message

        subs = "\\n".join(categories[message])

        session["step"] = "seller_sub"

        return jsonify({
            "reply":f"उप-श्रेणी चुनें:\\n\\n{subs}"
        })

    elif session["step"] == "seller_sub":

        session["subcategory"] = message
        session["step"] = "seller_other"

        return jsonify({
            "reply":"अन्य जानकारी लिखें"
        })

    elif session["step"] == "seller_other":

        session["other"] = message
        session["step"] = "seller_location"

        return jsonify({
            "reply":"लोकेशन दर्ज करें"
        })

    elif session["step"] == "seller_location":

        session["location"] = message
        session["step"] = "seller_whatsapp"

        return jsonify({
            "reply":"WhatsApp नंबर दर्ज करें"
        })

    elif session["step"] == "seller_whatsapp":

        session["whatsapp"] = message

        save_data(session)

        sessions.pop(user_id)

        return jsonify({
            "reply":"धन्यवाद 🙏\\n\\nSeller Registration सफल हुआ।"
        })

    return jsonify({
        "reply":"कुछ त्रुटि हुई है"
    })

# --------------------------
# Run
# --------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
