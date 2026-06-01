from app.db.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        print("Adding sub_target_parts column to exercise_plans table...")
        try:
            conn.execute(text("ALTER TABLE exercise_plans ADD COLUMN sub_target_parts TEXT"))
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed or column already exists: {e}")

if __name__ == "__main__":
    migrate()
