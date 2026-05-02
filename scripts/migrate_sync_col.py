import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import engine
from sqlalchemy import text

def migrate():
    print("Running migration for last_style_sync...")
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS last_style_sync TIMESTAMP;'))
            conn.commit()
            print("SUCCESS: last_style_sync column added.")
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    migrate()
