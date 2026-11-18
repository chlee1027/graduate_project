from typing import Dict, Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import ExercisePlan, ExerciseLog
from app.core.timezone import now_kst
from datetime import timedelta

# 근육 이름 한글 매핑 및 부상 간접 영향권 정의
MUSCLE_KO_MAP = {
    "legs": "하체", "chest": "가슴", "back": "등", "shoulder": "어깨", "arms": "팔", "core": "코어",
    "quadriceps": "대퇴사두(앞허벅지)", "hamstrings": "햄스트링(뒷허벅지)", "glutes": "둔근(엉덩이)",
    "adductor": "내전근(안쪽 허벅지)", "calves": "종아리",
    "upper_chest": "상부 가슴", "middle_chest": "중부 가슴", "lower_chest": "하부 가슴",
    "lats": "광배근(옆구리쪽 등)", "traps": "승모근", "lower_back": "기립근(허리)",
    "biceps": "이두(알통)", "triceps": "삼두(팔 뒤)", "forearms": "전완근(팔둑)",
    "abs": "복근", "obliques": "외복사근(옆구리)", "full_body": "전신",
    "front_deltoid": "전면 삼각근", "side_deltoid": "측면 삼각근", "rear_deltoid": "후면 삼각근",
    "middle_back": "등 가운데", "cardio": "유산소", "shoulder": "어깨"
}

# 통증·부상 부위(관절) 이름. MUSCLE_KO_MAP 의 lower_back 은 근육(기립근) 이름이라 따로 둔다.
JOINT_KO_MAP = {
    "knee": "무릎", "lower_back": "허리", "shoulder": "어깨", "wrist": "손목", "ankle": "발목",
    "elbow": "팔꿈치", "neck": "목", "hip": "골반",
}

# 통증 부위별 간접적으로 영향을 받는 부위 (해당 부위 운동 시 주의 필요)
PAIN_INDIRECT_IMPACT_MAP = {
    "wrist": ["chest", "back", "shoulder", "arms"], # 손목: 대부분의 상체 중량 운동
    "knee": ["legs"],                               # 무릎: 대부분의 하체 운동
    "lower_back": ["legs", "back", "core"],        # 허리: 스쿼트, 데드리프트, 로우 등
    "shoulder": ["chest", "back", "arms"],          # 어깨: 밀기, 당기기 운동 전체
    "ankle": ["legs"]                               # 발목: 스쿼트, 런지 등
}

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

    # 피로도에 따른 강도 제한 강화
    if fatigue >= 3:
        allowed = [x for x in allowed if x != "high"]
    if fatigue >= 4:
        allowed = ["low"]
    return allowed

PLAN_FIELDS = (
    "plan_id", "name", "location", "type", "required_equipment", "target_parts",
    "sub_target_parts", "avoid_if_pain", "intensity", "minutes", "sets", "reps",
    "target_rpe", "rest_seconds", "met_value", "is_stretching", "description", "tip",
    "video_url",
)


def plan_to_dict(plan_obj: ExercisePlan) -> Dict:
    """ORM 행을 후보 생성이 쓰는 딕셔너리로 바꾼다. 시뮬레이터는 같은 모양의 딕셔너리를 바로 넘긴다."""
    return {field: getattr(plan_obj, field) for field in PLAN_FIELDS}


def adjust_plan_dynamically(plan_in: Dict, experience_level: str, fatigue: int) -> Dict:
    """
    숙련도와 피로도에 따라 세트, 횟수, 휴식 시간을 동적으로 조정합니다.
    """
    plan = {field: plan_in.get(field) for field in PLAN_FIELDS}
    plan["rest_seconds"] = plan["rest_seconds"] or 60
    plan["is_stretching"] = bool(plan["is_stretching"])

    # 1. 숙련도별 기본 조정
    if experience_level == "beginner":
        plan["sets"] = max(1, plan["sets"] - 1)
        if plan["reps"] > 1:
            plan["reps"] = max(5, plan["reps"] - 2)
    elif experience_level == "advanced":
        plan["sets"] += 1
        if plan["reps"] > 1:
            plan["reps"] += 2

    # 2. 피로도별 동적 조정 (Advanced AI 로직)
    if fatigue == 3:
        plan["rest_seconds"] += 15
    elif fatigue == 4:
        plan["sets"] = max(1, plan["sets"] - 1)
        plan["rest_seconds"] += 30
        plan["target_rpe"] = max(5, (plan["target_rpe"] or 7) - 1)
    elif fatigue >= 5:
        plan["sets"] = 1
        plan["reps"] = max(1, int(plan["reps"] * 0.5))
        plan["rest_seconds"] += 60
        plan["target_rpe"] = 5

    return plan

