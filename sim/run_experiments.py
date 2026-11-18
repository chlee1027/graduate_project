"""추천 방식 비교 실험.

    python -m sim.run_experiments            # 조율 + 본 실험, 결과는 sim/results/
    python -m sim.run_experiments --quick    # seed 를 줄여 빨리 한 번

1. 조율: 개발 seed(0~4), main 시나리오에서 epsilon·alpha 후보를 돌려 기대 보상 평균이 가장 큰 값을 고른다.
2. 본 실험: 시험 seed(100~109)에서 네 시나리오 x 일곱 방식. 조율에 쓴 seed 는 다시 쓰지 않는다.
"""

from __future__ import annotations

import argparse
import math
import time
import warnings
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

RESULTS = Path(__file__).resolve().parent / "results"
DEV_SEEDS = list(range(0, 5))
TEST_SEEDS = list(range(100, 110))
TUNE_GRID = {
    # 빠른 실행에서 고른 값이 격자 끝(eps 0.3, hybrid 1.0)이어서 바깥쪽으로 넓혔다
    "eps": [0.05, 0.1, 0.2, 0.3, 0.5, 0.7],
    "shared": [0.1, 0.3, 1.0, 3.0],
    "hybrid": [0.1, 0.3, 1.0, 3.0],
}
CURVE_K = 40      # 사용자의 k 번째 세션 곡선을 몇 번째까지 남길지


def summarize(rows, spec, seed, scenario):
    df = pd.DataFrame(rows)
    df["regret"] = df["best_exp"] - df["exp_reward"]
    out = {
        "scenario": scenario, "policy": spec, "seed": seed, "sessions": len(df),
        "exp_reward": df.exp_reward.mean(), "regret": df.regret.mean(),
        "reward": df.reward.mean(), "completed": df.completed.mean(), "pain": df.pain.mean(),
        "rpe_good": df.rpe_good.mean(),
        "regret_k1_5": df[df.k <= 5].regret.mean(),
        "regret_k6_20": df[(df.k > 5) & (df.k <= 20)].regret.mean(),
        "regret_k21p": df[df.k > 20].regret.mean(),
    }
    for lvl in ["beginner", "intermediate", "advanced"]:
        out[f"regret_{lvl}"] = df[df.level == lvl].regret.mean()
    # 사용자별 운동 분포
    ent, top = [], []
    for _, g in df.groupby("user"):
        if len(g) < 10:
            continue
        parts = Counter(p.strip() for tp in g.target_parts for p in tp.split(",") if p.strip())
        tot = sum(parts.values())
        h = -sum(c / tot * math.log(c / tot) for c in parts.values())
        ent.append(h / math.log(6))      # 대분류 여섯이 고르면 1
        top.append(g.plan_id.value_counts().iloc[0] / len(g))
    out["part_entropy"] = sum(ent) / len(ent)
    out["top_plan_share"] = sum(top) / len(top)
    curve = (df[df.k <= CURVE_K].groupby("k")[["regret", "exp_reward"]].mean().reset_index()
             .assign(scenario=scenario, policy=spec, seed=seed))
    return out, curve


def job(args):
    from sim import simulator as S
    from sim.policies import make_policy
    spec, seed, scenario = args
    t = time.time()
    rows = S.run(make_policy(spec, seed), seed, S.SCENARIOS[scenario])
    out, curve = summarize(rows, spec, seed, scenario)
    out["seconds"] = time.time() - t
    return out, curve


def run_jobs(jobs, procs):
    with Pool(procs) as pool:
        res = pool.map(job, jobs, chunksize=1)
    return pd.DataFrame([r[0] for r in res]), pd.concat([r[1] for r in res], ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--procs", type=int, default=14)
    a = ap.parse_args()
    dev = DEV_SEEDS[:2] if a.quick else DEV_SEEDS
    test = TEST_SEEDS[:2] if a.quick else TEST_SEEDS
    RESULTS.mkdir(exist_ok=True)

    t0 = time.time()
    tune_jobs = [(f"{k}:{v:g}", s, "main") for k, vs in TUNE_GRID.items() for v in vs for s in dev]
    tune, _ = run_jobs(tune_jobs, a.procs)
    tune.to_csv(RESULTS / "tuning.csv", index=False)
    means = tune.groupby("policy").exp_reward.mean()
    best = {k: max((f"{k}:{v:g}" for v in vs), key=lambda p: means[p]) for k, vs in TUNE_GRID.items()}
    print("tuning", means.round(4).to_dict(), "->", best, f"{time.time() - t0:.0f}s")

    specs = ["random", "rule", "eps:0.2", best["eps"], best["shared"], best["hybrid"], "oracle"]
    specs = list(dict.fromkeys(specs))   # 앱 값 0.2 가 조율 결과와 같으면 한 번만
    test_jobs = [(p, s, sc) for sc in ["main", "shipped", "no_pref", "strong_pref"] for p in specs for s in test]
    runs, curves = run_jobs(test_jobs, a.procs)
    runs.to_csv(RESULTS / "runs.csv", index=False)
    curves.to_csv(RESULTS / "curves.csv", index=False)
    pd.Series(best).to_csv(RESULTS / "tuned.csv", header=["spec"])
    print(f"done {len(test_jobs)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
