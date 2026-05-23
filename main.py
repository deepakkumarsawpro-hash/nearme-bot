# send_response function ke andar ye naya logic add karein:

    elif "user_location_received" in text:
        payload = {
            "messaging_product": "whatsapp", "to": to, "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Categories Chunie"},
                "body": {"text": "Location mil gayi! Please niche di gayi categories mein se chunein (Aap ek ya ek se adhik chun sakte hain):"},
                "action": {
                    "button": "Categories Dekhein",
                    "sections": [
                        {
                            "title": "1. Construction & Home",
                            "rows": [
                                {"id": "mason", "title": "Mason (मिस्त्री)"},
                                {"id": "architect", "title": "Architect/Designer"},
                                {"id": "plumber", "title": "Plumber"},
                                {"id": "electrician", "title": "Electrician"},
                                {"id": "carpenter", "title": "Carpenter"},
                                {"id": "paint_hardware", "title": "Paint & Hardware"}
                            ]
                        },
                        {
                            "title": "2. Automotive & Logistics",
                            "rows": [
                                {"id": "mechanic", "title": "Mechanic"},
                                {"id": "spare_parts", "title": "Spare Parts"},
                                {"id": "transport", "title": "Transport"},
                                {"id": "courier", "title": "Courier"}
                            ]
                        },
                        {
                            "title": "3. Food & Hospitality",
                            "rows": [
                                {"id": "restaurant", "title": "Restaurant/Dhaba"},
                                {"id": "catering", "title": "Catering/Events"},
                                {"id": "bakery", "title": "Bakery/Dairy"}
                            ]
                        },
                        {
                            "title": "4. Retail & Daily Needs",
                            "rows": [
                                {"id": "grocery", "title": "Grocery/Kirana"},
                                {"id": "electronics", "title": "Electronics"},
                                {"id": "fashion", "title": "Fashion/Tailor"},
                                {"id": "stationery", "title": "Stationery/Printing"}
                            ]
                        },
                        {
                            "title": "5. Others",
                            "rows": [
                                {"id": "health", "title": "Healthcare/Clinic"},
                                {"id": "education", "title": "Coaching/Tutor"},
                                {"id": "personal", "title": "Salon/Beauty/Cleaning"},
                                {"id": "agri", "title": "Agriculture/Farming"}
                            ]
                        }
                    ]
                }
            }
        }
