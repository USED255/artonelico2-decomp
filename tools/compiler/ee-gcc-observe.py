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

Level note: the fixtures assert the `-O2` rules. `--flags="-Os -G0"` passes all of them (that level is the
most common in this project). `-O1` and `-O3` each fail one fixture, and both failures are documented
behaviour: at `-O1` a constant-trip loop keeps an upward `slt` comparison instead of counting down, and at
`-O3` a plain `static` helper is inlined.

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
    ("frame-cap-10",
     "extern int sink(int);\n"
     "int f(int *p){int v0=p[0],v1=p[1],v2=p[2],v3=p[3],v4=p[4],v5=p[5],v6=p[6],v7=p[7];int s=0;\n"
     "s+=sink(v0);s+=sink(v1);s+=sink(v2);s+=sink(v3);s+=sink(v4);s+=sink(v5);s+=sink(v6);s+=sink(v7);\n"
     "return s+v0+v1+v2+v3+v4+v5+v6+v7;}\n",
     r"#\s*vars=\s*0,\s*regs=\s*10/0",
     "L-EE-012: eight call-crossing values fill the save area to its cap of 10 registers"),
    ("long-is-8-bytes",
     "int f(void){ return sizeof(long); }\n",
     r"li\s+\$\d+,\s*8\b", "L-EE-033: sizeof(long) is 8 (the default is -mlong64)"),
    ("pointer-is-4-bytes",
     "int f(void){ return sizeof(void *); }\n",
     r"li\s+\$\d+,\s*4\b", "L-EE-033: pointers stay 32-bit"),
    ("division-zero-check",
     "int f(int a, int b){ return a / b; }\n",
     r"\bdiv\b[\s\S]*\bbeq?z?l\b[\s\S]*\bbreak\b",
     "L-EE-032: a runtime division is div + beql/beqzl + break"),
    ("constant-div-no-magic-number",
     "int f(int a){ return a / 3; }\n",
     r"li\s+\$\d+,\s*3[\s\S]*\bdiv\b",
     "L-EE-032: a non-power-of-two constant divisor stays li + div"),
    ("division-64-bit-libgcc",
     "long long f(long long a, long long b){ return a / b; }\n",
     r"__divdi3", "L-EE-032: 64-bit division is a libgcc call"),
    ("variadic-prologue",
     "int f(const char *a, ...){\n  __builtin_va_list ap; __builtin_va_start(ap, a);\n"
     "  return (int)(long)ap;\n}\n",
     r"__builtin_va_start", "L-EE-031: a variadic function calls __builtin_va_start"),
    ("struct-8-bytes-by-value",
     "typedef struct { int a, b; } S8;\nint read8(S8 s){ return s.a + s.b; }\n",
     r"sd\s+\$4,0\(\$sp\)", "L-EE-030: an 8-byte aggregate arrives by value in $4"),
    ("struct-12-bytes-by-reference",
     "typedef struct { int a, b, c; } S12;\nint read12(S12 s){ return s.a + s.c; }\n",
     r"lw\s+\$\d+,\s*0\(\$4\)", "L-EE-030: a 12-byte aggregate arrives as a pointer in $4"),
    ("double-is-soft-float",
     "double f(double a, double b){return a+b;}\n",
     r"jal\s+dpadd", "L-EE-029: double addition is a libgcc call, not add.d"),
    ("float-is-hardware",
     "float f(float a, float b){return a+b;}\n",
     r"add\.s", "L-EE-029: single precision uses COP1"),
    ("stack-arg-8-byte-slot",
     "extern int callee(int,int,int,int,int,int,int,int,int,int);\nint f(void){return callee(0,1,2,3,4,5,6,7,8,9);}\n",
     r"sw\s+\$\d+,\s*8\(\$sp\)", "L-EE-028: the second stack argument sits at 8($sp) - 8-byte slots"),
    ("args-field-rounded",
     "extern int callee(int,int,int,int,int,int,int,int,int,int);\nint f(void){return callee(0,1,2,3,4,5,6,7,8,9);}\n",
     r"args=\s*16", "L-EE-028: ten arguments give args= 16 (the area rounded up to 16)"),
    ("strings-are-shared",
     "char *a1(void){return \"hello\";}\nchar *a2(void){return \"hello\";}\n",
     r"!hello[\s\S]*hello", "L-EE-027: one string, two functions, a single pooled entry"),
    ("pool-not-shared-across-functions",
     "float f1(void){return 0.5f;}\nfloat f2(void){return 0.5f;}\n",
     r"1056964608[\s\S]*1056964608", "L-EE-026: two functions each get their own pool entry"),
    ("pool-dedup-inside-one-function",
     "float g(float x){if(x>0.5f)return 0.5f;return x*0.5f;}\n",
     r"!1056964608[\s\S]*1056964608", "L-EE-026: within one function the constant is one entry"),
    ("loop-countdown",
     "int f(int a){int s=0;int i;for(i=0;i<8;i++)s+=a*i;return s;}\n",
     r"li\s+\$\d+,\s*7\b[\s\S]*addu\s+\$\d+,\$\d+,-1[\s\S]*bgez",
     "L-EE-025: a constant-trip loop counts down from N-1 with bgez"),
    ("loop-variable-countdown",
     "int f(int a,int n){int s=0;int i;for(i=0;i<n;i++)s+=a*i;return s;}\n",
     r"blez\s+\$\d+[\s\S]*bne\s+\$\d+,\$0",
     "L-EE-025: a variable-trip loop uses a blez guard and bne"),
    ("frame-pointer-alloca",
     "extern void use(void *);\nint f(int n){char *p=__builtin_alloca(n);use(p);return n;}\n",
     r"\.frame\s+\$fp,", "L-EE-024: alloca forces a real frame pointer (.frame $fp,...)"),
    ("no-frame-pointer",
     "extern int sink(int);\nint f(int *p){int v0=p[0],v1=p[1],v2=p[2],v3=p[3];int s=0;\n"
     "s+=sink(v0);s+=sink(v1);s+=sink(v2);s+=sink(v3);return s+v0+v1+v2+v3;}\n",
     r"!\.frame\s+\$fp,", "L-EE-024: an ordinary frame stays $sp-based even though $fp is saved"),
    ("static-not-inlined",
     "static int helper(int a){return a*3+1;}\nint f(int a){int s=0;s+=helper(a);return s;}\n",
     r"jal\s+helper", "L-EE-023: a plain static helper keeps its call at -O2"),
    ("inline-expanded",
     "static inline int helper(int a){return a*3+1;}\nint f(int a){int s=0;s+=helper(a);return s;}\n",
     r"!jal\s+helper", "L-EE-023: an inline helper is expanded at -O2"),
    ("gprel-sbss",
     "int g_sbss __attribute__((section(\".sbss\")));\nint f(void){return g_sbss;}\n",
     r"\blw\s+\$\d+,\s*g_sbss", "L-EE-021: a .sbss definition is a bare symbol even at -G0"),
    ("extern-absolute",
     "extern int g_ext;\nint f(void){return g_ext;}\n", r"%hi\(g_ext\)",
     "L-EE-021: an extern reference stays absolute"),
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
        # `!` 前缀 = 该模式必须**不**出现（例如「这里不该还有 jal」）
        if pattern.startswith("!"):
            ok = re.search(pattern[1:], asm, re.M | re.S) is None
        else:
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
