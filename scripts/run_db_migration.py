from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)

def run_migration():
    print(f"Connecting to {DATABASE_URL}")
    with engine.begin() as conn:
        print("Checking/Adding columns to 'documents' table...")
        # PostgreSQL syntax for adding columns if they don't exist
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_correct BOOLEAN DEFAULT TRUE"))
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS rejection_reason TEXT"))
        print("Migration complete!")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"Migration failed: {e}")
