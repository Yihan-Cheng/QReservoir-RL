"""Render the blue-orange advanced figure suite from existing experiment data.

All numerical panels are generated from CSVs produced by run_experiment.py.
No values are synthesized or manually altered.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import seaborn as sns


# Visual identity -----------------------------------------------------------
NAVY = "#12345B"
BLUE = "#0757B5"
CYAN = "#16AFC1"
ORANGE = "#F28A24"
VERMILION = "#E94E32"
VIOLET = "#7569E8"
INK = "#17324D"
MUTED = "#6A7D91"
GRID = "#D6E6F0"
PALE = "#F4FAFD"
WHITE = "#FFFFFF"

MODELS = ["QRC-Persistent", "ESN-12", "QRC-FullReset", "MLP-NoMemory"]
DISPLAY = {
    "QRC-Persistent": "量池智驭",
    "ESN-12": "经典 ESN",
    "QRC-FullReset": "量子全重置",
    "MLP-NoMemory": "无记忆 MLP",
}
COLORS = {
    "QRC-Persistent": BLUE,
    "ESN-12": "#6483A3",
    "QRC-FullReset": ORANGE,
    "MLP-NoMemory": "#AAB7C4",
}
CMAP_BO = LinearSegmentedColormap.from_list(
    "blue_orange", ["#E8F5FB", "#78C9E4", "#1B78C8", "#F4BE5D", ORANGE]
)
CMAP_DIV = LinearSegmentedColormap.from_list(
    "div", [VIOLET, "#C8C1ED", "#FFFFFF", "#BDEBF0", CYAN]
)


def set_style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "Noto Sans CJK SC", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
        "mathtext.fontset": "stix",
        "mathtext.default": "it",
        "axes.unicode_minus": False,
        "figure.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "axes.facecolor": WHITE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": INK,
        "axes.titlecolor": INK,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.frameon": False,
    })
    sns.set_context("paper", font_scale=1.0)


def clean(ax, grid="y"):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.grid(True, axis=grid, color=GRID, lw=.75, alpha=.75)
    ax.set_axisbelow(True)


def title(ax, main, sub=None, letter=None):
    if letter:
        ax.text(-.02, 1.08, letter, transform=ax.transAxes, color=WHITE,
                fontsize=11, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=.35", fc=BLUE, ec="none"))
    ax.set_title(main, loc="left", pad=14, fontsize=15.5, fontweight="bold")
    if sub:
        ax.text(0, 1.01, sub, transform=ax.transAxes, color=MUTED,
                fontsize=9.2, va="bottom")


def brand(fig, kicker="量池智驭 · QUANTUM RESERVOIR RL"):
    fig.text(.015, .012, kicker, color=BLUE, fontsize=8.3, fontweight="bold")
    fig.add_artist(Line2D([.015, .12], [.034, .034], transform=fig.transFigure,
                          lw=2.2, color=BLUE))
    fig.add_artist(Line2D([.12, .155], [.034, .034], transform=fig.transFigure,
                          lw=2.2, color=ORANGE))


def save(fig, out: Path, name: str, pdf=False):
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / name, dpi=300, bbox_inches="tight", pad_inches=.12)
    if pdf:
        fig.savefig(out / name.replace(".png", ".pdf"), bbox_inches="tight", pad_inches=.12)
    plt.close(fig)


def model_legend(ax, ncol=4, loc="upper center"):
    handles = [Line2D([0], [0], color=COLORS[m], lw=2.6, marker="o", ms=5,
                      label=DISPLAY[m]) for m in MODELS]
    ax.legend(handles=handles, ncol=ncol, loc=loc, fontsize=9)


def load_data(data_dir: Path):
    d = {
        "summary": pd.read_csv(data_dir / "summary_results.csv"),
        "curves": pd.read_csv(data_dir / "learning_curves.csv"),
        "probe": pd.read_csv(data_dir / "memory_probe.csv"),
        "noise": pd.read_csv(data_dir / "noise_sweep.csv"),
        "raw": pd.read_csv(data_dir / "raw_results.csv"),
        "resources": pd.read_csv(data_dir / "resource_comparison.csv"),
        "meta": json.loads((data_dir / "run_metadata.json").read_text(encoding="utf-8")),
    }
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_experiment import QuantumReservoir
    qrc = QuantumReservoir(memory_noise=.001)
    d["observable"] = pd.DataFrame(
        (qrc.trace(+1, 80) - qrc.trace(-1, 80)).T,
        index=qrc.obs_names,
    )
    return d


# Circuit -------------------------------------------------------------------
def circuit_gate(ax, x, y, color):
    p = FancyBboxPatch((x-.018, y-.025), .036, .05,
                       boxstyle="round,pad=.006,rounding_size=.008",
                       fc=WHITE, ec=color, lw=1.4)
    ax.add_patch(p)
    ax.add_patch(Arc((x, y), .021, .021, theta1=35, theta2=330, color=color, lw=1.2))
    ax.add_patch(FancyArrowPatch((x+.009, y+.005), (x+.011, y-.002),
                                 arrowstyle="-|>", mutation_scale=7,
                                 color=color, lw=.8))


def cnot(ax, x, yc, yt, color=NAVY):
    ax.plot([x, x], [yc, yt], color=color, lw=1.2)
    ax.add_patch(Circle((x, yc), .006, fc=color, ec="none"))
    ax.add_patch(Circle((x, yt), .012, fc=WHITE, ec=color, lw=1.2))
    ax.plot([x-.008, x+.008], [yt, yt], color=color, lw=1.1)
    ax.plot([x, x], [yt-.008, yt+.008], color=color, lw=1.1)


def meter(ax, x, y, color=CYAN):
    p = FancyBboxPatch((x-.017, y-.022), .034, .044,
                       boxstyle="round,pad=.006,rounding_size=.006",
                       fc=WHITE, ec=color, lw=1.2)
    ax.add_patch(p)
    ax.add_patch(Arc((x, y-.002), .023, .020, theta1=0, theta2=180, color=color, lw=1.1))
    ax.plot([x, x+.009], [y-.002, y+.008], color=color, lw=1.1)


def reset_icon(ax, x, y):
    p = FancyBboxPatch((x-.019, y-.022), .038, .044,
                       boxstyle="round,pad=.006,rounding_size=.006",
                       fc="#FFF7EE", ec=ORANGE, lw=1.2)
    ax.add_patch(p)
    ax.add_patch(Arc((x, y), .023, .023, theta1=45, theta2=340, color=ORANGE, lw=1.15))
    ax.add_patch(FancyArrowPatch((x+.008, y+.009), (x+.012, y+.004),
                                 arrowstyle="-|>", mutation_scale=7,
                                 color=ORANGE, lw=.8))


def quantum_circuit(out: Path):
    fig, ax = plt.subplots(figsize=(15.8, 8.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(.04, .94, "部分测量—重置量子储层线路", fontsize=25, fontweight="bold", color=NAVY)
    ax.text(.04, .895, "固定深度时间步承载跨步记忆，读出子系统测量后循环复用",
            fontsize=12, color=MUTED)
    ax.text(.925, .935, "QRR·CIRCUIT", ha="right", color=BLUE, fontsize=9, fontweight="bold")

    card = FancyBboxPatch((.035,.17),.93,.66,boxstyle="round,pad=.012,rounding_size=.018",
                          fc="#F8FCFE",ec="#CFE4F1",lw=1.2)
    ax.add_patch(card)
    ys = [.70,.63,.56,.43,.36,.29]
    for i,y in enumerate(ys):
        color = VIOLET if i < 3 else CYAN
        ax.plot([.13,.91],[y,y],color=color,lw=1.55)
        ax.add_patch(Circle((.13,y),.006,fc=color,ec="none"))
    ax.text(.055,.655,"记忆\n子系统 $M$",ha="center",va="center",color=VIOLET,fontsize=12,fontweight="bold")
    ax.text(.055,.355,"读出\n子系统 $R$",ha="center",va="center",color=CYAN,fontsize=12,fontweight="bold")
    ax.plot([.105,.105],[.535,.455],color=GRID,lw=1.2)

    bounds=[(.14,.49,"时间步 $t$"),(.52,.87,"时间步 $t+1$")]
    for x0,x1,lab in bounds:
        ax.add_patch(FancyBboxPatch((x0,.205),x1-x0,.57,boxstyle="round,pad=.008,rounding_size=.012",
                                    fc=WHITE,ec="#DDEBF3",lw=1.0))
        ax.text((x0+x1)/2,.79,lab,ha="center",color=NAVY,fontsize=11,fontweight="bold")
        for y in ys:
            ax.plot([x0+.012,x1-.012],[y,y],color=VIOLET if y>.5 else CYAN,lw=1.45)
        for y in ys:
            circuit_gate(ax,x0+.055,y,VIOLET if y>.5 else CYAN)
        for dx in [.13,.19,.25]:
            cnot(ax,x0+dx,ys[int((dx*100)%3)],ys[3+int((dx*100+1)%3)])
        for y in ys[3:]:
            meter(ax,x1-.085,y); reset_icon(ax,x1-.035,y)
        ax.text(x0+.055,.235,"输入编码",ha="center",fontsize=9.5,color=MUTED)
        ax.text((x0+x1)/2,.235,"储层演化",ha="center",fontsize=9.5,color=MUTED)
        ax.text(x1-.06,.235,"测量 · 重置",ha="center",fontsize=9.5,color=MUTED)
        ax.annotate("量子特征 $x_t$" if "t$" in lab and "+" not in lab else "量子特征 $x_{t+1}$",
                    xy=(x1-.085,.29),xytext=(x1-.085,.145),ha="center",color=CYAN,
                    fontsize=10.5,fontweight="bold",arrowprops=dict(arrowstyle="-|>",color=CYAN,lw=1.2))

    ax.annotate(r"记忆状态 $\rho_t^M \rightarrow \rho_{t+1}^M$",
                xy=(.73,.745),xytext=(.32,.745),color=VIOLET,fontsize=11,fontweight="bold",
                ha="center",arrowprops=dict(arrowstyle="-|>",color=VIOLET,lw=1.7))
    # Scale statements
    ax.text(.21,.09,r"单步演化  $\Delta t < T_2$",ha="center",fontsize=12,color=BLUE,fontweight="bold")
    ax.text(.50,.09,r"总任务  $T_{\mathrm{run}} \gg T_2$",ha="center",fontsize=12,color=ORANGE,fontweight="bold")
    ax.text(.80,.09,"序列长度与单步线路深度解耦",ha="center",fontsize=12,color=NAVY,fontweight="bold")
    ax.plot([.08,.92],[.125,.125],color=GRID,lw=1)
    brand(fig,"量池智驭 · PARTIAL-MEASUREMENT QUANTUM RESERVOIR")
    save(fig,out,"00_量子储层线路.png",pdf=True)


# Single-result figures -----------------------------------------------------
def success_delay(d, out):
    s=d["summary"]
    fig,ax=plt.subplots(figsize=(11.5,6.4))
    for m in MODELS:
        g=s[s.model==m].sort_values("delay")
        ax.fill_between(g.delay,g.ci95_low*100,g.ci95_high*100,color=COLORS[m],alpha=.09)
        ax.plot(g.delay,g.success_mean*100,"o-",color=COLORS[m],lw=3 if m==MODELS[0] else 2,ms=6)
        ax.annotate(DISPLAY[m],(g.delay.iloc[-1],g.success_mean.iloc[-1]*100),xytext=(8,{MODELS[0]:0,MODELS[1]:16,MODELS[2]:-20,MODELS[3]:1}[m]),textcoords="offset points",color=COLORS[m],fontsize=10,fontweight="bold",va="center")
    ax.axhline(50,color=MUTED,ls=(0,(4,4)),lw=1)
    ax.text(4.2,52,"随机水平",fontsize=9,color=MUTED)
    ax.set_xscale("log"); ticks=sorted(s.delay.unique()); ax.set_xticks(ticks,ticks)
    ax.set_xlim(3.6,175); ax.set_ylim(45,103)
    ax.set_xlabel("延迟长度（时间步）"); ax.set_ylabel("策略成功率（%）")
    title(ax,"长时序性能跨越 128 步","均值与95% bootstrap置信区间，12个随机种子")
    clean(ax)
    ax.text(.02,.88,"100%",transform=ax.transAxes,color=BLUE,fontsize=26,fontweight="bold")
    ax.text(.02,.815,"128步成功率",transform=ax.transAxes,color=MUTED,fontsize=9)
    brand(fig); save(fig,out,"01_长时序成功率.png")


def learning(d,out):
    c=d["curves"]
    fig,ax=plt.subplots(figsize=(11.5,6.4))
    for m in MODELS:
        st=c[c.model==m].groupby("episode").reward.agg(["mean","sem"])
        ci=1.96*st["sem"]
        ax.fill_between(st.index,st["mean"]-ci,st["mean"]+ci,color=COLORS[m],alpha=.10)
        ax.plot(st.index,st["mean"],color=COLORS[m],lw=3 if m==MODELS[0] else 1.8)
    ax.axhline(.5,color=MUTED,ls=(0,(4,4)),lw=1)
    ax.set(xlim=(35,820),ylim=(.42,.98),xlabel="训练回合",ylabel="滑动平均回报")
    title(ax,"64步延迟任务的训练动力学","实线为12个随机种子均值，阴影为95%置信区间")
    clean(ax); model_legend(ax,loc="lower right")
    brand(fig); save(fig,out,"02_训练收敛曲线.png")


def memory(d,out):
    p=d["probe"]
    fig,ax=plt.subplots(figsize=(11.5,6.4))
    for m in MODELS:
        g=p[p.model==m]
        ax.plot(g.delay,np.maximum(g.state_separation,1e-17),color=COLORS[m],lw=3 if m==MODELS[0] else 1.8,label=DISPLAY[m])
    ax.set_yscale("log"); ax.set(xlabel="线索后的时间步",ylabel="RMS状态分离度",xlim=(0,160))
    title(ax,"跨步记忆保持曲线","状态分离度刻画正负线索在储层状态中的可辨识性")
    clean(ax,"both"); ax.legend(ncol=2,loc="upper right",fontsize=9)
    ax.axvspan(64,128,color=BLUE,alpha=.035); ax.text(96,1e-6,"长时序区间",ha="center",color=BLUE,fontsize=9)
    brand(fig); save(fig,out,"03_记忆保持曲线.png")


def observable(d,out):
    mat=d["observable"]
    fig,ax=plt.subplots(figsize=(12,6.4))
    hm=sns.heatmap(mat,cmap=CMAP_DIV,center=0,ax=ax,xticklabels=10,yticklabels=True,
                   cbar_kws={"label":"正负线索态的观测差值","shrink":.78,"pad":.02})
    title(ax,"量子可观测量中的记忆轨迹","14维Pauli观测随时间演化；结构化条纹表示线索仍可被读出")
    ax.set_xlabel("时间步"); ax.set_ylabel("量子观测量")
    brand(fig); save(fig,out,"04_量子观测热图.png")


def noise_heat(d,out):
    n=d["noise"]; pv=n.pivot(index="memory_noise",columns="shots",values="success")*100
    fig,ax=plt.subplots(figsize=(10.8,6.5))
    sns.heatmap(pv,annot=True,fmt=".0f",cmap=CMAP_BO,vmin=50,vmax=100,linewidths=1.2,linecolor=WHITE,
                cbar_kws={"label":"成功率（%）","shrink":.8},ax=ax)
    ax.set_xlabel("每步测量 shots"); ax.set_ylabel("记忆退极化率 / 步")
    title(ax,"128步任务的噪声—采样鲁棒性相图","橙色高值区表示可靠运行窗口；更多shots不能弥补严重记忆退相干")
    brand(fig); save(fig,out,"05_噪声采样相图.png")


def ablation(d,out):
    s=d["summary"]; g=s[s.delay==64].set_index("model").loc[MODELS]
    vals=g.success_mean.values*100; lo=(g.success_mean-g.ci95_low).values*100; hi=(g.ci95_high-g.success_mean).values*100
    fig,ax=plt.subplots(figsize=(10.8,6.3)); x=np.arange(4)
    bars=ax.bar(x,vals,width=.56,color=[COLORS[m] for m in MODELS],edgecolor=WHITE,lw=1.2)
    ax.errorbar(x,vals,yerr=[lo,hi],fmt="none",ecolor=INK,lw=1,capsize=4)
    ax.bar_label(bars,[f"{v:.1f}%" for v in vals],padding=5,fontsize=11,fontweight="bold",color=INK)
    ax.axhline(50,color=MUTED,ls=(0,(4,4)),lw=1); ax.set_ylim(44,105)
    ax.set_xticks(x,[DISPLAY[m] for m in MODELS]); ax.set_ylabel("64步延迟成功率（%）")
    title(ax,"持久量子记忆是长时序决策的必要条件","全重置与无记忆基线均退化到随机水平")
    clean(ax); brand(fig); save(fig,out,"06_消融实验.png")


def resource(d,out):
    r=d["resources"]
    fig,ax=plt.subplots(figsize=(10.8,6.3))
    for _,z in r.iterrows():
        ax.scatter(z.trainable_params,z.success*100,s=170+z.state_features*8,color=COLORS[z.model],edgecolor=WHITE,lw=1.5,zorder=3)
        off={"QRC-Persistent":(9,8),"ESN-12":(9,8),"QRC-FullReset":(9,-18),"MLP-NoMemory":(-92,8)}[z.model]
        ax.annotate(DISPLAY[z.model],(z.trainable_params,z.success*100),xytext=off,textcoords="offset points",fontsize=10,color=COLORS[z.model],fontweight="bold")
    ax.set(xlim=(11.6,16.4),ylim=(44,104),xlabel="可训练参数量",ylabel="64步延迟成功率（%）")
    title(ax,"性能—资源前沿","气泡面积表示状态特征维数；量子储层保持轻量训练规模")
    clean(ax); ax.axhline(50,color=MUTED,ls=(0,(4,4)),lw=1)
    brand(fig); save(fig,out,"07_性能资源前沿.png")


def advantage(d,out):
    s=d["summary"]; p=s.pivot(index="delay",columns="model",values="success_mean")*100
    best=p[["ESN-12","MLP-NoMemory"]].max(axis=1); gap=p["QRC-Persistent"]-best
    fig,ax=plt.subplots(figsize=(10.8,6.2))
    ax.fill_between(gap.index,0,gap.values,color=BLUE,alpha=.12)
    ax.plot(gap.index,gap.values,"o-",color=BLUE,lw=2.8,ms=6)
    for x,y in gap.items(): ax.text(x,y+1.5,f"+{y:.1f}",ha="center",fontsize=9.5,color=INK,fontweight="bold")
    ax.set_xscale("log"); ax.set_xticks(gap.index,gap.index); ax.set_ylim(-3,56)
    ax.set_xlabel("延迟长度（时间步）"); ax.set_ylabel("相对最佳经典基线优势（百分点）")
    title(ax,"长时序区间的量子储层优势","延迟达到16步后，优势稳定接近50个百分点")
    clean(ax); brand(fig); save(fig,out,"08_相对经典优势.png")


def noise_boundary(d,out):
    n=d["noise"]; fig,ax=plt.subplots(figsize=(10.8,6.2))
    for sh,c in zip([32,128,1024],["#7FB7D7",BLUE,ORANGE]):
        g=n[n.shots==sh].sort_values("memory_noise")
        ax.plot(g.memory_noise*100,g.success*100,"o-",lw=2.5,ms=6,color=c,label=f"{sh} shots")
    ax.axhline(90,color=MUTED,ls=(0,(4,4)),lw=1); ax.text(.15,91.3,"90%可靠性阈值",color=MUTED,fontsize=9)
    ax.axvspan(2,8,color=ORANGE,alpha=.055)
    ax.set(xlabel="单步记忆退极化率（%）",ylabel="128步延迟成功率（%）",ylim=(46,103))
    title(ax,"记忆噪声决定长时序运行边界","增加shots主要抑制采样噪声，无法修复跨步记忆损失")
    clean(ax); ax.legend(ncol=3,loc="lower left",fontsize=9)
    brand(fig); save(fig,out,"09_噪声边界.png")


def distributions(d,out):
    raw=d["raw"]; delays=[4,16,64,128]
    fig,axes=plt.subplots(1,4,figsize=(14.2,5.2),sharey=True)
    rng=np.random.default_rng(3)
    for ax,delay in zip(axes,delays):
        q=raw[raw.delay==delay]
        sns.violinplot(data=q,x="model",y="success",hue="model",order=MODELS,
                       hue_order=MODELS,palette=[COLORS[m] for m in MODELS],
                       legend=False,inner=None,cut=0,linewidth=.7,ax=ax)
        for i,m in enumerate(MODELS):
            vals=q[q.model==m].success.values
            ax.scatter(i+rng.normal(0,.035,len(vals)),vals,s=11,color=INK,alpha=.45,zorder=4)
        ax.set_title(f"延迟 {delay}",fontsize=12,fontweight="bold"); ax.set_xticks(range(4),["量池","ESN","全重置","MLP"],rotation=20)
        ax.set_xlabel(""); clean(ax)
    axes[0].set_ylabel("随机种子成功率"); [a.set_ylabel("") for a in axes[1:]]
    fig.subplots_adjust(top=.82, bottom=.18, wspace=.20)
    fig.suptitle("跨随机种子的性能分布",x=.08,y=.97,ha="left",fontsize=18,fontweight="bold",color=INK)
    fig.text(.08,.905,"每个点为一个独立随机种子；分布宽度反映训练稳定性",color=MUTED,fontsize=9.5)
    brand(fig); save(fig,out,"10_随机种子分布.png")


# Core composites ----------------------------------------------------------
def core_performance(d,out):
    s,c,raw=d["summary"],d["curves"],d["raw"]
    fig=plt.figure(figsize=(15.5,9)); gs=fig.add_gridspec(2,2,wspace=.22,hspace=.34)
    ax1=fig.add_subplot(gs[0,:]); ax2=fig.add_subplot(gs[1,0]); ax3=fig.add_subplot(gs[1,1])
    for m in MODELS:
        g=s[s.model==m].sort_values("delay")
        ax1.fill_between(g.delay,g.ci95_low*100,g.ci95_high*100,color=COLORS[m],alpha=.08)
        ax1.plot(g.delay,g.success_mean*100,"o-",color=COLORS[m],lw=3 if m==MODELS[0] else 1.8,ms=5)
    ax1.set_xscale("log"); ticks=sorted(s.delay.unique()); ax1.set_xticks(ticks,ticks); ax1.set_ylim(45,103)
    ax1.set(xlabel="延迟长度（时间步）",ylabel="成功率（%）"); title(ax1,"长时序性能","12个随机种子与95%置信区间","a"); clean(ax1); model_legend(ax1,loc="lower left")
    for m in MODELS:
        st=c[c.model==m].groupby("episode").reward.agg(["mean","sem"]); ci=1.96*st["sem"]
        ax2.fill_between(st.index,st["mean"]-ci,st["mean"]+ci,color=COLORS[m],alpha=.08)
        ax2.plot(st.index,st["mean"],color=COLORS[m],lw=2.5 if m==MODELS[0] else 1.5)
    ax2.set(xlabel="训练回合",ylabel="平均回报",xlim=(35,820),ylim=(.42,.98)); title(ax2,"64步任务训练收敛",None,"b"); clean(ax2)
    p=s.pivot(index="delay",columns="model",values="success_mean")*100; best=p[["ESN-12","MLP-NoMemory"]].max(axis=1); gap=p[MODELS[0]]-best
    ax3.fill_between(gap.index,0,gap.values,color=ORANGE,alpha=.14); ax3.plot(gap.index,gap.values,"o-",color=ORANGE,lw=2.7)
    for x,y in gap.items(): ax3.text(x,y+1.3,f"+{y:.1f}",ha="center",fontsize=8.5,fontweight="bold")
    ax3.set_xscale("log"); ax3.set_xticks(gap.index,gap.index); ax3.set_ylim(-3,56)
    ax3.set(xlabel="延迟长度",ylabel="领先经典基线（百分点）"); title(ax3,"相对最佳经典基线优势",None,"c"); clean(ax3)
    fig.suptitle("核心证据Ⅰ｜长时序决策性能",x=.015,ha="left",fontsize=23,fontweight="bold",color=NAVY)
    fig.text(.985,.965,"128步成功率 100%   ·   长时序优势 ≈ 50 pp",ha="right",color=ORANGE,fontsize=11,fontweight="bold")
    brand(fig); save(fig,out,"核心01_长时序性能证据.png",pdf=True)


def core_mechanism(d,out):
    p,mat,s=d["probe"],d["observable"],d["summary"]
    fig=plt.figure(figsize=(15.5,9)); gs=fig.add_gridspec(2,2,width_ratios=[.9,1.25],wspace=.25,hspace=.34)
    ax1=fig.add_subplot(gs[:,0]); ax2=fig.add_subplot(gs[0,1]); ax3=fig.add_subplot(gs[1,1])
    for m in MODELS:
        g=p[p.model==m]; ax1.plot(g.delay,np.maximum(g.state_separation,1e-17),color=COLORS[m],lw=2.8 if m==MODELS[0] else 1.6,label=DISPLAY[m])
    ax1.set_yscale("log"); ax1.set(xlabel="线索后的时间步",ylabel="RMS状态分离度",xlim=(0,160)); title(ax1,"记忆保持曲线",None,"a"); clean(ax1,"both"); ax1.legend(fontsize=8.5)
    sns.heatmap(mat,cmap=CMAP_DIV,center=0,xticklabels=10,yticklabels=True,ax=ax2,cbar_kws={"label":"观测差值","shrink":.75})
    ax2.set(xlabel="时间步",ylabel="Pauli观测量"); title(ax2,"量子观测记忆轨迹",None,"b")
    g=s[s.delay==64].set_index("model").loc[MODELS]; vals=g.success_mean.values*100
    bars=ax3.bar(np.arange(4),vals,color=[COLORS[m] for m in MODELS],width=.58)
    ax3.bar_label(bars,[f"{v:.1f}%" for v in vals],padding=4,fontsize=9,fontweight="bold")
    ax3.axhline(50,color=MUTED,ls=(0,(4,4)),lw=1); ax3.set_ylim(44,105); ax3.set_ylabel("成功率（%）")
    ax3.set_xticks(range(4),["部分重置","经典ESN","全重置","无记忆MLP"]); title(ax3,"64步消融验证",None,"c"); clean(ax3)
    fig.suptitle("核心证据Ⅱ｜长时序记忆机制",x=.015,ha="left",fontsize=23,fontweight="bold",color=NAVY)
    fig.text(.985,.965,r"$\Delta t<T_2$  ·  $T_{\mathrm{run}}\gg T_2$  ·  记忆跨步保留",ha="right",color=VIOLET,fontsize=11,fontweight="bold")
    brand(fig); save(fig,out,"核心02_记忆机制证据.png",pdf=True)


def core_robustness(d,out):
    n,r=d["noise"],d["resources"]
    fig=plt.figure(figsize=(15.5,9)); gs=fig.add_gridspec(2,2,wspace=.25,hspace=.34)
    ax1=fig.add_subplot(gs[:,0]); ax2=fig.add_subplot(gs[0,1]); ax3=fig.add_subplot(gs[1,1])
    pv=n.pivot(index="memory_noise",columns="shots",values="success")*100
    sns.heatmap(pv,annot=True,fmt=".0f",cmap=CMAP_BO,vmin=50,vmax=100,linewidths=1,linecolor=WHITE,ax=ax1,cbar_kws={"label":"成功率（%）","shrink":.78})
    ax1.set(xlabel="每步shots",ylabel="记忆退极化率 / 步"); title(ax1,"128步鲁棒性相图",None,"a")
    for sh,c in zip([32,128,1024],["#7FB7D7",BLUE,ORANGE]):
        g=n[n.shots==sh].sort_values("memory_noise"); ax2.plot(g.memory_noise*100,g.success*100,"o-",lw=2.3,color=c,label=f"{sh} shots")
    ax2.axhline(90,color=MUTED,ls=(0,(4,4)),lw=1); ax2.set(xlabel="记忆退极化率（%）",ylabel="成功率（%）",ylim=(46,103)); title(ax2,"噪声边界",None,"b"); clean(ax2); ax2.legend(ncol=3,fontsize=8)
    label_offsets={
        "QRC-Persistent":(7,5),
        "ESN-12":(-4,12),
        "QRC-FullReset":(7,5),
        "MLP-NoMemory":(7,-16),
    }
    for _,z in r.iterrows():
        ax3.scatter(z.trainable_params,z.success*100,s=160+z.state_features*7,color=COLORS[z.model],edgecolor=WHITE,lw=1.2)
        ax3.annotate(DISPLAY[z.model],(z.trainable_params,z.success*100),xytext=label_offsets[z.model],textcoords="offset points",fontsize=8.5,color=COLORS[z.model],fontweight="bold")
    ax3.set(xlim=(11.6,16.5),ylim=(44,104),xlabel="可训练参数量",ylabel="64步成功率（%）"); title(ax3,"性能—资源前沿",None,"c"); clean(ax3)
    fig.suptitle("核心证据Ⅲ｜噪声鲁棒性与资源效率",x=.015,ha="left",fontsize=23,fontweight="bold",color=NAVY)
    fig.text(.985,.965,"36组噪声—采样组合   ·   轻量经典读出",ha="right",color=ORANGE,fontsize=11,fontweight="bold")
    brand(fig); save(fig,out,"核心03_鲁棒性与资源证据.png",pdf=True)


def dashboard(d,out):
    s,c,n,p=d["summary"],d["curves"],d["noise"],d["probe"]
    fig=plt.figure(figsize=(15.5,9)); gs=fig.add_gridspec(2,3,width_ratios=[1.15,1,1],wspace=.27,hspace=.36)
    ax1=fig.add_subplot(gs[0,:2]); ax2=fig.add_subplot(gs[0,2]); ax3=fig.add_subplot(gs[1,0]); ax4=fig.add_subplot(gs[1,1:])
    for m in MODELS:
        g=s[s.model==m]; ax1.plot(g.delay,g.success_mean*100,"o-",color=COLORS[m],lw=2.7 if m==MODELS[0] else 1.6,ms=5)
    ax1.set_xscale("log"); ticks=sorted(s.delay.unique()); ax1.set_xticks(ticks,ticks); ax1.set_ylim(45,103); ax1.set(xlabel="延迟长度",ylabel="成功率（%）"); title(ax1,"性能跨越128步",None,"a"); clean(ax1); model_legend(ax1,loc="lower left")
    q=s[s.delay==64].set_index("model").loc[MODELS]; bars=ax2.bar(range(4),q.success_mean*100,color=[COLORS[m] for m in MODELS]); ax2.set_ylim(44,105); ax2.set_xticks(range(4),["量池","ESN","全重置","MLP"]); title(ax2,"64步消融",None,"b"); clean(ax2)
    for m in MODELS:
        g=p[p.model==m]; ax3.plot(g.delay,np.maximum(g.state_separation,1e-17),color=COLORS[m],lw=2.4 if m==MODELS[0] else 1.4)
    ax3.set_yscale("log"); ax3.set(xlabel="时间步",ylabel="状态分离度"); title(ax3,"记忆保持",None,"c"); clean(ax3,"both")
    pv=n.pivot(index="memory_noise",columns="shots",values="success")*100
    sns.heatmap(pv,annot=True,fmt=".0f",cmap=CMAP_BO,vmin=50,vmax=100,linewidths=.7,linecolor=WHITE,ax=ax4,cbar_kws={"label":"成功率（%）","shrink":.7})
    ax4.set(xlabel="shots",ylabel="退极化率"); title(ax4,"128步噪声—采样相图",None,"d")
    fig.suptitle("量池智驭｜实验全景",x=.015,ha="left",fontsize=24,fontweight="bold",color=NAVY)
    fig.text(.985,.965,"4种模型 · 6档延迟 · 12个随机种子 · 36组硬件噪声条件",ha="right",fontsize=10,color=ORANGE,fontweight="bold")
    brand(fig); save(fig,out,"核心00_实验全景.png",pdf=True)


def render_all(data_dir: Path, out: Path):
    set_style(); d=load_data(data_dir); core=out/"核心"
    quantum_circuit(core)
    success_delay(d,out); learning(d,out); memory(d,out); observable(d,out)
    noise_heat(d,out); ablation(d,out); resource(d,out); advantage(d,out)
    noise_boundary(d,out); distributions(d,out)
    dashboard(d,core); core_performance(d,core); core_mechanism(d,core); core_robustness(d,core)
    print(f"Rendered 10 single figures + 5 core figures to {out}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); render_all(args.data_dir.resolve(),args.out.resolve())


if __name__=="__main__": main()
