import sys
import os
sys.path.append('.')

from config.database import init_db

if __name__ == "__main__":
    print("Explicitly initializing database schema...")
    init_db()
    print("Schema initialized successfully.")
