#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the compiler handbook data: `docs/compiler/laws.json` and `docs/compiler/LAWS.md`.

What this stops
---------------
The handbook claims to be evidence-graded. Three silent failures would break that claim:

* a law written into `LAWS.md` but never indexed in `laws.json` (or the reverse), so the machine
  index and the prose drift apart;
* a `T1` law with no binary anchor, i.e. an "I read the source" claim that was never checked
  against the compiler that actually shipped;
* an anchor that points at a symbol or address the shipped `cc1` does not have (typo, or a
  different toolchain build).

The first two are hard failures everywhere. The anchor check needs the EE toolchain, so it is a
skip when `cc1` is absent (a normal CI runner does not have it).

Usage: `python3 tools/check/test_compiler_laws.py` (`make check` calls this script).
Exit code 0 = pass, 1 = failure.

本文件检查编译器手册的数据一致性：`laws.json` 与 `LAWS.md` 双向一致、证据分级的前置条件成立、
（本机有工具链时）锚点指向的符号与地址确实存在于出厂 `cc1`。无工具链时锚点检查跳过。
"""

from __future__ import annotations

import importlib.util
import json
import re
import os
import subprocess
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAWS_JSON = ROOT / "docs" / "compiler" / "laws.json"
LAWS_MD = ROOT / "docs" / "compiler" / "LAWS.md"
ANCHOR_TOOL = ROOT / "tools" / "compiler" / "ee-gcc-anchor.py"

FAILURES: list[str] = []
COUNT = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global COUNT
    COUNT += 1
    mark = "ok  " if ok else "FAIL"
    print(f"[{mark}] {COUNT:>2}. {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


def load_laws() -> dict | None:
    if not LAWS_JSON.is_file():
        check("docs/compiler/laws.json exists", False, str(LAWS_JSON))
        return None
    try:
        return json.loads(LAWS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        check("docs/compiler/laws.json parses", False, str(exc))
        return None


def check_index(data: dict) -> None:
    laws = data.get("laws") or []
    check("laws.json declares schema 1", data.get("schema") == 1)
    check("laws.json has at least one law", len(laws) > 0, f"{len(laws)} laws")

    ids = [law.get("id", "") for law in laws]
    check("law ids are unique", len(set(ids)) == len(ids))
    check("law ids use the L-EE-NNN form",
          all(len(i) == 8 and i.startswith("L-EE-") and i[5:].isdigit() for i in ids))

    mtime = LAWS_MD.read_text(encoding="utf-8") if LAWS_MD.is_file() else ""
    check("docs/compiler/LAWS.md exists", bool(mtime), str(LAWS_MD))
    for law_id in ids:
        check(f"LAWS.md documents {law_id}", law_id in mtime)

    toolchain = data.get("toolchain") or {}
    check("laws.json names the toolchain id", bool(toolchain.get("id")), str(toolchain.get("id", "")))


def check_tiers(data: dict) -> None:
    for law in data.get("laws") or []:
        law_id = law.get("id", "?")
        tier = law.get("tier")
        src = (law.get("source_anchor") or {}).get("file") or ""
        anchor = (law.get("binary_anchor") or {}).get("symbol") or ""
        check(f"{law_id}: tier is T1/T2/T3", tier in ("T1", "T2", "T3"), str(tier))
        check(f"{law_id}: scope is stated", bool((law.get("scope") or "").strip()))
        check(f"{law_id}: receipt is stated", bool((law.get("receipt") or "").strip()))
        if tier == "T1":
            check(f"{law_id}: T1 has a source anchor", bool(src))
            check(f"{law_id}: T1 has a binary anchor", bool(anchor))
        elif tier == "T2":
            check(f"{law_id}: T2 has a source or binary anchor", bool(src or anchor))


def check_binary_anchors(data: dict) -> None:
    """Verify anchors against the shipped cc1 when this machine has it (skip otherwise)."""
    spec = importlib.util.spec_from_file_location("ee_gcc_anchor", ANCHOR_TOOL)
    if spec is None or spec.loader is None:
        check("anchor tool importable", False, str(ANCHOR_TOOL))
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        cc1 = module.require_cc1(module.DEFAULT_CC1)
    except module.ToolError:
        print(f"[skip] no cc1 at {module.DEFAULT_CC1}: binary anchors are not checked on this machine")
        return
    rows = module.nm_symbols(cc1)
    for law in data.get("laws") or []:
        anchor = law.get("binary_anchor") or {}
        symbol, addr = anchor.get("symbol") or "", anchor.get("addr") or ""
        if not symbol or not addr:
            continue
        law_id = law.get("id", "?")
        anchors = [(symbol, addr)] + [(r.get("symbol", ""), r.get("addr", ""))
                                      for r in anchor.get("related", []) or []]
        for symbol, addr in anchors:
            if symbol and addr:
                check(f"{law_id}: {symbol} @ {addr} exists in cc1",
                      int(addr, 16) in [a for _n, _t, a in module.lookup_symbol(rows, symbol)],
                      f"candidates: {[hex(a) for _n, _t, a in module.lookup_symbol(rows, symbol)]}")
        hits = [a for _n, _t, a in module.lookup_symbol(rows, symbol)]
        want = int(addr, 16)
        check(f"{law_id}: {symbol} @ {addr} exists in cc1", want in hits,
              f"candidates: {[hex(a) for a in hits]}")
        if want in hits:
            loc = module.format_location(module.addr2line(cc1, [want])[0][1])
            note = (law.get("source_anchor") or {}).get("note", "")
            file_hint = note.split(".c")[0].split()[-1] if ".c" in note else ""
            check(f"{law_id}: {symbol} resolves to a source location", ":" in loc, loc)
            if file_hint.endswith(".c"):
                check(f"{law_id}: {symbol} resolves inside {file_hint}", file_hint in loc, loc)


def main() -> int:
    data = load_laws()
    if data is not None:
        check_index(data)
        check_tiers(data)
        check_binary_anchors(data)
    check_anchors()
    check_build_flags(data)
    print()
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} of {COUNT} checks failed")
        for item in FAILURES:
            print(f"  - {item}")
        return 1
    print(f"OK: {COUNT} checks passed")
    return 0


def check_build_flags(data: dict) -> None:
    """手册的 scope 说的构建旗标，必须与仓库现状一致。

    为什么：本手册所有条目都声明「在项目构建旗标下」，这些数字来自 `build_mixed.sh` 的 MATCHED_CFLAGS 默认值。
    若它变了，手册的 scope 就过期——而没有任何检查会因此变红。
    """
    toolchain = (data or {}).get("toolchain") or {}
    stated = toolchain.get("flags", "")
    script = ROOT / "build_mixed.sh"
    if not script.exists():
        check("build flags match the handbook", False, "build_mixed.sh missing")
        return
    m = re.search(r'MATCHED_CFLAGS="\$\{MATCHED_CFLAGS:-([^}]*)\}', script.read_text(encoding="utf-8"))
    if not m:
        check("build flags match the handbook", False, "MATCHED_CFLAGS default not found")
        return
    actual = m.group(1).strip()
    check("build flags match the handbook", actual == stated, f"script {actual!r} vs laws.json {stated!r}")

    # 有编译器时再核 dump 数量：PASSES.md 声称 3.2 有 26 份 `-da` dump
    gcc = Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / "ee-gcc"
    if not gcc.exists():
        return
    with tempfile.TemporaryDirectory(prefix="dumpcount-") as td:
        work = Path(td)
        (work / "t.c").write_text("int f(int a) { return a + 1; }\n", encoding="utf-8")
        subprocess.run([str(gcc), "-O2", "-da", "-c", "-o", "/dev/null", str(work / "t.c")],
                       capture_output=True, cwd=work, check=False)
        dumps = sorted(p.name.split("t.c.", 1)[1] for p in work.glob("t.c.[0-9]*"))
    check("2.96/3.2 dump inventory (26 for 3.2)", len(dumps) == 26, f"{len(dumps)} dumps: {dumps[:6]}")

    with tempfile.TemporaryDirectory(prefix="dumpcount-o1-") as td:
        work = Path(td)
        (work / "t.c").write_text("int f(int a, int b) { int s = 0; int i; for (i = 0; i < 4; i++) s += a * i + b; return s; }\n",
                                 encoding="utf-8")
        subprocess.run([str(gcc), "-O1", "-G0", "-da", "-c", "-o", "/dev/null", str(work / "t.c")],
                       capture_output=True, cwd=work, check=False)
        dumps_o1 = sorted(p.name.split("t.c.", 1)[1] for p in work.glob("t.c.[0-9]*"))
    check("-O1 dump inventory (20, six fewer than -O2)", len(dumps_o1) == 20,
          f"{len(dumps_o1)} dumps; missing {sorted(set(dumps) - set(dumps_o1))}")


def _gh_slug(heading: str) -> str:
    """GitHub 的标题锚点算法：小写、去标点（保留空格）、每个空格→连字符（**不折叠**）。"""
    text = heading.lstrip("#").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return text.replace(" ", "-")


def check_anchors() -> None:
    """页内锚点必须指向真实存在的标题。

    为什么单独查：相对**文件**链接有人查（`check_docs.py`），页内 `#anchor` 没人查；
    改一次标题就会静默产生 46 条死链（2026-10-15 实际发生过）。
    """
    base = ROOT / "docs" / "compiler"
    texts = {p.name: p.read_text(encoding="utf-8") for p in base.glob("*.md")}
    heads = {name: {_gh_slug(line) for line in text.splitlines() if line.startswith("#")}
             for name, text in texts.items()}
    bad = []
    for name, text in texts.items():
        for m in re.finditer(r"\]\(([A-Za-z0-9._-]+\.md)#([^)]+)\)", text):
            target, anchor = m.group(1), m.group(2)
            if target in heads and anchor not in heads[target]:
                bad.append(f"{name} -> {target}#{anchor}")
    check(f"in-page anchors resolve ({sum(len(h) for h in heads.values())} headings)",
          not bad, "; ".join(bad[:3]))


if __name__ == "__main__":
    sys.exit(main())
