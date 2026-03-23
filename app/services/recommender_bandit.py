import random
from typing import Dict, List
from app.services.fake_db import bandit_stats
from app.core.config import settings

EPSILON = settings.EPSILON


def _get_plan_stat(plan_id: str):
    if plan_id not in bandit_stats:
        bandit_stats[plan_id] = {
            "count": 0,
            "total_reward": 0.0,
            "avg_reward": 0.0,
        }
    return bandit_stats[plan_id]


def select_action(state: Dict, candidates: List[Dict]) -> Dict:
    if not candidates:
        raise ValueError("No candidates available")

    # exploration
    if random.random() < EPSILON:
        choice = random.choice(candidates)
        return {
            "selected_plan": choice,
            "reason": "exploration"
        }

    # exploitation
    best_candidate = None
    best_score = -1e9

    for candidate in candidates:
        stat = _get_plan_stat(candidate["plan_id"])
        score = stat["avg_reward"]

        # 간단한 context 반영 예시
        if state["fatigue"] >= 3 and candidate["intensity"] == "low":
            score += 0.2

        if state["available_minutes"] <= 10 and candidate["minutes"] <= 10:
            score += 0.2

        if state["recent_adherence_7d"] < 0.5 and candidate["intensity"] == "low":
            score += 0.1

        if score > best_score:
            best_score = score
            best_candidate = candidate

    return {
        "selected_plan": best_candidate,
        "reason": "exploitation"
    }


def update_bandit(plan_id: str, reward: float):
    stat = _get_plan_stat(plan_id)
    stat["count"] += 1
    stat["total_reward"] += reward
    stat["avg_reward"] = stat["total_reward"] / stat["count"]