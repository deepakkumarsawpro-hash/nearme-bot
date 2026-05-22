@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge")
    
    data = request.get_json()
    
    try:
        # 1. Message extract karna
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' in value:
            msg = value['messages'][0]
            sender = msg['from']
            
            # 2. Interactive Menu handle karna
            if 'interactive' in msg:
                sel_id = msg['interactive'].get('list_reply', {}).get('id')
                print(f"DEBUG: User selected ID -> {sel_id}") # Render logs mein check karein
                
                if sel_id == "buyer":
                    send_menu(sender, "Categories", "Select service:", [{"id": "kirana", "title": "Kirana"}, {"id": "hotel", "title": "Hotel"}])
                elif sel_id == "seller":
                    send_menu(sender, "Seller Menu", "Kya bechna chahte hain?", [{"id": "reg_prod", "title": "Product Add karein"}])
                elif sel_id == "kirana":
                    send_menu(sender, "Sub-Category", "Select item:", [{"id": "sabji", "title": "Sabji"}, {"id": "milk", "title": "Milk"}])
                else:
                    send_menu(sender, "Oops", "Kuch galat ho gaya, phir se try karein.", [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}])
            
            # 3. Normal Text / First Message
            else:
                send_menu(sender, "Welcome", "नमस्कार! NearMe में स्वागत है।", [{"id": "buyer", "title": "Buyer"}, {"id": "seller", "title": "Seller"}])
                
    except Exception as e:
        print(f"Error: {e}")
        
    return "OK", 200
    
