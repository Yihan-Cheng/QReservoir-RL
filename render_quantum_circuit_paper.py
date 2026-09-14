"""Publication-grade 4-qubit quantum-reservoir circuit figures.

The circuit matches run_experiment.QuantumReservoir:
3 memory qubits + 1 readout qubit, fixed Ising reservoir, partial trace/reset.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc, FancyArrowPatch
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


NAVY="#12345B"; BLUE="#0757B5"; CYAN="#18AFC2"; ORANGE="#F28A24"
VIOLET="#7569E8"; SLATE="#6E8AA6"; LIGHT="#AAB7C4"; INK="#17324D"
MUTED="#71859A"; GRID="#D7E6EF"; PALE="#F7FBFD"; WHITE="#FFFFFF"


def style():
    mpl.rcParams.update({
        "font.family":"sans-serif",
        "font.sans-serif":["Microsoft YaHei","Noto Sans CJK SC","SimHei","DejaVu Sans"],
        "mathtext.fontset":"stix", "mathtext.default":"it",
        "axes.unicode_minus":False, "figure.facecolor":WHITE,
        "savefig.facecolor":WHITE, "text.color":INK,
        "axes.labelcolor":MUTED, "xtick.color":MUTED, "ytick.color":MUTED,
    })


def save(fig,out,name):
    out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/name,dpi=320,bbox_inches="tight",pad_inches=.10)
    fig.savefig(out/name.replace(".png",".pdf"),bbox_inches="tight",pad_inches=.10)
    plt.close(fig)


def panel_badge(ax,letter,x=.015,y=.945):
    ax.text(x,y,letter,transform=ax.transAxes,fontsize=15,fontweight="bold",color=NAVY,
            ha="left",va="top")


def rounded(ax,xy,wh,fc=WHITE,ec=GRID,lw=1.0,r=.015,z=0):
    p=FancyBboxPatch(xy,*wh,boxstyle=f"round,pad=.008,rounding_size={r}",
                     fc=fc,ec=ec,lw=lw,zorder=z)
    ax.add_patch(p); return p


def gate(ax,x,y,label,fc,ec=None,w=.055,h=.09,fontsize=9):
    ec=ec or fc
    p=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=.004,rounding_size=.008",
                     fc=fc,ec=ec,lw=1.0,zorder=5)
    ax.add_patch(p)
    ax.text(x,y,label,ha="center",va="center",fontsize=fontsize,color=WHITE if fc!=WHITE else ec,
            fontweight="bold",zorder=6)


def rotation_icon(ax,x,y,color,w=.050,h=.08):
    p=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=.004,rounding_size=.008",
                     fc=WHITE,ec=color,lw=1.2,zorder=5)
    ax.add_patch(p)
    ax.add_patch(Arc((x,y),w*.48,h*.40,theta1=25,theta2=330,color=color,lw=1.2,zorder=6))
    ax.add_patch(FancyArrowPatch((x+w*.20,y+h*.05),(x+w*.22,y-h*.02),arrowstyle="-|>",
                                 mutation_scale=7,color=color,lw=.8,zorder=7))


def zz(ax,x,y1,y2,color=BLUE):
    ax.plot([x,x],[y1,y2],color=color,lw=1.15,zorder=3)
    for y in (y1,y2):
        ax.add_patch(Circle((x,y),.010,fc="#EAF2FF",ec=color,lw=1.2,zorder=4))
        ax.text(x,y,"Z",ha="center",va="center",fontsize=7,color=color,fontweight="bold",zorder=5)


def meter(ax,x,y,color=CYAN):
    p=FancyBboxPatch((x-.026,y-.042),.052,.084,boxstyle="round,pad=.004,rounding_size=.008",
                     fc="#F2FCFD",ec=color,lw=1.2,zorder=5)
    ax.add_patch(p)
    ax.add_patch(Arc((x,y-.004),.030,.028,theta1=0,theta2=180,color=color,lw=1.15,zorder=6))
    ax.plot([x,x+.011],[y-.004,y+.011],color=color,lw=1.1,zorder=6)


def reset(ax,x,y):
    p=FancyBboxPatch((x-.026,y-.042),.052,.084,boxstyle="round,pad=.004,rounding_size=.008",
                     fc="#FFF8EF",ec=ORANGE,lw=1.2,zorder=5)
    ax.add_patch(p)
    ax.add_patch(Arc((x,y),.030,.030,theta1=40,theta2=338,color=ORANGE,lw=1.2,zorder=6))
    ax.add_patch(FancyArrowPatch((x+.011,y+.011),(x+.015,y+.004),arrowstyle="-|>",
                                 mutation_scale=7,color=ORANGE,lw=.8,zorder=7))


def topology(ax):
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(.08,.92,"四比特耦合拓扑",fontsize=13,fontweight="bold",color=NAVY)
    ax.text(.08,.865,"线宽对应 $|J_{ij}|$",fontsize=8.5,color=MUTED)
    pos={"$M_0$":(.30,.67),"$M_1$":(.68,.67),"$M_2$":(.50,.37),"$R$":(.50,.10)}
    edges=[("$M_0$","$M_1$",.34),("$M_1$","$M_2$",.29),("$M_0$","$M_2$",.21),
           ("$M_0$","$R$",.045),("$M_1$","$R$",.052),("$M_2$","$R$",.039)]
    for a,b,w in edges:
        x1,y1=pos[a]; x2,y2=pos[b]
        ax.plot([x1,x2],[y1,y2],color=VIOLET if "$R$" not in (a,b) else CYAN,
                lw=.7+5*w,alpha=.82,zorder=1)
    for lab,(x,y) in pos.items():
        color=CYAN if lab=="$R$" else VIOLET
        ax.add_patch(Circle((x,y),.073,fc=WHITE,ec=color,lw=2,zorder=3))
        ax.add_patch(Circle((x,y),.055,fc=color,ec="none",alpha=.12,zorder=2))
        ax.text(x,y,lab,ha="center",va="center",color=color,fontsize=11,fontweight="bold",zorder=4)
    ax.text(.50,.77,"记忆",ha="center",fontsize=9,color=VIOLET,fontweight="bold")
    ax.text(.50,.00,"读出",ha="center",fontsize=9,color=CYAN,fontweight="bold")


def time_block(ax,x0,x1,ys,step_label,feature_label):
    rounded(ax,(x0,.13),(x1-x0,.72),fc="#FCFEFF",ec="#D7EAF3",lw=1.0,r=.012)
    ax.text((x0+x1)/2,.89,step_label,ha="center",va="center",fontsize=11.5,color=NAVY,fontweight="bold")
    # rails
    for i,y in enumerate(ys):
        ax.plot([x0+.015,x1-.015],[y,y],color=VIOLET if i<3 else CYAN,lw=1.55,zorder=2)
    # input encoding: M0 and R are driven; idle rotations are shown as light outlines
    gate(ax,x0+.065,ys[0],r"$R_y(1.24u_t)$" if "t$" in step_label and "+" not in step_label else r"$R_y(1.24u_{t+1})$",BLUE,w=.094,h=.085,fontsize=8)
    for y in ys[1:3]: rotation_icon(ax,x0+.065,y,VIOLET)
    gate(ax,x0+.065,ys[3],r"$R_y(0.22u_t)$" if "t$" in step_label and "+" not in step_label else r"$R_y(0.22u_{t+1})$",CYAN,w=.094,h=.085,fontsize=8)
    # fixed local evolution
    for y in ys:
        gate(ax,x0+.175,y,r"$R_x$",CYAN,w=.046,h=.075,fontsize=8)
        gate(ax,x0+.232,y,r"$R_z$",ORANGE,w=.046,h=.075,fontsize=8)
    # distributed Ising couplings matching model graph
    zz(ax,x0+.305,ys[0],ys[1],VIOLET)
    zz(ax,x0+.355,ys[1],ys[2],VIOLET)
    zz(ax,x0+.405,ys[0],ys[2],VIOLET)
    zz(ax,x0+.455,ys[0],ys[3],BLUE)
    zz(ax,x0+.505,ys[1],ys[3],BLUE)
    # measurement and reset only on R
    meter(ax,x1-.095,ys[3]); reset(ax,x1-.040,ys[3])
    ax.annotate(feature_label,xy=(x1-.095,ys[3]-.045),xytext=(x1-.095,.055),
                ha="center",va="center",fontsize=9.5,color=CYAN,fontweight="bold",
                arrowprops=dict(arrowstyle="-|>",color=CYAN,lw=1.2))
    ax.text(x0+.065,.17,"输入注入",ha="center",fontsize=8.5,color=MUTED)
    ax.text(x0+.215,.17,"局域旋转",ha="center",fontsize=8.5,color=MUTED)
    ax.text(x0+.405,.17,"$ZZ$耦合",ha="center",fontsize=8.5,color=MUTED)
    ax.text(x1-.067,.17,"测量/重置",ha="center",fontsize=8.5,color=MUTED)


def circuit(ax,compact=False):
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ys=[.70,.57,.44,.28]
    # labels and subsystem braces
    for lab,y,color in zip(["$M_0$","$M_1$","$M_2$","$R$"],ys,[VIOLET,VIOLET,VIOLET,CYAN]):
        ax.add_patch(Circle((.035,y),.018,fc=color,ec="none"))
        ax.text(.035,y,lab,ha="center",va="center",fontsize=8.5,color=WHITE,fontweight="bold")
    ax.text(.003,.57,"记忆",rotation=90,ha="center",va="center",fontsize=9,color=VIOLET,fontweight="bold")
    ax.text(.003,.28,"读出",rotation=90,ha="center",va="center",fontsize=9,color=CYAN,fontweight="bold")
    # initial state labels
    ax.text(.070,.79,r"$\rho_t^M \otimes |0\rangle\!\langle0|_R$",fontsize=10,color=INK)
    time_block(ax,.07,.50,ys,r"时间步 $t$",r"$x_t$（14维Pauli期望值）")
    time_block(ax,.53,.96,ys,r"时间步 $t+1$",r"$x_{t+1}$（14维Pauli期望值）")
    # memory continuity and ellipsis between blocks
    ax.annotate("",xy=(.79,.80),xytext=(.28,.80),arrowprops=dict(arrowstyle="-|>",color=VIOLET,lw=1.7))
    ax.text(.535,.815,r"$\rho_t^M \rightarrow \rho_{t+1}^M$",ha="center",fontsize=10,color=VIOLET,fontweight="bold")
    ax.text(.515,.50,r"$\cdots$",fontsize=17,color=INK,ha="center")
    ax.text(.985,.50,r"$\cdots\; n\in[N]$",fontsize=10,color=MUTED,ha="left")
    # reservoir bracket
    ax.annotate("",xy=(.245,.92),xytext=(.455,.92),arrowprops=dict(arrowstyle="|-|",color=BLUE,lw=1.2))
    ax.text(.35,.94,r"$U_{\mathrm{res}}=\exp(-iH\Delta t)$",ha="center",fontsize=10,color=BLUE,fontweight="bold")


def pure_circuit(out):
    fig=plt.figure(figsize=(15.8,7.8))
    gs=fig.add_gridspec(1,2,width_ratios=[.21,.79],left=.035,right=.98,top=.79,bottom=.19,wspace=.02)
    ax_top=fig.add_subplot(gs[0,0]); ax_c=fig.add_subplot(gs[0,1])
    topology(ax_top); circuit(ax_c)
    fig.text(.035,.93,"部分测量—重置量子储层线路",fontsize=25,fontweight="bold",color=NAVY)
    fig.text(.035,.875,"四比特固定Ising动力学：记忆子系统跨步演化，读出子系统测量后循环复用",fontsize=11.5,color=MUTED)
    fig.text(.965,.925,"QRR · CIRCUIT",ha="right",fontsize=9,color=BLUE,fontweight="bold")
    # legend
    fig.text(.035,.10,r"$R_y$ 输入编码",fontsize=9.5,color=BLUE,fontweight="bold")
    fig.text(.17,.10,r"$R_x/R_z$ 局域旋转",fontsize=9.5,color=CYAN,fontweight="bold")
    fig.text(.335,.10,r"$R_{zz}$ 相互作用",fontsize=9.5,color=VIOLET,fontweight="bold")
    fig.text(.50,.10,"部分测量",fontsize=9.5,color=CYAN,fontweight="bold")
    fig.text(.61,.10,"读出重置",fontsize=9.5,color=ORANGE,fontweight="bold")
    fig.text(.76,.10,r"$\Delta t<T_2$，$T_{\mathrm{run}}\gg T_2$",fontsize=10,color=NAVY,fontweight="bold")
    fig.add_artist(Line2D([.035,.15],[.045,.045],transform=fig.transFigure,color=BLUE,lw=2.5))
    fig.add_artist(Line2D([.15,.18],[.045,.045],transform=fig.transFigure,color=ORANGE,lw=2.5))
    fig.text(.035,.018,"量池智驭 · FOUR-QUBIT NISQ RESERVOIR",fontsize=8.5,color=BLUE,fontweight="bold")
    save(fig,out,"00_量子储层线路.png")


def composite(out,data_dir):
    probe=pd.read_csv(data_dir/"memory_probe.csv")
    fig=plt.figure(figsize=(13.0,10.3))
    gs=fig.add_gridspec(2,2,height_ratios=[1.0,1.03],width_ratios=[.21,.79],
                        left=.055,right=.97,top=.94,bottom=.07,hspace=.19,wspace=.03)
    ax_top=fig.add_subplot(gs[0,0]); ax_c=fig.add_subplot(gs[0,1]); ax=fig.add_subplot(gs[1,:])
    panel_badge(ax_top,"a",x=.0,y=1.02); topology(ax_top); circuit(ax_c)
    # lower evidence plot
    panel_badge(ax,"b",x=-.025,y=1.03)
    colors={"QRC-Persistent":BLUE,"ESN-12":SLATE,"QRC-FullReset":ORANGE,"MLP-NoMemory":LIGHT}
    names={"QRC-Persistent":"量池智驭","ESN-12":"经典 ESN","QRC-FullReset":"量子全重置","MLP-NoMemory":"无记忆 MLP"}
    offsets={"QRC-Persistent":8,"ESN-12":9,"QRC-FullReset":-12,"MLP-NoMemory":8}
    for m in ["QRC-Persistent","ESN-12","QRC-FullReset","MLP-NoMemory"]:
        g=probe[probe.model==m]
        y=np.maximum(g.state_separation.values,1e-17)
        ax.plot(g.delay,y,color=colors[m],lw=2.8 if m=="QRC-Persistent" else 1.7,zorder=3)
        ax.annotate(names[m],(g.delay.iloc[-1],y[-1]),xytext=(8,offsets[m]),textcoords="offset points",
                    fontsize=9,color=colors[m],fontweight="bold",va="center")
    ax.set_yscale("log"); ax.set_xlim(0,174); ax.set_ylim(2e-18,1.8)
    ax.set_xlabel("线索后的时间步",fontsize=11); ax.set_ylabel("RMS状态分离度",fontsize=11)
    ax.grid(True,color=GRID,lw=.7); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(GRID)
    ax.axvspan(64,128,color=BLUE,alpha=.035)
    ax.text(96,8e-17,"长时序区间",ha="center",color=BLUE,fontsize=9)
    ax.text(.01,.95,"持久量子记忆跨越160步",transform=ax.transAxes,fontsize=15,color=NAVY,fontweight="bold",va="top")
    ax.text(.01,.885,"部分测量保留可辨识状态；全重置立即退化",transform=ax.transAxes,fontsize=9,color=MUTED,va="top")
    ax.text(.985,.95,r"$\Delta t<T_2$   ·   $T_{\mathrm{run}}\gg T_2$",transform=ax.transAxes,ha="right",fontsize=10,color=ORANGE,fontweight="bold",va="top")
    fig.text(.055,.985,"量子储层结构与长时序记忆验证",fontsize=22,fontweight="bold",color=NAVY,va="top")
    fig.add_artist(Line2D([.055,.15],[.025,.025],transform=fig.transFigure,color=BLUE,lw=2.4))
    fig.add_artist(Line2D([.15,.18],[.025,.025],transform=fig.transFigure,color=ORANGE,lw=2.4))
    fig.text(.055,.007,"量池智驭 · CIRCUIT AND MEMORY EVIDENCE",fontsize=8,color=BLUE,fontweight="bold")
    save(fig,out,"00B_量子线路与记忆验证.png")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-dir",type=Path,required=True); ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); style(); pure_circuit(a.out); composite(a.out,a.data_dir)
    print("Rendered refined circuit figures")


if __name__=="__main__": main()
