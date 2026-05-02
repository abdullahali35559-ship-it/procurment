import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # Default 'postgres' database se connect karein
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Pakistan@1234',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Database create karne ki query (spaces ki wajah se double quotes zaroori hain)
        db_name = "general email reply"
        cur.execute(f'CREATE DATABASE "{db_name}"')
        
        print(f"✅ Database '{db_name}' created successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        if "already exists" in str(e):
            print(f"ℹ️ Database 'general email reply' already exists.")
        else:
            print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    create_database()
