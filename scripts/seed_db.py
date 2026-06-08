from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import ExercisePlan, Base

# Recreate tables to apply new schema
ExercisePlan.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(bind=engine)

SEED_EXERCISES = [
    # --- [LEGS / LOWER BODY] ---
    {"plan_id": "home_squat_standard", "name": "맨몸 스쿼트", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 5, "rest_seconds": 60, "met_value": 5.0, "description": "기본 하체 운동.", "tip": "무릎 주의.", "is_stretching": False},
    {"plan_id": "home_lunges", "name": "런지", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee", "intensity": "medium", "minutes": 12, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 60, "met_value": 6.0, "description": "하체 균형 발달.", "tip": "상체 수직 유지.", "is_stretching": False},
    {"plan_id": "home_side_lunges", "name": "사이드 런지", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "adductor,glutes", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 5, "rest_seconds": 60, "met_value": 4.0, "description": "허벅지 안쪽 강화.", "tip": "엉덩이를 뒤로 빼세요.", "is_stretching": False},
    {"plan_id": "home_glute_bridge", "name": "글루트 브릿지", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "glutes,hamstrings", "avoid_if_pain": "lower_back", "intensity": "low", "minutes": 8, "sets": 3, "reps": 15, "target_rpe": 4, "rest_seconds": 45, "met_value": 3.0, "description": "엉덩이 근육 고립 운동.", "tip": "괄약근을 조이듯 수축.", "is_stretching": False},
    {"plan_id": "gym_squat_barbell", "name": "바벨 백 스쿼트", "location": "gym", "type": "rep-based", "required_equipment": "barbell,squat_rack", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes,lower_back", "avoid_if_pain": "knee,lower_back", "intensity": "high", "minutes": 25, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 150, "met_value": 7.0, "description": "고강도 하체 운동.", "tip": "복압 유지.", "is_stretching": False},
    {"plan_id": "gym_leg_press", "name": "레그 프레스", "location": "gym", "type": "rep-based", "required_equipment": "leg_press_machine", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee,lower_back", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 120, "met_value": 5.0, "description": "안전한 하체 머신 운동.", "tip": "무릎 잠금 주의.", "is_stretching": False},
    {"plan_id": "gym_leg_extension", "name": "레그 익스텐션", "location": "gym", "type": "rep-based", "required_equipment": "leg_extension_machine", "target_parts": "legs", "sub_target_parts": "quadriceps", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "앞벅지 고립 운동.", "tip": "부드럽게 밀어주세요.", "is_stretching": False},
    {"plan_id": "gym_leg_curl", "name": "레그 컬", "location": "gym", "type": "rep-based", "required_equipment": "leg_curl_machine", "target_parts": "legs", "sub_target_parts": "hamstrings", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "뒷벅지 고립 운동.", "tip": "엉덩이가 뜨지 않게 주의.", "is_stretching": False},
    {"plan_id": "gym_hack_squat", "name": "핵 스쿼트", "location": "gym", "type": "rep-based", "required_equipment": "hack_squat_machine", "target_parts": "legs", "sub_target_parts": "quadriceps", "avoid_if_pain": "knee", "intensity": "high", "minutes": 20, "sets": 4, "reps": 10, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0, "description": "허벅지 전면 집중 타격.", "tip": "등을 패드에 밀착.", "is_stretching": False},
    {"plan_id": "gym_goblet_squat", "name": "덤벨 고블렛 스쿼트", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 15, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 90, "met_value": 5.0, "description": "덤벨을 가슴 앞에 들고 하는 스쿼트.", "tip": "상체를 세우기 용이합니다.", "is_stretching": False},
    {"plan_id": "gym_calf_raise", "name": "카프 레이즈", "location": "gym", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "calves", "avoid_if_pain": "ankle", "intensity": "low", "minutes": 10, "sets": 3, "reps": 20, "target_rpe": 5, "rest_seconds": 60, "met_value": 3.0, "description": "종아리 강화 운동.", "tip": "최대 수축 지점에서 멈춤.", "is_stretching": False},

    # --- [CHEST] ---
    {"plan_id": "home_pushup_standard", "name": "푸쉬업", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "chest", "sub_target_parts": "middle_chest,triceps,shoulder", "avoid_if_pain": "wrist,shoulder", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 8.0, "description": "최고의 맨몸 가슴 운동.", "tip": "몸을 일직선으로.", "is_stretching": False},
    {"plan_id": "home_incline_pushup", "name": "인클라인 푸쉬업", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "chest", "sub_target_parts": "lower_chest", "avoid_if_pain": "wrist", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 5, "rest_seconds": 60, "met_value": 4.0, "description": "손을 높은 곳에 짚고 하는 푸쉬업.", "tip": "초보자에게 추천.", "is_stretching": False},
    {"plan_id": "home_decline_pushup", "name": "디클라인 푸쉬업", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "chest", "sub_target_parts": "upper_chest", "avoid_if_pain": "wrist,shoulder", "intensity": "high", "minutes": 10, "sets": 3, "reps": 10, "target_rpe": 8, "rest_seconds": 90, "met_value": 9.0, "description": "발을 높은 곳에 두고 하는 푸쉬업.", "tip": "윗가슴에 강한 자극.", "is_stretching": False},
    {"plan_id": "gym_bench_press_barbell", "name": "바벨 벤치프레스", "location": "gym", "type": "rep-based", "required_equipment": "barbell,bench", "target_parts": "chest", "sub_target_parts": "middle_chest,triceps", "avoid_if_pain": "shoulder,wrist", "intensity": "high", "minutes": 20, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0, "description": "가슴 운동의 대명사.", "tip": "견갑 고정.", "is_stretching": False},
    {"plan_id": "gym_incline_press_dumbbell", "name": "인클라인 덤벨 프레스", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell,bench", "target_parts": "chest", "sub_target_parts": "upper_chest", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 5.0, "description": "윗가슴 발달.", "tip": "각도 30~45도.", "is_stretching": False},
    {"plan_id": "gym_chest_press_machine", "name": "체스트 프레스 머신", "location": "gym", "type": "rep-based", "required_equipment": "chest_press_machine", "target_parts": "chest", "sub_target_parts": "middle_chest", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 12, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 90, "met_value": 4.0, "description": "안전한 가슴 밀기 운동.", "tip": "초보자에게 추천.", "is_stretching": False},
    {"plan_id": "gym_chest_fly_machine", "name": "팩 덱 플라이", "location": "gym", "type": "rep-based", "required_equipment": "chest_fly_machine", "target_parts": "chest", "sub_target_parts": "middle_chest", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "가슴 안쪽 모으기.", "tip": "가슴을 열어주세요.", "is_stretching": False},
    {"plan_id": "gym_cable_crossover", "name": "케이블 크로스오버", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", "target_parts": "chest", "sub_target_parts": "lower_chest,middle_chest", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 3, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.0, "description": "가슴 근육 선명도 강화.", "tip": "끝까지 모아주세요.", "is_stretching": False},

    # --- [BACK] ---
    {"plan_id": "gym_lat_pulldown_wide", "name": "랫풀다운", "location": "gym", "type": "rep-based", "required_equipment": "lat_pulldown_machine", "target_parts": "back", "sub_target_parts": "lats", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0, "description": "넓은 등을 위한 운동.", "tip": "팔꿈치로 당기세요.", "is_stretching": False},
    {"plan_id": "gym_seated_row", "name": "시티드 로우", "location": "gym", "type": "rep-based", "required_equipment": "row_machine", "target_parts": "back", "sub_target_parts": "middle_back,lats", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0, "description": "등 두께 발달.", "tip": "허리 고정.", "is_stretching": False},
    {"plan_id": "gym_deadlift_conv", "name": "데드리프트", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "back,legs", "sub_target_parts": "lower_back,glutes,hamstrings", "avoid_if_pain": "lower_back,wrist", "intensity": "high", "minutes": 25, "sets": 5, "reps": 5, "target_rpe": 9, "rest_seconds": 180, "met_value": 8.0, "description": "전신 근력 강화.", "tip": "허리 말림 주의.", "is_stretching": False},
    {"plan_id": "gym_one_arm_dumbell_row", "name": "원 암 덤벨 로우", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell,bench", "target_parts": "back", "sub_target_parts": "lats,middle_back", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 15, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.5, "description": "등 광배근 하부 타겟.", "tip": "팔꿈치를 높게.", "is_stretching": False},
    {"plan_id": "gym_t_bar_row", "name": "T-바 로우", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "back", "sub_target_parts": "middle_back", "avoid_if_pain": "lower_back", "intensity": "high", "minutes": 20, "sets": 4, "reps": 10, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0, "description": "두꺼운 등을 만드는 로우 운동.", "tip": "반동을 최소화하세요.", "is_stretching": False},
    {"plan_id": "home_superman_hold", "name": "슈퍼맨 홀드", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "back", "sub_target_parts": "lower_back", "avoid_if_pain": "lower_back", "intensity": "low", "minutes": 5, "sets": 3, "reps": 1, "target_rpe": 4, "rest_seconds": 45, "met_value": 3.0, "description": "허리 기립근 강화.", "tip": "시선은 바닥을 보세요.", "is_stretching": False},

    # --- [SHOULDER] ---
    {"plan_id": "gym_shoulder_press_dumbbell", "name": "덤벨 숄더 프레스", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "front_deltoid", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 10, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.5, "description": "어깨 근육 전체 발달.", "tip": "팔꿈치가 너무 뒤로 가지 않게.", "is_stretching": False},
    {"plan_id": "gym_side_lateral_raise", "name": "사이드 레터럴 레이즈", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "side_deltoid", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 12, "sets": 4, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 3.0, "description": "넓은 어깨를 위한 측면 운동.", "tip": "어깨를 누르고 들어올리세요.", "is_stretching": False},
    {"plan_id": "gym_front_raise", "name": "프론트 레이즈", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "front_deltoid", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "어깨 전면 강화.", "tip": "손등이 위를 향하게.", "is_stretching": False},
    {"plan_id": "gym_face_pull", "name": "페이스 풀", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", "target_parts": "shoulder,back", "sub_target_parts": "rear_deltoid,traps", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "어깨 후면 및 라운드숄더 개선.", "tip": "얼굴 쪽으로 당기기.", "is_stretching": False},
    {"plan_id": "gym_upright_row", "name": "업라이트 로우", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "shoulder", "sub_target_parts": "side_deltoid,traps", "avoid_if_pain": "wrist,shoulder", "intensity": "medium", "minutes": 12, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0, "description": "어깨와 승모근 강화.", "tip": "바를 몸에 가깝게.", "is_stretching": False},

    # --- [ARMS] ---
    {"plan_id": "gym_barbell_curl", "name": "바벨 컬", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "arms", "sub_target_parts": "biceps", "avoid_if_pain": "wrist,elbow", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "이두 발달.", "tip": "반동 주의.", "is_stretching": False},
    {"plan_id": "gym_triceps_pushdown", "name": "케이블 푸쉬다운", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", "target_parts": "arms", "sub_target_parts": "triceps", "avoid_if_pain": "elbow", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "삼두 고립 운동.", "tip": "팔꿈치 고정.", "is_stretching": False},
    {"plan_id": "gym_hammer_curl", "name": "해머 컬", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "arms", "sub_target_parts": "biceps,forearms", "avoid_if_pain": "wrist", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0, "description": "이두 바깥쪽 발달.", "tip": "엄지가 위로.", "is_stretching": False},
    {"plan_id": "gym_kickback", "name": "덤벨 킥백", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "arms", "sub_target_parts": "triceps", "avoid_if_pain": "elbow", "intensity": "low", "minutes": 8, "sets": 3, "reps": 15, "target_rpe": 5, "rest_seconds": 45, "met_value": 2.5, "description": "삼두 상부 고립.", "tip": "팔꿈치를 옆구리에 고정.", "is_stretching": False},

    # --- [CORE] ---
    {"plan_id": "home_plank", "name": "플랭크", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "abs", "avoid_if_pain": "lower_back,shoulder", "intensity": "medium", "minutes": 5, "sets": 3, "reps": 1, "target_rpe": 6, "rest_seconds": 60, "met_value": 4.0, "description": "코어 안정성 강화.", "tip": "엉덩이 수평.", "is_stretching": False},
    {"plan_id": "home_crunch", "name": "크런치", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "abs", "avoid_if_pain": "neck,lower_back", "intensity": "low", "minutes": 8, "sets": 3, "reps": 20, "target_rpe": 5, "rest_seconds": 45, "met_value": 3.0, "description": "상복부 강화.", "tip": "허리가 뜨지 않게.", "is_stretching": False},
    {"plan_id": "home_leg_raise", "name": "레그 레이즈", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "abs", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 8, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.5, "description": "하복부 강화.", "tip": "허리 바닥에 밀착.", "is_stretching": False},
    {"plan_id": "home_mountain_climber", "name": "마운틴 클라이머", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "core,cardio", "sub_target_parts": "abs", "avoid_if_pain": "wrist,shoulder", "intensity": "high", "minutes": 10, "sets": 3, "reps": 1, "target_rpe": 8, "rest_seconds": 60, "met_value": 8.0, "description": "코어와 유산소를 동시에.", "tip": "엉덩이가 너무 들리지 않게.", "is_stretching": False},

    # --- [STRETCHING] ---
    {"plan_id": "home_cat_cow", "name": "캣 카우", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "back,core", "sub_target_parts": "lower_back", "avoid_if_pain": "wrist", "intensity": "low", "minutes": 5, "sets": 2, "reps": 10, "target_rpe": 2, "rest_seconds": 30, "met_value": 2.0, "is_stretching": True, "description": "척추 유연성 향상.", "tip": "호흡과 함께."},
    {"plan_id": "home_cobra_stretch", "name": "코브라 스트레칭", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "core,back", "sub_target_parts": "abs", "avoid_if_pain": "lower_back", "intensity": "low", "minutes": 5, "sets": 2, "reps": 5, "target_rpe": 2, "rest_seconds": 30, "met_value": 2.0, "is_stretching": True, "description": "복부 및 척추 스트레칭.", "tip": "무리하게 젖히지 마세요."},
    {"plan_id": "gym_foam_roller_full", "name": "전신 폼롤러", "location": "gym", "type": "time-based", "required_equipment": "foam_roller", "target_parts": "full_body", "sub_target_parts": "full_body", "avoid_if_pain": "", "intensity": "low", "minutes": 15, "sets": 1, "reps": 1, "target_rpe": 3, "rest_seconds": 0, "met_value": 2.5, "is_stretching": True, "description": "근막 이완 및 피로 회복.", "tip": "아픈 부위는 천천히."},
]

def generate_variations():
    variations = []
    for ex in SEED_EXERCISES:
        if ex["location"] == "home" and not ex.get("is_stretching", False):
            new_ex = ex.copy()
            new_ex["plan_id"] = "gym_" + ex["plan_id"].replace("home_", "")
            new_ex["location"] = "gym"
            variations.append(new_ex)
        
        if ex["intensity"] in ["high", "medium"]:
            low_ex = ex.copy()
            low_ex["plan_id"] = ex["plan_id"] + "_light"
            low_ex["name"] = ex["name"] + " (가볍게)"
            low_ex["intensity"] = "low"
            low_ex["sets"] = max(1, ex["sets"] - 1)
            low_ex["reps"] = max(5, int(ex["reps"] * 0.8))
            low_ex["minutes"] = max(5, int(ex["minutes"] * 0.7))
            variations.append(low_ex)

    return variations

FINAL_EXERCISES = SEED_EXERCISES + generate_variations()

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
