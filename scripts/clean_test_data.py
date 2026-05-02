"""
Clean test data from database
"""
import sys
sys.path.append('.')

from database.connection import engine
from sqlalchemy import text

def clean_test_data():
    """Remove test tender data"""
    print("=" * 60)
    print("CLEANING TEST DATA")
    print("=" * 60)
    print()
    
    with engine.connect() as conn:
        try:
            # Delete test tender documents
            result = conn.execute(text("DELETE FROM documents WHERE tender_id LIKE 'TND-2026-%'"))
            print(f"✅ Deleted {result.rowcount} document(s)")
            
            # Delete test tenders
            result = conn.execute(text("DELETE FROM tenders WHERE tender_id LIKE 'TND-2026-%'"))
            print(f"✅ Deleted {result.rowcount} tender(s)")
            
            # Delete test projects
            result = conn.execute(text("DELETE FROM projects WHERE tender_id LIKE 'TND-2026-%'"))
            print(f"✅ Deleted {result.rowcount} project(s)")
            
            # Delete test clients (optional)
            # result = conn.execute(text("DELETE FROM clients WHERE client_name = 'Neom'"))
            # print(f"✅ Deleted {result.rowcount} client(s)")
            
            conn.commit()
            
            print("\n✅ Database cleaned successfully!")
            
        except Exception as e:
            print(f"\n❌ Error cleaning database: {e}")
            conn.rollback()

if __name__ == "__main__":
    clean_test_data()
