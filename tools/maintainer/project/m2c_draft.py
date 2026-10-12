#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate m2c drafts. Turn splat asm/cod/<sym>.s into m2c input and a C draft.

Background (2026-10-04, measured): the standard community setup is m2c
(decompile) and decomp-permuter (converge). This repository already has a Ghidra
draft pipeline and a permuter pipeline. The m2c tool is usually better at
expressions and types that are close to the compiler output. Class F (3,017
functions) and class G (2,509 functions) have 0 hits at this time, so they are
the main hope.

Three input fixes are necessary.

  1. Register names: m2c does not know numeric registers such as `$31` and `$29`.
     It then reports "Unable to determine jump table for jr" by mistake.
     Convert the numbers to ABI names such as `$ra`, `$sp`, and `$v0`.
  2. Remove the splat wrapper (`.include`, `nonmatching`, `glabel`, `endlabel`).
     Keep the `.set` lines and the instruction block. Keep local labels
     `.L<hex>` because m2c knows them. Jump table labels are `jtbl_*` already.
  3. Unknown return type: m2c writes `? func_x(s32);`, which is not valid C.
     The post-processing step changes it to `int`.

Usage:
  python3 tools/maintainer/project/m2c_draft.py emit <sym> <outdir>

生成 m2c 草稿：把 splat 的 asm/cod/<sym>.s 变成 m2c 能吃的输入，并产出 C 草稿。

背景（2026-10-04 `[实测]`）：社区标准搭配是 **m2c（反编译）+ decomp-permuter（收敛）**。
本仓库已有 Ghidra 草稿 + permuter 流水线；m2c 在「贴近编译器原写的表达式/类型」上通常更好，
对 **F 类 3,017 / G 类 2,509**（当前 0 命中）是主要希望。

三个必须的输入适配（缺一不可）：
  1. **寄存器名**：m2c 不认 `$31`/`$29` 这类数字寄存器（会误报 "Unable to determine jump table for jr"），
     必须转成 `$ra`/`$sp`/`$v0`… ABI 名。
  2. **去掉 `.include`/`nonmatching`/`glabel`/`endlabel`** 等 splat 包装，只留 `.set` + 指令块；
     局部标签 `.L<hex>` 保留（m2c 认），跳转表标签本就叫 `jtbl_*`（m2c 认）。
  3. **未知返回类型**：m2c 会写 `? func_x(s32);`（非法 C）——后处理成 `int`。

用法：
  python3 tools/maintainer/project/m2c_draft.py emit <sym> <outdir>
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Make the shared tools in tools/project importable.  让 tools/project 的共享工具可被导入。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project"))
from at2_paths import PROJECT_ROOT as ROOT, WORK_ROOT, ASMDIR, INCLUDE  # noqa: E402  layout independent
M2C = Path.home() / "eecc" / "m2c" / "m2c.py"

REG = {0: "zero", 1: "at", 2: "v0", 3: "v1", 4: "a0", 5: "a1", 6: "a2", 7: "a3",
       8: "t0", 9: "t1", 10: "t2", 11: "t3", 12: "t4", 13: "t5", 14: "t6", 15: "t7",
       16: "s0", 17: "s1", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
       24: "t8", 25: "t9", 26: "k0", 27: "k1", 28: "gp", 29: "sp", 30: "fp", 31: "ra"}

PREAMBLE = """/* Fixed preamble for m2c drafts (types and our own shim) */
typedef signed char s8;      typedef unsigned char u8;
typedef short s16;           typedef unsigned short u16;
typedef int s32;             typedef unsigned int u32;
typedef long long s64;       typedef unsigned long long u64;
typedef float f32;           typedef double f64;
typedef unsigned char undefined1;  typedef unsigned short undefined2;
typedef unsigned int undefined4;   typedef unsigned long long undefined8;
typedef unsigned char byte;  typedef unsigned char code;
typedef unsigned int uint;
/* m2c uses s128/u128 for 128-bit integers (lq/sq and MMI). GCC vector mode
   types make assignment and address-of work. */
typedef int s128 __attribute__((mode(V4SI)));
typedef int u128 __attribute__((mode(V4SI)));   /* Same type as s128. This avoids type errors on s128/u128 assignment. */
typedef int          s64_ __attribute__((unused));
#define NULL 0
/* m2c writes `sp` ($29) directly when it cannot turn a stack access into a local
   variable. This placeholder declaration lets the file compile at least. objdiff
   decides the match. Such drafts usually do not match, but they cost nothing extra. */
extern unsigned char *sp;
/* Common placeholder macros for m2c --valid-syntax. We define them here, so the
   output does not depend on headers outside the workspace. */
typedef s32 M2C_UNK;   typedef s8  M2C_UNK8;
typedef s16 M2C_UNK16; typedef s32 M2C_UNK32; typedef s64 M2C_UNK64;
#define M2C_FIELD(expr, type_ptr, offset) (*(type_ptr)((s8 *)(expr) + (offset)))
#define M2C_BITWISE(type, expr) ((type)(expr))
#define M2C_LIKELY(x) (x)
#define M2C_UNLIKELY(x) (x)
"""


