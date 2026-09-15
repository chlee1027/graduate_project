"""추천에 쓰인 운동이 exercise_plans 에 반드시 남아 있게 한다.

ExerciseLog.plan_id 는 exercise_plans.plan_id 를 가리키는 외래키다. 그런데
seed 에 없는 plan_id 가 추천으로 나가는 자리가 둘 있다.

  - 후보가 하나도 남지 않았을 때의 대체 운동 (candidate_generator 의 fallback)
  - 스트릭 테스트용 기록 (routers/debug)

그대로 두면 사용자가 그 운동을 마쳤을 때 로그 저장이 외래키 위반으로 깨지고
500 이 나간다. 저장하기 전에 해당 plan 을 만들어 두어 막는다.
"""

from sqlalchemy.orm import Session

from app.db.models import ExercisePlan


def ensure_plan_exists(db: Session, plan: dict) -> None:
    """plan 딕셔너리가 가리키는 운동이 없으면 만들어 둔다. 있으면 아무것도 하지 않는다."""
    plan_id = (plan or {}).get("plan_id")
    if not plan_id:
        return

    existing = db.query(ExercisePlan).filter(ExercisePlan.plan_id == plan_id).first()
    if existing:
        return

    db.add(ExercisePlan(
        plan_id=plan_id,
        name=plan.get("name") or plan_id,
        location=plan.get("location") or "home",
        type=plan.get("type") or "time-based",
        required_equipment=plan.get("required_equipment") or "",
        target_parts=plan.get("target_parts") or "full_body",
        sub_target_parts=plan.get("sub_target_parts"),
        avoid_if_pain=plan.get("avoid_if_pain") or "",
        intensity=plan.get("intensity") or "low",
        minutes=plan.get("minutes") or 10,
        sets=plan.get("sets") or 1,
        reps=plan.get("reps") or 1,
        target_rpe=plan.get("target_rpe"),
        # 통계의 칼로리 계산이 met_value 를 곱하므로 비워 두면 안 된다.
        rest_seconds=plan.get("rest_seconds") or 60,
        met_value=plan.get("met_value") or 3.0,
        is_stretching=bool(plan.get("is_stretching")),
        description=plan.get("description"),
        tip=plan.get("tip"),
        video_url=plan.get("video_url"),
    ))
    db.flush()
