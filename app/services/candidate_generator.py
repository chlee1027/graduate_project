from typing import List, Dict
import copy
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import ExercisePlan, ExerciseLog
from datetime import datetime, timedelta

def is_equipment_satisfied(required_str: str, available: List[str]) -> bool:
    if not required_str:
        return True
    required = [item.strip() for item in required_str.split(",") if item.strip()]
    return all(item in available for item in required)

def get_allowed_intensities(experience_level: str, fatigue: int) -> List[str]:
    if experience_level == "beginner":
        allowed = ["low"]
    elif experience_level == "intermediate":
        allowed = ["low", "medium"]
    else:
        allowed = ["low", "medium", "high"]

    if fatigue >= 3:
        allowed = [x for x in allowed if x != "high"]
    if fatigue >= 4:
        allowed = ["low"]
    return allowed

def adjust_plan_by_experience(plan_obj: ExercisePlan, experience_level: str) -> Dict:
    plan = {
        "plan_id": plan_obj.plan_id,
        "name": plan_obj.name,
        "location": plan_obj.location,
        "type": plan_obj.type,
        "required_equipment": plan_obj.required_equipment,
        "target_parts": plan_obj.target_parts,
        "sub_target_parts": plan_obj.sub_target_parts,
        "avoid_if_pain": plan_obj.avoid_if_pain,
        "intensity": plan_obj.intensity,
        "minutes": plan_obj.minutes,
        "sets": plan_obj.sets,
        "reps": plan_obj.reps,
        "target_rpe": plan_obj.target_rpe,
        "rest_seconds": plan_obj.rest_seconds,
        "met_value": plan_obj.met_value,
        "is_stretching": plan_obj.is_stretching,
        "video_url": plan_obj.video_url
    }

    if experience_level == "beginner":
        plan["sets"] = max(1, plan["sets"] - 1)
        if plan["reps"] > 1:
            plan["reps"] = max(5, plan["reps"] - 2)
        plan["minutes"] = max(5, plan["minutes"] - 5)
    elif experience_level == "advanced":
        plan["sets"] += 1
        if plan["reps"] > 1:
            plan["reps"] += 2
        plan["minutes"] += 5

    return plan

def get_detailed_usage_stats(user_id: str, db: Session) -> Dict[str, Dict[str, int]]:
    """
    최근 7일간 운동 로그를 분석하여, 대분류(target_parts) 및 소분류(sub_target_parts)별 수행 횟수를 반환합니다.
    """
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_logs = (
        db.query(ExercisePlan.target_parts, ExercisePlan.sub_target_parts)
        .join(ExerciseLog, ExerciseLog.plan_id == ExercisePlan.plan_id)
        .filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.completed == True,
            ExerciseLog.created_at >= seven_days_ago
        )
        .all()
    )

    major_counts = {}
    sub_counts = {}

    for target_parts, sub_target_parts in recent_logs:
        # 대분류 카운트
        if target_parts:
            parts = [p.strip() for p in target_parts.split(",") if p.strip()]
            for p in parts:
                major_counts[p] = major_counts.get(p, 0) + 1
        
        # 소분류 카운트
        if sub_target_parts:
            subs = [s.strip() for s in sub_target_parts.split(",") if s.strip()]
            for s in subs:
                sub_counts[s] = sub_counts.get(s, 0) + 1

    return {"major": major_counts, "sub": sub_counts}

