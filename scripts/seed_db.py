from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import ExercisePlan, Base
from app.data.exercise_catalog import FINAL_EXERCISES

# Recreate tables to apply new schema
ExercisePlan.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(bind=engine)

def seed_data():
    db: Session = SessionLocal()
    try:
        db.query(ExercisePlan).delete()
        db.commit()
        
        for ex_data in FINAL_EXERCISES:
            existing = db.query(ExercisePlan).filter(ExercisePlan.plan_id == ex_data["plan_id"]).first()
            if not existing:
                new_plan = ExercisePlan(**ex_data)
                db.add(new_plan)
        
        db.commit()
        print(f"Successfully seeded {db.query(ExercisePlan).count()} exercises.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
