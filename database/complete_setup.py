"""
Complete Database Setup - Creates database & tables
Run this to setup everything from scratch
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# PostgreSQL connection details
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "Pakistan@1234"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
DATABASE_NAME = "tender_system_db"

def create_database():
    """Create the database if it doesn't exist"""
    
    print("=" * 60)
    print("Procurement Agent - Complete Database Setup")
    print("=" * 60)
    
    print("\n[1/5] Connecting to PostgreSQL...")
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL service is running")
        print("2. Password is correct: Pakistan@1234")
        print("3. Port 5432 is accessible")
        return False
    
    print("\n[2/5] Checking if database exists...")
    try:
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DATABASE_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{DATABASE_NAME}' already exists")
        else:
            print(f"Creating database '{DATABASE_NAME}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DATABASE_NAME)
                )
            )
            print(f"✅ Database '{DATABASE_NAME}' created")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        cursor.close()
        conn.close()
        return False
    
    cursor.close()
    conn.close()
    
    print("\n[3/5] Connecting to tender_system_db...")
    try:
        # Now connect to our database
        conn = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=DATABASE_NAME
        )
        cursor = conn.cursor()
        print("✅ Connected to tender_system_db")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    print("\n[4/5] Creating tables...")
    try:
        # Now use SQLAlchemy to create tables
        sys.path.append('.')
        from config.database import Base, engine
        
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        cursor.close()
        conn.close()
        return False
    
    print("\n[5/5] Verifying setup...")
    try:
        tables = ['clients', 'projects', 'tenders', 'documents']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} records")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print("\nDatabase: tender_system_db")
        print("Tables: clients, projects, tenders, documents")
        print("\nNext: Run .\\process_emails.bat")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return True

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
