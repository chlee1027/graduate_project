from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import ExercisePlan, Base

# Create tables if not exist
Base.metadata.create_all(bind=engine)

SEED_EXERCISES = [
    # --- [LEGS / LOWER BODY] ---
    # Squat Variations
    {"plan_id": "home_squat_standard", "name": "맨몸 스쿼트", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 5, "rest_seconds": 60, "met_value": 5.0},
    {"plan_id": "home_squat_sumo", "name": "와이드(스모) 스쿼트", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "adductor,glutes", "avoid_if_pain": "hip,knee", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 5.0},
    {"plan_id": "gym_squat_barbell", "name": "바벨 백 스쿼트", "location": "gym", "type": "rep-based", "required_equipment": "barbell,squat_rack", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes,lower_back", "avoid_if_pain": "knee,lower_back", "intensity": "high", "minutes": 25, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 150, "met_value": 7.0},
    {"plan_id": "gym_squat_goblet", "name": "고블렛 스쿼트", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "legs", "sub_target_parts": "quadriceps,core", "avoid_if_pain": "knee", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 5.5},
    
    # Lunge & Others
    {"plan_id": "home_lunges", "name": "런지", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes,hamstrings", "avoid_if_pain": "knee,ankle", "intensity": "medium", "minutes": 12, "sets": 3, "reps": 20, "target_rpe": 7, "rest_seconds": 60, "met_value": 6.0},
    {"plan_id": "gym_leg_press", "name": "레그 프레스", "location": "gym", "type": "rep-based", "required_equipment": "leg_press_machine", "target_parts": "legs", "sub_target_parts": "quadriceps,glutes", "avoid_if_pain": "knee,lower_back", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 120, "met_value": 5.0},
    {"plan_id": "gym_leg_extension", "name": "레그 익스텐션", "location": "gym", "type": "rep-based", "required_equipment": "leg_extension_machine", "target_parts": "legs", "sub_target_parts": "quadriceps", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 4.0},
    {"plan_id": "gym_leg_curl", "name": "레그 컬", "location": "gym", "type": "rep-based", "required_equipment": "leg_curl_machine", "target_parts": "legs", "sub_target_parts": "hamstrings", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.5},

    # --- [CHEST / UPPER BODY PUSH] ---
    {"plan_id": "home_pushup_standard", "name": "푸쉬업", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "chest", "sub_target_parts": "middle_chest,triceps,shoulder", "avoid_if_pain": "wrist,shoulder", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 8.0},
    {"plan_id": "home_pushup_incline", "name": "인클라인 푸쉬업", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "chest", "sub_target_parts": "lower_chest", "avoid_if_pain": "wrist", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 5, "rest_seconds": 60, "met_value": 6.0},
    {"plan_id": "gym_bench_press_barbell", "name": "바벨 벤치프레스", "location": "gym", "type": "rep-based", "required_equipment": "barbell,bench", "target_parts": "chest", "sub_target_parts": "middle_chest,triceps,front_deltoid", "avoid_if_pain": "shoulder,wrist", "intensity": "high", "minutes": 20, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0},
    {"plan_id": "gym_bench_press_incline", "name": "인클라인 벤치프레스", "location": "gym", "type": "rep-based", "required_equipment": "barbell,incline_bench", "target_parts": "chest", "sub_target_parts": "upper_chest,front_deltoid", "avoid_if_pain": "shoulder", "intensity": "high", "minutes": 20, "sets": 4, "reps": 8, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0},
    {"plan_id": "gym_chest_fly_machine", "name": "체스트 플라이 머신", "location": "gym", "type": "rep-based", "required_equipment": "fly_machine", "target_parts": "chest", "sub_target_parts": "middle_chest,inner_chest", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 12, "sets": 3, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.0},

    # --- [BACK / UPPER BODY PULL] ---
    {"plan_id": "gym_lat_pulldown_wide", "name": "랫풀다운 (와이드)", "location": "gym", "type": "rep-based", "required_equipment": "lat_pulldown_machine", "target_parts": "back", "sub_target_parts": "latissimus_dorsi", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0},
    {"plan_id": "gym_seated_row_machine", "name": "시티드 로우", "location": "gym", "type": "rep-based", "required_equipment": "row_machine", "target_parts": "back", "sub_target_parts": "middle_back,rhomboids", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0},
    {"plan_id": "gym_deadlift_conv", "name": "컨벤셔널 데드리프트", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "back,legs", "sub_target_parts": "erector_spinae,glutes,hamstrings", "avoid_if_pain": "lower_back", "intensity": "high", "minutes": 25, "sets": 5, "reps": 5, "target_rpe": 9, "rest_seconds": 180, "met_value": 6.0},
    {"plan_id": "gym_pull_up", "name": "풀업 (턱걸이)", "location": "gym", "type": "rep-based", "required_equipment": "pullup_bar", "target_parts": "back", "sub_target_parts": "latissimus_dorsi,biceps", "avoid_if_pain": "shoulder,elbow", "intensity": "high", "minutes": 15, "sets": 4, "reps": 8, "target_rpe": 9, "rest_seconds": 120, "met_value": 8.0},

    # --- [SHOULDERS] ---
    {"plan_id": "gym_shoulder_press_dumbbell", "name": "덤벨 숄더 프레스", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "front_deltoid,side_deltoid", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 10, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.5},
    {"plan_id": "gym_lateral_raise_side", "name": "사이드 레터럴 레이즈", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "side_deltoid", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 12, "sets": 4, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_lateral_raise_bentover", "name": "벤트오버 레터럴 레이즈", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "rear_deltoid", "avoid_if_pain": "shoulder,lower_back", "intensity": "low", "minutes": 12, "sets": 4, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 3.0},

    # --- [ARMS] ---
    # Biceps
    {"plan_id": "gym_curl_barbell", "name": "바벨 컬", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "arms", "sub_target_parts": "biceps", "avoid_if_pain": "wrist", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_curl_dumbbell", "name": "덤벨 컬", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "arms", "sub_target_parts": "biceps", "avoid_if_pain": "wrist", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_curl_hammer", "name": "해머 컬", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "arms", "sub_target_parts": "brachialis,brachioradialis", "avoid_if_pain": "wrist", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0},
    # Triceps
    {"plan_id": "gym_triceps_pushdown", "name": "케이블 푸쉬다운", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", "target_parts": "arms", "sub_target_parts": "triceps", "avoid_if_pain": "elbow", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_dips", "name": "딥스", "location": "gym", "type": "rep-based", "required_equipment": "dip_station", "target_parts": "arms,chest", "sub_target_parts": "triceps,lower_chest", "avoid_if_pain": "shoulder,wrist", "intensity": "high", "minutes": 12, "sets": 3, "reps": 10, "target_rpe": 8, "rest_seconds": 90, "met_value": 7.0},

    # --- [CORE] ---
    {"plan_id": "home_crunch", "name": "크런치", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "upper_abs", "avoid_if_pain": "neck,lower_back", "intensity": "low", "minutes": 8, "sets": 3, "reps": 20, "target_rpe": 5, "rest_seconds": 45, "met_value": 3.0},
    {"plan_id": "home_leg_raise", "name": "레그 레이즈", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "lower_abs", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 8, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.5},
    {"plan_id": "home_plank", "name": "플랭크", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "abs,transverse_abdominis", "avoid_if_pain": "shoulder,lower_back", "intensity": "medium", "minutes": 5, "sets": 3, "reps": 1, "target_rpe": 6, "rest_seconds": 60, "met_value": 4.0},

    # --- [NEW ADDITIONS FOR VARIETY] ---
    # Home / No Equipment
    {"plan_id": "home_burpee", "name": "버피 테스트", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "full_body", "sub_target_parts": "cardio,quadriceps,chest", "avoid_if_pain": "wrist,knee", "intensity": "high", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 9, "rest_seconds": 90, "met_value": 10.0},
    {"plan_id": "home_mountain_climber", "name": "마운틴 클라이머", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "core", "sub_target_parts": "abs,hip_flexors", "avoid_if_pain": "wrist,shoulder", "intensity": "medium", "minutes": 8, "sets": 3, "reps": 30, "target_rpe": 7, "rest_seconds": 45, "met_value": 8.0},
    {"plan_id": "home_bird_dog", "name": "버드 독", "location": "home", "type": "rep-based", "required_equipment": "", "target_parts": "core,back", "sub_target_parts": "erector_spinae,glutes", "avoid_if_pain": "knee", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 4, "rest_seconds": 30, "met_value": 3.0},
    
    # Gym / Machine & Free Weight
    {"plan_id": "gym_romanian_deadlift", "name": "루마니안 데드리프트", "location": "gym", "type": "rep-based", "required_equipment": "barbell", "target_parts": "back,legs", "sub_target_parts": "hamstrings,glutes,erector_spinae", "avoid_if_pain": "lower_back", "intensity": "medium", "minutes": 20, "sets": 4, "reps": 10, "target_rpe": 7, "rest_seconds": 120, "met_value": 6.0},
    {"plan_id": "gym_cable_crossover", "name": "케이블 크로스오버", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", "target_parts": "chest", "sub_target_parts": "lower_chest,inner_chest", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.0},
    {"plan_id": "gym_arnold_press", "name": "아놀드 프레스", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell", "target_parts": "shoulder", "sub_target_parts": "front_deltoid,side_deltoid", "avoid_if_pain": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.5},
    {"plan_id": "gym_face_pull", "name": "페이스 풀", "location": "gym", "type": "rep-based", "required_equipment": "cable_machine", "target_parts": "shoulder,back", "sub_target_parts": "rear_deltoid,traps", "avoid_if_pain": "shoulder", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_skull_crusher", "name": "스컬 크러셔", "location": "gym", "type": "rep-based", "required_equipment": "barbell,bench", "target_parts": "arms", "sub_target_parts": "triceps", "avoid_if_pain": "elbow", "intensity": "medium", "minutes": 12, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 3.0},
    {"plan_id": "gym_preacher_curl", "name": "프리처 컬", "location": "gym", "type": "rep-based", "required_equipment": "dumbbell,bench", "target_parts": "arms", "sub_target_parts": "biceps", "avoid_if_pain": "wrist,elbow", "intensity": "low", "minutes": 12, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_hip_thrust", "name": "힙 쓰러스트", "location": "gym", "type": "rep-based", "required_equipment": "barbell,bench", "target_parts": "legs", "sub_target_parts": "glutes,hamstrings", "avoid_if_pain": "lower_back,hip", "intensity": "high", "minutes": 20, "sets": 4, "reps": 10, "target_rpe": 8, "rest_seconds": 150, "met_value": 6.0},

    # Stretching / Recovery
    {"plan_id": "all_cat_cow", "name": "캣 카우 스트레칭", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "back,core", "sub_target_parts": "erector_spinae", "avoid_if_pain": "", "intensity": "low", "minutes": 5, "sets": 1, "reps": 1, "is_stretching": True, "target_rpe": 2, "rest_seconds": 0, "met_value": 2.5},
    {"plan_id": "all_child_pose", "name": "차일드 포즈", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "back,shoulder", "sub_target_parts": "lower_back", "avoid_if_pain": "knee", "intensity": "low", "minutes": 3, "sets": 1, "reps": 1, "is_stretching": True, "target_rpe": 1, "rest_seconds": 0, "met_value": 2.0},
    {"plan_id": "all_cobra_stretch", "name": "코브라 스트레칭", "location": "home", "type": "time-based", "required_equipment": "", "target_parts": "core,back", "sub_target_parts": "abs", "avoid_if_pain": "lower_back", "intensity": "low", "minutes": 3, "sets": 1, "reps": 1, "is_stretching": True, "target_rpe": 2, "rest_seconds": 0, "met_value": 2.0},
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
