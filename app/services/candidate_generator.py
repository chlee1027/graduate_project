from typing import List, Dict
import copy

EXERCISE_POOL = [
    # --- HOME EXERCISES ---
    {
        "plan_id": "home_squat_basic",
        "name": "홈 스쿼트 기초",
        "location": "home",
        "type": "rep-based",
        "required_equipment": [],
        "target_parts": ["legs"],
        "avoid_if_pain": ["knee"],
        "intensity": "low",
        "minutes": 10,
        "sets": 3,
        "reps": 12,
        "video_url": "https://www.youtube.com/results?search_query=스쿼트+자세",
    },
    {
        "plan_id": "home_pushup_basic",
        "name": "홈 푸쉬업 기초",
        "location": "home",
        "type": "rep-based",
        "required_equipment": [],
        "target_parts": ["chest", "arms"],
        "avoid_if_pain": ["wrist", "shoulder"],
        "intensity": "medium",
        "minutes": 10,
        "sets": 3,
        "reps": 10,
        "video_url": "https://www.youtube.com/results?search_query=푸쉬업+자세",
    },
    {
        "plan_id": "home_pike_pushup",
        "name": "파이크 푸쉬업 (어깨)",
        "location": "home",
        "type": "rep-based",
        "required_equipment": [],
        "target_parts": ["shoulder", "arms"],
        "avoid_if_pain": ["wrist", "shoulder"],
        "intensity": "high",
        "minutes": 15,
        "sets": 4,
        "reps": 10,
        "video_url": "https://www.youtube.com/results?search_query=파이크+푸쉬업+자세",
    },
    {
        "plan_id": "home_plank_timer",
        "name": "코어 플랭크 버티기",
        "location": "home",
        "type": "time-based",
        "required_equipment": [],
        "target_parts": ["core"],
        "avoid_if_pain": ["lower_back"],
        "intensity": "medium",
        "minutes": 5,
        "sets": 3,
        "reps": 1,
        "video_url": "https://www.youtube.com/results?search_query=플랭크+자세",
    },
    {
        "plan_id": "home_burpee_power",
        "name": "홈 버피 파워 (전신)",
        "location": "home",
        "type": "rep-based",
        "required_equipment": [],
        "target_parts": ["full_body"],
        "avoid_if_pain": ["knee", "wrist", "shoulder"],
        "intensity": "high",
        "minutes": 15,
        "sets": 4,
        "reps": 15,
        "video_url": "https://www.youtube.com/results?search_query=버피테스트+자세",
    },

    # --- GYM EXERCISES ---
    {
        "plan_id": "gym_bench_press",
        "name": "바벨 벤치프레스",
        "location": "gym",
        "type": "rep-based",
        "required_equipment": ["barbell", "bench"],
        "target_parts": ["chest", "arms"],
        "avoid_if_pain": ["shoulder", "wrist"],
        "intensity": "high",
        "minutes": 20,
        "sets": 5,
        "reps": 8,
        "video_url": "https://www.youtube.com/results?search_query=벤치프레스+자세",
    },
    {
        "plan_id": "gym_deadlift",
        "name": "컨벤셔널 데드리프트",
        "location": "gym",
        "type": "rep-based",
        "required_equipment": ["barbell"],
        "target_parts": ["back", "legs", "core"],
        "avoid_if_pain": ["lower_back", "knee"],
        "intensity": "high",
        "minutes": 25,
        "sets": 5,
        "reps": 5,
        "video_url": "https://www.youtube.com/results?search_query=데드리프트+자세",
    },
    {
        "plan_id": "gym_barbell_squat",
        "name": "바벨 백 스쿼트",
        "location": "gym",
        "type": "rep-based",
        "required_equipment": ["barbell", "squat_rack"],
        "target_parts": ["legs", "core"],
        "avoid_if_pain": ["knee", "lower_back"],
        "intensity": "high",
        "minutes": 25,
        "sets": 5,
        "reps": 8,
        "video_url": "https://www.youtube.com/results?search_query=바벨+스쿼트+자세",
    },
    {
        "plan_id": "gym_lat_pulldown",
        "name": "랫풀다운 (등)",
        "location": "gym",
        "type": "rep-based",
        "required_equipment": ["lat_pulldown_machine"],
        "target_parts": ["back"],
        "avoid_if_pain": ["shoulder"],
        "intensity": "medium",
        "minutes": 15,
        "sets": 4,
        "reps": 12,
        "video_url": "https://www.youtube.com/results?search_query=랫풀다운+자세",
    },
    {
        "plan_id": "gym_leg_press",
        "name": "레그프레스 머신",
        "location": "gym",
        "type": "rep-based",
        "required_equipment": ["leg_press_machine"],
        "target_parts": ["legs"],
        "avoid_if_pain": ["knee"],
        "intensity": "medium",
        "minutes": 15,
        "sets": 4,
        "reps": 12,
        "video_url": "https://www.youtube.com/results?search_query=레그프레스+사용법",
    },
    {
        "plan_id": "gym_walking_treadmill",
        "name": "트레드밀 인터벌 러닝",
        "location": "gym",
        "type": "time-based",
        "required_equipment": ["treadmill"],
        "target_parts": ["cardio", "legs"],
        "avoid_if_pain": ["knee", "ankle"],
        "intensity": "medium",
        "minutes": 20,
        "sets": 1,
        "reps": 1,
        "video_url": "https://www.youtube.com/results?search_query=인터벌+러닝+가이드",
    },
    {
        "plan_id": "gym_bike_intense",
        "name": "실내 자전거 고강도",
        "location": "gym",
        "type": "time-based",
        "required_equipment": ["stationary_bike"],
        "target_parts": ["cardio", "legs"],
        "avoid_if_pain": ["knee"],
        "intensity": "high",
        "minutes": 20,
        "sets": 1,
        "reps": 1,
        "video_url": "https://www.youtube.com/results?search_query=사이클+고강도+훈련",
    },

    # --- RECOVERY / STRETCHING ---
    {
        "plan_id": "home_stretch_full",
        "name": "전신 이완 스트레칭",
        "location": "home",
        "type": "time-based",
        "required_equipment": [],
        "target_parts": ["full_body"],
        "avoid_if_pain": [],
        "intensity": "low",
        "minutes": 10,
        "sets": 1,
        "reps": 1,
        "is_stretching": True,
        "video_url": "https://www.youtube.com/results?search_query=전신+스트레칭+10분",
    },
    {
        "plan_id": "gym_foam_roller",
        "name": "폼롤러 근막 이완",
        "location": "gym",
        "type": "time-based",
        "required_equipment": ["foam_roller"],
        "target_parts": ["full_body"],
        "avoid_if_pain": [],
        "intensity": "low",
        "minutes": 15,
        "sets": 1,
        "reps": 1,
        "is_stretching": True,
        "video_url": "https://www.youtube.com/results?search_query=폼롤러+전신+루틴",
    },
]


def is_equipment_satisfied(required: List[str], available: List[str]) -> bool:
    # If no equipment required, it's satisfied
    if not required:
        return True
    # For now, if we don't have detailed equipment list from user, 
    # assume they have basic gym equipment if they prefer gym.
    # We will refine this later by actually using state["equipment_available"].
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
    
    # Ensure equipment_available is a list
    equipment_available = state.get("equipment_available", [])
    if not equipment_available and location == "gym":
        # Temporary fallback: assume gym has basic machines if in gym mode
        equipment_available = ["barbell", "bench", "lat_pulldown_machine", "leg_press_machine", "treadmill", "stationary_bike", "squat_rack"]

    experience_level = state["experience_level"]
    want_stretching = state.get("want_stretching", False)

    allowed_intensities = get_allowed_intensities(experience_level, fatigue)

    candidates = []

    for ex in EXERCISE_POOL:
        if ex["location"] != location:
            continue

        # If user wants stretching, only show stretching
        if want_stretching and not ex.get("is_stretching", False):
            continue
        
        # If normal workout day, but user didn't explicitly ask for stretch, 
        # still allow low-intensity ones but focus on intensities
        if not want_stretching and ex["intensity"] not in allowed_intensities:
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
                "type": "time-based",
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
