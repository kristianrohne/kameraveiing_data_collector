#!/usr/bin/env python3
"""
Setup script for Kameraveiing Data Collector
Run this to initialize the database
"""

import os
import sys
sys.path.append('.')

from models import init_db, SessionLocal, User

def setup_database():
    """Initialize the database and show configuration"""
    print("🐷 Kameraveiing Data Collector - Database Setup")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Check users and configuration
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        admin_count = db.query(User).filter(User.is_admin == True).count()
        
        print(f"📊 Users: {user_count}, Admins: {admin_count}")
        
        if admin_count == 0:
            print("⚠️  No admins found. After first login, run:")
            print("   UPDATE users SET is_admin = true WHERE email = 'your@email.com';")
        
        # Show OAuth config
        client_id = os.getenv('ANIMALIA_CLIENT_ID')
        environment = os.getenv('ANIMALIA_ENVIRONMENT', 'staging')
        
        print(f"\n🔐 OAuth Config:")
        print(f"   Client ID: {'✅ Set' if client_id else '❌ Missing'}")
        print(f"   Environment: {environment}")
        
        print(f"\n🚀 Next: python3 app.py")
        
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
