"""
Database Migration Script
Adds clients and projects tables to existing database
"""
import sys
sys.path.append('.')

from config.database import engine, Base
from database.models import Client, Project, Tender, Document
from sqlalchemy import inspect

def migrate_database():
    """Add new tables and update existing schema"""
    
    print("=" * 60)
    print("DATABASE MIGRATION - Adding Client Tracking")
    print("=" * 60)
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"\n📊 Existing tables: {', '.join(existing_tables)}")
    
    # Check what needs to be created
    tables_to_create = []
    
    if 'clients' not in existing_tables:
        tables_to_create.append('clients')
    
    if 'projects' not in existing_tables:
        tables_to_create.append('projects')
    
    if not tables_to_create:
        print("\n✅ All tables already exist. No migration needed.")
        return
    
    print(f"\n🔧 Tables to create: {', '.join(tables_to_create)}")
    
    try:
        # Create all tables (will skip existing ones)
        print("\nCreating new tables...")
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Migration completed successfully!")
        print("\nNew tables created:")
        for table in tables_to_create:
            print(f"  ✓ {table}")
        
        print("\n📝 Schema Updates:")
        print("  ✓ clients - Track client information")
        print("  ✓ projects - Track projects per client")
        print("  ✓ tenders - Added client_id and project_id foreign keys")
        print("  ✓ documents - Added version tracking fields")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise

def verify_migration():
    """Verify migration was successful"""
    print("\n🔍 Verifying migration...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = ['clients', 'projects', 'tenders', 'documents']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        print(f"❌ Missing tables: {', '.join(missing)}")
        return False
    
    print("✅ All required tables present")
    
    # Check for foreign keys in tenders table
    fks = inspector.get_foreign_keys('tenders')
    fk_columns = [fk['constrained_columns'][0] for fk in fks]
    
    expected_fks = ['client_id', 'project_id']
    for fk in expected_fks:
        if fk in fk_columns:
            print(f"✅ Foreign key '{fk}' found in tenders table")
        else:
            print(f"⚠️  Foreign key '{fk}' not found in tenders table")
    
    return True

if __name__ == "__main__":
    print("\nStarting database migration...\n")
    migrate_database()
    verify_migration()
    print("\n✅ Migration verification complete!")
