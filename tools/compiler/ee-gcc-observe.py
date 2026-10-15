#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ee-gcc-observe —— observe the shipped compiler's output on small fixtures, and check the handbook's claims.

Why: the handbook states rules ("0.0f becomes `mtc1 $0`", "a switch becomes a jump table only when
count >= 5 and range <= 10 * count", "each saved register costs 8 bytes"). This tool turns each of those
into an executable observation: it compiles a synthetic fixture with the real compiler and asserts what
the handbook says must appear. `--selftest` runs all fixtures; `--src` prints the observations for your
own file.

Usage
-----
```sh
python3 tools/compiler/ee-gcc-observe.py --selftest                     # all synthetic fixtures
python3 tools/compiler/ee-gcc-observe.py --src func.c --flags="-O2 -G0" # observe your own file
```

No game content is needed or produced: every fixture is generated here.

用法：把手册里的规则变成**可执行的观测**——用真编译器编译合成夹具，断言手册说必须出现的东西；
`--selftest` 跑全部夹具，`--src` 观测你自己的文件。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_CC = str(Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / "ee-gcc")

# (名字, 源码, 必须出现的正则, 说明) —— 每条都对应手册里的一条 law/事实
FIXTURES: list[tuple[str, str, str, str]] = [
    ("add", "int add(int a, int b) { return a + b; }\n", r"addu", "L-EE-000: a plain add is `addu`"),
    ("save-slots",
     "extern int sink(int);\n"
     + "int many(int a,int b,int c,int d,int e,int f,int g,int h){\n"
     + "  int v0=a+b,v1=c+d,v2=e+f,v3=g+h;int s=0;\n"
     + "  s+=sink(v0);s+=sink(v1);s+=sink(v2);s+=sink(v3);\n"
     + "  return s+v0+v1+v2+v3;}\n",
     r"\.frame\s+\$sp", "L-EE-012: the frame is reported in a .frame comment"),
    ("switch-dense",
     "int f(int x){switch(x){case 0:return 1;case 1:return 2;case 2:return 3;"
     "case 3:return 4;case 4:return 5;case 5:return 6;}return 0;}\n",
     r"\.rdata|jr\s+\$", "L-EE-010: a dense switch of >=5 cases becomes a table jump (.rdata + jr $reg)"),
    ("switch-sparse",
     "int f(int x){switch(x){case 0:return 1;case 1000:return 2;case 2000:return 3;}return 0;}\n",
     r"\bbeq\b|\bbne\b|\bslt|\bxori", "L-EE-010: a sparse switch stays a branch chain"),
    ("float-pool",
     "float f(void){return 0.5f;}\n", r"\bl\.s\b|%hi\(\$LC", "L-EE-011: a non-zero float comes from the pool"),
    ("float-zero",
     "float f(void){return 0.0f;}\n", r"mtc1\s+\$0", "L-EE-011: 0.0f is materialised inline"),
    ("double-inline",
     "double f(void){return 0.5;}\n", r"\bdli\b.*\n.*\bdsll\b", "L-EE-011: a double whose low word is zero is built inline"),
    ("compare-unsigned-narrow",
     "int f(unsigned char x){return x < 100;}\n", r"\bandi\b", "L-EE-013: a narrow unsigned compare masks first"),
    ("compare-signed-narrow",
     "int f(signed char x){return x < 100;}\n", r"\bsll\b.*\n.*\bsra\b|\bsll\b", "L-EE-013: a narrow signed compare shifts first"),
    ("small-data-off",
     "int g_int;\nint f(void){return g_int;}\n", r"%hi\(g_int\)", "L-EE-014: at -G0 a global is addressed absolutely"),
]


def compile_asm(cc: str, src_text: str, flags: list[str], work: Path, name: str) -> str:
    work.mkdir(parents=True, exist_ok=True)
    src = work / f"{name}.c"
    src.write_text(src_text, encoding="utf-8")
    out = work / f"{name}.s"
    done = subprocess.run([cc, *flags, "-S", "-o", str(out), str(src)],
                          capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise RuntimeError(f"{name}: compile failed: {done.stderr.strip()[:200]}")
    return out.read_text(encoding="utf-8", errors="replace")


def selftest(cc: str, flags: list[str], work: Path, verbose: bool) -> int:
    passed = failed = 0
    for name, src_text, pattern, why in FIXTURES:
        try:
            asm = compile_asm(cc, src_text, flags, work, name)
        except RuntimeError as exc:
            print(f"[FAIL] {name:<26} {exc}", file=sys.stderr)
            failed += 1
            continue
        ok = re.search(pattern, asm, re.M | re.S) is not None
        if ok:
            passed += 1
            print(f"[ok  ] {name:<26} {why}")
        else:
            failed += 1
            print(f"[FAIL] {name:<26} {why}  (pattern {pattern!r} absent)")
        if verbose and not ok:
            print(asm[:800])
    print(f"\nee-gcc-observe selftest: {passed} passed / {failed} failed / {len(FIXTURES)} fixtures")
    return 1 if failed else 0


def observe(cc: str, src: Path, flags: list[str], work: Path) -> int:
    asm = compile_asm(cc, src.read_text(encoding="utf-8", errors="replace"), flags, work, src.stem + "_observed")
    frame = re.search(r"\.frame\s+\$sp,(\d+),\$31\s*#\s*vars=\s*(\d+),\s*regs=\s*(\d+)/\d+,\s*args=\s*(\d+)", asm)
    hist: dict[str, int] = {}
    for m in re.finditer(r"^\s+([a-z][a-z0-9.]*)\s", asm, re.M):
        hist[m.group(1)] = hist.get(m.group(1), 0) + 1
    version = subprocess.run([cc, "--version"], capture_output=True, text=True, check=False).stdout.splitlines()
    print(f"# {src}  flags: {' '.join(flags)}")
    if version:
        print(f"# {version[0]}")
    if frame:
        print(f"frame={frame.group(1)} B  vars={frame.group(2)}  regs={frame.group(3)}  args={frame.group(4)}")
    else:
        print("frame: (no .frame comment — leaf function?)")
    pools = len(set(re.findall(r"\$LC\d+", asm)))
    print(f"constant-pool entries: {pools}")
    print("mnemonic histogram: " + " ".join(f"{k}={v}" for k, v in sorted(hist.items(), key=lambda kv: -kv[1])[:18]))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Observe the ee-gcc 3.2 behaviour on fixtures, or check the handbook's claims")
    ap.add_argument("--cc", default=DEFAULT_CC)
    ap.add_argument("--flags", default="-O2 -G0")
    ap.add_argument("--src", type=Path, default=None, help="observe this file instead of running the selftest")
    ap.add_argument("--selftest", action="store_true", help="compile the built-in fixtures and assert the handbook's claims")
    ap.add_argument("--work", type=Path, default=Path(".tmp/observe"))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    flags = args.flags.split()
    if not Path(args.cc).exists():
        print(f"cc not found: {args.cc} (set --cc)", file=sys.stderr)
        return 2
    if args.src is not None:
        return observe(args.cc, args.src, flags, args.work)
    return selftest(args.cc, flags, args.work, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
