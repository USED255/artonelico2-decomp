#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路线 B 进度报告：把「已 C 化函数清单」换算成函数数/字节数的匹配率。

数据来源（全部可重新生成，缺任一则打印 SKIP 并退出 0）：
  · routeb/config/matched_symbols.txt   已 C 化函数清单（hybrid 构建的唯一开关）
  · routeb/config/symbol_addrs.txt      全部符号 + 大小（由 tools/build/gen_symbol_addrs.py 生成）
  · out/ghidra/SLUS_217.88.functions.tsv  Ghidra 函数清单（可选，用于交叉核对）

用法：
  python3 tools/report/progress_report.py
  python3 tools/report/progress_report.py --top 15     # 附带「剩余最大的函数」清单
  python3 tools/report/progress_report.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

import argparse as _ap
_ap_pre = _ap.ArgumentParser(add_help=False)
_ap_pre.add_argument("--target", default="jp", choices=["jp", "us"])
_ap_pre.add_argument("--top", type=int, default=0)
_ap_pre.add_argument("--json", action="store_true")
_args, _ = _ap_pre.parse_known_args()
TARGET = _args.target
_PROJ = ROOT / ("routebjp" if TARGET == "jp" else "routeb")
MATCHED = _PROJ / "config" / "matched_symbols.txt"
SYMS = _PROJ / "config" / "symbol_addrs.txt"
TSV = ROOT / "out" / "ghidra" / "SLUS_217.88.functions.tsv"

SYM_RE = re.compile(
    r"^\s*(\S+)\s*=\s*(0x[0-9A-Fa-f]+)\s*;\s*(?://\s*type:(\w+))?"
    r"(?:\s*size:\s*(0x[0-9A-Fa-f]+|\d+))?"
)


def parse_matched(path: Path) -> list[tuple[str, str]]:
    """返回 [(symbol, tag)]；tag = 行尾注释（形状名或 stub_* 类别）。"""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        body = line.split("#", 1)
        sym = body[0].strip()
        if not sym or sym.startswith("#"):
            continue
        tag = body[1].strip().split()[0] if len(body) > 1 and body[1].strip() else ""
        if sym.startswith("#"):
            continue
        out.append((sym, tag))
    return out


def category_of(tag: str) -> str:
    if tag.startswith("stub_"):
        return "桩（内联汇编）"
    if not tag:
        return "无标签（M2 样板等）"
    if tag.startswith("ghidra_draft"):
        return "C 反推（Ghidra 草稿）"
    if tag.startswith("wrapper_"):
        return "C 反推（包装模板）"
    if tag.startswith("permuter"):
        # decomp-permuter 在 Ghidra 近失草稿上收敛出来的结果（口径单列，别混进形状库）
        return "C 反推（permuter 收敛）"
    if tag.startswith("m2c"):
        # m2c 草稿直接一次到位（2026-10-04 起；全量扫描 8,878 个候选命中 247）
        return "C 反推（m2c 草稿）"
    return "C 反推（形状库）"


def parse_symbols(path: Path) -> list[tuple[str, int, str]]:
    """返回 [(name, addr, kind)]，仅在能从注释里解析出 size 时附带。"""
    rows = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SYM_RE.match(line)
        if not m:
            continue
        name, addr, kind = m.group(1), int(m.group(2), 16), m.group(3) or ""
        size = 0
        sm = re.search(r"size:\s*(0x[0-9A-Fa-f]+|\d+)", line)
        if sm:
            tok = sm.group(1)
            size = int(tok, 16) if tok.lower().startswith("0x") else int(tok)
        rows.append((name, size, kind))
    return rows