def asm_block(sym: str) -> str | None:
    f = ROOT / "asm" / "cod" / f"{sym}.s"
    if not f.is_file():
        return None
    L = f.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next((i for i, l in enumerate(L) if re.match(r"\s*glabel\s+", l)), None)
    if gi is None:
        return None
    en = next((i for i in range(gi, len(L)) if re.match(r"\s*endlabel\s+", L[i])), len(L) - 1)
    return "\n".join(L[gi:en + 1])


def to_m2c_asm(block: str) -> str:
    """Change numeric registers to ABI names. All other lines stay as they are.

    把数字寄存器换成 ABI 名；其余行保持原样。
    """
    block = re.sub(r"\$(\d{1,2})\b", lambda m: "$" + REG.get(int(m.group(1)), m.group(1)), block)
    return block


def gen(sym: str) -> str | None:
    block = asm_block(sym)
    if block is None:
        return None
    asm = ".set noat\n.set noreorder\n.section .text\n" + to_m2c_asm(block) + "\n"
    tmp = WORK_ROOT / "m2c"
    tmp.mkdir(parents=True, exist_ok=True)
    f = tmp / f"{sym}.m2c.s"
    f.write_text(asm, encoding="utf-8")
    r = subprocess.run([sys.executable, str(M2C), "-t", "mips-gcc-c", "--valid-syntax",
                        "--globals", "used", str(f)],
                       capture_output=True, text=True, cwd=str(tmp))
    out = r.stdout
    if "Decompilation failure" in out or not out.strip():
        return None
    # Do not replace `?` with `M2C_UNK` in the whole file. That replacement
    # breaks the ternary operator `a ? b : c` (measured on 2026-10-04). It caused
    # "parse error before M2C_UNK" in a large part of 2,770 candidates.
    # The option --valid-syntax already handles unknown types.
    # The type inference of m2c is sometimes wrong. For example, m2c stores a
    # pointer argument in a field that it classified as f32. It then reports
    # "incompatible types in assignment".
    # This code relaxes the field type to u32* only at those positions. The
    # storage width of 4 bytes does not change. The code output does not change.
    # objdiff rejects a real error.
    # ⚠️ 不要做全局 `?` → `M2C_UNK` 替换：那会把**三元运算符** `a ? b : c` 打坏（2026-10-04 实测，
    #    造成 2,770 个候选里很大一部分 "parse error before M2C_UNK"）。--valid-syntax 已处理未知类型。
    # m2c 的类型推断偶有错（例如把指针参数存进它判成 f32 的字段）→ "incompatible types in assignment"。
    # 这里只在这些位置把字段类型放宽到 u32*（4 字节存储宽度不变，代码生成不变；真错了 objdiff 会拦下）。
    out = re.sub(r"(M2C_FIELD\([^;\n]*?,\s*)(?:f32|s32|u32)(\s*\*,\s*[^)]*\)\s*=\s*)([A-Za-z_]\w*|&[A-Za-z_]\w*)(;)",
                 lambda m: f"{m.group(1)}u32{m.group(2)}{m.group(3)}{m.group(4)}", out)
    # The build pipeline controls section alignment (objcopy
    # --set-section-alignment=...=4 in compile_sources.py).
    # Do not add __attribute__((aligned(4))) here. ee-gcc 3.2 then reports
    # "alignment may not be specified for ...".
    # 段对齐由构建流水线统一处理（compile_sources.py 的 objcopy --set-section-alignment=...=4），
    # 不要在这里加 __attribute__((aligned(4)))：ee-gcc 3.2 直接报 "alignment may not be specified for ..."。
    return PREAMBLE + "\n" + out


def emit(sym: str, outdir: Path) -> Path | None:
    src = gen(sym)
    if src is None:
        return None
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / f"{sym}.m2c.c"
    p.write_text(src, encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["emit"])
    ap.add_argument("sym")
    ap.add_argument("outdir", nargs="?", default="build/m2c/out")
    a = ap.parse_args()
    p = emit(a.sym, ROOT / a.outdir)
    print(p if p else "(m2c failed)")
    return 0 if p else 1


if __name__ == "__main__":
    sys.exit(main())
