# auth.py - OAuth-compatible authentication utilities
import jwt
import secrets
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User, SessionLocal
import os
from typing import Optional

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secure-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

def generate_farmer_id() -> str:
    """Generate a unique farmer ID for new users"""
    return f"F{secrets.token_hex(4).upper()}"

def create_jwt_token(user_id: str, farmer_id: str) -> str:
    """Create a JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'farmer_id': farmer_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by their UUID"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

def get_user_by_farmer_id(farmer_id: str) -> Optional[User]:
    """Get user by their farmer ID"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.farmer_id == farmer_id).first()
    finally:
        db.close()

def get_user_by_email(email: str) -> Optional[User]:
    """Get user by their email address"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def create_user_from_oauth(user_info: dict) -> User:
    """Create a new user from OAuth user information"""
    db = SessionLocal()
    try:
        # Generate unique farmer ID
        farmer_id = generate_farmer_id()
        while db.query(User).filter(User.farmer_id == farmer_id).first():
            farmer_id = generate_farmer_id()
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=user_info.get('email'),
            full_name=user_info.get('name', user_info.get('email', 'Unknown')),
            farmer_id=farmer_id,
            is_active=True,
            is_admin=False,  # New OAuth users are not admin by default
            last_login=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
        
    finally:
        db.close()
