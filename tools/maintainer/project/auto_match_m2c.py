#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch match of m2c drafts: send the C output of m2c directly to objdiff and keep the symbols at 100% (without the permuter).

Background (2026-10-04, measured): m2c often succeeds on the first try for a **small
function**. Of the 40 smallest class E candidates of the JP version, the m2c draft gives
**8 at objdiff 100%** and 22 at 80% or more. The m2c tool is therefore not only a front end
for the permuter. It is an **independent collector**.

Usage:
  python3 tools/maintainer/project/auto_match_m2c.py run  [--classes E_branch_only,...] [--limit N] [--jobs 4]
  python3 tools/maintainer/project/auto_match_m2c.py apply-only

m2c 草稿批量匹配：m2c 生成的 C 直接过 objdiff，收 100% 的符号（不经 permuter）。

背景（2026-10-04 `[实测]`）：m2c 在**小函数**上常常一次到位——
日版 E 类最小的 40 个候选里，m2c 草稿直接 **8 个 objdiff 100%**、22 个 ≥80%。
因此 m2c 不只是 permuter 的前端，本身就是**独立收割器**。

用法：
  python3 tools/maintainer/project/auto_match_m2c.py run  [--classes E_branch_only,...] [--limit N] [--jobs 4]
  python3 tools/maintainer/project/auto_match_m2c.py apply-only
