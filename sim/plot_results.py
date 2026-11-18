"""sim/results/ 의 CSV 로 docs/figures/ 그림을 그린다: python -m sim.plot_results"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "sim" / "results"
FIG = ROOT / "docs" / "figures"

plt.rcParams.update({
    "font.family": "Malgun Gothic", "axes.unicode_minus": False, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#8a8984",
    "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.8, "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
})
INK, MUTED = "#0b0b0b", "#8a8984"
SCEN_KO = {"main": "기본", "shipped": "앱이 보내는 고정값", "no_pref": "부위 선호 없음", "strong_pref": "부위 선호 강함"}


def labels(tuned):
    return {
        "random": "무작위", "rule": "규칙만", "eps:0.2": "지금 앱 (ε=0.2)",
        tuned["eps"]: f"ε-greedy 조율 (ε={tuned['eps'].split(':')[1]})",
        tuned["shared"]: f"LinUCB 공유 (α={tuned['shared'].split(':')[1]})",
        tuned["hybrid"]: f"LinUCB hybrid (α={tuned['hybrid'].split(':')[1]})",
        tuned["balance"]: f"hybrid + 부위 균형 (λ={tuned['balance'].split(':')[2]})",
        "oracle": "오라클 (상한)",
    }


def colors(tuned):
    # 참고 팔레트 categorical 순서(파랑, 주황, 청록, 노랑, 자홍). 무작위는 회색 점선 기준선.
    return {"random": MUTED, "rule": "#eda100", "eps:0.2": "#eb6834", tuned["eps"]: "#e87ba4",
            tuned["shared"]: "#1baf7a", tuned["hybrid"]: "#2a78d6", tuned["balance"]: "#6250d6",
            "oracle": INK}


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    runs = pd.read_csv(RES / "runs.csv")
    curves = pd.read_csv(RES / "curves.csv")
    tuned = pd.read_csv(RES / "tuned.csv", index_col=0)["spec"].to_dict()
    L, C = labels(tuned), colors(tuned)
    order = [p for p in ["random", "rule", "eps:0.2", tuned["eps"], tuned["shared"], tuned["hybrid"], tuned["balance"]]
             if p in set(runs.policy)]
    order = list(dict.fromkeys(order))

    # 1. 기본 시나리오: k 번째 세션의 regret
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    cm = curves[curves.scenario == "main"]
    for p in order:
        g = cm[cm.policy == p].groupby("k").regret
        m, s = g.mean(), g.std()
        ls = "--" if p == "random" else "-"
        ax.plot(m.index, m.values, ls, color=C[p], lw=2, label=L[p])
        ax.fill_between(m.index, m - s, m + s, color=C[p], alpha=0.10, lw=0)
        if p in (tuned["shared"],):   # 나머지 선은 겹쳐서 범례로만 가린다
            ax.annotate(L[p], (m.index[-1], m.values[-1]), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=8.5, color="#52514e")
    ax.set_xlabel("사용자의 k 번째 세션")
    ax.set_ylabel("세션당 regret (오라클과의 기대 보상 차)")
    ax.set_xlim(1, cm.k.max() + 11)
    ax.set_ylim(bottom=0)
    ax.set_xticks([1, 10, 20, 30, 40])
    ax.legend(frameon=False, fontsize=8.5, loc="upper right", ncol=2)
    ax.set_title("기본 시나리오, 시험 seed 10개 평균 (띠 = seed 간 표준편차)", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "sim_regret_curve.png", dpi=160)
    plt.close(fig)

    # 2. 시나리오별 기대 보상: 작은 그림 넷, 행 = 방식
    rows = order + ["oracle"]
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.6), sharey=True)
    for ax, sc in zip(axes, SCEN_KO):
        r = runs[runs.scenario == sc]
        for i, p in enumerate(rows):
            v = r[r.policy == p].exp_reward
            ax.errorbar(v.mean(), i, xerr=v.std(), fmt="o", ms=6, color=C[p], ecolor=C[p], elinewidth=1.5, capsize=0)
        ax.set_title(SCEN_KO[sc], fontsize=10, color=INK)
        ax.set_xlabel("세션당 기대 보상")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(range(len(rows)), [L[p] for p in rows])
    axes[0].invert_yaxis()
    fig.suptitle("시나리오별 기대 보상 (점 = 시험 seed 10개 평균, 막대 = ±1 표준편차)", fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "sim_scenarios.png", dpi=160)
    plt.close(fig)

    # 3. 기본 시나리오: 기대 보상 대 부위 고르기(엔트로피)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    r = runs[runs.scenario == "main"].groupby("policy")[["exp_reward", "part_entropy"]].mean()
    for p in rows:
        ax.plot(r.loc[p, "part_entropy"], r.loc[p, "exp_reward"], "o", ms=8, color=C[p])
        off = {"random": (8, 0), "rule": (0, -15), tuned["eps"]: (-8, 7), tuned["hybrid"]: (-8, 8),
               tuned["balance"]: (-8, -10)}.get(p, (7, -3))
        ax.annotate(L[p], (r.loc[p, "part_entropy"], r.loc[p, "exp_reward"]), xytext=off,
                    textcoords="offset points", fontsize=8.5, color="#52514e",
                    ha="right" if off[0] < 0 else ("center" if off[0] == 0 else "left"), va="center")
    ax.set_xlabel("부위 분포 엔트로피 (대분류 여섯이 고르면 1)")
    ax.set_ylim(bottom=r.exp_reward.min() - 0.022)
    ax.set_ylabel("세션당 기대 보상")
    ax.set_xlim(right=max(1.0, r.part_entropy.max() + 0.12))
    ax.set_title("기본 시나리오: 보상과 운동 부위 고르기", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "sim_reward_vs_balance.png", dpi=160)
    plt.close(fig)
    # 4. 균형 가중치 훑기 (개발 seed)
    bal = pd.read_csv(RES / "balance.csv")
    bm = bal.groupby("policy")[["exp_reward", "part_entropy"]].mean()
    rule = bm.loc["rule"]
    sweep = bm.drop(index="rule")
    sweep["lam"] = [float(p.split(":")[2]) for p in sweep.index]
    sweep = sweep.sort_values("lam")
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(sweep.part_entropy, sweep.exp_reward, "-o", color="#6250d6", lw=2, ms=6)
    for _, row in sweep.iterrows():
        chosen = f"{row.lam:g}" == tuned["balance"].split(":")[2]
        ax.annotate(f"λ={row.lam:g}" + (" (고름)" if chosen else ""), (row.part_entropy, row.exp_reward),
                    xytext=(6, 4), textcoords="offset points", fontsize=8.5,
                    color=INK if chosen else "#52514e", fontweight="bold" if chosen else "normal")
    ax.axvline(rule.part_entropy, color=MUTED, ls="--", lw=1.2)
    ax.annotate(f"규칙만의 엔트로피 {rule.part_entropy:.3f}", (rule.part_entropy, sweep.exp_reward.min()),
                xytext=(-6, 0), textcoords="offset points", ha="right", fontsize=8.5, color="#52514e")
    ax.set_xlabel("부위 분포 엔트로피")
    ax.set_ylabel("세션당 기대 보상")
    ax.set_xlim(right=sweep.part_entropy.max() + 0.015)
    ax.set_title("hybrid LinUCB 의 균형 가중치 λ (개발 seed 5개 평균)", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "sim_balance_sweep.png", dpi=160)
    plt.close(fig)
    print("saved", [p.name for p in FIG.glob("sim_*.png")])


if __name__ == "__main__":
    main()