def generate_candidates(state: Dict, db: Session) -> List[Dict]:
    user_id = state["user_id"]
    location = state["location"]
    available_minutes = state["available_minutes"]
    fatigue = state["fatigue"]
    pain_parts = set(state["pain_parts"])
    experience_level = state["experience_level"]
    want_stretching = state.get("want_stretching", False)

    equipment_available = state.get("equipment_available", [])
    if not equipment_available and location == "gym":
        equipment_available = ["barbell", "bench", "lat_pulldown_machine", "leg_press_machine", "treadmill", "stationary_bike", "squat_rack", "dumbbell", "cable_machine", "row_machine", "pullup_bar", "dip_station"]

    allowed_intensities = get_allowed_intensities(experience_level, fatigue)

    query = db.query(ExercisePlan).filter(ExercisePlan.location == location)
    
    if want_stretching:
        query = query.filter(ExercisePlan.is_stretching == True)
    else:
        query = query.filter(
            ExercisePlan.intensity.in_(allowed_intensities),
            ExercisePlan.is_stretching == False
        )

    all_plans = query.all()
    candidates = []

    # 상세 사용 통계 및 부위 우선순위 계산
    usage_stats = get_detailed_usage_stats(user_id, db)
    major_usage = usage_stats["major"]
    sub_usage = usage_stats["sub"]
    
    all_major_parts = ["legs", "chest", "back", "shoulder", "arms", "core"]
    # 대분류 우선순위 (수행 횟수가 적은 순)
    major_priority = sorted(all_major_parts, key=lambda x: major_usage.get(x, 0))
    
    for ex in all_plans:
        # 통증 부위 체크
        ex_avoid_parts = set([p.strip() for p in (ex.avoid_if_pain or "").split(",") if p.strip()])
        if pain_parts.intersection(ex_avoid_parts):
            continue

        # 장비 체크
        if not is_equipment_satisfied(ex.required_equipment, equipment_available):
            continue

        # 숙련도별 조정
        adjusted_ex = adjust_plan_by_experience(ex, experience_level)

        # 가용 시간 체크
        if adjusted_ex["minutes"] > available_minutes:
            continue
            
        # --- PT 코치 로직: 2단계 가중치 시스템 ---
        
        # 1. 대분류 점수 (Split Priority)
        # 6개 부위 중 순위에 따라 10~60점 부여
        ex_major_parts = [p.strip() for p in ex.target_parts.split(",") if p.strip()]
        max_major_score = 0
        for p in ex_major_parts:
            if p in major_priority:
                score = (len(major_priority) - major_priority.index(p)) * 10
                max_major_score = max(max_major_score, score)
        
        # 2. 소분류 점수 (Granular Balance)
        # 해당 소분류 근육을 최근 7일간 한 번도 안 했다면 보너스 점수(+15점)
        # 1~2회 했다면 약간의 보너스(+5점)
        ex_sub_parts = [s.strip() for s in (ex.sub_target_parts or "").split(",") if s.strip()]
        sub_bonus = 0
        for s in ex_sub_parts:
            count = sub_usage.get(s, 0)
            if count == 0:
                sub_bonus = max(sub_bonus, 15)
            elif count <= 2:
                sub_bonus = max(sub_bonus, 5)
        
        priority_score = max_major_score + sub_bonus
        
        # PT 코치 코멘트 생성 (간단 예시)
        coach_reason = ""
        
        # 근육 이름 한글 매핑
        muscle_ko = {
            "legs": "하체", "chest": "가슴", "back": "등", "shoulder": "어깨", "arms": "팔", "core": "코어",
            "quadriceps": "대퇴사두(앞허벅지)", "hamstrings": "햄스트링(뒷허벅지)", "glutes": "둔근(엉덩이)",
            "adductor": "내전근(안쪽 허벅지)", "calves": "종아리",
            "upper_chest": "상부 가슴", "middle_chest": "중부 가슴", "lower_chest": "하부 가슴",
            "lats": "광배근(옆구리쪽 등)", "traps": "승모근", "lower_back": "기립근(허리)",
            "biceps": "이두(알통)", "triceps": "삼두(팔 뒤)", "forearms": "전완근(팔둑)",
            "abs": "복근", "obliques": "외복사근(옆구리)"
        }

        if sub_bonus >= 15:
            muscle_en = ex_sub_parts[0] if ex_sub_parts else "해당 부위"
            muscle_name = muscle_ko.get(muscle_en, muscle_en)
            coach_reason = f"최근에 {muscle_name} 자극이 부족했네요. 균형을 위해 추천합니다!"
        elif max_major_score >= 50:
            major_en = ex_major_parts[0] if ex_major_parts else "해당"
            major_name = muscle_ko.get(major_en, major_en)
            coach_reason = f"오늘은 {major_name} 집중 훈련의 날입니다!"
            
        adjusted_ex["priority_score"] = priority_score
        adjusted_ex["coach_reason"] = coach_reason
        candidates.append(adjusted_ex)

    if not candidates:
        candidates.append({
            "plan_id": "fallback_walk_light",
            "name": "대체 가벼운 걷기/스트레칭",
            "location": location,
            "type": "time-based",
            "required_equipment": "",
            "target_parts": "full_body",
            "sub_target_parts": "cardio",
            "avoid_if_pain": "",
            "intensity": "low",
            "minutes": min(available_minutes, 10),
            "sets": 1,
            "reps": 1,
            "is_stretching": True,
            "priority_score": 0,
            "coach_reason": "무리가 가지 않게 가벼운 움직임을 추천해요."
        })

    # 우선순위 점수가 높은 순으로 정렬하여 상위 후보 반환
    candidates.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

    return candidates
