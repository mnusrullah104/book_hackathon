from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    FRONTEND_URL: str = "https://your-app.vercel.app"

settings = Settings()

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database tables
def init_db():
    from .user import User
    from .session import Session as SessionModel
    Base.metadata.create_all(bind=engine)
