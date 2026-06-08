from typing import List, Dict
import copy
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import ExercisePlan, ExerciseLog
from datetime import datetime, timedelta

# 근육 이름 한글 매핑 및 부상 간접 영향권 정의
MUSCLE_KO_MAP = {
    "legs": "하체", "chest": "가슴", "back": "등", "shoulder": "어깨", "arms": "팔", "core": "코어",
    "quadriceps": "대퇴사두(앞허벅지)", "hamstrings": "햄스트링(뒷허벅지)", "glutes": "둔근(엉덩이)",
    "adductor": "내전근(안쪽 허벅지)", "calves": "종아리",
    "upper_chest": "상부 가슴", "middle_chest": "중부 가슴", "lower_chest": "하부 가슴",
    "lats": "광배근(옆구리쪽 등)", "traps": "승모근", "lower_back": "기립근(허리)",
    "biceps": "이두(알통)", "triceps": "삼두(팔 뒤)", "forearms": "전완근(팔둑)",
    "abs": "복근", "obliques": "외복사근(옆구리)", "full_body": "전신"
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

def adjust_plan_dynamically(plan_obj: ExercisePlan, experience_level: str, fatigue: int) -> Dict:
    """
    숙련도와 피로도에 따라 세트, 횟수, 휴식 시간을 동적으로 조정합니다.
    """
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
        "rest_seconds": plan_obj.rest_seconds or 60,
        "met_value": plan_obj.met_value,
        "is_stretching": plan_obj.is_stretching,
        "description": plan_obj.description,
        "tip": plan_obj.tip,
        "video_url": plan_obj.video_url
    }

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
        if target_parts:
            parts = [p.strip() for p in target_parts.split(",") if p.strip()]
            for p in parts:
                major_counts[p] = major_counts.get(p, 0) + 1
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
    user_goal = state.get("goal", "health")
    want_stretching = state.get("want_stretching", False)

    equipment_available = state.get("equipment_available", [])
    if not equipment_available and location == "gym":
        equipment_available = ["barbell", "bench", "lat_pulldown_machine", "leg_press_machine", "treadmill", "stationary_bike", "squat_rack", "dumbbell", "cable_machine", "row_machine", "pullup_bar", "dip_station"]

    allowed_intensities = get_allowed_intensities(experience_level, fatigue)

    query = db.query(ExercisePlan).filter(ExercisePlan.location == location)
    
    # 피로도가 극심하면 스트레칭 강제 권장
    if fatigue >= 5:
        query = query.filter(ExercisePlan.is_stretching == True)
    elif want_stretching:
        query = query.filter(ExercisePlan.is_stretching == True)
    else:
        query = query.filter(
            ExercisePlan.intensity.in_(allowed_intensities),
            ExercisePlan.is_stretching == False
        )

    all_plans = query.all()
    candidates = []

    usage_stats = get_detailed_usage_stats(user_id, db)
    major_usage = usage_stats["major"]
    sub_usage = usage_stats["sub"]
    
    all_major_parts = ["legs", "chest", "back", "shoulder", "arms", "core"]
    major_priority = sorted(all_major_parts, key=lambda x: major_usage.get(x, 0))
    
    for ex in all_plans:
        # 1. 직접적 통증 부위 필터링 (완전 제외)
        ex_avoid_parts = set([p.strip() for p in (ex.avoid_if_pain or "").split(",") if p.strip()])
        if pain_parts.intersection(ex_avoid_parts):
            continue

        # 2. 간접적 통증 영향권 점수 감점 (Smart Filtering)
        indirect_penalty = 0
        ex_target_parts = [p.strip() for p in ex.target_parts.split(",") if p.strip()]
        for pain in pain_parts:
            affected = PAIN_INDIRECT_IMPACT_MAP.get(pain, [])
            for target in ex_target_parts:
                if target in affected:
                    indirect_penalty += 30 # 큰 감점을 주어 하단으로 밀어냄

        # 3. 장비 체크
        if not is_equipment_satisfied(ex.required_equipment, equipment_available):
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
        ex_sub_parts = [s.strip() for s in (ex.sub_target_parts or "").split(",") if s.strip()]
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
            relevant_pains = [MUSCLE_KO_MAP.get(p, p) for p in pain_parts if ex_target_parts[0] in PAIN_INDIRECT_IMPACT_MAP.get(p, [])]
            coach_reason = f"현재 {', '.join(relevant_pains)} 부위의 통증을 고려하여, 해당 부위에 무리가 덜 가도록 강도를 조절한 {main_muscle_ko} 운동입니다."
        
        # 2. 피로도 고려 사유
        elif fatigue >= 4:
            coach_reason = f"오늘은 피로도가 높으시네요. 평소보다 세트수와 강도를 낮춰 {main_muscle_ko} 근육을 가볍게 자극하는 방향으로 구성했습니다."
        
        # 3. 불균형 해소 사유
        elif sub_bonus >= 20:
            coach_reason = f"최근 일주일간 {main_muscle_ko} 부위 운동량이 거의 없었습니다. 신체 균형을 위해 오늘 꼭 수행하시길 권장합니다."
        
        # 4. 목표 및 숙련도 맞춤
        elif user_goal == "diet":
            coach_reason = f"체지방 연소 효율이 높은 {main_muscle_ko} 복합 운동입니다. 다이어트 목표 달성에 효과적입니다."
        elif experience_level == "advanced":
            coach_reason = f"상급자 수준에 맞춰 높은 자극을 줄 수 있는 {main_muscle_ko} 타겟팅 루틴입니다."
        
        if not coach_reason:
            coach_reason = f"전체적인 루틴 밸런스를 고려할 때 오늘은 {main_muscle_ko} 운동을 하기에 최적의 타이밍입니다."
            
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
            "priority_score": -100,
            "coach_reason": "현재 컨디션과 부상 상태를 고려하여 무리하지 않는 선에서 가벼운 움직임을 추천해요."
        })

    candidates.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    return candidates
