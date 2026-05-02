import sys
import os
sys.path.append('.')

from database.connection import SessionLocal
from database.models import Tag

def init_default_tags():
    print("Initializing default tags...")
    db = SessionLocal()
    
    default_tags = [
        {"name": "Urgent", "color": "#ef4444"},        # Red
        {"name": "Procurement", "color": "#f97316"},           # Orange
        {"name": "Missing Info", "color": "#eab308"},  # Yellow
        {"name": "Technical", "color": "#3b82f6"},     # Blue
        {"name": "Commercial", "color": "#10b981"},    # Green
        {"name": "Approved", "color": "#22c55e"},      # Emerald
        {"name": "Follow-up", "color": "#8b5cf6"},      # Violet
    ]
    
    try:
        for tag_data in default_tags:
            # Check if tag already exists
            existing = db.query(Tag).filter(Tag.name == tag_data['name']).first()
            if not existing:
                new_tag = Tag(name=tag_data['name'], color=tag_data['color'])
                db.add(new_tag)
                print(f"  [+] Added tag: {tag_data['name']}")
            else:
                print(f"  [--] Tag already exists: {tag_data['name']}")
        
        db.commit()
        print("Initialization complete.")
    except Exception as e:
        print(f"Error initializing tags: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_default_tags()
