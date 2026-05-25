import os
import psycopg2
import redis
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    return conn

def get_redis_connection():
    r = redis.from_url(os.getenv('REDIS_URL'))
    return r

def test_connections():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        cur.close()
        conn.close()
        
        r = get_redis_connection()
        r.ping()
        return True
    except Exception as e:
        print(f"Connection error: {e}")
        return False
