from typing import List, Dict
import copy

EXERCISE_POOL = [
    {
        "plan_id": "home_squat_basic",
        "name": "홈 스쿼트 기초",
        "location": "home",
        "required_equipment": [],
        "target_parts": ["legs"],
        "avoid_if_pain": ["knee"],
        "intensity": "low",
        "minutes": 10,
        "sets": 2,
        "reps": 10,
    },
    {
        "plan_id": "home_pushup_basic",
        "name": "홈 푸쉬업 기초",
        "location": "home",
        "required_equipment": [],
        "target_parts": ["chest", "arms"],
        "avoid_if_pain": ["wrist", "shoulder"],
        "intensity": "medium",
        "minutes": 10,
        "sets": 3,
        "reps": 8,
    },
    {
        "plan_id": "home_stretch_light",
        "name": "가벼운 전신 스트레칭",
        "location": "home",
        "required_equipment": ["mat"],
        "target_parts": ["full_body"],
        "avoid_if_pain": [],
        "intensity": "low",
        "minutes": 5,
        "sets": 1,
        "reps": 1,
    },
    {
        "plan_id": "home_burpee_power",
        "name": "홈 버피 파워",
        "location": "home",
        "required_equipment": [],
        "target_parts": ["full_body"],
        "avoid_if_pain": ["knee", "wrist", "shoulder"],
        "intensity": "high",
        "minutes": 15,
        "sets": 4,
        "reps": 12,
    },
    {
        "plan_id": "gym_leg_press",
        "name": "레그프레스 루틴",
        "location": "gym",
        "required_equipment": ["leg_press_machine"],
        "target_parts": ["legs"],
        "avoid_if_pain": ["knee"],
        "intensity": "medium",
        "minutes": 20,
        "sets": 4,
        "reps": 12,
    },
    {
        "plan_id": "gym_lat_pulldown",
        "name": "랫풀다운 루틴",
        "location": "gym",
        "required_equipment": ["lat_pulldown_machine"],
        "target_parts": ["back"],
        "avoid_if_pain": ["shoulder"],
        "intensity": "medium",
        "minutes": 20,
        "sets": 4,
        "reps": 10,
    },
    {
        "plan_id": "gym_deadlift_heavy",
        "name": "데드리프트 고강도 루틴",
        "location": "gym",
        "required_equipment": ["barbell"],
        "target_parts": ["back", "legs"],
        "avoid_if_pain": ["waist", "knee"],
        "intensity": "high",
        "minutes": 30,
        "sets": 5,
        "reps": 5,
    },
]


def is_equipment_satisfied(required: List[str], available: List[str]) -> bool:
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


def adjust_plan_by_experience(plan: Dict, experience_level: str) -> Dict:
    adjusted = copy.deepcopy(plan)

    if experience_level == "beginner":
        adjusted["sets"] = max(1, adjusted["sets"] - 1)
        if adjusted["reps"] > 1:
            adjusted["reps"] = max(5, adjusted["reps"] - 2)
        adjusted["minutes"] = max(5, adjusted["minutes"] - 5)

    elif experience_level == "intermediate":
        # 기본값 유지
        pass

    elif experience_level == "advanced":
        adjusted["sets"] += 1
        if adjusted["reps"] > 1:
            adjusted["reps"] += 2
        adjusted["minutes"] += 5

    return adjusted


def generate_candidates(state: Dict) -> List[Dict]:
    location = state["location"]
    available_minutes = state["available_minutes"]
    fatigue = state["fatigue"]
    pain_parts = set(state["pain_parts"])
    equipment_available = state["equipment_available"]
    experience_level = state["experience_level"]

    allowed_intensities = get_allowed_intensities(experience_level, fatigue)

    candidates = []

    for ex in EXERCISE_POOL:
        if ex["location"] != location:
            continue

        if ex["intensity"] not in allowed_intensities:
            continue

        if pain_parts.intersection(set(ex["avoid_if_pain"])):
            continue

        if not is_equipment_satisfied(ex["required_equipment"], equipment_available):
            continue

        adjusted_ex = adjust_plan_by_experience(ex, experience_level)

        if adjusted_ex["minutes"] > available_minutes:
            continue

        candidates.append(adjusted_ex)

    if not candidates:
        candidates.append(
            {
                "plan_id": "fallback_walk_light",
                "name": "대체 가벼운 걷기/스트레칭",
                "location": location,
                "required_equipment": [],
                "target_parts": ["full_body"],
                "avoid_if_pain": [],
                "intensity": "low",
                "minutes": min(available_minutes, 10),
                "sets": 1,
                "reps": 1,
            }
        )

    return candidates