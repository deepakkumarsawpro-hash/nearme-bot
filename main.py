const express = require('express');
const axios = require('axios');
const fs = require('fs');
const app = express();
app.use(express.json());

const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;
const PHONE_NUMBER_ID = process.env.PHONE_NUMBER_ID;
const VERIFY_TOKEN = process.env.VERIFY_TOKEN;

const DB_FILE = 'users.json';
if (!fs.existsSync(DB_FILE)) fs.writeFileSync(DB_FILE, '{}');

// Category Data
const CATEGORIES = {
  customer: [
    { id: "grocery", title: "Kirana/Grocery" },
    { id: "medical", title: "Medical/Pharmacy" },
    { id: "electronics", title: "Electronics" },
    { id: "clothes", title: "Kapde/Fashion" }
  ],
  provider: [
    { id: "electrician", title: "Electrician" },
    { id: "plumber", title: "Plumber" },
    { id: "carpenter", title: "Carpenter" },
    { id: "ac_repair", title: "AC Repair" }
  ]
};

function getUser(number) {
  const db = JSON.parse(fs.readFileSync(DB_FILE));
  return db[number] || { step: 1, role: null, data: {} };
}

function saveUser(number, data) {
  const db = JSON.parse(fs.readFileSync(DB_FILE));
  db[number] = {...getUser(number),...data, updated: new Date().toISOString() };
  fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2));
}

// Button bhejne ka function
async function sendButtons(to, bodyText, buttons) {
  await axios.post(`https://graph.facebook.com/v20.0/${PHONE_NUMBER_ID}/messages`, {
    messaging_product: 'whatsapp',
    to: to,
    type: 'interactive',
    interactive: {
      type: 'button',
      body: { text: bodyText },
      action: { buttons: buttons }
    }
  }, { headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` } });
}

// List bhejne ka function 
async function sendList(to, bodyText, buttonText, sections) {
  await axios.post(`https://graph.facebook.com/v20.0/${PHONE_NUMBER_ID}/messages`, {
    messaging_product: 'whatsapp',
    to: to,
    type: 'interactive',
    interactive: {
      type: 'list',
      body: { text: bodyText },
      action: { button: buttonText, sections: sections }
    }
  }, { headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` } });
}

async function sendText(to, text) {
  await axios.post(`https://graph.facebook.com/v20.0/${PHONE_NUMBER_ID}/messages`, {
    messaging_product: 'whatsapp',
    to: to,
    text: { body: text }
  }, { headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` } });
}

app.get('/webhook', (req, res) => {
  if (req.query['hub.verify_token'] === VERIFY_TOKEN) {
    res.send(req.query['hub.challenge']);
  } else {
    res.sendStatus(403);
  }
});

app.post('/webhook', async (req, res) => {
  const entry = req.body.entry?.[0]?.changes?.[0]?.value;
  const msg = entry?.messages?.[0];

  if (msg) {
    const from = msg.from;
    const user = getUser(from);
    
    // Button/List reply handle karna
    let msg_body = '';
    if (msg.type === 'text') msg_body = msg.text.body;
    if (msg.type === 'interactive') {
      if (msg.interactive.type === 'button_reply') msg_body = msg.interactive.button_reply.id;
      if (msg.interactive.type === 'list_reply') msg_body = msg.interactive.list_reply.id;
    }
    
    console.log('Step:', user.step, 'Msg:', msg_body);

    // STEP 1: WELCOME - Koi bhi message pe
    if (user.step === 1) {
      saveUser(from, { step: 2 });
      await sendButtons(from, 
        `Welcome to NearMe 🙏\n\nAap kaun hai?`,
        [
          { type: 'reply', reply: { id: 'role_customer', title: '👤 Customer' } },
          { type: 'reply', reply: { id: 'role_provider', title: '🏪 Provider' } }
        ]
      );
    
    // STEP 2: ROLE BRANCHING
    } else if (user.step === 2) {
      if (msg_body === 'role_customer') {
        saveUser(from, { step: 3, role: 'customer' });
        await sendText(from, `Kitne KM ke andar dukaan chahiye?\n\nJaise: 2km, 5km ya 10km likho`);
      
      } else if (msg_body === 'role_provider') {
        saveUser(from, { step: 3, role: 'provider' });
        await sendText(from, `Apni Shop/Business ka naam kya hai?\n\nType karke bhejo`);
      }
    
    // STEP 3: LOCATION
    } else if (user.step === 3) {
      if (user.role === 'customer') {
        saveUser(from, { step: 4, data: { distance: msg_body } });
        await sendText(from, `📍 Apna Current Location bhejo\n\n📎 icon → Location → "Send current location" dabao`);
      
      } else if (user.role === 'provider') {
        saveUser(from, { step: 4, data: { shop_name: msg_body } });
        await sendText(from, `📍 Shop ka Location bhejo\n\n📎 icon → Location bhejo ya Google Maps link paste karo`);
      }
    
    // STEP 4: CATEGORY - List format
    } else if (user.step === 4 && msg.type === 'location') {
      saveUser(from, { 
        step: 5, 
        data: {...user.data, lat: msg.location.latitude, lng: msg.location.longitude }
      });
      
      const cats = user.role === 'customer'? CATEGORIES.customer : CATEGORIES.provider;
      await sendList(from,
        `Category choose karo:`,
        `Categories`,
        [{ title: 'Available Options', rows: cats }]
      );
    
    // STEP 5: SUB-CATEGORY 
    } else if (user.step === 5) {
      saveUser(from, { step: 6, data: {...user.data, category: msg_body } });
      await sendButtons(from,
        `Sub-Category select karo ya 'Other' dabao:`,
        [
          { type: 'reply', reply: { id: 'sub_1', title: 'Option 1' } },
          { type: 'reply', reply: { id: 'sub_2', title: 'Option 2' } },
          { type: 'reply', reply: { id: 'sub_other', title: 'Other' } }
        ]
      );
    
    // STEP 6: DATA CAPTURE - Other Info
    } else if (user.step === 6) {
      saveUser(from, { step: 7, data: {...user.data, sub_category: msg_body } });
      await sendText(from, `Koi extra details? \n\nJaise: Timing, Special offer, etc\n\nNahi hai to 'Skip' likho`);
    
    // STEP 7: WHATSAPP NUMBER
    } else if (user.step === 7) {
      saveUser(from, { step: 8, data: {...user.data, other_info: msg_body } });
      await sendText(from, `Contact WhatsApp Number bhejo\n\n10 digit number only: 8292716185`);
    
    // STEP 8: CONFIRMATION + RESTART
    } else if (user.step === 8) {
      saveUser(from, { step: 9, data: {...user.data, contact: msg_body } });
      await sendButtons(from,
        `✅ Success! Data save ho gaya\n\nRole: ${user.role}\nCategory: ${user.data.category}\n\nDobara shuru karna hai?`,
        [{ type: 'reply', reply: { id: 'restart', title: '🔄 Restart' } }]
      );
    
    // RESTART
    } else if (msg_body === 'restart') {
      saveUser(from, { step: 1, role: null, data: {} });
      await sendButtons(from, 
        `Welcome to NearMe 🙏\n\nAap kaun hai?`,
        [
          { type: 'reply', reply: { id: 'role_customer', title: '👤 Customer' } },
          { type: 'reply', reply: { id: 'role_provider', title: '🏪 Provider' } }
        ]
      );
    }
  }
  
  res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`NearMe Bot Running`));
