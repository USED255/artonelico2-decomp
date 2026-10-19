#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report the static progress upper bound from the symbol table.

This tool needs no toolchain. It reads two public files:
  * `config/matched_symbols.txt` -- the matched-function ledger (the mixed build switch);
  * `config/symbol_addrs.txt`    -- every symbol with its size.

The tool counts the matched functions and their bytes, and compares them with the
full function set. The result is a static upper bound by symbol-table bytes. The
published numbers come from `progress/SLPS_258.19_report.json`, which a verified
objdiff run writes. The functions agree with the published report. The byte
denominator can differ by a small amount, because objdiff counts code sections.

The cross-check with the private Ghidra list is optional. The tool prints the
cross-check line only when the TSV file exists.

Usage:
  python3 tools/report/progress_report.py
  python3 tools/report/progress_report.py --top 15
  python3 tools/report/progress_report.py --json

Exit code is 0 when a data file is absent. The tool then prints `SKIP: ...`.

静态进度上界报告（按符号表字节数），不需要工具链。

本工具只读两个公开文件：`config/matched_symbols.txt`（已 C 化函数台账，也是混合构建开关）
与 `config/symbol_addrs.txt`（全部符号及其大小）。它统计已匹配的函数数与字节数，再与函数
全集比较；这是**静态上界口径**，发布的数字来自一次已验证 objdiff 运行写出的
`progress/SLPS_258.19_report.json`。函数数与发布报告一致；字节分母可能有小差异，因为 objdiff
只统计代码段。与私有 Ghidra 清单的交叉核对是可选项：只有 TSV 文件存在时才打印该行。

数据文件缺失时退出码为 0，并打印 `SKIP: ...`（与旧工具一致）。

用法见上。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Make the shared path helper importable.  让共享路径助手可被导入。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "project"))
from at2_paths import (  # noqa: E402  layout-independent path resolution (see the top of at2_paths.py)
    MATCHED_LIST,
    PRIVATE_ROOT,
    PROJECT_ROOT as ROOT,
    SYMBOL_ADDRS,
)

# The first output line must state the scope.  首行必须声明口径。
SCOPE = (
    "Static upper bound by symbol-table bytes. "
    "The published numbers come from progress/SLPS_258.19_report.json."
)

# A symbol line looks like: `name = 0x0010001c; // type:func size:0x240`.
# 符号行形如：`name = 0x0010001c; // type:func size:0x240`。
SYM_RE = re.compile(
    r"^\s*(\S+)\s*=\s*(0x[0-9A-Fa-f]+)\s*;\s*(?://\s*type:(\w+))?"
    r"(?:\s*size:\s*(0x[0-9A-Fa-f]+|\d+))?"
)
SIZE_RE = re.compile(r"size:\s*(0x[0-9A-Fa-f]+|\d+)")

# The Ghidra function list is private input. Try each candidate.  私有输入，逐个候选尝试。
GHIDRA_TSV_CANDIDATES = [
    ROOT / "out" / "ghidra" / "SLUS_217.88.functions.tsv",
    *([PRIVATE_ROOT / "out" / "ghidra" / "SLUS_217.88.functions.tsv"] if PRIVATE_ROOT else []),
]


def parse_matched(path: Path) -> list[tuple[str, str]]:
    """Return [(symbol, tag)]. The tag is the first word of the trailing comment.

    A blank line and a comment line are skipped.

    返回 [(符号, tag)]；tag = 行尾注释的第一个词。空行与 `#` 注释行跳过。
    """
    if not path.is_file():
        return []
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        code, _sep, comment = line.partition("#")
        sym = code.strip()
        if not sym:
            continue
        body = comment.strip()
        tag = body.split()[0] if body else ""
        rows.append((sym, tag))
    return rows


