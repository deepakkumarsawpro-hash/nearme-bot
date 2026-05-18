const express = require('express');
const axios = require('axios');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

// MongoDB Setup
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('MongoDB Connected...'))
  .catch(err => console.log(err));

// Webhook Verification for Meta/WhatsApp
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];
    if (mode && token === process.env.VERIFY_TOKEN) {
        res.status(200).send(challenge);
    } else {
        res.sendStatus(403);
    }
});

// Incoming WhatsApp Messages
app.post('/webhook', async (req, res) => {
    res.sendStatus(200); // Meta को तुरंत रिप्लाई दें
    const body = req.body;
    if (body.object === 'whatsapp_business_account' && body.entry?.[0]?.changes?.[0]?.value?.messages?.[0]) {
        const msg = body.entry[0].changes[0].value.messages[0];
        const from = msg.from; // यूज़र का नंबर
        const text = msg.text?.body;

        if (text) {
            console.log(`Message from ${from}: ${text}`);
            // यहाँ से आगे हम सेलर/बायर का डेटा मोंगो-डीबी में सेव करेंगे
        }
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`NearMe Bot is running on port ${PORT}`));
