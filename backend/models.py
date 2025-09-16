# models.py
from datetime import datetime
from sqlalchemy import create_engine, String, Float, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import uuid
import os

# Database configuration
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/app.db')

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    farmer_id: Mapped[str] = mapped_column(String(20))  # The user-friendly ID like "farmer_abc123"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Upload(Base):
    __tablename__ = "uploads"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    pig_uid: Mapped[str] = mapped_column(String(20))               # Pig unique identifier
    user_id: Mapped[str] = mapped_column(String(20))              # Farmer/User ID (now references User.farmer_id)
    picture_number: Mapped[int] = mapped_column()                 # Picture number for this pig
    filename: Mapped[str] = mapped_column(String(512))             # relative path under uploads/
    weight_kg: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(engine)