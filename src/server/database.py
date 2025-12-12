# src/server/database.py



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# -----------------------------
# DATABASE URL
# -----------------------------
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# -----------------------------
# ENGINE & SESSION
# -----------------------------
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Base class for models
Base = declarative_base()

# -----------------------------
# IMPORT MODELS HERE
# -----------------------------
# IMPORTANT: this must come AFTER Base = declarative_base()

from .models.user import User     # ⬅️ REQUIRED
# If you add more models later:
# from .models.event import Event
# from .models.availability import Availability

# -----------------------------
# CREATE ALL TABLES
# -----------------------------
def init_db():
    """Creates database tables if they don’t exist."""
    print("📌 Creating PostgreSQL tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready!")
# -----------------------------
# RAW CONNECTION TEST
# -----------------------------
def get_connection():
    try:
        conn = engine.raw_connection()
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# -----------------------------
# DB SESSION GENERATOR
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
