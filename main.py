def process_step(to, text):
    # Step 0: Welcome
    if "hi" in text or "hello" in text:
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "button", "body": {"text": "Namaste! NearMe mein swagat hai. Aap kya hain?"},
            "action": {"buttons": [{"type": "reply", "reply": {"id": "sale_service", "title": "सेल & सर्विस"}}, {"type": "reply", "reply": {"id": "customer", "title": "ग्राहक"}}]}}})

    # Step 1: Location & Categories
    elif text == "sale_service":
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Great! Pin icon par click karke location share karein."}})
    
    elif text == "step_location_received":
        # (Yahan wahi 7 Main Categories wali list rahegi jo pichle code mein thi)
        pass 

    # Step 2: Sub-Category select hone par Keywords dikhana
    elif text == "sub_mason": # Example: Mason select hua
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {
            "type": "list", "header": {"type": "text", "text": "Keywords Chunein"}, "body": {"text": "Mason ke liye keywords chunein:"},
            "action": {"button": "Keywords", "sections": [{"title": "Keywords", "rows": [
                {"id": "kw_raj", "title": "Raj Mistri"}, {"id": "kw_cement", "title": "Cement Work"}]}]}}})

    # Step 3: Keywords select hone par WhatsApp Number maangna
    elif text.startswith("kw_"):
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Keywords select ho gaye! \n\nAb apna WhatsApp Number type karke bhejein jahan hum aapse contact kar sakein:"}})

    # Step 4: Final Step (Number capture)
    elif len(text) >= 10 and text.isdigit() and not text.startswith(("cat_", "sub_", "kw_")):
        send_msg(to, {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": "Dhanyavad! Apka number " + text + " save ho gaya hai. Hum jald aapse sampark karenge."}})
        
