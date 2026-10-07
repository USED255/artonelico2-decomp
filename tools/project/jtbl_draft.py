#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""jtbl 池专项工具：真实池画像 / 样本选择 / （Stage 2）草稿生成。

背景（见 `at2/docs/kb/reports/` 与 OPEN-ISSUES O-20）：
  `m3_workqueue.py` 的 `jtbl` 列是**整份 `.s` 文件**判定的（P-32），而公开 `asm/cod/<sym>.s`
  里常含同地址段的**兄弟函数** ⇒ 316 个里 7 个是污染。本工具的判定域是**目标块**
  （`glabel/endlabel <sym>` 之间），得到的才是真池：309 个 / 334,632 B。

三类子问题（决定能不能用「extern 表 + 计算 goto」表达）：
  * `table_in`  ：表项指向的地址落在目标块内 ⇒ 有 case 体要在 C 里保活；
  * `table_out` ：表项指向目标块外（别人的函数/共享尾）⇒ C 不需要表达，表本身仍是原数据；
  * `branch_out`：**条件分支**指向声明范围外 ⇒ 说明 symbol_addrs 的函数边界切短了，
                  C 不可能匹配（不能 goto 外部标签）⇒ 本轮排除。

用法：
  python3 tools/project/jtbl_draft.py stats [--tsv out.tsv]
  python3 tools/project/jtbl_draft.py list [--kind clean|boundary|dispatch] [--limit N]
  python3 tools/project/jtbl_draft.py prepare <sym> [--outdir DIR]   # 目标块 → target.o + skeleton
  python3 tools/project/jtbl_draft.py probe <sym> --dir DIR          # DIR/*.c 逐档打分（Stage 1）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from at2_paths import (  # noqa: E402
    ASMDIR, PRIVATE_ROOT, PROJECT_ROOT as ROOT, WORKQUEUE,
    GCC, AS, OBJDIFF, INCLUDE,
)

DATA_DIR = ROOT / "asm" / "data"
SYMADDRS = ROOT / "config" / "symbol_addrs.txt"
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
_PRIV = Path(PRIVATE_ROOT) if PRIVATE_ROOT else ROOT.parent / "at2"
WORK = Path(os.environ.get("AT2_JTBL_WORK", str(_PRIV / "routebjp" / "build" / "jtbl")))

# 与 auto_match_permuter.py 同口径的档位矩阵（17 档）
FLAG_SETS = [["-Os"], ["-O2"], ["-O1"], ["-O3"], ["-O2", "-G8"], ["-O1", "-G8"], ["-O3", "-G8"],
             ["-Os", "-G8"], ["-O2", "-fno-common"], ["-O2", "-fomit-frame-pointer"],
             ["-O1", "-fomit-frame-pointer"], ["-O2", "-fno-builtin"],
             ["-O2", "-fno-optimize-sibling-calls"], ["-Os", "-fno-optimize-sibling-calls"],
             ["-O1", "-fno-optimize-sibling-calls"], ["-O2", "-mno-split-addresses"]]

BRANCH = re.compile(r"^\s*(?:/\*.*?\*/\s*)?(b\w+|j|jal|jr)\s+(.*)$", re.M)
LABEL = re.compile(r"^(?:glabel|jlabel|alabel)\s+(\S+)\s*$", re.M)
LOCAL = re.compile(r"\.L([0-9A-Fa-f]+)")
HIREF = re.compile(r"jtbl_[0-9A-Fa-f]+")


def block_of(text: str, sym: str) -> str | None:
    """目标块（`glabel/jlabel/alabel <sym>` → `endlabel <sym>`）文本。"""
    m = re.search(
        r"^(?:glabel|jlabel|alabel)\s+%s\b.*?$(.*?)^endlabel\s+%s\b" % (re.escape(sym), re.escape(sym)),
        text, re.M | re.S)
    return m.group(1) if m else None


