from sqlalchemy import text
from database.connection import engine
from database.models import Base

def migrate():
    print("Starting migration...")
    with engine.connect() as conn:
        # 1. Create new table
        print("Creating new tables if not exist...")
        Base.metadata.create_all(bind=engine)
        
        # 2. Add column to existing table
        try:
            print("Adding conversation_id to assistant_chat...")
            conn.execute(text("ALTER TABLE assistant_chat ADD COLUMN conversation_id INTEGER REFERENCES assistant_conversations(id)"))
            conn.commit()
            print("Successfully added conversation_id")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Column conversation_id already exists.")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    migrate()