def main() -> int:
    global MATCHED, SYMS, TARGET
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=TARGET, choices=["jp", "us"], help="jp=日版（主目标，默认）/ us=美版参照")
    ap.add_argument("--top", type=int, default=0, help="附带 N 个剩余最大的函数")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.target != TARGET:
        TARGET = args.target
        _p = ROOT / ("routebjp" if TARGET == "jp" else "routeb")
        MATCHED = _p / "config" / "matched_symbols.txt"
        SYMS = _p / "config" / "symbol_addrs.txt"

    missing = [p for p in (MATCHED, SYMS) if not p.is_file()]
    if missing:
        msg = "SKIP：缺少 " + "、".join(str(p.relative_to(ROOT)) for p in missing) + \
              "（先在 routeb/ 跑一次构建与符号表生成）"
        print(msg if not args.json else json.dumps({"status": "skip", "reason": msg}, ensure_ascii=False))
        return 0

    matched_rows = parse_matched(MATCHED)
    matched = {s for s, _ in matched_rows}
    tags = {s: t for s, t in matched_rows}
    syms = [(n, s, k) for (n, s, k) in parse_symbols(SYMS) if k == "func"]
    if not syms:
        print("SKIP：symbol_addrs.txt 里没有解析到 type:func 条目")
        return 0

    total_n = len(syms)
    total_b = sum(s for _, s, _ in syms)
    m_rows = [r for r in syms if r[0] in matched]
    matched_n = len(m_rows)
    matched_b = sum(s for _, s, _ in m_rows)
    unknown = sorted(matched - {r[0] for r in syms})

    # 分项（C 反推 / 桩 / 无标签）：桩类不得混进「反推 C」的口径
    by_cat: dict[str, list[int]] = {}
    for n, sz, _k in m_rows:
        cat = category_of(tags.get(n, ""))
        by_cat.setdefault(cat, [0, 0])
        by_cat[cat][0] += 1
        by_cat[cat][1] += sz

    pct_n = (100.0 * matched_n / total_n) if total_n else 0.0
    pct_b = (100.0 * matched_b / total_b) if total_b else 0.0

    if args.json:
        print(json.dumps({
            "status": "ok",
            "matched_functions": matched_n, "total_functions": total_n,
            "matched_functions_percent": round(pct_n, 4),
            "matched_bytes": matched_b, "total_bytes": total_b,
            "matched_bytes_percent": round(pct_b, 4),
            "matched_symbols_unknown": unknown,
            "matched_by_category": {k: {"functions": v[0], "bytes": v[1]}
                                    for k, v in sorted(by_cat.items())},
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"== 路线 B 进度（{TARGET.upper()}：已 C 化 / 全量主程序函数）==")
    print(f"  函数： {matched_n:,} / {total_n:,}   （{pct_n:.4f}%）")
    print(f"  字节： {matched_b:,} / {total_b:,}   （{pct_b:.4f}%）")
    print(f"  数据来源：{MATCHED.relative_to(ROOT)} + {SYMS.relative_to(ROOT)}")
    if by_cat:
        print("  分项（口径单列，勿只报合计）：")
        for k in sorted(by_cat):
            print(f"    {k:22s} {by_cat[k][0]:5d} 函数 / {by_cat[k][1]:8,d} B")
    if TSV.is_file():
        tsv_n = sum(1 for _ in TSV.read_text(encoding='utf-8', errors='replace').splitlines()[1:])
        print(f"  交叉核对：Ghidra 函数清单 {tsv_n:,} 条（{TSV.relative_to(ROOT)}）")
    if unknown:
        print(f"  ⚠️ 清单里有 {len(unknown)} 个符号在符号表中找不到：{', '.join(unknown[:8])}"
              + (" …" if len(unknown) > 8 else ""))
    if args.top:
        rest = sorted((r for r in syms if r[0] not in matched), key=lambda r: -r[1])[:args.top]
        print(f"\n  剩余最大的 {len(rest)} 个函数：")
        for n, s, _ in rest:
            print(f"    {n:<28} {s:>6} B")
    print("\n注：这是**静态上界口径**（按符号表字节数），与 objdiff 的实际匹配率不同。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
