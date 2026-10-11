#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目路径解析 —— **布局无关**（私有 `routebjp/` 布局与公开扁平布局都能用）。

## 为什么需要这个模块

工具原先住在 `routebjp/tools/`，用 `Path(__file__).resolve().parent.parent` 当项目根；
2026-10-05 工作区重构后它们搬到 `tools/project/`，同样写法就**少了一级**（解析成 `tools/`），
于是 `auto_match_*` 等批量工具集体失效（找不到 `config/matched_symbols.txt`）。

同时重构把数据分成了两类，解析规则也不同：

| 类别 | 现在在哪 | 用途 |
| --- | --- | --- |
| 源码 / 配置 / 汇编树 / include | **项目根**（公开仓库） | `config/matched_symbols.txt`、`src/matched/`、`asm/cod/`、`include/` |
| 证据 / 批量工作状态 | **私有仓库** | `out/evidence/jp_m3_workqueue.tsv`、`routebjp/build/{m2c,m2,screen}` |

## 解析顺序（都可用环境变量强制覆盖）

* `AT2_PROJECT_ROOT` —— 项目根：默认从本文件向上找同时含 `config/matched_symbols.txt` /
  `splat.yaml` / `asm/cod` 的目录。
* `AT2_EVIDENCE_ROOT` —— 证据目录：`<项目根>/out/evidence` → `<项目根>/../at2/out/evidence`。
* `AT2_WORK_ROOT` —— 批量工作目录：`<项目根>/routebjp/build` → `<项目根>/../at2/routebjp/build`
  → `<项目根>/build`。
* `AT2_PRIVATE_ROOT` —— 私有仓库根：默认沿项目根的祖先逐级找 `<祖先>/at2`（要求含 `routebjp/` 或 `out/`）。

自检：`python3 tools/project/at2_paths.py`
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

MARKERS = ("config/matched_symbols.txt", "splat.yaml", "asm/cod")


def _find_project_root(start: Path) -> Path:
    for cand in [start] + list(start.parents):
        for m in MARKERS:
            if (cand / m).exists():
                return cand
    return start.parent


def _first_existing(*cands: Path) -> Path | None:
    for c in cands:
        try:
            if c.exists():
                return c
        except OSError:
            continue
    return None


def _find_private_root(project_root: Path) -> Path | None:
    """定位私有仓库根（受限材料与工作状态）。

    不能只试 `<项目根>/../at2`：任务工作树位于 `<工作区>/worktrees/<repo>-<slug>`，
    它的上一级是 `worktrees/` 而不是工作区根，于是私有根解析失败、证据目录落到工作树里
    （2026-10-06 实测：工作树 `make check` 因此多 1 条 warn，主检出 0 条）。

    这里沿祖先逐级试 `<祖先>/at2`，并要求它**看起来像**私有仓库（有 `routebjp/` 或 `out/`），
    避免把任意同名目录当私有根。
    """
    for anc in [project_root, *project_root.parents]:
        cand = anc / "at2"
        try:
            if cand.is_dir() and ((cand / "routebjp").is_dir() or (cand / "out").is_dir()):
                return cand
        except OSError:
            continue
    return None


_HERE = Path(__file__).resolve().parent

# ---- 项目根（源码/配置/汇编树/include）----
_env_proj = os.environ.get("AT2_PROJECT_ROOT")
PROJECT_ROOT: Path = Path(_env_proj).resolve() if _env_proj else _find_project_root(_HERE)

# ---- 私有仓库根（受限材料与工作状态）----
_env_priv = os.environ.get("AT2_PRIVATE_ROOT")
PRIVATE_ROOT: Path | None = (
    Path(_env_priv).resolve() if _env_priv else _find_private_root(PROJECT_ROOT)
)

# ---- 证据目录（工作队列、难度画像等派生证据）----
_env_ev = os.environ.get("AT2_EVIDENCE_ROOT")
EVIDENCE_ROOT: Path = (
    Path(_env_ev).resolve()
    if _env_ev
    else (
        _first_existing(
            PROJECT_ROOT / "out" / "evidence",
            *([PRIVATE_ROOT / "out" / "evidence"] if PRIVATE_ROOT else []),
        )
        or (PROJECT_ROOT / "out" / "evidence")
    )
)

