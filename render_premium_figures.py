"""Render matching premium dark/light figure sets from experiment CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


MODELS = ["QRC-Persistent", "ESN-12", "QRC-FullReset", "MLP-NoMemory"]
COLORS = {
    "QRC-Persistent": "#00BFA6",
    "ESN-12": "#4E79A7",
    "QRC-FullReset": "#F28E2B",
    "MLP-NoMemory": "#9AA4B2",
}


THEMES = {
    "dark": {
        "bg": "#07111F", "panel": "#07111F", "text": "#EDF4FC",
        "muted": "#A9B9CC", "grid": "#50637A", "edge": "#718399",
        "heat": "crest", "div": "vlag",
    },
    "light": {
        "bg": "#F7F9FC", "panel": "#F7F9FC", "text": "#10243A",
        "muted": "#60758C", "grid": "#C9D5E2", "edge": "#7C8EA3",
        "heat": "crest", "div": "vlag",
    },
}


def apply_theme(theme: dict) -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
        "mathtext.fontset": "stix",
        "mathtext.default": "it",
        "axes.unicode_minus": False,
        "figure.facecolor": theme["bg"], "savefig.facecolor": theme["bg"],
        "axes.facecolor": theme["panel"], "text.color": theme["text"],
        "axes.labelcolor": theme["muted"], "xtick.color": theme["muted"],
        "ytick.color": theme["muted"], "axes.edgecolor": theme["edge"],
        "grid.color": theme["grid"], "grid.alpha": .28,
        "axes.titleweight": "bold", "axes.titlesize": 17,
        "axes.labelsize": 12, "legend.frameon": False,
    })
    sns.set_context("talk", font_scale=.72)


def clean(ax, theme, grid="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(theme["edge"])
    ax.spines["bottom"].set_color(theme["edge"])
    ax.grid(True, axis=grid, linewidth=.8)
    ax.set_axisbelow(True)


def save(fig, out: Path, name: str):
    fig.savefig(out / name, dpi=260, bbox_inches="tight", pad_inches=.16,
                facecolor=fig.get_facecolor())
    plt.close(fig)


def direct_label(ax, x, y, label, color, theme, dy=0):
    ax.annotate(label, (x, y), xytext=(10, dy), textcoords="offset points",
                color=color, fontsize=10.5, va="center", fontweight="bold")


def success_chart(summary, out, theme):
    fig, ax = plt.subplots(figsize=(10.8, 5.9))
    for model in MODELS:
        g = summary[summary.model == model].sort_values("delay")
        lw = 3.2 if model == "QRC-Persistent" else 2.2
        ax.plot(g.delay, g.success_mean*100, "o-", lw=lw, ms=6.5,
                color=COLORS[model], label=model, zorder=4)
        if model in ["QRC-Persistent", "ESN-12"]:
            ax.fill_between(g.delay, g.ci95_low*100, g.ci95_high*100,
                            color=COLORS[model], alpha=.10)
        direct_label(ax, int(g.delay.iloc[-1]), float(g.success_mean.iloc[-1]*100),
                     model, COLORS[model], theme,
                     dy={"QRC-Persistent": 0, "ESN-12": 22,
                         "QRC-FullReset": -20, "MLP-NoMemory": 1}[model])
    ax.axhline(50, color=theme["muted"], lw=1, ls=(0, (4, 4)), alpha=.65)
    ax.set_xscale("log")
    ticks = sorted(summary.delay.unique())
    ax.set_xticks(ticks, labels=ticks)
    ax.set_xlim(3.6, 178)
    ax.set_ylim(44, 103.5)
    ax.set(title="长期记忆让策略性能跨越 128 步延迟",
           xlabel="延迟长度（步）", ylabel="策略成功率（%）")
    clean(ax, theme)
    fig.text(.01, .01, "均值与 95% bootstrap 置信区间，12 个随机种子",
             color=theme["muted"], fontsize=9)
    save(fig, out, "01_success_vs_delay.png")


def learning_chart(curves, out, theme):
    fig, ax = plt.subplots(figsize=(10.8, 5.9))
    for model in MODELS:
        g = curves[curves.model == model]
        stats = g.groupby("episode").reward.agg(["mean", "sem"]).reset_index()
        ci = 1.96 * stats["sem"]
        ax.plot(stats.episode, stats["mean"], lw=3 if model == "QRC-Persistent" else 1.9,
                color=COLORS[model])
        ax.fill_between(stats.episode, stats["mean"]-ci, stats["mean"]+ci,
                        color=COLORS[model], alpha=.10)
        direct_label(ax, int(stats.episode.iloc[-1]), float(stats["mean"].iloc[-1]),
                     model, COLORS[model], theme,
                     dy={"QRC-Persistent": 0, "ESN-12": 11,
                         "QRC-FullReset": -11, "MLP-NoMemory": 10}[model])
    ax.axhline(.5, color=theme["muted"], lw=1, ls=(0, (4, 4)), alpha=.65)
    ax.set(xlim=(35, 910), ylim=(.4, .97), title="量子储层策略在 800 回合内稳定收敛",
           xlabel="训练回合", ylabel="滑动平均回报")
    clean(ax, theme)
    save(fig, out, "02_learning_curves_delay64.png")


def memory_chart(probe, out, theme):
    fig, ax = plt.subplots(figsize=(10.8, 5.9))
    for model in MODELS:
        g = probe[probe.model == model]
        ax.plot(g.delay, np.maximum(g.state_separation, 1e-17),
                lw=3 if model == "QRC-Persistent" else 2,
                color=COLORS[model], label=model)
    ax.set_yscale("log")
    ax.set(title="部分复位保持可读状态，经典储层记忆快速衰减",
           xlabel="输入线索后的时间步", ylabel="每维 RMS 状态分离度")
    clean(ax, theme, "both")
    ax.legend(ncol=2, loc="center right", fontsize=10)
    save(fig, out, "03_memory_retention.png")


def observable_chart(observable, out, theme):
    fig, ax = plt.subplots(figsize=(11.6, 5.9))
    sns.heatmap(observable, cmap=theme["div"], center=0, ax=ax,
                xticklabels=10, linewidths=0,
                cbar_kws={"label": "正负线索态的观测差值", "shrink": .82})
    ax.set(title="14 个 Pauli 观测量持续携带早期线索",
           xlabel="时间步", ylabel="量子观测量")
    save(fig, out, "04_quantum_observable_heatmap.png")


def noise_chart(noise, out, theme):
    pivot = noise.pivot(index="memory_noise", columns="shots", values="success")*100
    fig, ax = plt.subplots(figsize=(9.8, 6.1))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap=theme["heat"], vmin=50, vmax=100,
                linewidths=1.1, linecolor=theme["bg"],
                cbar_kws={"label": "成功率（%）", "shrink": .82}, ax=ax)
    ax.set(title="更多 shots 能缓解采样噪声，但不能修复记忆退相干",
           xlabel="每步测量 shots", ylabel="记忆退极化率 p / 步")
    save(fig, out, "05_noise_shots_heatmap.png")


def ablation_chart(summary, out, theme):
    g = summary[summary.delay == 64].set_index("model").loc[MODELS]
    vals = g.success_mean.to_numpy()*100
    fig, ax = plt.subplots(figsize=(10.3, 5.8))
    x = np.arange(4)
    bars = ax.bar(x, vals, width=.56, color=[COLORS[m] for m in MODELS])
    lo = (g.success_mean-g.ci95_low).to_numpy()*100
    hi = (g.ci95_high-g.success_mean).to_numpy()*100
    ax.errorbar(x, vals, yerr=[lo, hi], fmt="none", ecolor=theme["text"],
                lw=1.2, capsize=4)
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in vals], padding=6,
                 color=theme["text"], fontsize=12, fontweight="bold")
    ax.axhline(50, color=theme["muted"], lw=1, ls=(0, (4, 4)))
    ax.set_xticks(x, ["部分复位 QRC", "经典 ESN", "全部复位 QRC", "无记忆 MLP"])
    ax.set(title="移除持久记忆后，64 步任务退化到随机水平",
           ylabel="策略成功率（%）", ylim=(44, 104))
    clean(ax, theme)
    save(fig, out, "06_ablation_delay64.png")


def resource_chart(resources, out, theme):
    fig, ax = plt.subplots(figsize=(10.1, 5.8))
    for _, r in resources.iterrows():
        ax.scatter(r.trainable_params, r.success*100, s=300, color=COLORS[r.model],
                   edgecolor=theme["text"], linewidth=.9, alpha=.95)
        offsets = {"QRC-Persistent": (9, 8), "ESN-12": (9, 9),
                   "QRC-FullReset": (9, 8), "MLP-NoMemory": (9, -20)}
        ax.annotate(r.model, (r.trainable_params, r.success*100),
                    xytext=offsets[r.model], textcoords="offset points",
                    color=COLORS[r.model], fontsize=10.5, fontweight="bold")
    ax.set(title="固定储层只需训练 13 至 15 个策略参数",
           xlabel="可训练参数量", ylabel="64 步延迟成功率（%）",
           xlim=(11.8, 16.2), ylim=(44, 103.5))
    clean(ax, theme)
    save(fig, out, "07_performance_resource.png")


def advantage_chart(summary, out, theme):
    p = summary.pivot(index="delay", columns="model", values="success_mean")*100
    best_classical = p[["ESN-12", "MLP-NoMemory"]].max(axis=1)
    gap = p["QRC-Persistent"] - best_classical
    fig, ax = plt.subplots(figsize=(10.5, 5.7))
    ax.fill_between(gap.index, 0, gap.values, color=COLORS["QRC-Persistent"], alpha=.18)
    ax.plot(gap.index, gap.values, "o-", color=COLORS["QRC-Persistent"], lw=3, ms=7)
    for x, y in gap.items():
        ax.text(x, y+1.5, f"+{y:.1f}", ha="center", color=theme["text"],
                fontsize=10, fontweight="bold")
    ax.set_xscale("log")
    ax.set_xticks(gap.index, labels=gap.index)
    ax.set(title="延迟达到 16 步后，量子策略领先最佳经典基线约 50 个百分点",
           xlabel="延迟长度（步）", ylabel="成功率优势（百分点）", ylim=(-3, 57))
    clean(ax, theme)
    save(fig, out, "08_advantage_over_classical.png")


def noise_boundary_chart(noise, out, theme):
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    selected = [32, 128, 1024]
    for shots in selected:
        g = noise[noise.shots == shots].sort_values("memory_noise")
        ax.plot(g.memory_noise*100, g.success*100, "o-", lw=2.6,
                label=f"{shots} shots")
    ax.axhline(90, color=theme["muted"], ls=(0, (4, 4)), lw=1)
    ax.axvspan(2, 8, color=COLORS["QRC-FullReset"], alpha=.07)
    ax.set(title="128 步任务存在清晰的记忆噪声边界",
           xlabel="单步退极化率（%）", ylabel="策略成功率（%）", ylim=(46, 103))
    clean(ax, theme)
    ax.legend(title="测量预算", ncol=3, loc="upper right", fontsize=10)
    save(fig, out, "09_noise_boundary.png")


def dashboard(summary, curves, noise, out, theme):
    fig = plt.figure(figsize=(15.5, 8.7))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.08, .92], wspace=.22, hspace=.34)
    ax1, ax2, ax3 = fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    for model in MODELS:
        g = summary[summary.model == model].sort_values("delay")
        ax1.plot(g.delay, g.success_mean*100, "o-", lw=2.8 if model=="QRC-Persistent" else 1.9,
                 ms=5.5, color=COLORS[model], label=model)
    ax1.set_xscale("log"); ticks=sorted(summary.delay.unique()); ax1.set_xticks(ticks, labels=ticks)
    ax1.set(title="性能跨越 128 步延迟", xlabel="延迟步数", ylabel="成功率（%）", ylim=(44,103))
    ax1.legend(ncol=4, loc="lower left", fontsize=9); clean(ax1, theme)
    for model in MODELS:
        g = curves[curves.model==model].groupby("episode").reward.mean()
        ax2.plot(g.index, g.values, lw=2.4 if model=="QRC-Persistent" else 1.6, color=COLORS[model])
    ax2.set(title="64 步任务收敛", xlabel="训练回合", ylabel="平均回报", ylim=(.4,.97)); clean(ax2, theme)
    pivot=noise.pivot(index="memory_noise",columns="shots",values="success")*100
    sns.heatmap(pivot, cmap=theme["heat"], vmin=50, vmax=100, ax=ax3,
                cbar_kws={"label":"成功率（%）", "shrink":.78})
    ax3.set(title="128 步硬件鲁棒性", xlabel="shots", ylabel="退极化率")
    fig.suptitle("量池智驭实验结果", fontsize=25, fontweight="bold", y=.99)
    fig.text(.99, .012, "4 比特密度矩阵模拟 · 12 个随机种子 · 有限 shots",
             ha="right", color=theme["muted"], fontsize=9)
    save(fig, out, "00_experiment_dashboard.png")


def render_all(data_dir: Path, out: Path, mode: str):
    theme = THEMES[mode]
    apply_theme(theme)
    out.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(data_dir / "summary_results.csv")
    curves = pd.read_csv(data_dir / "learning_curves.csv")
    probe = pd.read_csv(data_dir / "memory_probe.csv")
    noise = pd.read_csv(data_dir / "noise_sweep.csv")
    resources = pd.read_csv(data_dir / "resource_comparison.csv")

    # Reconstruct the observable-difference matrix from the existing experiment
    # by importing the simulator saved alongside this renderer.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_experiment import QuantumReservoir
    qrc = QuantumReservoir(memory_noise=.001)
    observable = pd.DataFrame((qrc.trace(+1, 80)-qrc.trace(-1, 80)).T,
                              index=qrc.obs_names)

    dashboard(summary, curves, noise, out, theme)
    success_chart(summary, out, theme)
    learning_chart(curves, out, theme)
    memory_chart(probe, out, theme)
    observable_chart(observable, out, theme)
    noise_chart(noise, out, theme)
    ablation_chart(summary, out, theme)
    resource_chart(resources, out, theme)
    advantage_chart(summary, out, theme)
    noise_boundary_chart(noise, out, theme)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--dark-out", type=Path, required=True)
    ap.add_argument("--light-out", type=Path, required=True)
    args = ap.parse_args()
    render_all(args.data_dir.resolve(), args.dark_out.resolve(), "dark")
    render_all(args.data_dir.resolve(), args.light_out.resolve(), "light")
    print(f"Rendered 10 dark + 10 light figures")


if __name__ == "__main__":
    main()
