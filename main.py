    elif request.method == 'POST':
        data = request.get_json()
        try:
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                message = data['entry'][0]['changes'][0]['value']['messages'][0]
                sender_id = message['from']
                text = message['text']['body'].lower() 
                
                # Naya Logic (Yahan saare triggers define hain)
                if any(x in text for x in ["hi", "hello"]):
                    reply = "Namaste! Main aapka AI assistant hoon. Main aapki kya madad kar sakta hoon?"
                elif "kaise ho" in text:
                    reply = "Main ek bot hoon, bilkul mast! Aap bataiye?"
                elif "price" in text:
                    reply = "Hamari services ka price 500 rupaye se shuru hota hai."
                elif "nirma" in text:
                    reply = "Ji haan, hamare paas nirma detergent uplabdh hai."
                else:
                    reply = f"Mujhe aapka message mila: '{text}'. Main abhi seekh raha hoon!"
                
                send_reply(sender_id, reply)
        except Exception as e:
            print(f"Error: {e}")
        return "OK", 200