"""

# Private layout names (routebjp/build/m2c, jp_m3_workqueue.tsv), do not rename.  私有布局名（routebjp/build/m2c、jp_m3_workqueue.tsv），勿改名。

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m2c_draft as M2C  # noqa: E402

# Make the shared tools in tools/project importable.  让 tools/project 的共享工具可被导入。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project"))
from at2_paths import (  # noqa: E402  layout-independent path resolution (see the top of at2_paths.py)
    PROJECT_ROOT as ROOT,
    PRIVATE_ROOT,
    EVIDENCE_ROOT,
    WORK_ROOT,
    MATCHED_LIST,
    SRCDIR,
    FLAGS_TSV,
    ASMDIR,
    WORKQUEUE,
    GCC,
    AS,
    OBJDIFF,
)

REPO = PRIVATE_ROOT or ROOT          # Legacy alias: the private work area
CFLAGS = ["-O2", "-falign-functions=4", "-ffunction-sections"]
OUT = WORK_ROOT / "m2c" / "batch"
MATCHED = MATCHED_LIST
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
SKIP = {"no_asm", "unknown"}


def unmatched() -> list[dict]:
    have = set()
    for line in MATCHED.read_text(encoding="utf-8").splitlines():
        a = line.split("#", 1)[0].strip()
        if a:
            have.add(a.split()[0])
    rows = []
    for line in WORKQUEUE.read_text(encoding="utf-8").splitlines()[1:]:
        p = line.split("\t")
        if len(p) > 12 and p[0] not in have:
            # The gate column (index 11) holds direct/residual (safe to split) or
            # blocked_* (**no safe split**, so the code cannot add the symbol to the list).
            # gate 列（index 11）：取值 direct/residual（可拆）或 blocked_*（**无法安全拆分**，不能进清单）
            if p[11].strip().startswith("blocked"):
                continue
            rows.append({"sym": p[0], "size": int(p[2]), "class": p[12]})
    return rows


def probe(rec: dict, flags_sets: list[list[str]]) -> dict:
    sym = rec["sym"]
    d = OUT / sym
    d.mkdir(parents=True, exist_ok=True)
    out = {"sym": sym, "class": rec["class"], "size": rec["size"], "match": None, "flags": None, "err": None}
    src = M2C.emit(sym, d)
    if src is None:
        out["err"] = "m2c failed"
        return out
    f = ROOT / "asm" / "cod" / f"{sym}.s"
    L = f.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next((i for i, l in enumerate(L) if re.match(r"\s*glabel\s+", l)), None)
    en = next((i for i in range(gi or 0, len(L)) if re.match(r"\s*endlabel\s+", L[i])), None)
    if gi is None or en is None:
        out["err"] = "no glabel/endlabel"
        return out
    (d / "target.s").write_text(PREAMBLE + "\n".join(L[gi:en + 1]) + "\n", encoding="utf-8")
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(d / "target.o"), str(d / "target.s")],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        out["err"] = "target assembly failed"
        return out
    for fs in flags_sets:
        o = d / "cand.o"
        r = subprocess.run([GCC, *CFLAGS, *fs, "-I", "include", "-c", "-o", str(o), str(src)],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode:
            out["err"] = "compile failed"
            continue
        j = d / "diff.json"
        r = subprocess.run([OBJDIFF, "diff", "-1", str(d / "target.o"), "-2", str(o), "-o", str(j), "--format", "json"],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode:
            out["err"] = "objdiff failed"
            continue
        try:
            data = json.loads(j.read_text(encoding="utf-8"))
        except Exception:
            out["err"] = "objdiff output is not valid"
            continue
        per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
               if s.get("kind") == "SYMBOL_FUNCTION"}
        m = per.get(sym)
        if m is None:
            out["err"] = "symbol not found"
            continue
        if out["match"] is None or m > out["match"]:
            out["match"] = float(m)
            out["flags"] = " ".join(fs)
        if m == 100.0:
            break
    return out


def apply(results: list[dict]) -> None:
    win = [r for r in results if r.get("match") == 100.0]
    SRCDIR.mkdir(parents=True, exist_ok=True)
    fmap: dict[str, str] = {}
    if FLAGS_TSV.is_file():
        # Line 1 is the header row (source-basename<TAB>extra-cflags). Skip it, or the key
        # source-basename becomes a false entry.
        # 第 1 行是表头（source-basename<TAB>extra-cflags），跳过；否则会写入伪键 source-basename。
        for line in FLAGS_TSV.read_text(encoding="utf-8").splitlines()[1:]:
            p = line.split("\t")
            if len(p) >= 2:
                fmap[p[0]] = p[1]
    for r in win:
        sym = r["sym"]
        shutil.copyfile(OUT / sym / f"{sym}.m2c.c", SRCDIR / f"{sym}.c")
        if r.get("flags"):
            # The key must agree with the query key of build_mixed.sh: the second list
            # column (the symbol name by default, **without .c**). The form `<sym>.c` would
            # make this flag entry useless (measured on 2026-10-04, P-34).
            # ⚠️ 键必须与 build_mixed.sh 的查询键一致：清单第二列（默认 = 符号名，**不带 .c**）。
            #    写 `<sym>.c` 会让该条标志永不生效（2026-10-04 实测，P-34）。
            fmap[sym] = r["flags"]
    FLAGS_TSV.parent.mkdir(parents=True, exist_ok=True)
    # Write the frozen header row first. This tool rewrites the whole file, so without the
    # header row one apply would erase it.
    # 先写冻结的表头行。本工具整份重写该文件；不写表头就会被一次 apply 抹掉。
    lines = ["source-basename\textra-cflags"] + ["\t".join(kv) for kv in sorted(fmap.items())]
    FLAGS_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    add = {r["sym"] for r in win}
    lines = MATCHED.read_text(encoding="utf-8").splitlines()
    kept = [l for l in lines if l.split("#", 1)[0].strip().split(" ")[0] not in add]
    kept += [f"{s}    # m2c_draft" for s in sorted(add)]
    MATCHED.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"apply: wrote {len(win)} C sources; list {len(lines)} -> {len(kept)}; flag table {len(fmap)} entries")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "apply-only"])
    ap.add_argument("--classes", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--symbols-file", default="")
    # 2026-10-04: earlier tests used only the O2 and O2 -G8 flag levels for the compile axis
    # (the second level never won). Measurement shows that -O1 brings some functions from 75%
    # directly to 100%. The default therefore uses more flag levels and takes the best score
    # of each level. It stops on a 100% hit.
    # 2026-10-04：编译档轴此前只试过 O2 与 O2 -G8（第二档从未赢过）。实测 -O1 能让部分函数从 75% 直接到 100%，
    # 因此默认扩到 5 档，取各档中最高分（命中 100% 即停）。
    ap.add_argument("--flags", default="Os,O2,O1,O3,O2 -G8,O1 -G8,O3 -G8,O2 -fno-common,O2 -fomit-frame-pointer,O1 -fomit-frame-pointer,O2 -fno-builtin,O2 -fno-optimize-sibling-calls,Os -fno-optimize-sibling-calls,O1 -fno-optimize-sibling-calls,O2 -mno-split-addresses,Os -mno-split-addresses")
    a = ap.parse_args()

    if a.mode == "apply-only":
        data = json.loads((OUT / "result.json").read_text(encoding="utf-8"))
        apply(data)
        return 0

    rows = unmatched()
    if a.classes:
        want = set(a.classes.split(","))
        rows = [r for r in rows if r["class"] in want]
    else:
        rows = [r for r in rows if r["class"] not in SKIP]
    if a.symbols_file:
        want = [l.strip() for l in Path(a.symbols_file).read_text(encoding="utf-8").splitlines() if l.strip()]
        by = {r["sym"]: r for r in rows}
        rows = [by[s] for s in want if s in by]
    rows.sort(key=lambda r: r["size"])
    if a.limit:
        rows = rows[:a.limit]
    flags_sets = []
    for item in a.flags.split(","):
        item = item.strip()
        flags_sets.append([] if not item else [t if t.startswith("-") else "-" + t for t in item.split()])
    print(f"== m2c draft batch: {len(rows)} candidates (flag levels {a.flags}, parallel {a.jobs}) ==")
    OUT.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for i, res in enumerate(pool.map(lambda r: probe(r, flags_sets), rows), 1):
            results.append(res)
            if i % 200 == 0 or i == len(rows):
                ok = sum(1 for x in results if x.get("match") == 100.0)
                print(f"   ... {i}/{len(rows)} (100% = {ok})")
    # Merge the results by symbol, so a partial rescan cannot overwrite the full pool
    # 结果**合并**（按符号），避免局部重扫把全量池覆盖掉
    merged: dict[str, dict] = {}
    rj = OUT / "result.json"
    if rj.is_file():
        try:
            for r in json.loads(rj.read_text(encoding="utf-8")):
                merged[r["sym"]] = r
        except Exception:
            pass
    for r in results:
        merged[r["sym"]] = r
    rj.write_text(json.dumps(sorted(merged.values(), key=lambda r: r["sym"]), indent=1, ensure_ascii=False),
                  encoding="utf-8")
    results = list(merged.values())
    by = Counter(r["class"] for r in results if r.get("match") == 100.0)
    tot = Counter(r["class"] for r in results)
    print("  class                  n     100%")
    for c in sorted(tot):
        print(f"  {c:20s} {tot[c]:5d} {by.get(c,0):7d}")
    ok = sum(by.values())
    print(f"  total: candidates {len(results)}, objdiff 100% = {ok} ({100.0*ok/max(1,len(results)):.1f}%)")
    if a.mode == "run":
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
