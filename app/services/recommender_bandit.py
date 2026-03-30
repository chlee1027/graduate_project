import random
from typing import Dict, List

from app.services.fake_db import get_user_bandit_stats, get_user_plan_stat
from app.core.config import settings

EPSILON = settings.EPSILON


def select_action(user_id: str, state: Dict, candidates: List[Dict]) -> Dict:
    if not candidates:
        raise ValueError("No candidates available")

    user_stats = get_user_bandit_stats(user_id)

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
        avg_reward = user_stats.get(plan_id, {}).get("avg_reward", 0.0)
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


def update_bandit(user_id: str, plan_id: str, reward: float) -> dict:
    stat = get_user_plan_stat(user_id, plan_id)

    stat["count"] += 1
    stat["total_reward"] += reward
    stat["avg_reward"] = round(stat["total_reward"] / stat["count"], 4)

    return stat