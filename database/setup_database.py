"""
Create Database and Tables for Procurement Agent
Run this script to setup the database
"""

import sys
sys.path.append('.')

from database.connection import engine, Base, SessionLocal
from database.models import Client, Tender, Document, Project
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create all database tables"""
    
    print("=" * 60)
    print("Procurement Agent - Database Setup")
    print("=" * 60)
    
    print("\n[1/3] Checking database connection...")
    try:
        # Test connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database 'procurement_multi_agent_db' exists")
        print("3. Credentials in .env are correct")
        return False
    
    print("\n[2/3] Creating tables...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("[OK] Tables created successfully")
    except Exception as e:
        print(f"[ERROR] Table creation failed: {e}")
        return False
    
    print("\n[3/3] Verifying tables...")
    try:
        db = SessionLocal()
        
        # Check each table with new generic names
        tables = ['contacts', 'topics', 'threads', 'attachments', 'emails', 'users']
        for table in tables:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            print(f"  [DB] {table}: {count} records")
        
        db.close()
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Database is ready to use")
    print("2. Start the backend: python api/main.py")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = create_database()
    
    if not success:
        print("\n[ALERT] Setup failed. Please fix errors and try again.")
        sys.exit(1)
    else:
        print("System is now ready.")
        sys.exit(0)
