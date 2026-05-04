from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from db.models import Base
import os

os.makedirs("data", exist_ok=True)
DB_FILE = os.environ.get("STUDYVISTA_DB", "data/study_tracker.db")

engine = create_engine(
    f"sqlite:///{DB_FILE}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# --- Lightweight migration for existing DBs ---
# Add new columns if they don't already exist
_inspector = inspect(engine)

if _inspector.has_table("study_logs"):
    existing_cols = {col["name"] for col in _inspector.get_columns("study_logs")}
    with engine.connect() as conn:
        if "notes" not in existing_cols:
            conn.execute(text("ALTER TABLE study_logs ADD COLUMN notes TEXT DEFAULT ''"))
            conn.commit()
        if "created_at" not in existing_cols:
            conn.execute(text("ALTER TABLE study_logs ADD COLUMN created_at DATETIME"))
            conn.commit()

if _inspector.has_table("users"):
    existing_cols = {col["name"] for col in _inspector.get_columns("users")}
    with engine.connect() as conn:
        if "created_at" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
            conn.commit()
