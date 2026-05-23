from flask import Flask, request, jsonify

app = Flask(__name__)

# Aapka wahi token jo verify ho chuka hai
VERIFY_TOKEN = "my_secret_token_123"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403

    data = request.get_json()
    
    # Yahan hum message handle karenge
    if 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        # Yahan hum user ka reply check karenge
                        print(f"Received: {message}")
                        
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000)