def parse_symbols(path: Path) -> list[tuple[str, int, int, str]]:
    """Return [(name, addr, size, kind)]. The size is 0 when the line has no size.

    返回 [(名字, 地址, 大小, 类别)]；行里没有 `size:` 时大小为 0。
    """
    rows: list[tuple[str, int, int, str]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SYM_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        addr = int(m.group(2), 16)
        kind = m.group(3) or ""
        size = 0
        sm = SIZE_RE.search(line)
        if sm:
            tok = sm.group(1)
            size = int(tok, 16) if tok.lower().startswith("0x") else int(tok)
        rows.append((name, addr, size, kind))
    return rows


def category_of(tag: str) -> str:
    """Map a ledger tag to one report category. Keep each category separate.

    把台账 tag 映射到一个报告分类；各分类单列，不要只报合计。
    """
    if tag.startswith(("transcription_", "mmi_asm")):
        return "asm transcription (no reconstructed C; separate metric)"
    if tag.startswith("stub_"):
        return "hand-written stub (inline assembly)"
    if not tag:
        return "untagged (build boilerplate)"
    if tag.startswith("ghidra_draft"):
        return "C reverse-engineering (Ghidra draft)"
    if tag.startswith("wrapper_"):
        return "C reverse-engineering (wrapper template)"
    if tag.startswith("permuter"):
        return "C reverse-engineering (permuter convergence)"
    if tag.startswith("m2c"):
        return "C reverse-engineering (m2c draft)"
    return "C reverse-engineering (shape library)"


def find_ghidra_tsv() -> Path | None:
    """Return the first Ghidra TSV that exists, or None.  返回第一个存在的清单，没有则 None。"""
    for cand in GHIDRA_TSV_CANDIDATES:
        try:
            if cand.is_file():
                return cand
        except OSError:
            continue
    return None


def display_path(path: Path) -> str:
    """Show a path under the project root or the private root. 显示项目根或私有根下的相对路径。"""
    for base in (ROOT, PRIVATE_ROOT):
        if base is None:
            continue
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return path.name


def main() -> int:
    ap = argparse.ArgumentParser(description="Report the static progress upper bound from the symbol table.")
    ap.add_argument("--top", type=int, default=0, help="list the N largest functions that remain unmatched")
    ap.add_argument("--json", action="store_true", help="write one JSON object")
    args = ap.parse_args()

    missing = [p for p in (MATCHED_LIST, SYMBOL_ADDRS) if not p.is_file()]
    if missing:
        reason = "SKIP: missing " + ", ".join(str(p) for p in missing)
        print(reason if not args.json else json.dumps({"status": "skip", "reason": reason}, indent=2))
        return 0

    matched_rows = parse_matched(MATCHED_LIST)
    matched = {s for s, _ in matched_rows}
    tags = {s: t for s, t in matched_rows}
    syms = [r for r in parse_symbols(SYMBOL_ADDRS) if r[3] == "func"]
    if not syms:
        reason = "SKIP: config/symbol_addrs.txt holds no type:func entry"
        print(reason if not args.json else json.dumps({"status": "skip", "reason": reason}, indent=2))
        return 0

    total_n = len(syms)
    total_b = sum(r[2] for r in syms)
    all_rows = [r for r in syms if r[0] in matched]
    # The main progress counts reconstructed C only. Assembly transcriptions are a SEPARATE
    # metric (see config/transcription_symbols.txt) and must not inflate the headline.
    # 主进度只计重建的 C；汇编转录是**独立口径**（见 config/transcription_symbols.txt），不得灌进主数字。
    m_rows = [r for r in all_rows
              if not category_of(tags.get(r[0], "")).startswith("asm transcription")]
    matched_n = len(m_rows)
    matched_b = sum(r[2] for r in m_rows)
    unknown = sorted(matched - {r[0] for r in syms})

    # Subtotals by category. A stub must not count as reverse-engineered C.
    # 按分类小计；桩类不得混进「反推 C」的口径。
    by_cat: dict[str, list[int]] = {}
    for name, _addr, size, _kind in all_rows:
        cat = category_of(tags.get(name, ""))
        by_cat.setdefault(cat, [0, 0])
        by_cat[cat][0] += 1
        by_cat[cat][1] += size

    pct_n = (100.0 * matched_n / total_n) if total_n else 0.0
    pct_b = (100.0 * matched_b / total_b) if total_b else 0.0

    if args.json:
        print(json.dumps({
            "scope": SCOPE,
            "status": "ok",
            "matched_functions": matched_n,
            "total_functions": total_n,
            "matched_functions_percent": round(pct_n, 4),
            "matched_bytes": matched_b,
            "total_bytes": total_b,
            "matched_bytes_percent": round(pct_b, 4),
            "matched_symbols_unknown": unknown,
            "matched_by_category": {
                k: {"functions": v[0], "bytes": v[1]} for k, v in sorted(by_cat.items())
            },
        }, indent=2))
        return 0

    print(SCOPE)
    print()
    print("Main metric = reconstructed C only; asm transcriptions are reported separately below.")
    print(f"Matched functions: {matched_n:,} of {total_n:,} ({pct_n:.4f} percent)")
    print(f"Matched bytes:     {matched_b:,} of {total_b:,} ({pct_b:.4f} percent)")
    print(f"Data source:       {MATCHED_LIST.relative_to(ROOT)} and {SYMBOL_ADDRS.relative_to(ROOT)}")
    if by_cat:
        print()
        print("Subtotals by category. Report each part separately.")
        for key in sorted(by_cat):
            print(f"  {key:46s} {by_cat[key][0]:5d} functions / {by_cat[key][1]:9,d} B")
    tsv = find_ghidra_tsv()
    if tsv is not None:
        try:
            tsv_n = sum(1 for _ in tsv.read_text(encoding="utf-8", errors="replace").splitlines()[1:])
        except OSError:
            tsv_n = 0
        print(f"\nCross-check: the Ghidra function list holds {tsv_n:,} lines ({display_path(tsv)}).")
    if unknown:
        head = ", ".join(unknown[:8]) + (" ..." if len(unknown) > 8 else "")
        print(f"\nWARNING: {len(unknown)} ledger symbols are absent from the symbol table: {head}")
    if args.top:
        rest = sorted((r for r in syms if r[0] not in matched), key=lambda r: -r[2])[:args.top]
        print(f"\nThe {len(rest)} largest functions that remain unmatched:")
        for name, _addr, size, _kind in rest:
            print(f"  {name:<32} {size:>7} B")
    print("\nThis count is a static upper bound by symbol-table bytes. The objdiff report is the published measure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
