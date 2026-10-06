#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 包装函数自动匹配（-O1 / -O2 两种空壳栈帧模板，日版 SLPS_258.19）。

背景（2026-10-03 实测，见 docs/R10 §3.4）：
  本作有大量「薄包装」函数，只有两种机器码形态，且**分别对应不同编译档**：

  -O1 档（jal 形态，无 sibling-call 优化）：
      addiu $29,$29,-0x10
      sd    $31,0x0($29)
      jal   <T>
      <延迟槽: nop | daddu $R,$0,$0>
      ld    $31,0x0($29)
      jr    $31
      addiu $29,$29,0x10
  -O2 档（j 尾调用形态）：
      addiu $29,$29,-0x10
      [daddu $R,$0,$0]              # 需要清零尾参时在 prologue 之后
      sd    $31,0x0($29)
      ld    $31,0x0($29)
      j     <T>
      addiu $29,$29,0x10

  实测 4/4 个真实目标（func_0010264c / func_0011b1a8 / func_001e3ce0 / func_001a0188）
  用 `-O1` + `extern void T(); void sym(...){ T(...); }` 得到 objdiff 100%。

用法：
  python3 routebjp/tools/auto_match_wrapper.py scan [--tier small]
  python3 routebjp/tools/auto_match_wrapper.py run  [--tier small] [--apply]

落地时会写 `routebjp/config/source_flags.tsv`（<source-basename>\\t<extra-cflags>），
`build_hybrid.sh` 按它给对应源追加编译标志（-O1 等；-O2 为默认，不写字）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auto_match_trivial import (  # noqa: E402
    ROOT, WORK_ROOT, ASMDIR, MATCHED_LIST, SRCDIR, GCC, AS, OBJDIFF, CFLAGS, split_mode, matched_in_list,
    M3_BEGIN, M3_END, A0, A1, A2, A3, ZERO, CARG, ARG_OF_REG,
)

FLAGS_FILE = ROOT / "config" / "source_flags.tsv"
BUILDDIR = WORK_ROOT / "m2" / "m3wrap"
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
INS_RE = re.compile(r"/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
PROLOG = "addiu $29, $29, -0x10"
EPILOG = "addiu $29, $29, 0x10"
SAVE_RA = "sd $31, 0x0($29)"
LOAD_RA = "ld $31, 0x0($29)"
TIERS = ("trivial", "small", "medium", "large", "huge")
ZERO_RE = re.compile(r"^daddu (\$\d+), \$0, \$0$")


def body_ins(sym: str) -> list[str] | None:
    p = ASMDIR / f"{sym}.s"
    if not p.is_file():
        return None
    lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = None
    for i, l in enumerate(lines):
        if re.match(r"\s*glabel\s+", l):
            gi = i
            break
    if gi is None:
        return None
    en = None
    for i in range(gi, len(lines)):
        if re.match(r"\s*endlabel\s+", lines[i]):
            en = i
            break
    if en is None:
        return None
    return [re.sub(r"\s+", " ", l.split("*/", 1)[-1].strip())
            for l in lines[gi + 1:en] if INS_RE.search(l)]


def _zero_index(op: str):
    """'daddu $5, $0, $0' -> 1（第 1 号参数清零）；不是清零则 None。"""
    m = ZERO_RE.match(op)
    if not m:
        return None
    reg = m.group(1)
    return ARG_OF_REG.get(reg)


def recognize(sym: str):
    """返回 dict(flags, tgt, nargs, zero_at, kind) 或 None。"""
    ins = body_ins(sym)
    if not ins or len(ins) < 5:
        return None

    # ---- -O1：jal 形态 ----
    if (len(ins) == 7 and ins[0] == PROLOG and ins[1] == SAVE_RA
            and ins[2].startswith("jal ") and ins[4] == LOAD_RA and ins[5] == "jr $31"
            and ins[6] == EPILOG):
        tgt = ins[2].split(" ", 1)[1].strip()
        slot = ins[3]
        zero_at = None
        if slot != "nop":
            zero_at = _zero_index(slot)
            if zero_at is None:
                return None
        if re.search(r"[^\w.]", tgt):
            return None
        return {"flags": "-O1", "tgt": tgt, "zero_at": zero_at, "kind": "o1_jal"}

    # ---- -O2：j 尾调用形态（可选 0/1 个清零参数）----
    if len(ins) in (5, 6):
        i = 0
        zero_at = None
        if len(ins) == 6:
            zero_at = _zero_index(ins[0])
            if zero_at is None:
                return None
            i = 1
        if (ins[i] == PROLOG and ins[i + 1] == SAVE_RA and ins[i + 2] == LOAD_RA
                and ins[i + 3].startswith("j ") and ins[i + 4] == EPILOG):
            tgt = ins[i + 3].split(" ", 1)[1].strip()
            if re.search(r"[^\w.]", tgt):
                return None
            return {"flags": "", "tgt": tgt, "zero_at": zero_at, "kind": "o2_tail"}
    return None


def c_source(sym: str, info: dict) -> str:
    tgt, z = info["tgt"], info["zero_at"]
    if z is None:
        params, call = "", f"{tgt}()"
    else:
        names = CARG[:z]
        params = ", ".join("int " + n for n in names)
        # ⚠️ 必须带上被调用者：early 版本漏了 `{tgt}(`，生成出 `{ a, 0; }` 这种空语句
        call = f"{tgt}(" + ", ".join(list(names) + ["0"]) + ")"
    hdr = (f"/* {sym} : 空壳栈帧包装（{info['kind']}，编译档 {info['flags'] or '-O2'}）\n"
           f" * 由 routebjp/tools/auto_match_wrapper.py 生成；objdiff 100% 后纳入 hybrid。\n"
           f" * 语义：本函数只做参数整理后调用 {tgt}（延迟槽/nop 由模板决定）。 */\n")
    return hdr + f"extern void {tgt}();\n\nvoid {sym}({params}) {{ {call}; }}\n"


def workqueue_rows(tier: str):
    tsv = ROOT.parent / "out/evidence/jp_m3_workqueue.tsv"
    lines = tsv.read_text(encoding="utf-8").splitlines()
    idx = {k: i for i, k in enumerate(lines[0].split("\t"))}
    out = []
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) < len(idx) or p[idx["tier"]] != tier:
            continue
        out.append((p[idx["name"]], p[idx["eligible"]] == "1", p[idx["gate"]]))
    return out


