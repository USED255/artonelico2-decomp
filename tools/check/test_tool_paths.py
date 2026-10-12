#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Path self-check. This tool stops "a moved tool resolves the wrong project root" from returning.

Background (2026-10-06, P-41): the batch matching tools moved from `routebjp/tools/` to
`tools/project/`, but they still used `Path(__file__).resolve().parent.parent` as the project
root. That path resolved to `tools/`, so every `auto_match_*` tool failed to find
`config/matched_symbols.txt`. No check caught the failure, because a tool reports
FileNotFoundError only when a batch run starts.
On 2026-10-12 the maintainer tools moved again, to `tools/maintainer/project/`. This check
covers that move too: every batch tool must still resolve the project root.

This script does two things:
  1. Hard failure: every project path that `at2_paths` resolves must exist. The `ROOT` of
     each batch tool must equal the project root.
  2. Soft warning: a missing assembly tree (run `make split` first) or a missing private
     evidence directory only warns.

Usage: `python3 tools/check/test_tool_paths.py` (`make check` calls this script).

路径自检 —— 防止「工具搬家后路径锚点失效」再犯。

背景（2026-10-06，P-41）：批量匹配工具从 `routebjp/tools/` 搬到 `tools/project/` 后，
仍然写 `Path(__file__).resolve().parent.parent` 当项目根 ⇒ 解析成 `tools/`，
`auto_match_*` 集体失效（找不到 `config/matched_symbols.txt`），而**没有任何自检会发现**——
因为工具只在真正跑批时才报 FileNotFoundError。
2026-10-12 这批维护者工具又搬到 `tools/maintainer/project/`；本自检同样覆盖这次搬迁：
每个批量工具的 `ROOT` 仍必须等于项目根。

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
sys.path.insert(0, str(ROOT / "tools" / "maintainer" / "project"))   # the batch tools live here since 2026-10-12

import at2_paths as AP  # noqa: E402

# These paths must resolve (the public repository contains them).
# 这些必须能用（公开仓库里就有）。
HARD_PATHS = ("MATCHED_LIST", "SRCDIR", "FLAGS_TSV", "SYMBOL_ADDRS")
# Batch tools that must point ROOT at the project root after import.
# 导入后必须把 ROOT 指向项目根的批量工具。
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
        problems.append(f"{name} does not exist: {p}")

for name in TOOLS:
    try:
        mod = importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"import {name} failed: {type(exc).__name__}: {exc}")
        continue
    got = getattr(mod, "ROOT", None)
    if got is None:
        problems.append(f"{name} has no ROOT (it must import at2_paths)")
    elif Path(got).resolve() != AP.PROJECT_ROOT:
        problems.append(f"{name}.ROOT = {got} != project root {AP.PROJECT_ROOT} (a missing parent is the usual cause)")

if not AP.ASMDIR.is_dir():
    warnings.append(f"the assembly tree is absent: {AP.ASMDIR} (run `make split` in a public clone)")
if not AP.WORKQUEUE.is_file():
    warnings.append(f"the difficulty work queue is absent: {AP.WORKQUEUE} (private derived data, the batch matching tools need it)")
if AP.WORK_ROOT is None or not Path(AP.WORK_ROOT).is_dir():
    warnings.append(f"the batch work directory is absent: {AP.WORK_ROOT}")

def test_private_root_from_worktree() -> list[str]:
    """Regression: the private repository root must resolve from a task worktree too.

    2026-10-06 real trap: the old implementation tried `<project root>/../at2` only, and a
    worktree lives at `<workspace>/worktrees/<repo>-<slug>`. Its parent is `worktrees/`, so the
    private root was empty and the evidence directory landed inside the worktree (`make check`
    showed one extra warning). This test builds a synthetic workspace, imports in a subprocess
    with environment overrides, and asserts the resolved paths.

    回归：**任务工作树**里也必须能解析到私有仓库根。

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
            return [f"worktree path regression: the subprocess failed: {r.stderr.strip()[:200]}"]
        lines = [x.strip() for x in r.stdout.splitlines() if x.strip()]
        want_priv = str(ws / "at2")
        want_ev = str(ws / "at2" / "out" / "evidence")
        bad: list[str] = []
        got_priv = lines[0] if lines else "?"
        got_ev = lines[1] if len(lines) > 1 else "?"
        if got_priv != want_priv:
            bad.append(f"worktree path regression: PRIVATE_ROOT = {got_priv}, expected {want_priv}")
        if got_ev != want_ev:
            bad.append(f"worktree path regression: EVIDENCE_ROOT = {got_ev}, expected {want_ev}")
        return bad


problems.extend(test_private_root_from_worktree())

for w in warnings:
    print(f"[warn ] {w}")
if problems:
    for p in problems:
        print(f"[FAIL ] {p}")
    print(f"FAIL: the path self-check failed ({len(problems)} problems)")
    sys.exit(1)
print(f"OK: the path self-check passed ({len(TOOLS)} tools have the correct ROOT, {len(warnings)} warnings)")

# probe: a pure test file only, so the classifier must pick the skip lane