# ---- 批量工作目录（m2c 评分池 / permuter 工作区 / 筛查结果）----
_env_work = os.environ.get("AT2_WORK_ROOT")
WORK_ROOT: Path = (
    Path(_env_work).resolve()
    if _env_work
    else (
        _first_existing(
            PROJECT_ROOT / "routebjp" / "build",
            *([PRIVATE_ROOT / "routebjp" / "build"] if PRIVATE_ROOT else []),
            PROJECT_ROOT / "build",
        )
        or (PROJECT_ROOT / "build")
    )
)

# ---- 汇编树（splat 产物；公开克隆里 `make split` 后才有）----
ASMDIR: Path = (
    _first_existing(
        PROJECT_ROOT / "asm" / "cod",
        *([PRIVATE_ROOT / "routebjp" / "asm" / "cod"] if PRIVATE_ROOT else []),
    )
    or (PROJECT_ROOT / "asm" / "cod")
)

# ---- 常用固定路径 ----
MATCHED_LIST: Path = PROJECT_ROOT / "config" / "matched_symbols.txt"
SRCDIR: Path = PROJECT_ROOT / "src" / "matched"
FLAGS_TSV: Path = PROJECT_ROOT / "config" / "source_flags.tsv"
WORKQUEUE: Path = EVIDENCE_ROOT / "jp_m3_workqueue.tsv"
INCLUDE: Path = PROJECT_ROOT / "include"

# ---- 工具链（可用环境变量覆盖）----
GCC: str = os.environ.get("GCC", os.path.expanduser("~/eecc/ee-gcc3.2-040921/bin/ee-gcc"))
BINUTILS: str = os.environ.get("BINUTILS", os.path.expanduser("~/eecc/ps2binutils"))
AS: str = os.environ.get("AS", os.path.join(BINUTILS, "mips-ps2-decompals-as"))
OBJDUMP: str = os.environ.get("OBJDUMP", os.path.join(BINUTILS, "mips-ps2-decompals-objdump"))
OBJDIFF: str = os.environ.get("OBJDIFF", os.path.expanduser("~/eecc/objdiff-cli"))
# 与 build_hybrid.sh 的 MATCHED_CFLAGS 完全一致：只有在这里 100% 的才会在混合构建里 100%
CFLAGS = ["-O2", "-falign-functions=4", "-ffunction-sections"]


def summary() -> str:
    """一行一项地报告解析结果与存在性（排查路径问题用）。"""
    rows = [
        ("PROJECT_ROOT", PROJECT_ROOT),
        ("PRIVATE_ROOT", PRIVATE_ROOT),
        ("EVIDENCE_ROOT", EVIDENCE_ROOT),
        ("WORK_ROOT", WORK_ROOT),
        ("MATCHED_LIST", MATCHED_LIST),
        ("SRCDIR", SRCDIR),
        ("FLAGS_TSV", FLAGS_TSV),
        ("ASMDIR", ASMDIR),
        ("WORKQUEUE", WORKQUEUE),
        ("INCLUDE", INCLUDE),
    ]
    out = []
    for name, p in rows:
        if p is None:
            out.append(f"  {name:15s} (未找到)")
        else:
            out.append(f"  {name:15s} {'✓' if p.exists() else '✗'} {p}")
    return "\n".join(out)


if __name__ == "__main__":
    print("at2_paths 解析结果：")
    print(summary())
    missing = [n for n, p in [("MATCHED_LIST", MATCHED_LIST), ("WORKQUEUE", WORKQUEUE)] if not p.exists()]
    if missing:
        print("\n⚠️ 缺失：", ", ".join(missing), "（检查 AT2_PROJECT_ROOT / AT2_EVIDENCE_ROOT）", file=sys.stderr)
        sys.exit(1)
    print("\n✅ 关键路径齐备")
