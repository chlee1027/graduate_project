import random
from typing import Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import BanditStat

EPSILON = settings.EPSILON


def get_user_plan_avg_reward(db: Session, user_id: str, plan_id: str) -> float:
    stat = (
        db.query(BanditStat)
        .filter(BanditStat.user_id == user_id, BanditStat.plan_id == plan_id)
        .first()
    )
    return stat.avg_reward if stat else 0.0


def select_action(
    candidates: List[Dict],
    state: Dict,
    avg_reward_of: Callable[[str], float],
    epsilon: float = EPSILON,
    rng: Optional[random.Random] = None,
) -> Dict:
    """ε-greedy 선택. DB 없이 돌도록 과거 보상 평균은 avg_reward_of(plan_id) 로 받는다.

    rng 를 넘기면 그 난수열을 쓰고(시뮬레이터), 안 넘기면 random 모듈 전역 난수를 쓴다(앱).
    """
    if not candidates:
        raise ValueError("No candidates available")
    r = rng or random

    if r.random() < epsilon:
        choice = r.choice(candidates)
        return {
            "selected_plan": choice,
            "reason": "exploration",
        }

    best_score = None
    best_candidates = []

    for candidate in candidates:
        avg_reward = avg_reward_of(candidate["plan_id"])
        score = rule_score(candidate, state, base=avg_reward)

        if best_score is None or score > best_score:
            best_score = score
            best_candidates = [candidate]
        elif score == best_score:
            best_candidates.append(candidate)

    selected = r.choice(best_candidates)

    return {
        "selected_plan": selected,
        "reason": "exploitation",
    }


def rule_score(candidate: Dict, state: Dict, base: float = 0.0) -> float:
    """base(과거 보상 평균)에 손 규칙 점수를 더한다. 부위 우선순위 점수를 0.01 배 하고 상황 가산점을 더한다.

    더하는 순서가 바뀌면 부동소수 반올림이 달라져 동점 판정이 바뀔 수 있으므로 예전 순서를 지킨다.
    """
    # 0.01 단위 가중치로 조정하여 보상값 영향력 강화
    score = base + candidate.get("priority_score", 0) * 0.01

    if state["fatigue"] >= 3 and candidate["intensity"] == "low":
        score += 0.2
    if state["available_minutes"] <= 10 and candidate["minutes"] <= 10:
        score += 0.2
    if state["recent_adherence_7d"] < 0.5 and candidate["intensity"] == "low":
        score += 0.1
    return score


def select_action_db(db: Session, user_id: str, state: Dict, candidates: List[Dict]) -> Dict:
    return select_action(
        candidates,
        state,
        lambda plan_id: get_user_plan_avg_reward(db, user_id, plan_id),
    )


def update_bandit_db(db: Session, user_id: str, plan_id: str, reward: float) -> dict:
    stat = (
        db.query(BanditStat)
        .filter(BanditStat.user_id == user_id, BanditStat.plan_id == plan_id)
        .first()
    )

    if not stat:
        stat = BanditStat(
            user_id=user_id,
            plan_id=plan_id,
            count=0,
            total_reward=0.0,
            avg_reward=0.0,
        )
        db.add(stat)

    stat.count += 1
    stat.total_reward += reward
    stat.avg_reward = round(stat.total_reward / stat.count, 4)

    db.commit()
    db.refresh(stat)

    return {
        "count": stat.count,
        "total_reward": stat.total_reward,
        "avg_reward": stat.avg_reward,
    }