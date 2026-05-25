import os
import requests
from flask import Flask, request
import psycopg
import redis
import json

app = Flask(__name__)

# =====================================================
# DATABASE + REDIS CONNECTION
# =====================================================
def get_db_connection():
    conn = psycopg.connect(os.getenv('DATABASE_URL'))
    return conn

def get_redis_connection():
    return redis.from_url(os.getenv('REDIS_URL'))

def get_redis():
    return redis.from_url(os.getenv('REDIS_URL'))

# =====================================================
# WHATSAPP CONFIG
# =====================================================

PHONE_ID = "1060745180462931"
TOKEN = "EAAMEDcGznz0BRsu61oQ6fDQDSLZC5fSSFHZCc0T563L09RZC6bZC2pPp0IuSRb5MWVSKHhfnbqaWVfcvZA8VqXfY4vm2SmZBBhuU7PpUHbZCCJRTpugaLqdPcbs4moBPtpqxtaOmYtOZCZBPdd1TYIeNLLczx9svvHOazqCy5ah3UHCiGrC169ZBNlk61JOsWO1XVtsgZDZD"
VERIFY_TOKEN = "my_secret_token_123"

# =====================================================
# FULL CATEGORY DATA
# =====================================================

categories = {
    "construction": {
        "title": "Construction",
        "subs": {
            "Mason": "नींव, ईंट जुड़ाई, प्लास्टर, टाइल्स",
            "Architect": "नक्शा, इंटीरियर डिजाइन, 3D व्यू",
            "Plumber": "पाइप लीकेज, मोटर, टैप फिटिंग",
            "Electrician": "वायरिंग
