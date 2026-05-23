 elif "sale_service" in text:
        # Ab button click hone par location ka message aur button bhejein
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Great! Ab aap apna location share karein (Attach > Location)."},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "share_loc_now", "title": "Location bhejein"}}
                    ]
                }
            }
        }
    elif "share_loc_now" in text:
        payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Theek hai, ab aap neeche diye gaye Pin icon par click karke apni location share karein."}}
