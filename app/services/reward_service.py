import math
from app.core.config import settings


def calculate_reward(
    completed: bool,
    rpe: float,
    pain_occurred: bool,
    streak: int
) -> tuple[float, dict]:

    reward = 0.0
    detail = {}

    # =========================
    # 1. 완료 여부
    # =========================
    if completed:
        reward += settings.COMPLETION_REWARD
        detail["completion"] = settings.COMPLETION_REWARD
    else:
        reward += settings.FAILURE_PENALTY
        detail["completion"] = settings.FAILURE_PENALTY

    # =========================
    # 2. RPE (난이도 적절성)
    # =========================
    if 6 <= rpe <= 8:
        reward += settings.RPE_GOOD_BONUS
        detail["rpe_bonus"] = settings.RPE_GOOD_BONUS
    elif rpe > 9:
        reward += settings.RPE_HIGH_PENALTY
        detail["rpe_bonus"] = settings.RPE_HIGH_PENALTY
    else:
        detail["rpe_bonus"] = 0.0

    # =========================
    # 3. 통증 패널티
    # =========================
    if pain_occurred:
        reward += settings.PAIN_PENALTY
        detail["pain_penalty"] = settings.PAIN_PENALTY
    else:
        detail["pain_penalty"] = 0.0

    # =========================
    # 4. streak 보너스
    # =========================
    streak_bonus = settings.STREAK_COEF * math.log(1 + streak)
    reward += streak_bonus
    detail["streak_bonus"] = round(streak_bonus, 4)

    # =========================
    # 최종 정리
    # =========================
    detail["total_reward"] = round(reward, 4)

    return round(reward, 4), detail