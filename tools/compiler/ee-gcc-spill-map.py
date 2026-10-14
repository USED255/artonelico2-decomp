#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ee-gcc-spill-map —— map a function's stack accesses back to source lines.

Why: a frame that is too large is the most common residual in a big function. The frame is
`[vars][outgoing args][8 B per saved register]` (L-EE-012), so the first question is *which block*
differs — and the second is *which source line* fills it. This tool answers both from one compile.

How: compile with `-gdwarf-2 -fverbose-asm`, read the `.frame` comment for the block sizes, then walk
`.loc` markers and the `sw`/`sd`/`lw`/`ld` instructions whose offsets fall inside each block.

Usage
-----
```sh
python3 tools/compiler/ee-gcc-spill-map.py \
    --cc ~/eecc/ee-gcc3.2-040921/bin/ee-gcc \
    --src func.c --include include --flags "-Os -fno-thread-jumps" --frame 176
```

Output: the `.frame` breakdown, the store/load counts per source line for the `vars` block, and a
per-slot histogram. No game content is printed — only line numbers, offsets and counts.

用法（中文）：把「帧偏大」定位到**区块**（vars / args / 保存寄存器）与**源码行**。编译一次即可。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_CC = str(Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / "ee-gcc")

FRAME_RE = re.compile(r"\.frame\s+\$sp,(\d+),\$31\s*#\s*vars=\s*(\d+),\s*regs=\s*(\d+)/\d+,\s*args=\s*(\d+)")
LOC_RE = re.compile(r"^\s*\.loc\s+(\d+)\s+(\d+)")
MEM_RE = re.compile(r"^\s+(sw|sd|usw|lw|ld|lwu|lh|lhu|sh|sb|lbu)\s+\$(\d+),\s*(-?\d+)\(\$sp\)")


def compile_asm(cc: str, src: Path, include: str, flags: list[str], out: Path, debug: bool) -> str:
    """`-gdwarf-2` gives `.loc` markers but replaces the `.frame` pseudo-op with CFI, so the two
    halves are collected from two compiles."""
    cmd = [cc] + flags + ["-fverbose-asm", "-S", "-o", str(out)]
    if debug:
        cmd.append("-gdwarf-2")
    if include:
        cmd += ["-I", include]
    cmd.append(str(src))
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise SystemExit(f"compile failed: {done.stderr.strip()[:300]}")
    return out.read_text(encoding="utf-8", errors="replace")


