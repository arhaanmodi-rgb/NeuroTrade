import os
import sqlite3
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 1. Detect Database URL from Environment or Default to Local SQLite
ENV_DB_URL = os.getenv("DATABASE_URL", "").strip()

if ENV_DB_URL:
    # Fix postgres:// to postgresql:// for compatibility with Render/Supabase/Railway
    if ENV_DB_URL.startswith("postgres://"):
        DATABASE_URL = ENV_DB_URL.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = ENV_DB_URL
else:
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, 'neurotrade.db')
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# 2. Configure SQLAlchemy Engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL / Cloud Engine with connection pooling & ping
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def apply_migrations():
    """Ensure newly added columns exist in SQLite or create tables in Cloud DB."""
    if DATABASE_URL.startswith("sqlite"):
        DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        db_file = os.path.join(DB_DIR, 'neurotrade.db')
        if not os.path.exists(db_file):
            return
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            # Add target_price and stop_loss to user_holdings if missing
            try:
                cursor.execute("ALTER TABLE user_holdings ADD COLUMN target_price REAL")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE user_holdings ADD COLUMN stop_loss REAL")
            except Exception:
                pass
            # Add target_price and stop_loss to user_trades if missing
            try:
                cursor.execute("ALTER TABLE user_trades ADD COLUMN target_price REAL")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE user_trades ADD COLUMN stop_loss REAL")
            except Exception:
                pass
            conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
