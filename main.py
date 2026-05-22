from flask import Flask, request
import os

app = Flask(__name__)

# Wahi token jo aapne Meta dashboard mein dala hai
VERIFY_TOKEN = "my_secret_token_123"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Meta verification ke liye
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    
    elif request.method == 'POST':
        # Yahan message receive hoga
        data = request.get_json()
        print(data) # Yeh Render ke "Logs" mein dikhega
        return "OK", 200

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    # Render ke liye zaroori port setting
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