def get_detailed_usage_stats(user_id: str, db: Session) -> Dict[str, Dict[str, int]]:
    """
    최근 7일간 운동 로그를 분석하여, 대분류(target_parts) 및 소분류(sub_target_parts)별 수행 횟수를 반환합니다.
    """
    seven_days_ago = now_kst() - timedelta(days=7)
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
        if target_parts:
            parts = [p.strip() for p in target_parts.split(",") if p.strip()]
            for p in parts:
                major_counts[p] = major_counts.get(p, 0) + 1
        if sub_target_parts:
            subs = [s.strip() for s in sub_target_parts.split(",") if s.strip()]
            for s in subs:
                sub_counts[s] = sub_counts.get(s, 0) + 1

    return {"major": major_counts, "sub": sub_counts}

def build_candidates(plans: Iterable[Dict], state: Dict, usage_stats: Dict[str, Dict[str, int]]) -> List[Dict]:
    """DB 없이 후보를 만든다. plans 는 plan_to_dict 모양의 딕셔너리, usage_stats 는
    get_detailed_usage_stats 와 같은 모양({"major": {...}, "sub": {...}})이다."""
    location = state["location"]
    available_minutes = state["available_minutes"]
    fatigue = state["fatigue"]
    pain_parts = set(state["pain_parts"])
    experience_level = state["experience_level"]
    user_goal = state.get("goal", "health")
    want_stretching = state.get("want_stretching", False)

    equipment_available = state.get("equipment_available", [])
    if not equipment_available and location == "gym":
        equipment_available = ["barbell", "bench", "lat_pulldown_machine", "leg_press_machine", "treadmill", "stationary_bike", "squat_rack", "dumbbell", "cable_machine", "row_machine", "pullup_bar", "dip_station"]

    allowed_intensities = get_allowed_intensities(experience_level, fatigue)

    # 예전에는 SQL 로 걸던 장소·강도·스트레칭 필터. 시뮬레이터도 같은 규칙을 쓰도록 여기로 옮겼다.
    stretching_only = fatigue >= 5 or want_stretching
    all_plans = []
    for ex in plans:
        if ex["location"] != location:
            continue
        if stretching_only:
            if not ex.get("is_stretching"):
                continue
        elif ex.get("is_stretching") or ex["intensity"] not in allowed_intensities:
            continue
        all_plans.append(ex)

    candidates = []

    major_usage = usage_stats["major"]
    sub_usage = usage_stats["sub"]

    all_major_parts = ["legs", "chest", "back", "shoulder", "arms", "core"]
    major_priority = sorted(all_major_parts, key=lambda x: major_usage.get(x, 0))
    
    for ex in all_plans:
        # 1. 직접적 통증 부위 필터링 (완전 제외)
        ex_avoid_parts = set([p.strip() for p in (ex.get("avoid_if_pain") or "").split(",") if p.strip()])
        if pain_parts.intersection(ex_avoid_parts):
            continue

        # 2. 간접적 통증 영향권 점수 감점 (Smart Filtering)
        indirect_penalty = 0
        ex_target_parts = [p.strip() for p in ex["target_parts"].split(",") if p.strip()]
        for pain in pain_parts:
            affected = PAIN_INDIRECT_IMPACT_MAP.get(pain, [])
            for target in ex_target_parts:
                if target in affected:
                    indirect_penalty += 30 # 큰 감점을 주어 하단으로 밀어냄

        # 3. 장비 체크
        if not is_equipment_satisfied(ex.get("required_equipment"), equipment_available):
            continue

        # 4. 동적 조정 (피로도/숙련도 반영)
        adjusted_ex = adjust_plan_dynamically(ex, experience_level, fatigue)

        # 5. 가용 시간 체크
        if adjusted_ex["minutes"] > available_minutes:
            continue
            
        # --- PT 코치 로직: 가중치 시스템 ---
        
        # 대분류 점수
        max_major_score = 0
        for p in ex_target_parts:
            if p in major_priority:
                score = (len(major_priority) - major_priority.index(p)) * 10
                max_major_score = max(max_major_score, score)
        
        # 소분류 점수
        ex_sub_parts = [s.strip() for s in (ex.get("sub_target_parts") or "").split(",") if s.strip()]
        sub_bonus = 0
        for s in ex_sub_parts:
            count = sub_usage.get(s, 0)
            if count == 0: sub_bonus = max(sub_bonus, 20)
            elif count <= 2: sub_bonus = max(sub_bonus, 10)
        
        priority_score = max_major_score + sub_bonus - indirect_penalty
        
        # --- PT 코치 코멘트 생성 (고급화) ---
        coach_reason = ""
        main_muscle_ko = MUSCLE_KO_MAP.get(ex_sub_parts[0] if ex_sub_parts else ex_target_parts[0], "전신")

        # 1. 통증/부상 고려 사유 (최우선)
        if indirect_penalty > 0:
            # 감점과 같은 규칙(운동의 모든 대상 부위)으로 어떤 통증 때문인지 고른다
            relevant_pains = sorted(
                JOINT_KO_MAP.get(p, p) for p in pain_parts
                if set(ex_target_parts) & set(PAIN_INDIRECT_IMPACT_MAP.get(p, []))
            )
            coach_reason = f"{', '.join(relevant_pains)} 쪽이 불편한 점을 고려해, 그 부위에 무리가 덜 가는 {main_muscle_ko} 운동을 골랐어요."
        
        # 2. 피로도 고려 사유
        elif fatigue >= 4:
            coach_reason = f"피로도가 높아 평소보다 세트와 강도를 낮춘 {main_muscle_ko} 운동을 골랐어요."
        
        # 3. 불균형 해소 사유
        elif sub_bonus >= 20:
            coach_reason = f"최근 7일 동안 {main_muscle_ko} 운동을 하지 않아서 골랐어요."
        
        # 4. 목표 및 숙련도 맞춤
        elif user_goal == "weight_loss":
            coach_reason = f"체중 감량 목표에 맞춰 {main_muscle_ko} 운동을 골랐어요."
        elif experience_level == "advanced":
            coach_reason = f"상급 숙련도에 맞춰 {main_muscle_ko} 운동을 골랐어요."
        
        if not coach_reason:
            coach_reason = f"최근 운동한 부위를 보고 {main_muscle_ko} 운동을 골랐어요."
            
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
            "target_rpe": 3,
            "rest_seconds": 60,
            # seed 에 없는 운동이라 로그 저장 때 exercise_plans 에 만들어 넣는다.
            # 통계의 칼로리 계산이 met_value 를 곱하므로 값을 비워 두지 않는다.
            "met_value": 3.0,
            "is_stretching": True,
            "description": "가볍게 걷거나 몸을 풀어 주는 회복 위주의 움직임입니다.",
            "tip": "숨이 차지 않는 속도로 움직이세요.",
            "video_url": None,
            "priority_score": -100,
            "coach_reason": "조건에 맞는 운동이 없어 가벼운 걷기와 스트레칭을 골랐어요."
        })

    candidates.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    return candidates


def generate_candidates(state: Dict, db: Session) -> List[Dict]:
    plans = [plan_to_dict(p) for p in db.query(ExercisePlan).filter(ExercisePlan.location == state["location"]).all()]
    usage_stats = get_detailed_usage_stats(state["user_id"], db)
    return build_candidates(plans, state, usage_stats)
