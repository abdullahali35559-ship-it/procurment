"""
Initialize PostgreSQL database with schema
"""

import sys
sys.path.append('.')

from config.database import init_db, engine
from sqlalchemy import text

def create_schema():
    """Create database schema"""
    
    print("Creating database schema...")
    
    # Initialize tables
    init_db()
    
    print("✅ Database schema created successfully!")
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection test passed!")

if __name__ == "__main__":
    create_schema()
