"""
Database Migration - Add Version Tracking Columns
Adds missing columns to documents table for version tracking
"""
import sys
sys.path.append('.')

from config.database import engine
from sqlalchemy import text

def add_version_columns():
    """Add version tracking columns to documents table"""
    
    print("=" * 60)
    print("DATABASE MIGRATION - Add Version Tracking Columns")
    print("=" * 60)
    
    with engine.connect() as conn:
        try:
            print("\nAdding columns to documents table...")
            
            # Add previous_version_id column
            try:
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN previous_version_id INTEGER REFERENCES documents(id)
                """))
                print("  ✓ Added previous_version_id column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  ⚠️  previous_version_id already exists")
                else:
                    raise
            
            # Add version_reason column
            try:
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN version_reason TEXT
                """))
                print("  ✓ Added version_reason column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  ⚠️  version_reason already exists")
                else:
                    raise
            
            # Add replaced_at column
            try:
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN replaced_at TIMESTAMP
                """))
                print("  ✓ Added replaced_at column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  ⚠️  replaced_at already exists")
                else:
                    raise
            
            conn.commit()
            
            print("\n✅ Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("\nStarting database migration...\n")
    add_version_columns()
    print("\n✅ Migration complete!")
