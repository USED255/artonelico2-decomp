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

for w in warnings:
    print(f"[warn ] {w}")
if problems:
    for p in problems:
        print(f"[FAIL ] {p}")
    print(f"结论：❌ 路径自检失败（{len(problems)} 项）")
    sys.exit(1)
print(f"结论：✅ 路径自检通过（{len(TOOLS)} 个工具 ROOT 正确，{len(warnings)} 条警告）")
