from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)

def check_columns():
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT is_correct, rejection_reason FROM documents LIMIT 1"))
            print("Columns is_correct and rejection_reason exist.")
        except Exception as e:
            print(f"Error: {e}")
            if "column \"is_correct\" does not exist" in str(e):
                print("Columns is_correct and rejection_reason are missing. Adding them...")
                try:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN is_correct BOOLEAN DEFAULT TRUE"))
                    conn.execute(text("ALTER TABLE documents ADD COLUMN rejection_reason TEXT"))
                    conn.commit()
                    print("Successfully added columns.")
                except Exception as ex:
                    print(f"Failed to add columns: {ex}")
            else:
                print("An error occurred but it's not the missing columns error.")

if __name__ == "__main__":
    check_columns()
