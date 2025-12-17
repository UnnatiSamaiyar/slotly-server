# src/server/database.py



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# IMPORT MODELS (IMPORTANT)
from .models.user import User

def init_db():
    """Run ONCE manually"""
    print("📌 Creating PostgreSQL tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready!")

def get_connection():
    try:
        conn = engine.raw_connection()
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