def m3_section_syms() -> set:
    if not MATCHED_LIST.is_file():
        return set()
    text = MATCHED_LIST.read_text(encoding="utf-8")
    if M3_BEGIN not in text:
        return set()
    seg = text.split(M3_BEGIN, 1)[1].split(M3_END, 1)[0]
    return {l.split("#", 1)[0].strip() for l in seg.split("\n") if l.split("#", 1)[0].strip()}


def candidates(tier: str):
    already = matched_in_list() - m3_section_syms()   # 自己写进 M3 段的要重新验证
    out = []
    for sym, elig, gate in workqueue_rows(tier):
        if sym in already or not elig or gate.startswith("blocked"):
            continue
        info = recognize(sym)
        if info:
            out.append({"sym": sym, **info})
    return out


def run_objdiff(sym: str, info: dict, work: Path) -> float | None:
    d = work / sym
    d.mkdir(parents=True, exist_ok=True)
    ins = body_ins(sym)
    L = (ASMDIR / f"{sym}.s").read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next(i for i, l in enumerate(L) if re.match(r"\s*glabel\s+", l))
    en = next(i for i in range(gi, len(L)) if re.match(r"\s*endlabel\s+", L[i]))
    (d / "target.s").write_text(PREAMBLE + "\n".join(L[gi:en + 1]) + "\n", encoding="utf-8")
    (d / "probe.c").write_text(c_source(sym, info), encoding="utf-8")
    t_o, c_o, dj = d / "t.o", d / "c.o", d / "diff.json"
    flags = (info["flags"].split() if info["flags"] else [])
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(t_o), str(d / "target.s")],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    # ⚠️ 额外标志必须排在默认 CFLAGS **之后**：gcc 取最后一个 -O 档（-O1 覆盖 -O2）
    r = subprocess.run([GCC, *CFLAGS, *flags, "-I", "include", "-c", "-o", str(c_o), str(d / "probe.c")],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    r = subprocess.run([OBJDIFF, "diff", "-1", str(t_o), "-2", str(c_o), "-o", str(dj), "--format", "json"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    data = json.loads(dj.read_text(encoding="utf-8"))
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    return per.get(sym)


def do_apply(winners: dict):
    SRCDIR.mkdir(parents=True, exist_ok=True)
    for sym, info in winners.items():
        (SRCDIR / f"{sym}.c").write_text(c_source(sym, info), encoding="utf-8")

    # 清单 M3 段（合并式）
    text = MATCHED_LIST.read_text(encoding="utf-8")
    pre = text.split(M3_BEGIN)[0].rstrip("\n") if M3_BEGIN in text else text.rstrip("\n")
    post = text.split(M3_END, 1)[1].lstrip("\n") if M3_END in text else ""
    existing: "OrderedDict[str, str]" = OrderedDict()
    if M3_BEGIN in text:
        for line in text.split(M3_BEGIN, 1)[1].split(M3_END, 1)[0].split("\n"):
            a = line.split("#", 1)
            if a[0].strip():
                existing[a[0].strip()] = a[1].strip() if len(a) > 1 else ""
    n0 = len(existing)
    for sym, info in winners.items():
        existing[sym] = f"wrapper_{info['kind']}"
    out = [pre, "", M3_BEGIN] + [f"{s}    # {existing[s]}" for s in sorted(existing)] + [M3_END]
    body = "\n".join(out)
    if post:
        body = body.rstrip("\n") + "\n" + post
    MATCHED_LIST.write_text(body.rstrip("\n") + "\n", encoding="utf-8")

    # 编译标志旁路表（只有非默认档才写）
    flags = {}
    if FLAGS_FILE.is_file():
        for line in FLAGS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            a = line.split()
            flags[a[0]] = " ".join(a[1:])
    for sym, info in winners.items():
        if info["flags"]:
            flags[sym] = info["flags"]
        else:
            flags.pop(sym, None)
    lines = ["# 每源额外编译标志（build_hybrid.sh 读取；-O2 为默认，不写）",
             "# 格式：<source-basename>\\t<extra-cflags>"]
    for s in sorted(flags):
        lines.append(f"{s}\t{flags[s]}")
    FLAGS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"apply: 写 {len(winners)} 个 C 源；清单 M3 段 {n0} -> {len(existing)}；"
          f"标志表 {len(flags)} 条 -> {FLAGS_FILE.relative_to(ROOT.parent)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["scan", "run"])
    ap.add_argument("--tier", default="small", choices=TIERS)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cands = candidates(args.tier)
    if args.mode == "scan":
        c = Counter((i["kind"], i["flags"] or "-O2") for i in cands)
        print(f"== {args.tier} 包装候选：{len(cands)} 个 ==")
        for k, v in c.most_common():
            print(f"   {k[0]:8s} {k[1]:4s} {v}")
        return 0

    BUILDDIR.mkdir(parents=True, exist_ok=True)
    winners, fails = OrderedDict(), OrderedDict()
    for info in cands:
        sym = info["sym"]
        mp = run_objdiff(sym, info, BUILDDIR)
        info["match"] = mp
        (winners if mp == 100.0 else fails)[sym] = info
    print(f"== {args.tier} 包装：尝试 {len(cands)}，objdiff 100% = {len(winners)} ==")
    c = Counter((i["kind"], i["flags"] or "-O2") for i in winners.values())
    for k, v in c.most_common():
        print(f"   {k[0]:8s} {k[1]:4s} {v}")
    (BUILDDIR / f"result_{args.tier}.json").write_text(json.dumps({
        "tier": args.tier, "n_candidates": len(cands), "n_matched": len(winners),
        "matched": {s: {k: i[k] for k in ("tgt", "zero_at", "kind", "flags", "match")}
                    for s, i in winners.items()},
        "failed": {s: {k: i[k] for k in ("tgt", "zero_at", "kind", "flags", "match")}
                   for s, i in fails.items()},
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"结果 JSON -> {BUILDDIR / ('result_' + args.tier + '.json')}")
    if args.apply:
        do_apply(winners)
    return 0


if __name__ == "__main__":
    sys.exit(main())
