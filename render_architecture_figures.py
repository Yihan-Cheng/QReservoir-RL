"""Create publication-style architecture, circuit, roadmap, and evidence figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
import pandas as pd
import seaborn as sns

from render_premium_figures import THEMES, COLORS, apply_theme, clean


ACCENT = "#00BFA6"
PURPLE = "#7C5CFC"
BLUE = "#4E79A7"
ORANGE = "#F28E2B"


def save(fig, out, name):
    fig.savefig(out / name, dpi=280, bbox_inches="tight", pad_inches=.16,
                facecolor=fig.get_facecolor())
    plt.close(fig)


def box(ax, xy, wh, title, body, theme, color=ACCENT, lw=1.5,
        title_size=12, body_size=9.2, alpha=.07, radius=.025):
    x, y = xy; w, h = wh
    patch = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=lw, edgecolor=color, facecolor=color, alpha=alpha)
    ax.add_patch(patch)
    ax.text(x+.035*w, y+h*.69, title, color=theme["text"], fontsize=title_size,
            fontweight="bold", va="center")
    ax.text(x+.035*w, y+h*.34, body, color=theme["muted"], fontsize=body_size,
            va="center", linespacing=1.35)
    return patch


def arrow(ax, start, end, theme, color=None, lw=1.7, style="-|>", rad=0):
    a = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=13,
                        linewidth=lw, color=color or theme["edge"],
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    return a


def label_chip(ax, x, y, text, theme, color, width=.09):
    p = FancyBboxPatch((x-width/2, y-.027), width, .054,
                       boxstyle="round,pad=.005,rounding_size=.012",
                       facecolor=color, edgecolor="none", alpha=.15)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.5,
            color=color, fontweight="bold")


def roadmap(out, theme):
    fig, ax = plt.subplots(figsize=(14.2, 7.5))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(.04, .925, "量池智驭技术路线", fontsize=25, fontweight="bold",
            color=theme["text"])
    ax.text(.04, .875, "长时序输入由固定量子动力学编码，仅训练轻量策略读出层",
            fontsize=12, color=theme["muted"])
    xs = [.045, .245, .445, .645, .825]
    widths = [.16, .16, .16, .16, .13]
    titles = ["长时序任务", "量子特征编码", "部分复位储层", "强化学习读出", "策略执行"]
    bodies = [
        "早期线索 $u_0$\n空白延迟 $D$\n末端稀疏奖励",
        "$R_y(u_t)$ 数据注入\n固定 Ising 演化\n多体 Pauli 特征",
        "M：记忆比特持续演化\nR：测量后确定性复位\n跨步保留历史状态",
        "$x_t$ 输入线性策略头\nREINFORCE 更新 $W_{\\pi}$\n储层参数保持冻结",
        "动作 $a_t$\n环境奖励 $r_t$\n闭环更新"
    ]
    cs = [BLUE, PURPLE, ACCENT, ORANGE, "#D95F76"]
    for i, (x,w,t,b,c) in enumerate(zip(xs,widths,titles,bodies,cs)):
        box(ax,(x,.48),(w,.25),t,b,theme,c,title_size=12.5,body_size=9.4,alpha=.09)
        ax.text(x+.018,.755,f"0{i+1}",fontsize=9.5,color=c,fontweight="bold")
        if i < 4:
            arrow(ax,(x+w+.012,.605),(xs[i+1]-.012,.605),theme,color=cs[i+1])
    # Long-sequence track.
    ax.plot([.07,.92],[.34,.34],color=theme["edge"],lw=1.3,alpha=.6)
    for i, xpos in enumerate(np.linspace(.08,.91,15)):
        height=.055 if i in [0,14] else .025
        ax.plot([xpos,xpos],[.34,.34+height],color=ACCENT if i==0 else theme["muted"],lw=2)
    ax.text(.07,.275,r"$u_0$",color=ACCENT,fontsize=14,fontweight="bold")
    ax.text(.45,.275,"持续流式处理：每一步线路深度固定",color=theme["muted"],fontsize=10,ha="center")
    ax.text(.91,.275,r"$a_D$",color=ORANGE,fontsize=14,fontweight="bold")
    # Closed-loop feedback.
    arrow(ax,(.89,.45),(.16,.43),theme,color=ORANGE,lw=1.5,rad=-.17)
    ax.text(.53,.16,"奖励反馈更新策略头，不反传穿越量子储层",
            ha="center", color=ORANGE, fontsize=10.5, fontweight="bold")
    ax.text(.04,.055,"核心协同：算法侧控制记忆时间尺度，硬件侧提供中途测量、RESET 与有限 shots 执行",
            color=theme["text"],fontsize=11.5,fontweight="bold")
    save(fig,out,"10_technical_roadmap.png")


def origin_stack(out, theme):
    fig, ax = plt.subplots(figsize=(13.4, 8.0))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(.05,.93,"面向本源量子平台的软硬件协同路线",fontsize=24,fontweight="bold",color=theme["text"])
    ax.text(.05,.88,"从训练任务到真实超导量子后端的四层映射",fontsize=11.5,color=theme["muted"])
    layers=[
        (.72,"应用与任务层", "长时序 POMDP · 延迟线索控制 · 工业时序决策", "#D95F76"),
        (.54,"量池智驭算法层", "固定 4 比特 QRC · 部分复位 · 线性策略头 · REINFORCE", ACCENT),
        (.36,"本源量子软件层", "QPanda3 / PyQPanda：QCircuit、OriginIR、线路优化与芯片映射", PURPLE),
        (.18,"运行与硬件层", "本源司南 + QPanda3 Runtime · 本源悟空量子云 / 超导 QPU", BLUE),
    ]
    for y,t,b,c in layers:
        box(ax,(.08,y),(.84,.125),t,b,theme,c,title_size=13,body_size=10,alpha=.075,radius=.018)
    for y in [.705,.525,.345]:
        arrow(ax,(.5,y),(.5,y-.035),theme,color=theme["edge"],lw=1.5)
    # Side capability rail.
    ax.plot([.045,.045],[.185,.84],color=theme["edge"],lw=1.2)
    for y,txt,c in [(.78,"问题定义", "#D95F76"),(.60,"算法固化",ACCENT),(.42,"编译映射",PURPLE),(.24,"真实执行",BLUE)]:
        ax.add_patch(Circle((.045,y),.012,facecolor=c,edgecolor="none"))
        ax.text(.022,y,txt,rotation=90,ha="center",va="center",color=c,fontsize=9,fontweight="bold")
    # Hardware co-design annotations.
    notes=[(.14,"中途测量 / RESET",ACCENT),(.38,"拓扑映射与门分解",PURPLE),(.62,"shots 批量调度",ORANGE),(.82,"噪声校正与回传",BLUE)]
    for x,txt,c in notes:
        label_chip(ax,x,.09,txt,theme,c,width=.16)
    ax.text(.5,.035,"部署原则：单步浅线路反复执行，序列长度不再等于单条量子线路深度",
            ha="center",color=theme["text"],fontsize=11,fontweight="bold")
    save(fig,out,"11_origin_quantum_stack.png")


def gate(ax,x,y,text,theme,color=PURPLE,w=.055,h=.058,fs=8.5):
    p=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=.004,rounding_size=.008",
                     facecolor=color,edgecolor=color,alpha=.13,linewidth=1.4)
    ax.add_patch(p); ax.text(x,y,text,ha="center",va="center",fontsize=fs,color=theme["text"],fontweight="bold")


def cphase(ax,x,y1,y2,theme,label="ZZ"):
    ax.plot([x,x],[y1,y2],color=BLUE,lw=1.5)
    for y in [y1,y2]: ax.add_patch(Circle((x,y),.009,facecolor=BLUE,edgecolor="none"))
    ax.text(x+.012,(y1+y2)/2,label,color=BLUE,fontsize=8,va="center")


def circuit(out, theme):
    fig, ax=plt.subplots(figsize=(15.2,7.8)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(.035,.93,"部分复位量子储层线路",fontsize=25,fontweight="bold",color=theme["text"])
    ax.text(.035,.88,"3 个记忆比特持续演化，1 个读出比特逐步测量并复位",
            fontsize=11.5,color=theme["muted"])
    ys=[.70,.59,.48,.32]; labels=[r"$q_{M_0}$  Memory",r"$q_{M_1}$  Memory",r"$q_{M_2}$  Memory",r"$q_R$   Readout"]
    for y,l in zip(ys,labels):
        ax.plot([.10,.91],[y,y],color=theme["edge"],lw=1.5)
        ax.text(.025,y,l,va="center",fontsize=10.5,color=ACCENT if "Memory" in l else BLUE,fontweight="bold")
    # Two unrolled time steps.
    for k,(x0,tag) in enumerate([(.13,r"时间步 $t$"),(.52,r"时间步 $t+1$")]):
        ax.add_patch(FancyBboxPatch((x0-.025,.25),.33,.52,boxstyle="round,pad=.012,rounding_size=.018",
                    facecolor=PURPLE,edgecolor=PURPLE,alpha=.045,linewidth=1.5))
        ax.text(x0+.14,.79,tag,ha="center",fontsize=11,color=PURPLE,fontweight="bold")
        gate(ax,x0+.025,ys[0],r"$R_y(u)$",theme,ACCENT,w=.06)
        gate(ax,x0+.025,ys[3],r"$R_y(\beta u)$",theme,ACCENT,w=.065)
        gate(ax,x0+.095,ys[0],r"$R_x$",theme); gate(ax,x0+.095,ys[1],r"$R_z$",theme)
        gate(ax,x0+.095,ys[2],r"$R_x$",theme); gate(ax,x0+.095,ys[3],r"$R_x$",theme)
        cphase(ax,x0+.155,ys[0],ys[1],theme); cphase(ax,x0+.195,ys[1],ys[2],theme)
        cphase(ax,x0+.235,ys[0],ys[3],theme)
        ax.text(x0+.165,.405,r"$U_{\mathrm{res}}=\exp(-iH\Delta t)$",ha="center",fontsize=9,color=theme["muted"])
        gate(ax,x0+.285,ys[3],"M",theme,ORANGE,w=.045)
        gate(ax,x0+.32,ys[3],r"$|0\rangle$",theme,BLUE,w=.045)
        ax.text(x0+.302,.267,"测量 + RESET",ha="center",fontsize=8.2,color=ORANGE,fontweight="bold")
    ax.text(.475,.55,"···",fontsize=23,color=theme["muted"],ha="center")
    # Classical feature/readout lane.
    arrow(ax,(.84,.29),(.84,.18),theme,color=ORANGE)
    box(ax,(.67,.065),(.29,.105),"有限 shots 特征估计",
        r"$x_t=[\langle Z_i\rangle,\;\langle X_i\rangle,\;\langle Z_iZ_j\rangle]$    $\pi(a|x)=\mathrm{softmax}(W_{\pi}x+b)$",
        theme,ORANGE,title_size=11.5,body_size=9.2,alpha=.075,radius=.016)
    ax.text(.13,.14,"记忆线不复位",fontsize=11,color=ACCENT,fontweight="bold")
    arrow(ax,(.24,.145),(.42,.31),theme,color=ACCENT,lw=1.4,rad=-.15)
    ax.text(.035,.035,"仿真实验读取 14 个 Pauli 期望；本源量子上机时按芯片可测子集与拓扑裁剪",
            fontsize=10,color=theme["muted"])
    save(fig,out,"12_partial_reset_quantum_circuit.png")


def coherence(out, theme):
    fig,ax=plt.subplots(figsize=(13.8,6.7)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(.045,.92,"跨越相干时间的执行机制",fontsize=24,fontweight="bold",color=theme["text"])
    ax.text(.045,.865,"长序列被拆成固定深度的量子时间步，读出比特在每一步重新开始",
            fontsize=11.5,color=theme["muted"])
    # Timeline segments.
    y=.58; ax.plot([.08,.92],[y,y],color=theme["edge"],lw=2)
    bounds=np.linspace(.09,.91,9)
    for i in range(8):
        x1,x2=bounds[i],bounds[i+1]
        ax.add_patch(Rectangle((x1,y-.07),x2-x1-.008,.14,facecolor=ACCENT if i%2==0 else PURPLE,
                               edgecolor="none",alpha=.12))
        ax.text((x1+x2)/2-.004,y,rf"$U(u_{i})$"+"\nM→R\nRESET R",ha="center",va="center",
                fontsize=8.5,color=theme["text"])
        ax.plot([x1,x1],[y-.095,y+.095],color=theme["edge"],lw=.8)
    arrow(ax,(.91,y),(.95,y),theme,color=theme["edge"])
    # Brackets / scales.
    ax.annotate("",xy=(bounds[0],.75),xytext=(bounds[1]-.008,.75),arrowprops=dict(arrowstyle="|-|",color=BLUE,lw=1.6))
    ax.text((bounds[0]+bounds[1])/2,.79,r"单步 $\Delta t < T_2$",ha="center",color=BLUE,fontsize=10,fontweight="bold")
    ax.annotate("",xy=(bounds[0],.34),xytext=(bounds[-1],.34),arrowprops=dict(arrowstyle="|-|",color=ORANGE,lw=1.8))
    ax.text(.5,.275,r"总运行时间 $T_{\mathrm{run}} \gg T_2$",ha="center",color=ORANGE,fontsize=12,fontweight="bold")
    box(ax,(.075,.035),(.25,.15),"记忆来源",r"跨步密度矩阵 $\rho_t^M$"+"\n而非单条深线路的全局相干",theme,ACCENT,title_size=11,body_size=8.7,alpha=.07)
    box(ax,(.375,.035),(.25,.15),"硬件动作","中途测量 · RESET\n重复 shots · 噪声校正",theme,PURPLE,title_size=11,body_size=8.7,alpha=.07)
    box(ax,(.675,.035),(.25,.15),"算法收益","线路深度与序列长度解耦\n支持在线强化学习特征流",theme,ORANGE,title_size=11,body_size=8.7,alpha=.07)
    save(fig,out,"13_coherence_barrier_mechanism.png")


def core_evidence(data, out, theme):
    summary,curves,noise,probe=data
    fig=plt.figure(figsize=(15.5,9.2)); gs=fig.add_gridspec(2,2,wspace=.24,hspace=.32)
    axes=[fig.add_subplot(gs[i,j]) for i in range(2) for j in range(2)]
    # a success
    ax=axes[0]
    for m in ["QRC-Persistent","ESN-12","QRC-FullReset"]:
        g=summary[summary.model==m].sort_values("delay")
        ax.plot(g.delay,g.success_mean*100,"o-",color=COLORS[m],lw=2.5 if m=="QRC-Persistent" else 1.8,label=m)
    ax.set_xscale("log"); ticks=sorted(summary.delay.unique()); ax.set_xticks(ticks,labels=ticks)
    ax.set(title="a  长延迟策略成功率",xlabel="延迟步数",ylabel="成功率（%）",ylim=(45,103)); clean(ax,theme); ax.legend(fontsize=8)
    # b advantage
    ax=axes[1]; p=summary.pivot(index="delay",columns="model",values="success_mean")*100
    gap=p["QRC-Persistent"]-p[["ESN-12","MLP-NoMemory"]].max(axis=1)
    ax.fill_between(gap.index,0,gap.values,color=ACCENT,alpha=.16); ax.plot(gap.index,gap.values,"o-",color=ACCENT,lw=2.7)
    ax.set_xscale("log"); ax.set_xticks(gap.index,labels=gap.index); ax.set(title="b  相对最佳经典基线",xlabel="延迟步数",ylabel="优势（百分点）",ylim=(-2,55)); clean(ax,theme)
    # c training
    ax=axes[2]
    for m in ["QRC-Persistent","ESN-12","QRC-FullReset","MLP-NoMemory"]:
        g=curves[curves.model==m].groupby("episode").reward.mean(); ax.plot(g.index,g.values,color=COLORS[m],lw=2.4 if m=="QRC-Persistent" else 1.5)
    ax.set(title="c  64 步任务训练收敛",xlabel="训练回合",ylabel="滑动平均回报",ylim=(.4,.96)); clean(ax,theme)
    # d noise
    ax=axes[3]; pivot=noise.pivot(index="memory_noise",columns="shots",values="success")*100
    sns.heatmap(pivot,cmap=theme["heat"],vmin=50,vmax=100,annot=True,fmt=".0f",ax=ax,
                cbar_kws={"label":"成功率（%）","shrink":.75})
    ax.set(title="d  128 步噪声与 shots",xlabel="shots",ylabel="退极化率 p / 步")
    fig.suptitle("核心实验证据矩阵",fontsize=25,fontweight="bold",y=.985)
    fig.text(.99,.012,"4 比特密度矩阵模拟 · 12 个随机种子 · 仅训练线性策略头",ha="right",fontsize=9,color=theme["muted"])
    save(fig,out,"14_core_evidence_matrix.png")


def mechanism_evidence(data,out,theme):
    summary,curves,noise,probe=data
    fig=plt.figure(figsize=(15.5,9.0)); gs=fig.add_gridspec(2,2,wspace=.25,hspace=.33)
    ax1,ax2,ax3,ax4=[fig.add_subplot(gs[i,j]) for i in range(2) for j in range(2)]
    # memory retention
    for m in ["QRC-Persistent","ESN-12","QRC-FullReset"]:
        g=probe[probe.model==m]; ax1.plot(g.delay,np.maximum(g.state_separation,1e-17),color=COLORS[m],lw=2.4,label=m)
    ax1.set_yscale("log"); ax1.set(title="a  状态记忆保留",xlabel="时间步",ylabel="RMS 状态分离度"); clean(ax1,theme,"both"); ax1.legend(fontsize=8)
    # ablation bars
    g=summary[summary.delay==64].set_index("model").loc[["QRC-Persistent","ESN-12","QRC-FullReset","MLP-NoMemory"]]
    vals=g.success_mean.to_numpy()*100; labs=["部分复位\nQRC","ESN","全部复位\nQRC","MLP"]
    ax2.bar(np.arange(4),vals,color=[COLORS[m] for m in g.index],width=.58); ax2.set_xticks(np.arange(4),labs)
    ax2.set(title="b  64 步复位机制消融",ylabel="成功率（%）",ylim=(44,104)); clean(ax2,theme)
    for i,v in enumerate(vals): ax2.text(i,v+1.3,f"{v:.1f}%",ha="center",fontsize=9,color=theme["text"],fontweight="bold")
    # noise boundary
    for shots in [32,128,1024]:
        h=noise[noise.shots==shots].sort_values("memory_noise"); ax3.plot(h.memory_noise*100,h.success*100,"o-",lw=2.2,label=f"{shots} shots")
    ax3.axhline(90,color=theme["muted"],ls="--",lw=1); ax3.set(title="c  记忆噪声边界",xlabel="单步退极化率（%）",ylabel="成功率（%）",ylim=(47,103)); clean(ax3,theme); ax3.legend(fontsize=8,ncol=3)
    # compact quantitative table
    ax4.axis("off"); rows=[
        ["QRC @ 128 步","100.0%","长时性能"],
        ["ESN @ 128 步","50.4%","接近随机"],
        ["量子优势","+49.6 pp","对最佳经典基线"],
        ["QRC 可训练参数","15","固定储层"],
        ["低噪声 32 shots","94.3%","p=0.5% / 步"],
        ["失效区间","1% 至 2%","128 步任务"],
    ]
    table=ax4.table(cellText=rows,colLabels=["指标","结果","含义"],cellLoc="left",colLoc="left",loc="center",colWidths=[.38,.22,.4])
    table.auto_set_font_size(False); table.set_fontsize(10); table.scale(1,1.75)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor(theme["grid"]); cell.set_linewidth(.6); cell.set_facecolor(theme["bg"] if r else ACCENT)
        cell.get_text().set_color(theme["text"] if r else "#FFFFFF");
        if r==0: cell.get_text().set_fontweight("bold")
    ax4.set_title("d  核心指标汇总",fontsize=15,fontweight="bold",color=theme["text"],pad=16)
    fig.suptitle("机制、消融与硬件边界",fontsize=25,fontweight="bold",y=.985)
    save(fig,out,"15_mechanism_and_hardware_evidence.png")


def render(data_dir,out,mode):
    theme=THEMES[mode]; apply_theme(theme); out.mkdir(parents=True,exist_ok=True)
    data=(pd.read_csv(data_dir/"summary_results.csv"),pd.read_csv(data_dir/"learning_curves.csv"),
          pd.read_csv(data_dir/"noise_sweep.csv"),pd.read_csv(data_dir/"memory_probe.csv"))
    roadmap(out,theme); origin_stack(out,theme); circuit(out,theme); coherence(out,theme)
    core_evidence(data,out,theme); mechanism_evidence(data,out,theme)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-dir",type=Path,required=True); ap.add_argument("--dark-out",type=Path,required=True); ap.add_argument("--light-out",type=Path,required=True)
    a=ap.parse_args(); render(a.data_dir.resolve(),a.dark_out.resolve(),"dark"); render(a.data_dir.resolve(),a.light_out.resolve(),"light")
    print("Rendered 6 dark + 6 light architecture/evidence figures")


if __name__=="__main__": main()