def trace_values(asm: str, frame: int, vars_b: int, saves_start: int) -> list[tuple[int, int, int, int | None]]:
    """For every store into the vars block, find the most recent line that defined the stored
    register. Returns `(slot_offset, call_site_line, register, defining_line)`.

    Reading: `(8, 80, 14, 65)` means "at the call on line 80, slot 8 holds register 14, last written
    on line 65" — that value has to survive the call, so line 65 is the thing to restructure.
    """
    loc = re.compile(r"^\s*\.loc\s+(\d+)\s+(\d+)")
    insn = re.compile(r"^\s+([a-z][a-z0-9.]*)\s+([^#\n]*)$")
    line: int | None = None
    last_def: dict[int, int] = {}
    out: list[tuple[int, int, int, int | None]] = []
    for text in asm.splitlines():
        text = text.split("#", 1)[0]
        m = loc.match(text)
        if m:
            line = int(m.group(2))
            continue
        m = insn.match(text)
        if not m or line is None:
            continue
        mnemonic, operands = m.group(1), m.group(2)
        if mnemonic in ("sw", "sd", "usw"):
            mm = re.match(r"^\$(\d+),\s*(-?\d+)\(\$sp\)", operands)
            if mm and 0 <= int(mm.group(2)) < vars_b:
                out.append((int(mm.group(2)), line, int(mm.group(1)), last_def.get(int(mm.group(1)))))
                continue
        first = operands.split(",")[0].strip()
        dm = re.match(r"^\$(\d+)", first)
        if dm:
            last_def[int(dm.group(1))] = line
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="把栈访问映射回源码行（帧偏大的第一诊断）")
    ap.add_argument("--cc", default=DEFAULT_CC)
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--include", default="")
    ap.add_argument("--flags", default="-Os")
    ap.add_argument("--frame", type=int, default=0, help="帧大小；省略则从 .frame 注释读")
    ap.add_argument("--work", type=Path, default=Path(".tmp/spillmap"))
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--trace-values", action="store_true",
                    help="for every vars-block store, report the line that last defined the stored register")
    args = ap.parse_args()

    args.work.mkdir(parents=True, exist_ok=True)
    plain = compile_asm(args.cc, args.src, args.include, args.flags.split(), args.work / "plain.s", False)
    asm = compile_asm(args.cc, args.src, args.include, args.flags.split(), args.work / "annotated.s", True)

    m = FRAME_RE.search(plain)
    if m:
        frame, vars_b, regs, out_args = (int(x) for x in m.groups())
        print(f"frame={frame} B  vars={vars_b}  regs={regs} (8 B each)  args={out_args}")
    else:
        prologue = re.search(r"addiu\s+\$sp,\s*\$sp,\s*-(\d+)", plain)
        frame = args.frame or (int(prologue.group(1)) if prologue else 0)
        vars_b, regs, out_args = 48, 0, 48
        print(f"frame={frame} B (no .frame comment; vars/args defaulted to 48/48 — pass --frame/vars "
              f"if the split matters)")

    saves_start = vars_b + out_args
    accesses: dict[int, list[tuple[str, int, int]]] = defaultdict(list)
    var_of: dict[tuple[int, int], str] = {}
    line = None
    for text in asm.splitlines():
        comment = text.split("#", 1)[1].strip() if "#" in text else ""
        text = text.split("#", 1)[0]
        loc = LOC_RE.match(text)
        if loc:
            line = int(loc.group(2))
            continue
        mem = MEM_RE.match(text)
        if not mem or line is None:
            continue
        op, reg, off = mem.group(1), int(mem.group(2)), int(mem.group(3))
        if off < 0 or off >= frame:
            continue
        accesses[line].append((op, reg, off))
        if comment and 0 <= off < vars_b:
            var_of[(line, off)] = comment

    def block(off: int) -> str:
        if off < vars_b:
            return "vars"
        if off < saves_start:
            return "args"
        return "saves"

    stores, loads = Counter(), Counter()
    slots: Counter = Counter()
    for ln, items in accesses.items():
        for op, _reg, off in items:
            if block(off) != "vars":
                continue
            if op in ("sw", "sd", "usw"):
                stores[ln] += 1
            else:
                loads[ln] += 1
            slots[off // 8] += 1

    if not accesses:
        print("no stack accesses found (is the function using the frame at all?)")
        return 0
    print(f"\nvars 区（0..{vars_b - 1}）访问涉及的源码行：{len(stores) + len(loads) and len({k for k in list(stores) + list(loads)})}")
    print(f"{'line':>6} {'store':>6} {'load':>5}  offsets / spilled variable names")
    for ln in sorted(set(stores) | set(loads), key=lambda k: -(stores[k] + loads[k]))[:args.top]:
        offs = sorted({off for _op, _r, off in accesses[ln] if block(off) == "vars"})
        names = sorted({var_of[(ln, o)] for o in offs if (ln, o) in var_of})
        suffix = f"   {', '.join(names)}" if names else ""
        print(f"{ln:>6} {stores[ln]:>6} {loads[ln]:>5}  {offs}{suffix}")
    if args.trace_values:
        rows = trace_values(asm, frame, vars_b, saves_start)
        print("\nvars-block stores, traced to the value's defining line")
        print(f"{'offset':>7} {'call line':>10} {'reg':>4} {'value defined on line':>22}")
        seen = set()
        for off, call_line, reg, def_line in rows:
            key = (off, call_line, reg, def_line)
            if key in seen:
                continue
            seen.add(key)
            print(f"{off:>7} {call_line:>10} {reg:>4} {str(def_line):>22}")
        print("\nreading: those defining lines are the values that must survive the call; they are the")
        print("         candidates for recomputation after it.")
    if slots:
        print("\nper 8 B slot (vars block):")
        for slot, count in sorted(slots.items()):
            print(f"  slot {slot} ({slot * 8}..{slot * 8 + 7} B): {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
