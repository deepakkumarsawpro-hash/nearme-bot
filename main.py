from flask import Flask, request
import os

app = Flask(__name__)

# यहाँ वही टोकन डालें जो Meta पोर्टल में है
VERIFY_TOKEN = "my_secret_token_123"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
  
