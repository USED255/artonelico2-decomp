#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for tools/project/data_patch.py. Needs ee-gcc, the asm tree and a baseline link.

The patch decides whether a C object's own data reference may be redirected to the splat data
symbol. A wrong redirect is **invisible to objdiff** (it compares `.text` only): the function
would score 100 and the wrong string would only show up at runtime. That is why the content
check is mandatory, and why it has its own negative control here.

Cases
  1. --check finds the pair and writes nothing
  2. the patch removes every `.text` -> C-data reference, the gate passes, the data bytes stay
  3. a same-length but different literal is refused, and the object is left byte-identical
  4. an asm block with two references (count mismatch) is refused
  5. a second run is a no-op (idempotent)
  6. block_refs reads a real splat block (skipped when the asm tree is absent)

Usage: python3 tools/check/test_data_patch.py

data_patch.py 的测试（需要 ee-gcc、asm 树与基线链接）。

补丁决定 C 对象自产的数据引用能否改指到 splat 数据符号。改错**在 objdiff 里看不见**
（它只比 `.text`）：函数照样 100 分，错的字符串只在运行期暴露。所以内容校验不可省，也必须带负面对照。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "project"))

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


def find_tool(name: str, env: str) -> str | None:
    v = os.environ.get(env)
    if v and Path(v).is_file():
        return v
    hit = shutil.which(name)
    if hit:
        return hit
    for cand in (Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / name,
                 Path.home() / "eecc" / "ps2binutils" / name):
        if cand.is_file():
            return str(cand)
    return None


GCC = find_tool("ee-gcc", "EE_GCC")
READELF = find_tool("mips-ps2-decompals-readelf", "READELF") or find_tool("readelf", "READELF")
IMAGE = ROOT / "build" / "SLPS_258.19.elf"
ASM_SAMPLE = ROOT / "asm" / "cod" / "func_001d7154.s"

if not (GCC and READELF and IMAGE.is_file()):
    print("SKIP: needs ee-gcc, readelf and build/SLPS_258.19.elf (run build.sh first)")
    sys.exit(0)

import data_patch as dp  # noqa: E402
import obj_gate  # noqa: E402

WORK = ROOT / ".tmp" / "data_patch_test"
shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True, exist_ok=True)

print("[0] the baseline image answers symbol and byte queries")
img = dp.Image(IMAGE)
syms = img.symbols()
NAME = "D_008B33E8"
val, size, typ, shndx = syms[NAME]
literal = img.read(val, size).split(b"\0")[0]
check(f"{NAME} is an OBJECT with bytes", typ == 1 and len(literal) > 8, repr(literal))
check("a VMA outside any PT_LOAD reads as None", img.read(0xFFFFFF00, 4) is None)

SRC = WORK / "t.c"
SRC.write_text(
    "extern void sink(const char *, int);\n"
    'void func_test(int n) { sink("%s", n); }\n' % literal.decode("latin-1"),
    encoding="utf-8")
ASM = WORK / "func_test.s"
# The instruction lines carry splat's `/* file-offset VMA word */` comment: the patch keys the
# reference by the instruction offset inside the block, and that offset comes from this comment.
# 指令行带 splat 的 `/* 文件偏移 VMA 字 */` 注释：补丁按块内指令偏移配对，偏移取自这条注释。
ASM.write_text(
    "    .set noreorder\n"
    "glabel func_test\n"
    "    /* 0 00100000 00000000 */  lui $4, %hi(" + NAME + ")\n"
    "    /* 4 00100004 00000000 */  nop\n"
    "    /* 8 00100008 00000000 */  nop\n"
    "    /* C 0010000C 00000000 */  nop\n"
    "    /* 10 00100010 00000000 */  addiu $4, $4, %lo(" + NAME + ")\n"
    "    /* 8 00100008 00000000 */  jal sink\n"
    "    /* C 0010000C 00000000 */  nop\n"
    "endlabel func_test\n", encoding="utf-8")


def compile_to(dst: Path, src: Path) -> bool:
    r = subprocess.run([GCC, "-O2", "-G0", "-falign-functions=4", "-ffunction-sections",
                        "-I", "include", "-c", "-o", str(dst), str(src)],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
    return r.returncode == 0


print("[1] --check pairs the reference and writes nothing")
obj = WORK / "t.o"
check("compile", compile_to(obj, SRC))
before = obj.read_bytes()
ok, msg = dp.patch(obj, "func_test", ASM, IMAGE, check=True)
check("check mode succeeds", ok, msg)
check("check mode writes nothing", obj.read_bytes() == before)

print("[2] the patch removes the .text -> C-data reference and the gate passes")
out = WORK / "t_patched.o"
ok, msg = dp.patch(obj, "func_test", ASM, IMAGE, out=out)
check("patch succeeds", ok, msg)
obj_gate.configure(readelf=READELF, objdir=str(WORK), srcdir=str(WORK), modes={},
                   residual_dir=str(WORK), asm_cod_dir=str(WORK))
check("the unpatched object is refused by the gate",
      obj_gate.bad_sections(str(obj)) != [], repr(obj_gate.bad_sections(str(obj))))
check("the patched object passes the gate", obj_gate.bad_sections(str(out)) == [],
      repr(obj_gate.bad_sections(str(out))))
rel = subprocess.run([READELF, "-rW", str(out)], capture_output=True, text=True).stdout
check("no .rodata reference remains", ".rodata" not in rel, rel[-400:])
check("the reference now names the data symbol", NAME in rel, rel[-400:])

print("[3] a different literal of the same length is refused and the object is left alone")
BAD = WORK / "t_bad.c"
last = chr((literal[-1] + 1) % 0x7F)
BAD.write_text(
    "extern void sink(const char *, int);\n"
    'void func_test(int n) { sink("%s", n); }\n'
    % (literal[:-1].decode("latin-1") + last), encoding="utf-8")
bad_obj = WORK / "t_bad.o"
check("compile", compile_to(bad_obj, BAD))
bad_before = bad_obj.read_bytes()
ok, msg = dp.patch(bad_obj, "func_test", ASM, IMAGE)
check("content mismatch refused", not ok and "content mismatch" in msg, msg)
check("the refused object is unchanged", bad_obj.read_bytes() == bad_before)

print("[4] a reference with no asm counterpart at that offset is refused")
TWO = WORK / "two.s"
TWO.write_text(
    "glabel func_test\n"
    "    /* 0 00100000 00000000 */  lui $4, %hi(" + NAME + ")\n"
    "    /* 4 00100004 00000000 */  nop\n"
    "    /* 8 00100008 00000000 */  nop\n"
    "    /* C 0010000C 00000000 */  nop\n"
    "    /* 20 00100020 00000000 */  addiu $4, $4, %lo(" + NAME + ")\n"
    "endlabel func_test\n", encoding="utf-8")
ok, msg = dp.patch(obj, "func_test", TWO, IMAGE)
check("layout mismatch refused", not ok and "has no %lo" in msg, msg)

print("[5] the patch is idempotent")
ok, msg = dp.patch(out, "func_test", ASM, IMAGE, check=True)
check("second run is a no-op", ok and "nothing to patch" in msg, msg)

print("[6] block_refs reads a real splat block")
if ASM_SAMPLE.is_file():
    refs = dp.block_refs(ASM_SAMPLE.read_text(encoding="utf-8", errors="replace"), "func_001d7154")
    check("a switch table reference is found", refs == [(0x18, "jtbl_00965B58", 0)], repr(refs))
else:
    print("  skip — the asm tree is absent")

print()
if fails:
    print("FAILED: %d" % len(fails))
    sys.exit(1)
print("all data_patch checks passed")
