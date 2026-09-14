# QReservoir-RL

**Quantum Reservoir Reinforcement Learning for Long-Horizon Temporal Decision Tasks**

> 中文项目名称：量池智驭——面向长时序任务的量子储层强化学习系统

QReservoir-RL 是一个面向长时序决策任务的量子储层强化学习实验框架。项目利用具有持续记忆能力的部分复位量子储层处理部分可观测、稀疏奖励和长期信用分配问题，并通过经典模型对照、复位机制消融、噪声与测量次数扫描以及资源统计分析其有效性和适用边界。

本项目最初面向 2026 年度中国青年科技创新“揭榜挂帅”擂台赛学生赛道赛题 `XA-202605` 开展，赛题方向为“聚焦量子计算实用化瓶颈——算法创新与硬件适配协同攻关”。

## 核心思路

实验采用延迟线索决策任务。每个回合开始时，环境仅在第 0 步给出一次二元目标线索，随后进入长度为 \(D\) 的无信息等待区。智能体必须在序列末端依据最初线索选择动作：

```text
初始线索 → 无信息等待区 → 末端决策
   t=0        D steps        t=D
```

延迟长度设置为：

```text
D ∈ {4, 8, 16, 32, 64, 128}
```

量子储层由 3 个记忆量子比特和 1 个读出量子比特组成。每个时间步只测量并复位读出比特，记忆子系统继续跨步演化。固定量子动力学产生 14 维 Pauli 观测特征，随后由轻量线性策略头输出动作概率：

```text
环境观测
   ↓
量子数据编码
   ↓
固定量子储层演化
   ↓
读出比特测量与部分复位
   ↓
14维 Pauli 观测特征
   ↓
线性强化学习策略头
   ↓
末端动作
```

储层动力学保持固定，训练过程主要更新策略读出层，从而降低可训练参数规模，并避免深层参数化量子线路可能出现的优化困难。

## 对照模型

为区分量子特征映射、跨步记忆和策略读出层的作用，实验在统一强化学习训练口径下比较四种模型：

| 模型 | 结构与作用 |
| --- | --- |
| `QRC-Persistent` | 部分复位量子储层；保留记忆子系统，仅测量并复位读出比特 |
| `ESN-12` | 12 节点经典回声状态网络；用于比较经典循环记忆能力 |
| `QRC-FullReset` | 每步复位全部量子比特；用于消融跨时间步状态保留机制 |
| `MLP-NoMemory` | 仅使用当前观测的无记忆前馈策略；用于构造随机水平基线 |

所有模型使用同类 Bernoulli REINFORCE 策略更新和一致的训练、评估流程。

## 实验配置

正式实验的主要配置如下：

| 配置项 | 数值 |
| --- | ---: |
| 模型数量 | 4 |
| 时序延迟档位 | 6 |
| 独立随机种子 | 12 |
| 每组训练回合 | 800 |
| 每组评估回合 | 3000 |
| 默认测量次数 | 256 shots |
| 量子比特数 | 4 |
| Pauli 观测特征数 | 14 |

实验输出逐种子原始结果、统计汇总、强化学习曲线、长时记忆探针、噪声—shots 扫描、资源统计和运行元数据。

## 主要观察

在当前延迟线索任务和模拟参数下，`QRC-Persistent` 在最长 128 步延迟条件下仍保持稳定表现。`ESN-12` 在短延迟条件下能够完成任务，但随着等待长度增长，其内部状态对初始线索的区分能力逐渐衰减。`QRC-FullReset` 和 `MLP-NoMemory` 在长延迟条件下接近随机决策水平。

该消融结果表明，本实验中的长期性能与量子储层的跨步状态保留机制密切相关，不能简单归因于量子特征映射或线性策略头。

> **结果边界：** 当前数值结果来自本地四比特密度矩阵模拟，不构成普适量子优势、量子加速或量子真机性能证明。仓库中的本源超导与光量子 CIM 内容属于接口设计和后续验证路线。

## 环境要求

- Python 3.10 或更高版本
- NumPy 2.0+
- SciPy 1.14+
- Pandas 2.2+
- Matplotlib 3.9+
- Seaborn 0.13+

推荐使用独立虚拟环境：

```bash
git clone https://github.com/YOUR_USERNAME/QReservoir-RL.git
cd QReservoir-RL

python -m venv .venv
```

Windows：

