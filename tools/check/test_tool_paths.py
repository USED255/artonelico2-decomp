#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路径自检 —— 防止「工具搬家后路径锚点失效」再犯。

背景（2026-10-06，P-41）：批量匹配工具从 `routebjp/tools/` 搬到 `tools/project/` 后，
仍然写 `Path(__file__).resolve().parent.parent` 当项目根 ⇒ 解析成 `tools/`，
`auto_match_*` 集体失效（找不到 `config/matched_symbols.txt`），而**没有任何自检会发现**——
因为工具只在真正跑批时才报 FileNotFoundError。

本脚本做两件事：
  1. **硬失败**：`at2_paths` 解析出的项目内路径必须存在；每个批量工具的 `ROOT` 必须等于项目根。
  2. **软警告**：汇编树（需 `make split`）与私有证据/工作目录（外部克隆没有）缺失时只警告。

用法：`python3 tools/check/test_tool_paths.py`（`make check` 会调用）
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "project"))

import at2_paths as AP  # noqa: E402

# 这些必须能用（公开仓库里就有）
HARD_PATHS = ("MATCHED_LIST", "SRCDIR", "FLAGS_TSV")
# 导入后必须把 ROOT 指向项目根的批量工具
TOOLS = (
    "auto_match_trivial",
    "auto_match_m2c",
    "auto_match_ghidra",
    "auto_match_stub",
    "auto_match_wrapper",
    "m2c_draft",
    "ghidra_draft",
    "infer_sig",
    "p1a_pseudoc_probe",
    "screen_flags",
    "auto_match_permuter",
)

problems: list[str] = []
warnings: list[str] = []

for name in HARD_PATHS:
    p = getattr(AP, name)
    if not p.exists():
        problems.append(f"{name} 不存在：{p}")

for name in TOOLS:
    try:
        mod = importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"import {name} 失败：{type(exc).__name__}: {exc}")
        continue
    got = getattr(mod, "ROOT", None)
    if got is None:
        problems.append(f"{name} 没有 ROOT（应当 import at2_paths）")
    elif Path(got).resolve() != AP.PROJECT_ROOT:
        problems.append(f"{name}.ROOT = {got} ≠ 项目根 {AP.PROJECT_ROOT}（典型：少写一级 parent）")

if not AP.ASMDIR.is_dir():
    warnings.append(f"汇编树不在：{AP.ASMDIR}（公开克隆需先 `make split`）")
if not AP.WORKQUEUE.is_file():
    warnings.append(f"难度工作队列不在：{AP.WORKQUEUE}（私有侧派生数据；批量匹配需要它）")
if AP.WORK_ROOT is None or not Path(AP.WORK_ROOT).is_dir():
    warnings.append(f"批量工作目录不在：{AP.WORK_ROOT}")

def test_private_root_from_worktree() -> list[str]:
    """回归：**任务工作树**里也必须能解析到私有仓库根。

    2026-10-06 的真实坑：旧实现只试 `<项目根>/../at2`，而工作树在 `<工作区>/worktrees/<repo>-<slug>`，
    上一级是 `worktrees/` ⇒ 私有根落空、证据目录错误地落到工作树里（`make check` 多 1 条 warn）。
    这里造一个合成工作区、以子进程导入（环境变量覆盖项目根）来断言解析结果。
    """
    import os
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        ws = Path(td) / "ws"
        (ws / "at2" / "routebjp").mkdir(parents=True)
        (ws / "at2" / "out" / "evidence").mkdir(parents=True)
        wtree = ws / "worktrees" / "at2-public-x"
        wtree.mkdir(parents=True)
        env = dict(os.environ, AT2_PROJECT_ROOT=str(wtree), AT2_PRIVATE_ROOT="", AT2_EVIDENCE_ROOT="")
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import at2_paths as A;"
                "print(A.PRIVATE_ROOT); print(A.EVIDENCE_ROOT)")
        r = subprocess.run([sys.executable, "-c", code, str(ROOT / "tools" / "project")],
                           env=env, capture_output=True, text=True)
        if r.returncode != 0:
            return [f"工作树路径回归：子进程失败：{r.stderr.strip()[:200]}"]
        lines = [x.strip() for x in r.stdout.splitlines() if x.strip()]
        want_priv = str(ws / "at2")
        want_ev = str(ws / "at2" / "out" / "evidence")
        bad: list[str] = []
        got_priv = lines[0] if lines else "?"
        got_ev = lines[1] if len(lines) > 1 else "?"
        if got_priv != want_priv:
            bad.append(f"工作树路径回归：PRIVATE_ROOT = {got_priv}，应为 {want_priv}")
        if got_ev != want_ev:
            bad.append(f"工作树路径回归：EVIDENCE_ROOT = {got_ev}，应为 {want_ev}")
        return bad


problems.extend(test_private_root_from_worktree())

for w in warnings:
    print(f"[warn ] {w}")
if problems:
    for p in problems:
        print(f"[FAIL ] {p}")
    print(f"结论：❌ 路径自检失败（{len(problems)} 项）")
    sys.exit(1)
print(f"结论：✅ 路径自检通过（{len(TOOLS)} 个工具 ROOT 正确，{len(warnings)} 条警告）")
