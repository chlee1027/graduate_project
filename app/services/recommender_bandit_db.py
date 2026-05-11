import random
from typing import Dict, List

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


def select_action_db(db: Session, user_id: str, state: Dict, candidates: List[Dict]) -> Dict:
    if not candidates:
        raise ValueError("No candidates available")

    if random.random() < EPSILON:
        choice = random.choice(candidates)
        return {
            "selected_plan": choice,
            "reason": "exploration",
        }

    best_score = None
    best_candidates = []

    for candidate in candidates:
        plan_id = candidate["plan_id"]
        avg_reward = get_user_plan_avg_reward(db, user_id, plan_id)
        score = avg_reward

        if state["fatigue"] >= 3 and candidate["intensity"] == "low":
            score += 0.2
        if state["available_minutes"] <= 10 and candidate["minutes"] <= 10:
            score += 0.2
        if state["recent_adherence_7d"] < 0.5 and candidate["intensity"] == "low":
            score += 0.1

        if best_score is None or score > best_score:
            best_score = score
            best_candidates = [candidate]
        elif score == best_score:
            best_candidates.append(candidate)

    selected = random.choice(best_candidates)

    return {
        "selected_plan": selected,
        "reason": "exploitation",
    }


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