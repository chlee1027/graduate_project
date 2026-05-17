from sqlalchemy import text
from app.db.database import SessionLocal, engine

def migrate():
    print("Starting database migration...")
    with engine.connect() as conn:
        # Check if columns exist first (optional but safer)
        try:
            conn.execute(text("ALTER TABLE exercise_logs ADD COLUMN pain_parts TEXT"))
            print("Added column 'pain_parts' to 'exercise_logs'")
        except Exception as e:
            print(f"Column 'pain_parts' might already exist or error occurred: {e}")

        try:
            conn.execute(text("ALTER TABLE exercise_logs ADD COLUMN pain_severity VARCHAR"))
            print("Added column 'pain_severity' to 'exercise_logs'")
        except Exception as e:
            print(f"Column 'pain_severity' might already exist or error occurred: {e}")
            
        conn.commit()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
