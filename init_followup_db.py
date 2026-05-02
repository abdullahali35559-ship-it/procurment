import sys
import os
from sqlalchemy import create_engine, text

sys.path.append(os.getcwd())
from config.settings import DATABASE_URL
from database.models import Base

def init_followup_schema():
    engine = create_engine(DATABASE_URL)
    
    print("Initialising new schema components...")
    
    # 1. Create new table
    Base.metadata.create_all(engine)
    
    # 2. Add column to existing table (if not exists)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE emails ADD COLUMN is_sent BOOLEAN DEFAULT FALSE"))
            print("Added 'is_sent' column to 'emails' table.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("'is_sent' column already exists.")
            else:
                print(f"Error adding 'is_sent': {e}")
        
        try:
            conn.execute(text("ALTER TABLE draft_replies ADD COLUMN scheduled_at TIMESTAMP"))
            print("Added 'scheduled_at' column to 'draft_replies' table.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("'scheduled_at' column already exists.")
            else:
                print(f"Error adding 'scheduled_at': {e}")
        
        conn.commit()
    
    print("Database initialisation complete.")

if __name__ == "__main__":
    init_followup_schema()
