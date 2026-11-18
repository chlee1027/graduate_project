"""가상 사용자로 추천 방식을 비교하는 시뮬레이터.

앱과 같은 코드를 그대로 부른다.
  - 후보 생성: app.services.candidate_generator.build_candidates
  - 보상 계산: app.services.reward_service.calculate_reward
  - 지금의 선택 규칙: app.services.recommender_bandit_db.select_action (policies.py 에서)

앱이 모르는 것(사용자의 숨은 속성)은 여기서만 정한다. 이 가정이 결과를 좌우하므로
docs/simulation_eval.md 의 「시뮬레이터 가정」 절에 같은 값을 적어 두었다. 값을 바꾸면 그 절도 고친다.

용어
  세션: 사용자가 운동하는 날 한 번 추천을 받고 결과를 남기는 것.
  기대 보상: 같은 후보를 같은 날 무한히 다시 했을 때의 보상 평균. 숨은 속성을 아는 시뮬레이터만 계산할 수 있다.
  regret: 그 세션 후보 가운데 기대 보상이 가장 큰 것과 고른 것의 기대 보상 차.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.core.config import settings
from app.data.exercise_catalog import FINAL_EXERCISES
from app.services.candidate_generator import build_candidates
from app.services.reward_service import calculate_reward

# ---------------------------------------------------------------------------
# 시뮬레이터 가정 (docs/simulation_eval.md 와 같은 값)
# ---------------------------------------------------------------------------
LEVELS = ["beginner", "intermediate", "advanced"]
LEVEL_WEIGHTS = [0.4, 0.4, 0.2]
INTENSITY_LEVEL = {"low": 0, "medium": 1, "high": 2}
MAJOR_PARTS = ["legs", "chest", "back", "shoulder", "arms", "core", "cardio", "full_body"]
JOINTS = ["knee", "lower_back", "shoulder", "wrist", "ankle", "elbow"]

CAPACITY_NOISE = 0.5          # 실제 체력 = 신고 숙련도(0,1,2) + N(0, 0.5)
P_DECLARED_INJURY = 0.2       # 온보딩에서 부상 하나를 신고할 확률
P_HIDDEN_WEAK_JOINT = 0.35    # 신고 안 한 약한 관절이 하나 있을 확률
FATIGUE_WEIGHTS = [0.10, 0.25, 0.30, 0.20, 0.10, 0.05]   # 그날 피로도 0..5
MINUTES_CHOICES = [10, 15, 20, 30, 45, 60]
MINUTES_WEIGHTS = [0.10, 0.15, 0.20, 0.25, 0.15, 0.15]
P_WANT_STRETCHING = 0.08

# 결과 모형
FATIGUE_COEF = 0.35           # 난이도 d 에 피로도 (f - 2) 가 더하는 몫
SETS_COEF = 0.8               # 앱이 세트를 줄이면 d 가 0.8 * log(조정 세트/원래 세트) 만큼 준다
COMPLETE_BASE = 1.5           # 완료 로짓 = 1.5 + 0.8*선호 - 1.4*max(d,0) - 0.6*반복 - 2.0*시간초과
COMPLETE_PREF = 0.8
COMPLETE_HARD = 1.4
COMPLETE_REPEAT = 0.6
COMPLETE_OVERTIME = 2.0
RPE_BASE = 6.5                # RPE = 6.5 + 1.5*d + N(0, 0.8), 못 끝내면 +0.8
RPE_SLOPE = 1.5
RPE_NOISE = 0.8
RPE_FAIL_SHIFT = 0.8
PAIN_BASE = 0.02              # 통증 확률 = 0.02 + 0.30*[약한 관절이 그 운동의 금기 관절] + 0.04*max(d,0)
PAIN_WEAK_JOINT = 0.30
PAIN_HARD = 0.04
CARRYOVER_D = 0.5             # 전날 d > 0.5 인 운동을 끝냈으면 오늘 피로도 +1

ARRIVAL_DAYS = 60             # 사용자는 0~59일 사이 아무 날 가입한다
HORIZON_DAYS = 120

# 앱이 실제로 보내는 고정값 (frontend/app/recommend.tsx)
SHIPPED_REQUEST = {"fatigue": 2, "available_minutes": 60, "recent_adherence_7d": 0.8, "avg_rpe_last_7d": 5.0}


@dataclass
class Scenario:
    name: str
    pref_sigma: float = 0.8           # 부위 선호의 표준편차. 0 이면 선호 없음
    shipped_request: bool = False     # True 면 앱처럼 피로도·시간을 고정값으로 보낸다
    n_users: int = 200


SCENARIOS = {
    "main": Scenario("main"),
    "shipped": Scenario("shipped", shipped_request=True),
    "no_pref": Scenario("no_pref", pref_sigma=0.0),
    "strong_pref": Scenario("strong_pref", pref_sigma=1.5),
}


@dataclass
class SimUser:
    user_id: str
    experience_level: str
    capacity: float
    pref: Dict[str, float]
    injuries: List[str]
    weak_joint: Optional[str]
    location: str
    goal: str
    weekly_days: int
    arrival_day: int
    # 기록
    logs: List[dict] = field(default_factory=list)   # 세션마다 {day, plan_id, target_parts, sub_target_parts, completed, pain_parts, d}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _split(s: Optional[str]) -> List[str]:
    return [p.strip() for p in (s or "").split(",") if p.strip()]


def _rng(*key) -> random.Random:
    """키마다 독립인 난수열. 방식이 달라도 같은 (seed, 사용자, 날) 에는 같은 난수가 나온다(공통 난수)."""
    # 문자열 seed 는 Python 3 에서 실행마다 같은 난수열을 준다(hash() 와 달리 PYTHONHASHSEED 영향 없음)
    return random.Random("|".join(map(str, key)))


def make_users(seed: int, sc: Scenario) -> List[SimUser]:
    users = []
    for i in range(sc.n_users):
        r = _rng("user", seed, i)
        lvl = r.choices(LEVELS, LEVEL_WEIGHTS)[0]
        cap = LEVELS.index(lvl) + r.gauss(0, CAPACITY_NOISE)
        pref = {p: r.gauss(0, 1) * sc.pref_sigma for p in MAJOR_PARTS}
        injuries = [r.choice(JOINTS)] if r.random() < P_DECLARED_INJURY else []
        weak = None
        if r.random() < P_HIDDEN_WEAK_JOINT:
            weak = r.choice([j for j in JOINTS if j not in injuries])
        users.append(SimUser(
            user_id=f"sim_{i:03d}", experience_level=lvl, capacity=cap, pref=pref,
            injuries=injuries, weak_joint=weak, location=r.choice(["home", "gym"]),
            goal=r.choice(["health", "weight_loss", "muscle"]), weekly_days=r.randint(3, 6),
            arrival_day=r.randrange(ARRIVAL_DAYS),
        ))
    return users


# ---------------------------------------------------------------------------
# 기록에서 앱이 DB 로 계산하던 값들
# ---------------------------------------------------------------------------
def usage_stats(user: SimUser, day: int) -> Dict[str, Dict[str, int]]:
    """candidate_generator.get_detailed_usage_stats 와 같은 규칙: 최근 7일 완료 기록."""
    major, sub = {}, {}
    for lg in user.logs:
        if lg["completed"] and day - lg["day"] <= 7:
            for p in _split(lg["target_parts"]):
                major[p] = major.get(p, 0) + 1
            for s in _split(lg["sub_target_parts"]):
                sub[s] = sub.get(s, 0) + 1
    return {"major": major, "sub": sub}


def recent_pain_parts(user: SimUser, day: int) -> List[str]:
    out = set()
    for lg in user.logs:
        if lg["pain_parts"] and day - lg["day"] <= 7:
            out.update(lg["pain_parts"])
    return sorted(out)


def streak(user: SimUser, day: int, include_today: bool) -> int:
    """streak_service.get_current_streak 와 같은 규칙. 오늘 또는 어제부터 거꾸로 연속 완료일을 센다."""
    done = {lg["day"] for lg in user.logs if lg["completed"]}
    if include_today and day in done:
        check = day
    elif (day - 1) in done:
        check = day - 1
    else:
        return 0
    n = 0
    while check in done:
        n += 1
        check -= 1
    return n


# ---------------------------------------------------------------------------
# 결과 모형
# ---------------------------------------------------------------------------
@dataclass
class DayContext:
    fatigue: int
    minutes: int
    want_stretching: bool
    session: bool


def day_context(seed: int, user: SimUser, day: int) -> DayContext:
    r = _rng("ctx", seed, user.user_id, day)
    f = r.choices(range(6), FATIGUE_WEIGHTS)[0]
    last = user.logs[-1] if user.logs else None
    if last and last["day"] == day - 1 and last["completed"] and last["d"] > CARRYOVER_D:
        f = min(5, f + 1)
    return DayContext(
        fatigue=f,
        minutes=r.choices(MINUTES_CHOICES, MINUTES_WEIGHTS)[0],
        want_stretching=r.random() < P_WANT_STRETCHING,
        session=r.random() < user.weekly_days / 7,
    )


def _base_sets(plan_id: str) -> int:
    return _CATALOG[plan_id]["sets"] if plan_id in _CATALOG else 1


def outcome_params(user: SimUser, ctx: DayContext, cand: dict) -> dict:
    """후보 하나를 그날 했을 때의 숨은 확률들. 정책은 이 값을 볼 수 없다."""
    lvl = INTENSITY_LEVEL[cand["intensity"]]
    d = lvl - user.capacity + FATIGUE_COEF * (ctx.fatigue - 2)
    base_sets = _base_sets(cand["plan_id"])
    if base_sets > 0 and cand["sets"] > 0:
        d += SETS_COEF * math.log(cand["sets"] / base_sets)
    parts = _split(cand["target_parts"])
    pref = sum(user.pref.get(p, 0.0) for p in parts) / max(1, len(parts))
    recent = [lg["plan_id"] for lg in user.logs[-2:]]
    repeat = 1.0 if cand["plan_id"] in recent else 0.0
    overtime = 1.0 if cand["minutes"] > ctx.minutes else 0.0
    logit = (COMPLETE_BASE + COMPLETE_PREF * pref - COMPLETE_HARD * max(d, 0.0)
             - COMPLETE_REPEAT * repeat - COMPLETE_OVERTIME * overtime)
    avoid = _split(cand.get("avoid_if_pain"))
    weak_hit = user.weak_joint is not None and user.weak_joint in avoid
    p_pain = min(1.0, PAIN_BASE + (PAIN_WEAK_JOINT if weak_hit else 0.0) + PAIN_HARD * max(d, 0.0))
    return {"d": d, "p_complete": _sigmoid(logit), "rpe_mu": RPE_BASE + RPE_SLOPE * d,
            "p_pain": p_pain, "weak_hit": weak_hit, "avoid": avoid}


def _rpe_bonus_expect(mu: float) -> float:
    p_good = _phi((8 - mu) / RPE_NOISE) - _phi((6 - mu) / RPE_NOISE)
    p_high = 1 - _phi((9 - mu) / RPE_NOISE)
    return settings.RPE_GOOD_BONUS * p_good + settings.RPE_HIGH_PENALTY * p_high


def expected_reward(op: dict, streak_if_done: int, streak_if_fail: int) -> float:
    """calculate_reward 의 기댓값. tests/test_sim.py 가 몬테카를로와 맞춰 본다."""
    pc = op["p_complete"]
    sb = lambda s: settings.STREAK_COEF * math.log(1 + s)
    done = settings.COMPLETION_REWARD + _rpe_bonus_expect(op["rpe_mu"]) + sb(streak_if_done)
    fail = settings.FAILURE_PENALTY + _rpe_bonus_expect(op["rpe_mu"] + RPE_FAIL_SHIFT) + sb(streak_if_fail)
    return pc * done + (1 - pc) * fail + settings.PAIN_PENALTY * op["p_pain"]


def draw_outcome(op: dict, noise: random.Random) -> dict:
    completed = noise.random() < op["p_complete"]
    rpe = op["rpe_mu"] + noise.gauss(0, RPE_NOISE) + (0 if completed else RPE_FAIL_SHIFT)
    rpe = min(10.0, max(1.0, rpe))
    u = noise.random()
    pain = u < op["p_pain"]
    pain_parts: List[str] = []
    if pain:
        # 약한 관절 때문이면 그 관절을, 아니면 그 운동의 첫 금기 관절을 신고한다
        if op["weak_hit"] and u < PAIN_WEAK_JOINT:
            pain_parts = [op["weak_joint"]]
        elif op["avoid"]:
            pain_parts = [op["avoid"][0]]
    return {"completed": completed, "rpe": rpe, "pain": pain, "pain_parts": pain_parts}


_CATALOG = {ex["plan_id"]: ex for ex in FINAL_EXERCISES}
PLANS = [dict(ex) for ex in FINAL_EXERCISES]
for _p in PLANS:
    for _k in ("sub_target_parts", "target_rpe", "video_url", "description", "tip"):
        _p.setdefault(_k, None)


def build_state(user: SimUser, ctx: DayContext, day: int, sc: Scenario) -> dict:
    """recommend 라우터가 만드는 state 와 같은 모양."""
    done7 = sum(1 for lg in user.logs if lg["completed"] and day - lg["day"] <= 7)
    rpes = [lg["rpe"] for lg in user.logs if day - lg["day"] <= 7]
    req = {
        "fatigue": ctx.fatigue,
        "available_minutes": ctx.minutes,
        "recent_adherence_7d": min(1.0, done7 / user.weekly_days),
        "avg_rpe_last_7d": sum(rpes) / len(rpes) if rpes else 5.0,
    }
    if sc.shipped_request:
        req.update(SHIPPED_REQUEST)
    return {
        "user_id": user.user_id, "location": user.location, "sleep_hours": 7.0,
        "equipment_available": [], "want_stretching": ctx.want_stretching,
        **req,
        "experience_level": user.experience_level, "goal": user.goal,
        "streak": streak(user, day, include_today=True),
        "pain_parts": sorted(set(user.injuries) | set(recent_pain_parts(user, day))),
    }


def run(policy, seed: int, sc: Scenario, record_sessions: bool = True) -> List[dict]:
    """한 seed 를 처음부터 끝까지 돌린다. 세션마다 한 행을 돌려준다."""
    users = make_users(seed, sc)
    rows = []
    for day in range(HORIZON_DAYS):
        for user in users:
            if day < user.arrival_day:
                continue
            ctx = day_context(seed, user, day)
            if not ctx.session:
                continue
            state = build_state(user, ctx, day, sc)
            cands = build_candidates(PLANS, state, usage_stats(user, day))
            s_done = streak(user, day, include_today=False) + 1
            s_fail = streak(user, day, include_today=False)
            ops = [outcome_params(user, ctx, c) for c in cands]
            for op in ops:
                op["weak_joint"] = user.weak_joint
            exp = [expected_reward(op, s_done, s_fail) for op in ops]
            hist = {"recent_plan_ids": [lg["plan_id"] for lg in user.logs[-2:]],
                    "true_expected": exp}
            idx = policy.select(user.user_id, state, cands, hist)
            cand, op = cands[idx], ops[idx]
            out = draw_outcome(op, _rng("noise", seed, user.user_id, day))
            log = {"day": day, "plan_id": cand["plan_id"], "target_parts": cand["target_parts"],
                   "sub_target_parts": cand.get("sub_target_parts"), "completed": out["completed"],
                   "pain_parts": out["pain_parts"], "rpe": out["rpe"], "d": op["d"]}
            user.logs.append(log)
            # reward 라우터는 로그를 저장한 뒤 스트릭을 센다
            reward, _ = calculate_reward(out["completed"], out["rpe"], out["pain"],
                                         streak(user, day, include_today=True))
            policy.update(user.user_id, state, cands, idx, hist, reward)
            if record_sessions:
                rows.append({
                    "day": day, "user": user.user_id, "k": len(user.logs), "plan_id": cand["plan_id"],
                    "intensity": cand["intensity"], "target_parts": cand["target_parts"],
                    "n_cands": len(cands), "exp_reward": exp[idx], "best_exp": max(exp),
                    "reward": reward, "completed": out["completed"], "pain": out["pain"],
                    "rpe_good": 6 <= out["rpe"] <= 8, "d": op["d"], "level": user.experience_level,
                })
    return rows