def load_symbols() -> dict[str, int]:
    sym: dict[str, int] = {}
    for line in SYMADDRS.read_text(errors="replace").splitlines():
        m = re.match(r"(\S+) = (0x[0-9a-fA-F]+);", line)
        if m:
            sym[m.group(1)] = int(m.group(2), 16)
    return sym


_TABLES: dict[str, list[str]] | None = None


def load_tables() -> dict[str, list[str]]:
    """数据段里的 `jtbl_*` 表：{表名: [表项符号名, ...]}（表项名本身带地址后缀）。"""
    global _TABLES
    if _TABLES is not None:
        return _TABLES
    tables: dict[str, list[str]] = {}
    for f in sorted(DATA_DIR.rglob("*.s")):
        txt = f.read_text(errors="replace")
        for m in re.finditer(r"^dlabel (jtbl_[0-9A-Fa-f]+)\n(.*?)^enddlabel", txt, re.M | re.S):
            tables[m.group(1)] = re.findall(r"\.word\s+(\S+)", m.group(2))
    _TABLES = tables
    return tables


def name_to_addr(name: str) -> int | None:
    """`.L001F68B8` / `func_001F68C0` / `baseelf_163` / `D_0096F0C4` → 地址。"""
    m = re.match(r"\.L([0-9A-Fa-f]+)$", name)
    if m:
        return int(m.group(1), 16)
    m = re.match(r"[A-Za-z_][\w]*?_([0-9A-Fa-f]{6,})$", name)
    if m:
        return int(m.group(1), 16)
    return None


def workqueue_rows() -> list[dict]:
    rows = []
    lines = WORKQUEUE.read_text(errors="replace").splitlines()
    head = lines[0].split("\t")
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) != len(head):
            continue
        rows.append(dict(zip(head, p)))
    return rows


def analyze(row: dict, tables: dict[str, list[str]]) -> dict | None:
    sym, addr, size = row["name"], int(row["addr"], 16), int(row["size"])
    f = ASMDIR / ("%s.s" % sym)
    if not f.is_file():
        return None
    blk = block_of(f.read_text(errors="replace"), sym)
    if blk is None or not HIREF.search(blk):
        return None
    tabs = sorted(set(HIREF.findall(blk)))
    in_blk = out_blk = 0
    for t in tabs:
        for e in tables.get(t, []):
            a = name_to_addr(e)
            if a is None:
                continue
            if addr <= a < addr + size:
                in_blk += 1
            else:
                out_blk += 1
    branch_out = []
    for m in BRANCH.finditer(blk):
        if not m.group(1).startswith("b"):
            continue
        for a in LOCAL.findall(m.group(2)):
            if not (addr <= int(a, 16) < addr + size):
                branch_out.append(int(a, 16))
    return {
        "name": sym, "addr": addr, "size": size,
        "tables": tabs, "entries_in": in_blk, "entries_out": out_blk,
        "jal": len(re.findall(r"^\s*(?:/\*.*?\*/\s*)?jal\s", blk, re.M)),
        "branch_out": len(set(branch_out)),
        "labels": len(set(LOCAL.findall(blk))),
        "cls": row.get("class", ""),
    }


def collect() -> list[dict]:
    tables = load_tables()
    recs = []
    for row in workqueue_rows():
        if row.get("jtbl") != "1":
            continue
        r = analyze(row, tables)
        if r:
            recs.append(r)
    return recs


def kind_of(r: dict) -> str:
    if r["branch_out"]:
        return "boundary"
    if r["entries_out"] == 0 and r["entries_in"] > 0:
        return "clean"
    if r["entries_out"] > 0 and r["entries_in"] == 0:
        return "dispatch"
    return "partial"


