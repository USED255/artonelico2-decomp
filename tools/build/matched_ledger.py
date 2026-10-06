#!/usr/bin/env python3
"""`config/matched_symbols.txt` 的**唯一解析实现**（报告生成器与增量检查共用）。

台账格式（见文件头部注释）：
    <symbol> [<source-basename>]        # <tag>          ← `#` 起行内注释；第二列可省略
  · 省略第二列时，源文件基名 = 符号名；
  · 一个源文件可以提供多个符号（同一 .c 里多个函数已在台账登记）。

2026-10-06 修复：此前增量检查把**整行**（含注释与第二列）当成符号名，导致带注释的台账行
一律匹配不上，`make delta` 会把绝大多数函数跳过却仍报「全部 100%」。
"""
from __future__ import annotations
from pathlib import Path

STUB_PREFIX = "stub_"


def parse_ledger(path: Path) -> dict[str, tuple[str, str]]:
    """→ `{symbol: (source_basename, tag)}`；tag = 行内注释去掉 `#` 后的原文（已 strip）。"""
    out: dict[str, tuple[str, str]] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        body, _, comment = raw.partition("#")
        body = body.strip()
        if not body:
            continue
        parts = body.split()
        sym = parts[0]
        src = parts[1] if len(parts) > 1 else sym
        out[sym] = (src, comment.strip())
    return out


def entry_stats(path: Path) -> tuple[int, int, int]:
    """条目级统计：`(总条目, stub 条目, 去重后的非 stub 符号数)`。"""
    total = stub = 0
    non_stub: set[str] = set()
    if not path.exists():
        return 0, 0, 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        body, _, comment = raw.partition("#")
        body = body.strip()
        if not body:
            continue
        total += 1
        if comment.strip().startswith(STUB_PREFIX):
            stub += 1
        else:
            non_stub.add(body.split()[0])
    return total, stub, len(non_stub)


def by_source(index: dict[str, tuple[str, str]]) -> dict[str, set[str]]:
    """源文件基名 → 该源提供的全部符号（一个源可以多个符号）。"""
    out: dict[str, set[str]] = {}
    for sym, (src, _tag) in index.items():
        out.setdefault(src, set()).add(sym)
    return out


def resolve_changed(index: dict[str, tuple[str, str]], changed_files: list[str],
                    path_prefix: str = "") -> tuple[set[str], list[str]]:
    """把「改动过的匹配源文件」映射成「需要逐一比对的符号」。

    · 匹配规则：`<sym>.c` 命中符号名，或命中台账第二列的源基名（两者可能不同）；
    · 未登记的新文件（既不是符号名也不是源名）→ 返回在 unregistered 里，**由调用方显式计数**。
    """
    srcs = by_source(index)
    hit: set[str] = set()
    unregistered: list[str] = []
    for rel in changed_files:
        stem = Path(rel).stem
        found = set()
        if stem in index:
            found.add(stem)
        found |= srcs.get(stem, set())
        if found:
            hit |= found
        else:
            unregistered.append(rel)
    return hit, unregistered
