#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1a 实验：Ghidra 伪 C 作为「匹配草稿」到底能不能用（闸门 G1）。

做法：分层抽样未匹配函数（默认每类 10 个：B 直筒 / D 单调用 / E 仅分支 / F 分支+调用），
对每个函数：抽伪 C → 补 shim → 用 ee-gcc 默认标志编译 → 与原函数目标块 objdiff。
记录「编译是否通过」「objdiff 匹配率」，给出 G1 结论。

判定线（长期计划 §4/P1a）：B/D 类命中 ≥15% ⇒ 伪 C 作为草稿来源全面接入；<5% ⇒ 放弃伪 C。

用法：
  python3 routebjp/tools/p1a_pseudoc_probe.py [--per-class 10] [--classes B_straight,D_single_call]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_draft  # noqa: E402

from at2_paths import (  # noqa: E402  布局无关的路径解析（说明见 at2_paths.py 顶部）
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

REPO = PRIVATE_ROOT or ROOT
MATCHED = MATCHED_LIST
BUILD = WORK_ROOT / "m2" / "p1a"
CFLAGS = ["-O2", "-falign-functions=4", "-ffunction-sections"]
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'


def matched() -> set:
    out = set()
    for line in MATCHED.read_text(encoding="utf-8").splitlines():
        body = line.split("#", 1)[0].strip()
        if body:
            out.add(body.split()[0])
    return out


def rows():
    lines = WORKQUEUE.read_text(encoding="utf-8").splitlines()
    idx = {k: i for i, k in enumerate(lines[0].split("\t"))}
    out = []
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) >= len(idx):
            out.append({k: p[i] for k, i in idx.items()})
    return out


def target_block(sym: str) -> str | None:
    f = ROOT / "asm" / "cod" / f"{sym}.s"
    if not f.is_file():
        return None
    import re
    L = f.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next((i for i, x in enumerate(L) if re.match(r"\s*glabel\s+", x)), None)
    en = next((i for i in range(gi or 0, len(L)) if re.match(r"\s*endlabel\s+", L[i])), None)
    if gi is None or en is None:
        return None
    return PREAMBLE + "\n".join(L[gi:en + 1]) + "\n"


def probe(sym: str) -> dict:
    d = BUILD / sym
    d.mkdir(parents=True, exist_ok=True)
    src = ghidra_draft.emit(sym, BUILD)
    rec = {"sym": sym, "draft": bool(src)}
    if not src:
        return rec
    ts = d / "target.s"
    tb = target_block(sym)
    if not tb:
        rec["error"] = "no_target_block"
        return rec
    ts.write_text(tb, encoding="utf-8")
    t_o = d / "t.o"
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(t_o), str(ts)],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        rec["error"] = "target_as_fail"
        return rec
    c_o = d / "c.o"
    r = subprocess.run([GCC, *CFLAGS, "-I", "include", "-c", "-o", str(c_o), str(src)],
                       cwd=str(ROOT), capture_output=True, text=True)
    rec["compile_ok"] = (r.returncode == 0)
    if r.returncode:
        lines = [l for l in r.stderr.splitlines() if "error" in l.lower()]
        rec["compile_error"] = (lines[0] if lines else r.stderr.splitlines()[-1] if r.stderr else "?")[:160]
        return rec
    dj = d / "diff.json"
    r = subprocess.run([OBJDIFF, "diff", "-1", str(t_o), "-2", str(c_o), "-o", str(dj), "--format", "json"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        rec["error"] = "objdiff_fail"
        return rec
    data = json.loads(dj.read_text(encoding="utf-8"))
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    rec["match"] = per.get(sym)
    rec["match"] = float(rec["match"]) if rec["match"] is not None else None
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=10)
    ap.add_argument("--classes", default="B_straight,D_single_call,E_branch_only,F_branch_call")
    ap.add_argument("--mode", choices=["smallest", "random"], default="smallest",
                    help="smallest=取该类最小函数（上界）；random=无偏随机抽样（估真实命中率）")
    ap.add_argument("--seed", type=int, default=20261003)
    args = ap.parse_args()
    classes = args.classes.split(",")
    have = matched()
    BUILD.mkdir(parents=True, exist_ok=True)
    import random
    rng = random.Random(args.seed)

    out = []
    for cls in classes:
        pool = [r for r in rows() if r["class"] == cls and r["name"] not in have]
        if args.mode == "smallest":
            pool.sort(key=lambda r: int(r["size"]))
            picked = pool[:args.per_class]
        else:
            picked = rng.sample(pool, min(args.per_class, len(pool)))
        for r in picked:
            rec = probe(r["name"])
            rec["class"] = cls
            rec["size"] = int(r["size"])
            out.append(rec)

    (BUILD / "result.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"== P1a 伪 C 草稿实验（每类 {args.per_class} 个，共 {len(out)}）==")
    by = {}
    for rec in out:
        k = rec["class"]
        by.setdefault(k, {"n": 0, "compile": 0, "match100": 0, "best": 0.0})
        by[k]["n"] += 1
        by[k]["compile"] += 1 if rec.get("compile_ok") else 0
        m = rec.get("match")
        if m == 100.0:
            by[k]["match100"] += 1
        if m:
            by[k]["best"] = max(by[k]["best"], m)
    tot_c = tot_m = tot_n = 0
    for k, v in by.items():
        print(f"  {k:16s} n={v['n']:3d}  编译通过 {v['compile']:3d}  objdiff100 {v['match100']:3d}  最高 {v['best']:.1f}%")
        tot_c += v["compile"]; tot_m += v["match100"]; tot_n += v["n"]
    print(f"  合计：编译通过 {tot_c}/{tot_n}；objdiff 100% = {tot_m}/{tot_n}")
    errs = Counter(r.get("compile_error", "")[:60] for r in out if not r.get("compile_ok"))
    for e, c in errs.most_common(5):
        print(f"    编译失败 [{c}] {e}")
    print(f"结果 JSON -> {BUILD / 'result.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
