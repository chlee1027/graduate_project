import csv
import os

# 데이터 가져오기 (seed_db.py의 최신 데이터를 기반으로 함)
SEED_EXERCISES = [
    {"plan_id": "home_squat_standard", "name": "맨몸 스쿼트", "location": "home", "type": "rep-based", "target_parts": "legs,glutes", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 5.0},
    {"plan_id": "home_pushup_standard", "name": "푸쉬업", "location": "home", "type": "rep-based", "target_parts": "chest,arms,shoulder", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 8.0},
    {"plan_id": "home_lunges", "name": "워킹 런지", "location": "home", "type": "rep-based", "target_parts": "legs,glutes", "intensity": "high", "minutes": 12, "sets": 3, "reps": 20, "target_rpe": 8, "rest_seconds": 60, "met_value": 6.0},
    {"plan_id": "home_diamond_pushup", "name": "다이아몬드 푸쉬업", "location": "home", "type": "rep-based", "target_parts": "arms,chest", "intensity": "high", "minutes": 10, "sets": 3, "reps": 8, "target_rpe": 8, "rest_seconds": 90, "met_value": 8.0},
    {"plan_id": "home_crunch", "name": "크런치", "location": "home", "type": "rep-based", "target_parts": "core", "intensity": "low", "minutes": 8, "sets": 3, "reps": 20, "target_rpe": 5, "rest_seconds": 45, "met_value": 3.0},
    {"plan_id": "home_leg_raise", "name": "레그 레이즈", "location": "home", "type": "rep-based", "target_parts": "core,legs", "intensity": "medium", "minutes": 8, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.5},
    {"plan_id": "home_plank_updown", "name": "플랭크 업다운", "location": "home", "type": "rep-based", "target_parts": "core,shoulder,arms", "intensity": "high", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 8, "rest_seconds": 60, "met_value": 7.0},
    {"plan_id": "home_glute_bridge", "name": "글루트 브릿지", "location": "home", "type": "rep-based", "target_parts": "glutes,lower_back", "intensity": "low", "minutes": 10, "sets": 3, "reps": 20, "target_rpe": 4, "rest_seconds": 45, "met_value": 3.0},
    {"plan_id": "home_superman", "name": "슈퍼맨 홀드", "location": "home", "type": "time-based", "target_parts": "back,glutes", "intensity": "medium", "minutes": 5, "sets": 3, "reps": 1, "target_rpe": 6, "rest_seconds": 45, "met_value": 3.0},
    {"plan_id": "home_burpee_classic", "name": "버피 테스트", "location": "home", "type": "rep-based", "target_parts": "full_body", "intensity": "high", "minutes": 15, "sets": 4, "reps": 15, "target_rpe": 9, "rest_seconds": 60, "met_value": 10.0},
    {"plan_id": "home_mountain_climber", "name": "마운틴 클라이머", "location": "home", "type": "time-based", "target_parts": "core,cardio", "intensity": "high", "minutes": 10, "sets": 3, "reps": 1, "target_rpe": 8, "rest_seconds": 60, "met_value": 8.0},
    {"plan_id": "home_wall_sit", "name": "벽 대고 버티기 (월싯)", "location": "home", "type": "time-based", "target_parts": "legs", "intensity": "medium", "minutes": 6, "sets": 3, "reps": 1, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.0},
    {"plan_id": "gym_deadlift_conv", "name": "컨벤셔널 데드리프트", "location": "gym", "type": "rep-based", "target_parts": "back,legs,core", "intensity": "high", "minutes": 25, "sets": 5, "reps": 5, "target_rpe": 9, "rest_seconds": 180, "met_value": 6.0},
    {"plan_id": "gym_bench_press_barbell", "name": "바벨 벤치프레스", "location": "gym", "type": "rep-based", "target_parts": "chest,arms", "intensity": "high", "minutes": 20, "sets": 5, "reps": 8, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0},
    {"plan_id": "gym_squat_barbell", "name": "바벨 백 스쿼트", "location": "gym", "type": "rep-based", "target_parts": "legs,glutes", "intensity": "high", "minutes": 25, "sets": 5, "reps": 8, "target_rpe": 9, "rest_seconds": 150, "met_value": 7.0},
    {"plan_id": "gym_lat_pulldown_wide", "name": "랫풀다운 (와이드)", "location": "gym", "type": "rep-based", "target_parts": "back", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0},
    {"plan_id": "gym_shoulder_press_dumbbell", "name": "덤벨 숄더 프레스", "location": "gym", "type": "rep-based", "target_parts": "shoulder", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 10, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.5},
    {"plan_id": "gym_leg_press_machine", "name": "레그 프레스", "location": "gym", "type": "rep-based", "target_parts": "legs", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 120, "met_value": 5.0},
    {"plan_id": "gym_seated_row_machine", "name": "시티드 로우", "location": "gym", "type": "rep-based", "target_parts": "back", "intensity": "medium", "minutes": 15, "sets": 4, "reps": 12, "target_rpe": 7, "rest_seconds": 90, "met_value": 4.0},
    {"plan_id": "gym_incline_bench_press", "name": "인클라인 벤치프레스", "location": "gym", "type": "rep-based", "target_parts": "chest,shoulder", "intensity": "high", "minutes": 20, "sets": 4, "reps": 8, "target_rpe": 8, "rest_seconds": 120, "met_value": 6.0},
    {"plan_id": "gym_leg_curl", "name": "레그 컬 (햄스트링)", "location": "gym", "type": "rep-based", "target_parts": "legs", "intensity": "low", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.5},
    {"plan_id": "gym_side_lateral_raise", "name": "사이드 레터럴 레이즈", "location": "gym", "type": "rep-based", "target_parts": "shoulder", "intensity": "low", "minutes": 12, "sets": 4, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_barbell_curl", "name": "바벨 컬 (이두)", "location": "gym", "type": "rep-based", "target_parts": "arms", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_triceps_pushdown", "name": "케이블 푸쉬다운 (삼두)", "location": "gym", "type": "rep-based", "target_parts": "arms", "intensity": "low", "minutes": 10, "sets": 3, "reps": 12, "target_rpe": 6, "rest_seconds": 60, "met_value": 3.0},
    {"plan_id": "gym_chest_fly_machine", "name": "체스트 플라이 머신", "location": "gym", "type": "rep-based", "target_parts": "chest", "intensity": "medium", "minutes": 12, "sets": 3, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.0},
    {"plan_id": "gym_romanian_deadlift", "name": "루마니안 데드리프트", "location": "gym", "type": "rep-based", "target_parts": "back,glutes,legs", "intensity": "high", "minutes": 20, "sets": 4, "reps": 10, "target_rpe": 8, "rest_seconds": 120, "met_value": 5.5},
    {"plan_id": "gym_pull_up", "name": "풀업 (턱걸이)", "location": "gym", "type": "rep-based", "target_parts": "back,arms", "intensity": "high", "minutes": 15, "sets": 4, "reps": 8, "target_rpe": 9, "rest_seconds": 120, "met_value": 8.0},
    {"plan_id": "gym_dips", "name": "딥스 (삼두/가슴)", "location": "gym", "type": "rep-based", "target_parts": "arms,chest", "intensity": "high", "minutes": 12, "sets": 3, "reps": 10, "target_rpe": 8, "rest_seconds": 90, "met_value": 7.0},
    {"plan_id": "gym_leg_extension", "name": "레그 익스텐션", "location": "gym", "type": "rep-based", "target_parts": "legs", "intensity": "medium", "minutes": 10, "sets": 3, "reps": 15, "target_rpe": 7, "rest_seconds": 60, "met_value": 4.0},
    {"plan_id": "gym_treadmill_interval", "name": "트레드밀 인터벌", "location": "gym", "type": "time-based", "target_parts": "cardio", "intensity": "high", "minutes": 20, "sets": 1, "reps": 1, "target_rpe": 8, "rest_seconds": 0, "met_value": 10.0},
    {"plan_id": "gym_stationary_bike", "name": "실내 자전거", "location": "gym", "type": "time-based", "target_parts": "cardio,legs", "intensity": "medium", "minutes": 30, "sets": 1, "reps": 1, "target_rpe": 6, "rest_seconds": 0, "met_value": 7.0},
    {"plan_id": "gym_elliptical", "name": "엘립티컬", "location": "gym", "type": "time-based", "target_parts": "cardio,full_body", "intensity": "medium", "minutes": 20, "sets": 1, "reps": 1, "target_rpe": 5, "rest_seconds": 0, "met_value": 5.0},
    {"plan_id": "home_stretch_morning", "name": "모닝 전신 스트레칭", "location": "home", "type": "time-based", "target_parts": "full_body", "intensity": "low", "minutes": 10, "sets": 1, "reps": 1, "target_rpe": 3, "rest_seconds": 0, "met_value": 2.5},
    {"plan_id": "home_stretch_back", "name": "허리 통증 완화 스트레칭", "location": "home", "type": "time-based", "target_parts": "back,core", "intensity": "low", "minutes": 10, "sets": 1, "reps": 1, "target_rpe": 3, "rest_seconds": 0, "met_value": 2.0},
    {"plan_id": "home_stretch_neck", "name": "거북목 교정 스트레칭", "location": "home", "type": "time-based", "target_parts": "neck,shoulder", "intensity": "low", "minutes": 5, "sets": 1, "reps": 1, "target_rpe": 2, "rest_seconds": 0, "met_value": 1.5},
    {"plan_id": "home_stretch_hip", "name": "골반 교정 스트레칭", "location": "home", "type": "time-based", "target_parts": "glutes,legs", "intensity": "low", "minutes": 12, "sets": 1, "reps": 1, "target_rpe": 4, "rest_seconds": 0, "met_value": 2.3},
    {"plan_id": "home_foam_roller_legs", "name": "하체 폼롤러 마사지", "location": "home", "type": "time-based", "target_parts": "legs,glutes", "intensity": "low", "minutes": 15, "sets": 1, "reps": 1, "target_rpe": 4, "rest_seconds": 0, "met_value": 2.5},
    {"plan_id": "home_foam_roller_back", "name": "등/허리 폼롤러 마사지", "location": "home", "type": "time-based", "target_parts": "back", "intensity": "low", "minutes": 10, "sets": 1, "reps": 1, "target_rpe": 3, "rest_seconds": 0, "met_value": 2.5},
    {"plan_id": "home_yoga_basic", "name": "기초 요가 루틴", "location": "home", "type": "time-based", "target_parts": "full_body,core", "intensity": "low", "minutes": 20, "sets": 1, "reps": 1, "target_rpe": 4, "rest_seconds": 0, "met_value": 3.3},
    {"plan_id": "home_dynamic_warmup", "name": "동적 웜업 루틴", "location": "home", "type": "time-based", "target_parts": "full_body", "intensity": "medium", "minutes": 8, "sets": 1, "reps": 1, "target_rpe": 5, "rest_seconds": 0, "met_value": 4.0},
    {"plan_id": "gym_foam_roller_full", "name": "전신 폼롤러 근막이완", "location": "gym", "type": "time-based", "target_parts": "full_body", "intensity": "low", "minutes": 15, "sets": 1, "reps": 1, "target_rpe": 4, "rest_seconds": 0, "met_value": 2.5},
    {"plan_id": "home_bedtime_stretch", "name": "취면 전 숙면 스트레칭", "location": "home", "type": "time-based", "target_parts": "full_body", "intensity": "low", "minutes": 10, "sets": 1, "reps": 1, "target_rpe": 2, "rest_seconds": 0, "met_value": 1.5}
]

# 컬럼 헤더 (영문 -> 한글 변환)
headers = {
    "name": "운동 이름",
    "location": "장소",
    "type": "유형",
    "target_parts": "타겟 부위",
    "intensity": "강도",
    "minutes": "전체 시간(분)",
    "sets": "세트 수",
    "reps": "회수/세트",
    "target_rpe": "권장 RPE",
    "rest_seconds": "휴식(초)",
    "met_value": "MET 지수"
}

desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "바탕 화면", "운동_데이터베이스_가이드.csv")

with open(desktop_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers.keys(), extrasaction='ignore')
    # 한글 헤더 쓰기
    f.write(",".join(headers.values()) + "\n")
    for row in SEED_EXERCISES:
        writer.writerow(row)

print(f"Excel-compatible CSV created at: {desktop_path}")
