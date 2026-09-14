"""One-click acceptance runner and evidence report for 量池智驭."""

from __future__ import annotations

import argparse
import csv
import html
import json
import subprocess
import sys
import time
from pathlib import Path

from platform_adapters import list_backend_profiles


REQUIRED_OUTPUTS = (
    "summary_results.csv",
    "raw_results.csv",
    "learning_curves.csv",
    "memory_probe.csv",
    "noise_sweep.csv",
    "resource_comparison.csv",
    "run_metadata.json",
)


def run_quick_benchmark(code_dir: Path, acceptance_root: Path) -> Path:
    run_root = acceptance_root / "快速复现实验"
    cmd = [
        sys.executable,
        str(code_dir / "run_experiment.py"),
        "--quick",
        "--output-root",
        str(run_root),
        "--target-backend",
        "originq-superconducting",
    ]
    completed = subprocess.run(cmd, check=False, text=True, capture_output=True)
    (acceptance_root / "快速复现实验_控制台日志.txt").write_text(
        completed.stdout + "\n" + completed.stderr, encoding="utf-8"
    )
    if completed.returncode != 0:
        raise RuntimeError("快速复现实验失败，请查看控制台日志。")
    return run_root / "figure"


def read_summary(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description="量池智驭一键验收")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--rerun", action="store_true", help="先执行缩短版复现实验")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    code_dir = Path(__file__).resolve().parent
    acceptance_root = project_root / "验收成果"
    acceptance_root.mkdir(parents=True, exist_ok=True)
    figure_dir = run_quick_benchmark(code_dir, acceptance_root) if args.rerun else project_root / "figure"

    checks = []
    for name in REQUIRED_OUTPUTS:
        target = figure_dir / name
        checks.append({"item": name, "passed": target.exists(), "path": str(target)})

    summary = read_summary(figure_dir / "summary_results.csv")
    qrc_rows = [r for r in summary if r.get("model") == "QRC-Persistent"]
    max_delay = max((int(float(r["delay"])) for r in qrc_rows), default=None)
    max_delay_success = next(
        (float(r["success_mean"]) for r in qrc_rows if int(float(r["delay"])) == max_delay), None
    )
    manifest = {
        "project": "量池智驭：面向长时序任务的量子储层强化学习系统",
        "challenge": "XA-202605 聚焦量子计算实用化瓶颈",
        "issuer": "量子科技长三角产业创新中心",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execution": "quick rerun" if args.rerun else "existing result audit",
        "evidence_directory": str(figure_dir),
        "checks": checks,
        "key_metric": {"max_delay": max_delay, "qrc_success_mean": max_delay_success},
        "backend_profiles": list_backend_profiles(),
        "boundary": (
            "当前数值结果来自本地密度矩阵模拟。OriginQ 超导真机与天工 Kaiwu CIM "
            "均为待验证后端，只有保存原始计数、编译信息和平台任务记录后才能形成真机证据。"
        ),
    }
    (acceptance_root / "验收清单.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    passed = sum(int(x["passed"]) for x in checks)
    rows = "".join(
        f"<tr><td>{html.escape(x['item'])}</td><td class={'ok' if x['passed'] else 'bad'}>"
        f"{'通过' if x['passed'] else '缺失'}</td><td>{html.escape(x['path'])}</td></tr>"
        for x in checks
    )
    metric = "未读取" if max_delay is None else f"延迟 {max_delay} 步，平均成功率 {max_delay_success:.2%}"
    report = f"""<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>
<title>量池智驭验收报告</title><style>
body{{font-family:'Microsoft YaHei',sans-serif;margin:42px;color:#102a56;background:#f4f9ff}}
main{{max-width:1050px;margin:auto;background:white;padding:42px 52px;box-shadow:0 12px 40px #a9c7e755}}
h1{{color:#0759b5}} h2{{margin-top:34px;border-left:5px solid #ff7a00;padding-left:12px}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #cbd9e8;padding:10px;text-align:left}}
th{{background:#0a5eb5;color:white}} .ok{{color:#087f5b;font-weight:bold}} .bad{{color:#c92a2a;font-weight:bold}}
.boundary{{background:#eef6ff;padding:16px 20px;border-left:5px solid #ff7a00;line-height:1.7}}
</style></head><body><main><h1>量池智驭验收报告</h1>
<p>发榜单位：量子科技长三角产业创新中心<br>揭榜赛题：XA-202605 聚焦量子计算实用化瓶颈<br>参赛单位：西北工业大学</p>
<h2>运行结论</h2><p>检查项 {passed}/{len(checks)} 通过。核心读数：{metric}。</p>
<h2>可复现产物</h2><table><tr><th>文件</th><th>状态</th><th>路径</th></tr>{rows}</table>
<h2>证据边界</h2><p class='boundary'>{html.escape(manifest['boundary'])}</p>
<h2>平台路线</h2><p>当前基线采用本地密度矩阵模拟。近期适配 QPanda、OriginIR 与本源超导平台；后续在天工平台通过 Kaiwu SDK 接入光量子 CIM，用于 QUBO 子问题求解，并与经典求解器进行同口径比较。</p>
</main></body></html>"""
    (acceptance_root / "量池智驭_验收报告.html").write_text(report, encoding="utf-8")
    print(f"验收完成：{acceptance_root / '量池智驭_验收报告.html'}")


if __name__ == "__main__":
    main()
