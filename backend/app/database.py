from typing import Generator
from app.db.base import SessionLocal, engine

def get_db() -> Generator:
    """
    Create a database session and ensure it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()