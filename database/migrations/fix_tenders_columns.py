import sys
sys.path.append('.')

from sqlalchemy import text
from config.database import engine

def migrate():
    print(f"Connecting to database using SQLAlchemy engine...")
    
    try:
        with engine.connect() as conn:
            print("\n🔧 Adding missing columns to 'tenders' table...")
            
            # Check existing columns
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tenders'"))
            existing_columns = [row[0] for row in result]
            
            updates = []
            
            # Use raw SQL to alter the table
            if 'client_id' not in existing_columns:
                print("  ➡️ Adding 'client_id' column...")
                conn.execute(text("ALTER TABLE tenders ADD COLUMN client_id INTEGER REFERENCES clients(id)"))
                updates.append("client_id")
                
            if 'project_id' not in existing_columns:
                print("  ➡️ Adding 'project_id' column...")
                conn.execute(text("ALTER TABLE tenders ADD COLUMN project_id INTEGER REFERENCES projects(id)"))
                updates.append("project_id")
            
            conn.commit()
            
            if updates:
                print(f"\n✅ Successfully added columns: {', '.join(updates)}")
            else:
                print("\n✅ All columns already exist. No updates needed.")
                
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate()
