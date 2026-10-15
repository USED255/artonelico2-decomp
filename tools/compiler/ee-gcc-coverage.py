#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ee-gcc-coverage —— measure how much of a binary the handbook actually explains.

Why: the handbook is a set of rules about what this compiler emits. "How complete is it?" is an
answerable question: take a disassembly, collect the mnemonics, and check which of them the handbook
mentions anywhere. The leftovers then classify themselves:

  explained  a rule in the handbook names it and the compiler can emit it from C
  ASM_ONLY   the compiler cannot emit it from C, so it comes from hand-written assembly
             (COP2/VU0, MMI packed arithmetic, privileged instructions - see L-EE-048)
  OTHER      nobody has explained it yet; these are the handbook's real gaps

Classification runs first: naming an assembly-only mnemonic in prose does not make it explained.

Usage
-----
```sh
# a disassembly produced by the project's objdump (address: word  mnemonic ...)
mips-ps2-decompals-objdump -d prog.elf | python3 tools/compiler/ee-gcc-coverage.py --asm -

# an assembly listing
python3 tools/compiler/ee-gcc-coverage.py --asm func.s

# an ELF directly (needs --objdump, or the default project path)
python3 tools/compiler/ee-gcc-coverage.py --elf prog.elf

python3 tools/compiler/ee-gcc-coverage.py --selftest
```

No game content is needed or produced: `--selftest` builds a synthetic listing on the spot.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DOCS = HERE.parent.parent / "docs" / "compiler"
DEFAULT_OBJDUMP = Path.home() / "eecc" / "ps2binutils" / "mips-ps2-decompals-objdump"

# objdump line: "  100270:\t27bdfff0 \taddiu\tsp,sp,-16"
OBJDUMP_LINE = re.compile(r"^\s+[0-9a-f]+:\s+[0-9a-f]{8}\s+(\S+)")
# plain assembly listing line: "\taddiu\tsp,sp,-16" or "  move $2,$4"
ASM_LINE = re.compile(r"^\s+([a-z][a-z0-9._]*)\s")

# Instructions this compiler cannot produce from C (L-EE-048 and the MMI/privileged families).
COP2_VU0 = {
    "lqc2", "sqc2", "qmfc2", "qmtc2", "cfc2", "ctc2", "c2", "vnop", "vwaitq", "vdiv", "vsqrt",
    "vrsqrt", "vclip", "vabs", "vmov", "vmax", "vmin", "vopm", "vmr32", "vftoi0", "vftoi4",
    "vitof0", "vitof4", "vrn", "vnop", "vcallms", "vcallmsr",
}
PRIVILEGED = {
    "syscall", "break", "sync", "sync.p", "cache", "pref", "eret", "tlbr", "tlbwi", "tlbwr",
    "tlbp", "mfc0", "mtc0", "cfc0", "ctc0", "di", "ei", "wait",
    # traps
    "tne", "teq", "tge", "tgeu", "tlt", "tltu", "tnei", "tgei", "tlti", "tltiu", "teqi",
    "sdbbp",
    # HI/LO and COP1 control registers: no C construct writes these here (64-bit mul/div is libgcc,
    # and the rounding mode is not settable from C in this compiler)
    "mthi", "mtlo", "mthi1", "mtlo1", "mfsa", "mtsa", "ctc1", "cfc1",
}
# MMI packed arithmetic and the EE's second multiply/divide unit.
MMI_PREFIXES = ("padd", "psub", "pmax", "pmin", "psra", "psrl", "psll", "pcpy", "pext", "pand",
                "por", "pnor", "pxor", "ppac", "pceq", "pcgt", "plzc", "pmf", "pmth", "prot")
MMI_EXACT = {"qfsrv", "mtsab", "mtsah", "mult1", "multu1", "div1", "divu1", "madd1", "maddu1",
             "mflo1", "mfhi1", "mthi1", "mtlo1", "mfsa", "mtsa"}


def classify(mnemonic: str) -> str:
    """ASM_ONLY when the compiler cannot emit it from C (L-EE-048), else OTHER (a real gap)."""
    m = mnemonic.split(".")[0]
    if mnemonic in COP2_VU0 or m == "c2":
        return "ASM_ONLY"
    if m.startswith("v") and m not in ("v0", "v1"):
        return "ASM_ONLY"                     # VU0 macro mode
    if mnemonic in PRIVILEGED or m in PRIVILEGED:
        return "ASM_ONLY"
    if mnemonic in MMI_EXACT or m in MMI_EXACT or mnemonic.startswith(MMI_PREFIXES):
        return "ASM_ONLY"
    return "OTHER"


def handbook_text(docs: Path) -> str:
    parts = []
    for page in sorted(docs.glob("*.md")):
        if ".zh-CN." in page.name:
            continue
        parts.append(page.read_text(encoding="utf-8"))
    return "\n".join(parts)


def mnemonics_from_text(text: str) -> "dict[str, int]":
    counts: dict[str, int] = {}
    for line in text.splitlines():
        m = OBJDUMP_LINE.match(line) or ASM_LINE.match(line)
        if not m:
            continue
        name = m.group(1)
        if name.startswith((".", "#")):  # directives
            continue
        if re.fullmatch(r"[0-9a-f]+", name):  # a bare word that is not a mnemonic
            continue
        counts[name] = counts.get(name, 0) + 1
    return counts


