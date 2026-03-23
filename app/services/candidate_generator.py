from typing import List, Dict

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
        "sets": 3,
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
]


def is_equipment_satisfied(required: List[str], available: List[str]) -> bool:
    return all(item in available for item in required)


def generate_candidates(state: Dict) -> List[Dict]:
    location = state["location"]
    available_minutes = state["available_minutes"]
    fatigue = state["fatigue"]
    pain_parts = set(state["pain_parts"])
    equipment_available = state["equipment_available"]
    experience_level = state["experience_level"]

    candidates = []

    for ex in EXERCISE_POOL:
        if ex["location"] != location:
            continue

        if ex["minutes"] > available_minutes:
            continue

        if pain_parts.intersection(set(ex["avoid_if_pain"])):
            continue

        if not is_equipment_satisfied(ex["required_equipment"], equipment_available):
            continue

        if fatigue >= 3 and ex["intensity"] == "medium":
            continue

        if experience_level == "beginner" and ex["intensity"] == "high":
            continue

        candidates.append(ex)

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