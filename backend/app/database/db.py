from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use environment variable for database path if set, otherwise use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "./inventory.db")
# Convert to absolute path and ensure it uses forward slashes for SQLite
if DATABASE_PATH.startswith("./"):
    DATABASE_PATH = DATABASE_PATH[2:]
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
