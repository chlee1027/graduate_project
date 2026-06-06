import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import User, ExercisePlan, ExerciseLog, Recommendation, BanditStat, Base

# 가상 데이터 생성 설정
NUM_USERS = 100
SIMULATION_DAYS = 50

def generate_simulation_data():
    db: Session = SessionLocal()
    try:
        # 기존 데이터 초기화 (선택 사항 - 발표용으로 깨끗하게 시작)
        print("Cleaning up old simulation data...")
        db.query(ExerciseLog).delete()
        db.query(Recommendation).delete()
        db.query(BanditStat).delete()
        db.query(User).delete()
        db.commit()

        # 1. 가상 유저 100명 생성
        print(f"Generating {NUM_USERS} virtual users...")
        users = []
        goals = ["diet", "muscle", "health"]
        levels = ["beginner", "intermediate", "advanced"]
        places = ["home", "gym"]
        
        for i in range(NUM_USERS):
            user_id = f"user_{i:03d}"
            user = User(
                user_id=user_id,
                age=random.randint(20, 50),
                sex=random.choice(["M", "F"]),
                height_cm=random.uniform(160, 190),
                weight_kg=random.uniform(50, 90),
                goal=random.choice(goals),
                experience_level=random.choice(levels),
                weekly_available_days=random.randint(3, 6),
                place_preference=random.choice(places)
            )
            users.append(user)
            db.add(user)
        db.commit()

        # 2. 운동 플랜 목록 가져오기
        plans = db.query(ExercisePlan).all()
        if not plans:
            print("No exercise plans found. Please run seed_db.py first.")
            return

        # 3. 50일간의 로그 시뮬레이션
        print(f"Simulating {SIMULATION_DAYS} days of logs for each user...")
        start_date = datetime.now() - timedelta(days=SIMULATION_DAYS)
        
        log_count = 0
        for day in range(SIMULATION_DAYS):
            current_date = start_date + timedelta(days=day)
            
            for user in users:
                # 매일 운동할 확률 (주당 가용 일수 기반)
                if random.random() > (user.weekly_available_days / 7):
                    continue
                
                # 유저 취향에 맞는 운동 선택 (간단한 시뮬레이션)
                # 실제 앱에서는 추천 알고리즘을 거치지만, 여기서는 랜덤+취향 가중치로 생성
                suitable_plans = [p for p in plans if p.location == user.place_preference]
                if not suitable_plans: suitable_plans = plans
                
                selected_plan = random.choice(suitable_plans)
                
                # 추천 기록 생성
                rec_id = f"rec_{user.user_id}_{day}"
                rec = Recommendation(
                    recommendation_id=rec_id,
                    user_id=user.user_id,
                    state_json="{}", # 시뮬레이션용 단순화
                    selected_plan_json="{}", 
                    reason="시뮬레이션 생성 데이터",
                    created_at=current_date
                )
                db.add(rec)
                db.flush() # Foreign Key 제약 조건 위반 방지를 위해 flush
                
                # 운동 로그 생성
                # 초보자는 가끔 실패(completed=False)할 수도 있게 설정
                completed = True if user.experience_level != "beginner" else (random.random() > 0.1)
                
                log = ExerciseLog(
                    recommendation_id=rec.recommendation_id,
                    user_id=user.user_id,
                    plan_id=selected_plan.plan_id,
                    completed=completed,
                    actual_minutes=selected_plan.minutes + random.randint(-2, 5),
                    actual_sets=selected_plan.sets,
                    actual_reps=selected_plan.reps,
                    rpe=random.uniform(5, 9),
                    pain_occurred=False,
                    created_at=current_date
                )
                db.add(log)
                log_count += 1
            
            # 매일 단위로 커밋 (안정성)
            db.commit()
            if day % 10 == 0:
                print(f"Simulated up to day {day}...")

        db.commit()
        print(f"Simulation complete! Generated {log_count} logs for {NUM_USERS} users.")

    except Exception as e:
        print(f"Error during simulation: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_simulation_data()