def report(counts: "dict[str, int]", text: str, top: int) -> int:
    total = sum(counts.values())
    # NOTE: classification comes first, and it does not depend on whether the handbook *mentions* the
    # mnemonic. Mentioning `mthi` in a sentence about inline assembly must not turn it into "explained".
    asm_only_total = {k: v for k, v in counts.items() if classify(k) == "ASM_ONLY"}
    explained = {k: v for k, v in counts.items()
                 if k not in asm_only_total and k in text}
    other = {k: v for k, v in counts.items()
             if k not in asm_only_total and k not in text}
    asm_documented = {k: v for k, v in asm_only_total.items() if k in text}
    cov = sum(explained.values())
    asm = sum(asm_only_total.values())
    print(f"instructions: {total}")
    if total:
        print(f"explained by a rule: {cov} ({100 * cov / total:.2f}%)")
        print(f"assembly-only (no C entry): {asm} ({100 * asm / total:.2f}%) "
              f"in {len(asm_only_total)} mnemonics"
              + (f", {len(asm_documented)} of them named in the handbook" if asm_documented else ""))
        print(f"unexplained: {sum(other.values())} ({100 * sum(other.values()) / total:.2f}%) "
              f"in {len(other)} mnemonics")
    print()
    print("OTHER (real gaps - the handbook should explain these): "
          f"{sum(other.values())} in {len(other)} mnemonics")
    for k, v in sorted(other.items(), key=lambda kv: -kv[1])[:top]:
        print(f"    {k:<14} {v}")
    print()
    print(f"ASM_ONLY (no C entry, hand-written assembly - L-EE-048): "
          f"{asm} in {len(asm_only_total)} mnemonics")
    for k, v in sorted(asm_only_total.items(), key=lambda kv: -kv[1])[:top]:
        print(f"    {k:<14} {v}")
    return 0 if not other else 1


def selftest() -> int:
    """Build a synthetic listing and check the classification, with no external input."""
    listing = "\n".join([
        "  100000:\t27bdfff0 \taddiu\tsp,sp,-16",
        "  100004:\t0080102d \tmove\tv0,a0",
        "  100008:\t98820001 \tlwr\tv0,1(a0)",
        "  10000c:\t03e00008 \tjr\tra",
        "  100010:\t00000000 \tnop",
        "  100014:\t4be20000 \tlqc2\t$vf0,0(ra)",
        "  100018:\t4a000000 \tvmulax.xyzw\t$ACC,$vf0,$vf1,$vf2",
        "  10001c:\t70001234 \tpaddsh\t$2,$3,$4",
        "  100020:\t0000000c \tsyscall",
        "  100024:\t4be21234 \tzzznotreal",   # unknown -> OTHER
    ])
    text = handbook_text(DEFAULT_DOCS)
    counts = mnemonics_from_text(listing)
    covered = {k for k in counts if k in text and classify(k) != "ASM_ONLY"}
    problems = []
    for want in ("addiu", "move", "jr", "nop", "lwr"):
        if want not in covered:
            problems.append(f"{want} should be explained")
    for want in ("lqc2", "vmulax.xyzw", "paddsh", "syscall"):
        if classify(want) != "ASM_ONLY":
            problems.append(f"{want} should classify ASM_ONLY, got {classify(want)}")
    if classify("zzznotreal") != "OTHER":
        problems.append("zzznotreal should classify OTHER")
    if "zzznotreal" in covered:
        problems.append("zzznotreal must not be covered")
    if problems:
        for p in problems:
            print(f"FAIL {p}")
        print(f"ee-gcc-coverage selftest: {len(problems)} failed")
        return 1
    asm = [k for k in counts if classify(k) == "ASM_ONLY"]
    print("ee-gcc-coverage selftest: OK "
          f"({len(counts)} mnemonics, {len(covered)} explained, {len(asm)} asm-only)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure how much of a binary the handbook explains.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--asm", help="disassembly or assembly listing, or - for stdin")
    src.add_argument("--elf", help="an ELF to disassemble first")
    src.add_argument("--selftest", action="store_true", help="classify a synthetic listing")
    ap.add_argument("--docs", default=str(DEFAULT_DOCS), help="handbook directory")
    ap.add_argument("--objdump", default=str(DEFAULT_OBJDUMP), help="objdump for --elf")
    ap.add_argument("--top", type=int, default=25, help="how many mnemonics to list per class")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.elf:
        objdump = Path(args.objdump)
        if not objdump.exists():
            print(f"objdump not found: {objdump}", file=sys.stderr)
            return 2
        text = subprocess.run([str(objdump), "-d", args.elf], capture_output=True, text=True).stdout
    elif args.asm == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.asm).read_text(encoding="utf-8", errors="replace")

    docs = Path(args.docs)
    if not docs.is_dir():
        print(f"handbook directory not found: {docs}", file=sys.stderr)
        return 2
    counts = mnemonics_from_text(text)
    if not counts:
        print("no instructions found (expected an objdump -d listing or an assembly file)",
              file=sys.stderr)
        return 2
    return report(counts, handbook_text(docs), args.top)


if __name__ == "__main__":
    sys.exit(main())
