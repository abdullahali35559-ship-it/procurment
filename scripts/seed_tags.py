from database.connection import SessionLocal
from database.models import Tag

def seed_tags():
    db = SessionLocal()
    default_tags = [
        {"name": "Client", "color": "#2563eb"},
        {"name": "Vendor", "color": "#7c3aed"},
        {"name": "Inquiry", "color": "#10b981"},
        {"name": "Urgent", "color": "#ef4444"},
        {"name": "Internal", "color": "#6b7280"},
        {"name": "Meeting", "color": "#f59e0b"},
        {"name": "Payment", "color": "#ec4899"}
    ]
    
    for tag_data in default_tags:
        exists = db.query(Tag).filter(Tag.name == tag_data['name']).first()
        if not exists:
            new_tag = Tag(**tag_data)
            db.add(new_tag)
            print(f"Added tag: {tag_data['name']}")
    
    db.commit()
    db.close()
    print("Done seeding tags.")

if __name__ == "__main__":
    seed_tags()