def cmd_stats(args) -> int:
    recs = collect()
    kinds: dict[str, list[dict]] = {}
    for r in recs:
        kinds.setdefault(kind_of(r), []).append(r)
    total_b = sum(r["size"] for r in recs)
    print("== jtbl 真池（目标块判定，目标块含 `jtbl_` 引用的工作队列行）==")
    print("  函数 %d 个 / %d B" % (len(recs), total_b))
    flagged = sum(1 for row in workqueue_rows() if row.get("jtbl") == "1")
    print("  工作队列整文件标 jtbl %d 个 ⇒ 污染 %d 个（P-32）" % (flagged, flagged - len(recs)))
    for k in ("clean", "partial", "dispatch", "boundary"):
        g = kinds.get(k, [])
        if not g:
            continue
        leaf = sum(1 for r in g if not r["jal"])
        sizes = sorted(r["size"] for r in g)
        print("  %-9s %3d 个 / %7d B   叶子 %2d  尺寸中位 %4d  最大 %6d"
              % (k, len(g), sum(r["size"] for r in g), leaf,
                 sizes[len(sizes) // 2], sizes[-1]))
    both = [r for r in recs if r["entries_in"] and r["entries_out"]]
    print("  表项「部分在外」%d 个；含 jal %d 个；叶子 %d 个"
          % (len(both), sum(1 for r in recs if r["jal"]), sum(1 for r in recs if not r["jal"])))
    if args.tsv:
        p = Path(args.tsv)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            fh.write("name\taddr\tsize\tkind\tjal\tentries_in\tentries_out\tbranch_out\tlabels\ttables\tclass\n")
            for r in sorted(recs, key=lambda x: x["addr"]):
                fh.write("%s\t0x%08x\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n"
                         % (r["name"], r["addr"], r["size"], kind_of(r), r["jal"], r["entries_in"],
                            r["entries_out"], r["branch_out"], r["labels"],
                            ",".join(r["tables"]), r["cls"]))
        print("  落盘：%s" % p)
    return 0


def cmd_list(args) -> int:
    recs = [r for r in collect() if (not args.kind or kind_of(r) == args.kind)]
    recs.sort(key=lambda r: (r["size"], r["addr"]))
    for r in recs[: args.limit or 20]:
        print("%-16s 0x%08x %5d  kind=%-9s jal=%-2d in=%-3d out=%-3d lab=%-3d %s"
              % (r["name"], r["addr"], r["size"], kind_of(r), r["jal"],
                 r["entries_in"], r["entries_out"], r["labels"], ",".join(r["tables"])))
    return 0


# --------------------------------------------------------------------------- Stage 1 探针

def _workdir(sym: str) -> Path:
    return WORK / sym


def _target_block(sym: str) -> str | None:
    f = ASMDIR / ("%s.s" % sym)
    if not f.is_file():
        return None
    blk = block_of(f.read_text(errors="replace"), sym)
    if blk is None:
        return None
    return "glabel %s\n%s\nendlabel %s\n" % (sym, blk.rstrip("\n"), sym)


def _build_target(sym: str, d: Path) -> bool:
    d.mkdir(parents=True, exist_ok=True)
    ts, to = d / "target.s", d / "target.o"
    ts.write_text(PREAMBLE + _target_block(sym), encoding="utf-8")
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(to), str(ts)],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        print("  [FAIL] 目标块汇编失败：%s" % r.stderr.strip()[:400], file=sys.stderr)
        return False
    return True


def _score(sym: str, src: Path, d: Path, flags: list[str]) -> float | None:
    o = d / "cand.o"
    r = subprocess.run([GCC, *flags, "-falign-functions=4", "-ffunction-sections",
                        "-I", str(INCLUDE), "-c", "-o", str(o), str(src)],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        (d / "compile.err").write_text(r.stderr[-4000:], encoding="utf-8")
        return None
    tj = d / "score.json"
    r = subprocess.run([OBJDIFF, "diff", "-1", str(d / "target.o"), "-2", str(o),
                        "-o", str(tj), "--format", "json"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    try:
        data = json.loads(tj.read_text(encoding="utf-8"))
    except Exception:
        return None
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    m = per.get(sym)
    return float(m) if m is not None else None


def cmd_prepare(args) -> int:
    sym = args.sym
    d = Path(args.outdir) if args.outdir else _workdir(sym)
    if not _build_target(sym, d):
        return 1
    blk = _target_block(sym) or ""
    body = "\n".join("    /* %s */" % l.strip() for l in blk.splitlines()
                     if re.search(r"/\*\s*[0-9A-Fa-f]{4,}", l))
    rec = next((r for r in collect() if r["name"] == sym), None)
    print("== %s ==" % sym)
    if rec:
        print("  addr=0x%08x size=%d kind=%s jal=%d entries_in=%d entries_out=%d branch_out=%d"
              % (rec["addr"], rec["size"], kind_of(rec), rec["jal"], rec["entries_in"],
                 rec["entries_out"], rec["branch_out"]))
        for t in rec["tables"]:
            ents = load_tables().get(t, [])
            print("  表 %s：%d 项" % (t, len(ents)))
            print("    " + " ".join(ents[:24]) + (" ..." if len(ents) > 24 else ""))
    (d / "asm.txt").write_text(blk, encoding="utf-8")
    print("  target.o=%s" % (d / "target.o"))
    print("  目标块已写 %s" % (d / "asm.txt"))
    return 0


def cmd_probe(args) -> int:
    sym = args.sym
    d = Path(args.dir) if args.dir else _workdir(sym)
    if not (d / "target.o").is_file() and not _build_target(sym, d):
        return 1
    cands = sorted(Path(args.dir).glob("*.c")) if args.dir else sorted(d.glob("*.c"))
    if not cands:
        print("没有候选 .c（先写一个到 %s）" % d, file=sys.stderr)
        return 2
    rows = []
    for c in cands:
        if c.name in ("base.c", "score.c"):
            continue
        best, bestf, ok = -1.0, "", False
        per_flag = []
        for fs in FLAG_SETS:
            m = _score(sym, c, d, fs)
            per_flag.append((m, " ".join(fs)))
            if m is not None:
                ok = True
                if m > best:
                    best, bestf = m, " ".join(fs)
            if best >= 100.0:
                break
        rows.append((best, c.name, bestf, ok))
        if args.all:
            print("  -- %s" % c.name)
            for m, f in per_flag:
                print("     %7s  %s" % ("%.2f" % m if m is not None else "编译失败", f))
    rows.sort(reverse=True)
    print("== probe %s（%d 个候选 × %d 档）==" % (sym, len(rows), len(FLAG_SETS)))
    for m, name, f, ok in rows:
        print("  %7.2f%%  %-24s %-32s %s" % (m if ok else -1, name, f, "" if ok else "(编译失败)"))
    return 0



def main() -> int:
    ap = argparse.ArgumentParser(description="jtbl 池专项工具")
    sub = ap.add_subparsers(dest="mode", required=True)
    s = sub.add_parser("stats", help="真池画像（可选落 TSV）")
    s.add_argument("--tsv", default="")
    s.set_defaults(func=cmd_stats)
    l = sub.add_parser("list", help="列样本")
    l.add_argument("--kind", default="clean", choices=["", "clean", "partial", "dispatch", "boundary"])
    l.add_argument("--limit", type=int, default=20)
    l.set_defaults(func=cmd_list)
    p = sub.add_parser("prepare", help="目标块 → target.o（探针用）")
    p.add_argument("sym")
    p.add_argument("--outdir", default="")
    p.set_defaults(func=cmd_prepare)
    r = sub.add_parser("probe", help="对目录里的候选 .c 逐档打分")
    r.add_argument("sym")
    r.add_argument("--dir", default="")
    r.add_argument("--all", action="store_true", help="打印每个档位的分数")
    r.set_defaults(func=cmd_probe)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
