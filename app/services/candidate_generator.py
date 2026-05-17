from typing import List, Dict
import copy
from sqlalchemy.orm import Session
from app.db.models import ExercisePlan


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

    # 피로도가 높으면 강도 제한
    if fatigue >= 3:
        allowed = [x for x in allowed if x != "high"]

    if fatigue >= 4:
        allowed = ["low"]

    return allowed


def adjust_plan_by_experience(plan_obj: ExercisePlan, experience_level: str) -> Dict:
    # Convert DB object to dict for modification
    plan = {
        "plan_id": plan_obj.plan_id,
        "name": plan_obj.name,
        "location": plan_obj.location,
        "type": plan_obj.type,
        "required_equipment": plan_obj.required_equipment,
        "target_parts": plan_obj.target_parts,
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

    elif experience_level == "intermediate":
        # 기본값 유지
        pass

    elif experience_level == "advanced":
        plan["sets"] += 1
        if plan["reps"] > 1:
            plan["reps"] += 2
        plan["minutes"] += 5

    return plan


def generate_candidates(state: Dict, db: Session) -> List[Dict]:
    location = state["location"]
    available_minutes = state["available_minutes"]
    fatigue = state["fatigue"]
    pain_parts = set(state["pain_parts"])
    
    # Ensure equipment_available is a list
    equipment_available = state.get("equipment_available", [])
    if not equipment_available and location == "gym":
        equipment_available = ["barbell", "bench", "lat_pulldown_machine", "leg_press_machine", "treadmill", "stationary_bike", "squat_rack"]

    experience_level = state["experience_level"]
    want_stretching = state.get("want_stretching", False)

    allowed_intensities = get_allowed_intensities(experience_level, fatigue)

    # Fetch from DB instead of hardcoded list
    query = db.query(ExercisePlan).filter(ExercisePlan.location == location)
    
    if want_stretching:
        # 회복 모드: 스트레칭 전용 운동만 추출
        query = query.filter(ExercisePlan.is_stretching == True)
    else:
        # 일반 운동 모드: 스트레칭이 아닌(is_stretching=False) 운동 중 허용된 강도 필터링
        query = query.filter(
            ExercisePlan.intensity.in_(allowed_intensities),
            ExercisePlan.is_stretching == False
        )

    all_plans = query.all()
    candidates = []

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

        candidates.append(adjusted_ex)

    if not candidates:
        candidates.append(
            {
                "plan_id": "fallback_walk_light",
                "name": "대체 가벼운 걷기/스트레칭",
                "location": location,
                "type": "time-based",
                "required_equipment": "",
                "target_parts": "full_body",
                "avoid_if_pain": "",
                "intensity": "low",
                "minutes": min(available_minutes, 10),
                "sets": 1,
                "reps": 1,
                "is_stretching": True
            }
        )

    return candidates
