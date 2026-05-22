import os
from flask import Flask, request
import requests

app = Flask(__name__)

# अपनी API क्रेडेंशियल्स यहाँ डालें
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge")
    
    # यहाँ से मैसेज हैंडलिंग शुरू होती है
    data = request.get_json()
    # [cite_start]रिपोर्ट के अनुसार कैटेगरी फ्लो[span_0](end_span)
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
