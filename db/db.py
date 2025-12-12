import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        print("✅ Connected to PostgreSQL successfully!")
        return conn
    except Exception as e:
        print("❌ Error connecting to PostgreSQL:", e)
        return None
