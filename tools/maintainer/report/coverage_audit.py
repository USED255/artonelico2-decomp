#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coverage audit: which unmatched candidates with a good draft were never fed to a channel.

Why this exists (measured 2026-10-13): 208 unmatched candidates had a draft at 80 % or better
and **no permuter work directory**. The reason was structural, not random -- the permuter pools
are normally driven with `--from routebjp/build/m2/ghidra_batch/result.json`, so a candidate
whose only good draft comes from the m2c batch never entered the run. All 60 candidates at
90 %+ in that gap shared that shape.

The lesson (R11 sections 11.45-11.57): coverage must be audited per (candidate, channel) pair.
A "pool" is not a channel; a candidate can be inside a pool and still never have been tried.

Usage:
  python3 tools/maintainer/report/coverage_audit.py                     # table + counts
  python3 tools/maintainer/report/coverage_audit.py --min 90            # only 90 % and better
  python3 tools/maintainer/report/coverage_audit.py --tsv out.tsv       # one row per gap

覆盖审计：哪些「有不错草稿但从未喂给某通道」的未匹配候选。

存在理由（2026-10-13 实测）：208 个未匹配候选草稿 ≥80% 却**没有 permuter 工作目录**；原因是结构性的
—— permuter 池通常用 `--from routebjp/build/m2/ghidra_batch/result.json` 驱动，于是「只有 m2c 草稿好」
的候选永远进不了跑批。该缺口里 90%+ 的 60 个全部是这一形态。

教训（R11 §11.45–11.57）：覆盖必须按 **(候选, 通道) 对**审计 ——「在池子里」不等于「试过」。
"""

# Private layout names (routebjp/build/m2c, routebjp/build/m2/ghidra_batch, routebjp/build/m2/perm),
# do not rename.  私有布局名，勿改名。

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project"))
from at2_paths import PRIVATE_ROOT, WORK_ROOT, MATCHED_LIST, WORKQUEUE  # noqa: E402

REPO = PRIVATE_ROOT or WORK_ROOT.parent
M2C = WORK_ROOT / "m2c" / "batch" / "result.json"
GHIDRA = WORK_ROOT / "m2" / "ghidra_batch" / "result.json"
PERM = WORK_ROOT / "m2" / "perm"
LLM = WORK_ROOT / "llm_eval" / "results.jsonl"
JTBL_SWEEP = WORK_ROOT / "jtbl" / "sweep_clean.jsonl"


def ledger_syms() -> set[str]:
    out: set[str] = set()
    for line in MATCHED_LIST.read_text(encoding="utf-8").splitlines():
        a = line.split("#", 1)[0].strip()
        if a:
            out.add(a.split()[0])
    return out


def workqueue() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    lines = WORKQUEUE.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) > 12:
            rows[p[0]] = {"size": int(p[2]), "class": p[12], "gate": p[11]}
    return rows


def draft_scores() -> dict[str, dict[str, float]]:
    """{sym: {channel: best score}} for every batch that produced a score."""
    out: dict[str, dict[str, float]] = {}
    for path, name in ((M2C, "m2c"), (GHIDRA, "ghidra"), (JTBL_SWEEP, "jtbl")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        records = json.loads(text) if text.lstrip().startswith("[") else [
            json.loads(l) for l in text.splitlines() if l.strip()]
        for r in records:
            v = r.get("match", r.get("best"))
            if isinstance(v, (int, float)):
                d = out.setdefault(r["sym"], {})
                d[name] = max(d.get(name, -1.0), float(v))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=80.0, help="only report drafts at this score or better")
    ap.add_argument("--tsv", default="", help="write one row per gap")
    a = ap.parse_args()

    have = ledger_syms()
    wq = workqueue()
    scores = draft_scores()
    permuted = {p.name for p in PERM.iterdir() if p.is_dir()} if PERM.is_dir() else set()
    llm_seen: set[str] = set()
    if LLM.is_file():
        for line in LLM.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                llm_seen.add(json.loads(line)["sym"])
            except Exception:
                continue

    gaps: list[dict] = []
    for sym, meta in wq.items():
        if sym in have:
            continue
        ch = scores.get(sym, {})
        best = max(ch.values()) if ch else None
        if best is None or best < a.min:
            continue
        gaps.append({"sym": sym, "best": best, "drafts": "+".join(sorted(ch)),
                     "class": meta["class"], "size": meta["size"], "gate": meta["gate"],
                     "in_permuter": sym in permuted, "in_llm": sym in llm_seen})

    gaps.sort(key=lambda g: -g["best"])
    open_perm = [g for g in gaps if not g["in_permuter"]]
    open_llm = [g for g in gaps if not g["in_llm"]]
    print(f"== coverage audit (draft >= {a.min:.0f}) ==")
    print(f"  unmatched candidates with a score      : {len(gaps)}")
    print(f"  ... never fed to the permuter          : {len(open_perm)}")
    print(f"  ... never fed to the LLM               : {len(open_llm)}")
    for lo, hi in ((95, 101), (90, 95), (85, 90), (80, 85)):
        b = [g for g in open_perm if lo <= g["best"] < hi]
        if b:
            print(f"  permuter gap {lo}-{hi}                  : {len(b)}")
    if open_perm:
        print("\n  -- permuter gaps (first 20) --")
        print(f"  {'symbol':22s} {'best':>7s} {'drafts':16s} {'class':16s} {'size':>6s}")
        for g in open_perm[:20]:
            print(f"  {g['sym']:22s} {g['best']:7.2f} {g['drafts']:16s} {g['class']:16s} {g['size']:6d}")
        shape = {}
        for g in open_perm:
            shape[g["drafts"]] = shape.get(g["drafts"], 0) + 1
        print("\n  gap shape by draft source:", ", ".join(f"{k}={v}" for k, v in sorted(shape.items(), key=lambda kv: -kv[1])))
    if a.tsv:
        cols = ["sym", "best", "drafts", "class", "size", "gate", "in_permuter", "in_llm"]
        Path(a.tsv).write_text("\t".join(cols) + "\n" + "\n".join(
            "\t".join(str(g[c]) for c in cols) for g in gaps) + "\n", encoding="utf-8")
        print(f"\n  wrote {a.tsv} ({len(gaps)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