```powershell
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux 或 macOS：

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 快速复现

在仓库根目录执行：

```bash
python acceptance_demo.py --project-root . --rerun
```

快速模式将运行缩短版实验，并生成：

```text
验收成果/
├─ 快速复现实验/
├─ 快速复现实验_控制台日志.txt
├─ 验收清单.json
└─ 量池智驭_验收报告.html
```

快速模式用于验证代码环境、输出链路和核心趋势，不代替正式多随机种子结果。

## 运行完整实验

```bash
python run_experiment.py --output-root .
```

程序将在 `figure/` 目录中生成正式实验数据和基础图表。完整模式包含多模型、多延迟和多随机种子实验，运行时间明显长于快速模式。

常用可选参数可通过以下命令查看：

```bash
python run_experiment.py --help
```

## 主要输出文件

| 文件 | 内容 |
| --- | --- |
| `raw_results.csv` | 每个模型、延迟和随机种子的原始实验结果 |
| `summary_results.csv` | 按模型和延迟统计的成功率、回报和离散程度 |
| `learning_curves.csv` | 强化学习训练过程和收敛轨迹 |
| `memory_probe.csv` | 不同时间位置的状态分离与记忆探针结果 |
| `noise_sweep.csv` | 不同噪声强度和测量 shots 下的成功率 |
| `resource_comparison.csv` | 模型参数量和资源指标对照 |
| `run_metadata.json` | 实验配置、软件环境、运行时间和时间戳 |

## 推荐仓库结构

```text
QReservoir-RL/
├─ README.md
├─ LICENSE                     # 确认公开许可后再添加
├─ .gitignore
├─ requirements.txt
├─ run_experiment.py
├─ acceptance_demo.py
├─ platform_adapters.py
├─ scripts/
│  ├─ render_advanced_blue_orange.py
│  ├─ render_architecture_figures.py
│  ├─ render_premium_figures.py
│  └─ render_quantum_circuit_paper.py
├─ results/
│  ├─ summary_results.csv
│  ├─ noise_sweep.csv
│  ├─ resource_comparison.csv
│  └─ run_metadata.json
└─ figures/
   ├─ performance.png
   ├─ memory.png
   └─ quantum_circuit.png
```

建议只在 `results/` 中提交体积较小、能够支撑README结论的代表性结果。逐回合或大规模中间数据可通过 Release、网盘或数据仓库单独发布。

## 平台适配路线

### 本源超导门模型平台

近期适配路线为使用 QPanda 构造线路，经 OriginIR 编译与物理比特映射后提交量子云任务。完整真机记录应至少包含：

- 后端名称与任务编号；
- 校准时间；
- 逻辑—物理量子比特映射；
- 编译后线路深度和双量子比特门数量；
- shots 与原始测量计数。

### 天工光量子 CIM

后续计划将 Pauli 观测量选择、稀疏策略读出和测量调度等离散子问题转换为 QUBO，通过 Kaiwu SDK 接入相干伊辛机，并与经典优化器进行同口径比较。

代码中出现目标后端名称或适配配置，不代表已经完成真实硬件运行。

## 可复现性

建议在发布结果时同时保存：

- Git commit ID；
- Python与依赖版本；
- 完整运行命令；
- 随机种子与实验配置；
- 原始和汇总CSV；
- `run_metadata.json`；
- 图表生成脚本。

报告中的成功率应追溯至 `summary_results.csv` 和 `raw_results.csv`，训练收敛结论应追溯至 `learning_curves.csv`，长期记忆结论应追溯至 `memory_probe.csv`，鲁棒性结论应追溯至 `noise_sweep.csv`。

## 参考文献

1. Hu, F. et al. *Overcoming the coherence time barrier in quantum machine learning on temporal data*. Nature Communications 15, 6548 (2024). https://doi.org/10.1038/s41467-024-51162-7
2. Kutvonen, A., Fujii, K. and Sagawa, T. *Optimizing a quantum reservoir computer for time series prediction*. Scientific Reports 10, 14687 (2020). https://doi.org/10.1038/s41598-020-71673-9
3. Chen, S. Y.-C. *Efficient quantum recurrent reinforcement learning via quantum reservoir computing*. arXiv:2309.07339 (2023). https://arxiv.org/abs/2309.07339

## Acknowledgements

项目由西北工业大学参赛团队完成，项目主持人为成弈含，指导老师为张伟伟教授
