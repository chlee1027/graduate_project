from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import ExercisePlan, Base

# Recreate tables to apply new schema (description, tip)
ExercisePlan.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(bind=engine)

SEED_EXERCISES = [
    # --- [LEGS / LOWER BODY] ---
    {
        "plan_id": "home_squat_standard", "name": "맨몸 스쿼트", "location": "home", "type": "rep-based", "required_equipment": "", 
        "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee", "intensity": "low", 
        "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 5, "rest_seconds": 60, "met_value": 5.0,
        "description": "가장 기본적인 하체 운동으로, 의자에 앉듯 엉덩이를 뒤로 빼며 내려갑니다.",
        "tip": "무릎이 발끝보다 너무 앞으로 나가지 않게 주의하고, 체중을 뒤꿈치에 실어보세요."
    },
    {
        "plan_id": "gym_squat_barbell", "name": "바벨 백 스쿼트", "location": "gym", "type": "rep-based", "required_equipment": "barbell,squat_rack", 
        "target_parts": "legs", "sub_target_parts": "quadriceps,glutes,lower_back", "avoid_if_pain": "knee,lower_back", "intensity": "high", 
        "minutes": 25, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 150, "met_value": 7.0,
        "description": "바벨을 등에 얹고 수행하는 고강도 하체 운동입니다. 전신 근력 발달에 필수적입니다.",
        "tip": "복압을 유지하여 허리가 굽지 않게 하고, 시선은 정면을 향하는 것이 좋습니다."
    },
    {
        "plan_id": "gym_leg_press", "name": "레그 프레스", "location": "gym", "type": "rep-based", "required_equipment": "leg_press_machine", 
        "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee,lower_back", "intensity": "medium", 
        "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 120, "met_value": 5.0,
        "description": "머신을 이용하여 안전하게 무거운 무게를 밀어낼 수 있는 하체 운동입니다.",
        "tip": "다리를 밀 때 무릎을 완전히 펴서 잠그지(Lock) 마세요. 관절 손상의 원인이 됩니다."
    },

    # --- [CHEST / UPPER BODY PUSH] ---
    {
        "plan_id": "home_pushup_standard", "name": "푸쉬업", "location": "home", "type": "rep-based", "required_equipment": "", 
        "target_parts": "chest", "sub_target_parts": "middle_chest,triceps,shoulder", "avoid_if_pain": "wrist,shoulder", "intensity": "medium", 
        "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 8.0,
        "description": "맨몸으로 가슴과 팔의 근력을 키울 수 있는 최고의 상체 운동입니다.",
        "tip": "엉덩이가 처지거나 올라가지 않게 몸을 일직선으로 유지하는 것이 핵심입니다."
    },
    {
        "plan_id": "gym_bench_press_barbell", "name": "바벨 벤치프레스", "location": "gym", "type": "rep-based", "required_equipment": "barbell,bench", 
        "target_parts": "chest", "sub_target_parts": "middle_chest,triceps,front_deltoid", "avoid_if_pain": "shoulder,wrist", "intensity": "high", 
        "minutes": 20, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0,
        "description": "벤치에 누워 바벨을 미는 운동으로 상체 전면 근육을 발달시킵니다.",
        "tip": "바를 내릴 때 가슴 중앙부에 오도록 하고, 어깨뼈(견갑)를 벤치에 고정하세요."
    },

    # --- [BACK / UPPER BODY PULL] ---
    {
        "plan_id": "gym_lat_pulldown_wide", "name": "랫풀다운 (와이드)", "location": "gym", "type": "rep-based", "required_equipment": "lat_pulldown_machine", 
        "target_parts": "back", "sub_target_parts": "latissimus_dorsi", "avoid_if_pain": "shoulder", "intensity": "medium", 
        "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0,
        "description": "등을 넓게 만들어주는 광배근 운동입니다. 바를 쇄골 쪽으로 당깁니다.",
        "tip": "팔로 당기기보다 팔꿈치를 옆구리에 찍는다는 느낌으로 광배근의 수축에 집중하세요."
    },

    # --- [CORE] ---
    {
        "plan_id": "home_plank", "name": "플랭크", "location": "home", "type": "time-based", "required_equipment": "", 
        "target_parts": "core", "sub_target_parts": "abs,transverse_abdominis", "avoid_if_pain": "shoulder,lower_back", "intensity": "medium", 
        "minutes": 5, "sets": 3, "reps": 1, "target_rpe": 6, "rest_seconds": 60, "met_value": 4.0,
        "description": "정적인 자세로 코어의 안정성을 강화하는 전신 코어 운동입니다.",
        "tip": "호흡을 참지 말고 일정하게 유지하며, 복근을 강하게 수축시켜 버티세요."
    },

    # --- [SPECIALIZED / NEW VARIETY] ---
    {
        "plan_id": "gym_arnold_press", "name": "아놀드 프레스", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", 
        "target_parts": "shoulder", "sub_target_parts": "front_deltoid,side_deltoid", "avoid_if_pain": "shoulder", "intensity": "medium", 
        "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.5,
        "description": "덤벨을 회전시키며 밀어올려 어깨의 전면과 측면을 동시에 자극합니다.",
        "tip": "덤벨을 내릴 때 얼굴 앞에서 손바닥이 얼굴을 향하게 회전시키는 것이 특징입니다."
    },
    {
        "plan_id": "home_burpee", "name": "버피 테스트", "location": "home", "type": "rep-based", "required_equipment": "", 
        "target_parts": "full_body", "sub_target_parts": "cardio,quadriceps,chest", "avoid_if_pain": "wrist,knee", "intensity": "high", 
        "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 9, "rest_seconds": 90, "met_value": 10.0,
        "description": "심폐지구력과 근력을 동시에 키우는 고강도 전신 유산소 운동입니다.",
        "tip": "빠르게 하기보다 정확한 푸쉬업과 점프 자세를 유지하는 것이 부상 방지에 좋습니다."
    },
    {
        "plan_id": "gym_hip_thrust", "name": "힙 쓰러스트", "location": "gym", "type": "rep-based", "required_equipment": "barbell,bench", 
        "target_parts": "legs", "sub_target_parts": "glutes,hamstrings", "avoid_if_pain": "lower_back,hip", "intensity": "high", 
        "minutes": 20, "sets": 4, "reps": 10, "target_rpe": 8, "rest_seconds": 150, "met_value": 6.0,
        "description": "엉덩이(둔근) 근육을 가장 효과적으로 고립하여 발달시킬 수 있는 운동입니다.",
        "tip": "최고 지점에서 엉덩이를 1~2초간 꽉 짜주면 훨씬 강한 자극을 느낄 수 있습니다."
    },
    {
        "plan_id": "home_mountain_climber", "name": "마운틴 클라이머", "location": "home", "type": "rep-based", "required_equipment": "", 
        "target_parts": "core", "sub_target_parts": "abs,hip_flexors", "avoid_if_pain": "wrist,shoulder", "intensity": "medium", 
        "minutes": 8, "sets": 3, "reps": 30, "target_rpe": 7, "rest_seconds": 45, "met_value": 8.0,
        "description": "엎드린 자세에서 산을 타듯 다리를 빠르게 교차하며 코어와 하체를 단련합니다.",
        "tip": "상체는 고정하고 다리만 빠르게 움직여 복부의 긴장감을 유지하세요."
    },
    {
        "plan_id": "gym_face_pull", "name": "페이스 풀", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", 
        "target_parts": "shoulder,back", "sub_target_parts": "rear_deltoid,traps", "avoid_if_pain": "shoulder", "intensity": "low", 
        "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0,
        "description": "어깨 후면과 등 상부를 타겟팅하며 라운드 숄더 개선에 효과적입니다.",
        "tip": "로프를 얼굴 쪽으로 당길 때 팔꿈치를 뒤로 보내기보다 옆으로 벌린다는 느낌을 가져보세요."
    }
]

def seed_data():
    db: Session = SessionLocal()
    try:
        # Clear existing data to ensure correct mapping of new columns
        db.query(ExercisePlan).delete()
        db.commit()
        
        for ex_data in SEED_EXERCISES:
            new_plan = ExercisePlan(**ex_data)
            db.add(new_plan)
        
        db.commit()
        print(f"Successfully seeded {len(SEED_EXERCISES)} exercises with sub-target parts.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
