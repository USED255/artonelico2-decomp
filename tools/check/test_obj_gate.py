#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for tools/project/obj_gate.py. No toolchain, no build, no network.

The gate decides whether a C object may replace an asm block. The heredoc it came from had no
tests at all, so a regression there only showed up as a red CI run (P-135). This test pins
every rule with a fake `readelf`: it feeds the exact text shape that the real parser expects,
so it runs on a machine without binutils.

Cases
  1. a C object with .text only                -> pass
  2. a referenced .rodata (a string literal)   -> FAIL (2026-10 negative control)
  3. an unreferenced .rodata                   -> pass (P-52: /DISCARD/ drops it)
  4. .sdata defined WEAK, size matches         -> pass (P2a)
  5. .sdata with a non-WEAK symbol             -> FAIL
  6. a referenced .bss object                  -> FAIL
  7. the target symbol is not defined          -> FAIL
  8. the replaced asm object holds .data       -> FAIL
  9. residual mode: missing object / target redefined / lost symbol / clean -> FAIL,FAIL,FAIL,pass

Usage: python3 tools/check/test_obj_gate.py

obj_gate.py 的测试（不需要工具链 / 构建 / 网络）。闸门原先的 heredoc 没有测试，回归只能靠 CI 变红
（P-135）。本测试用假的 `readelf` 覆盖每条规则：喂给解析器真实格式的文本，因此在没有 binutils 的
机器上也能跑。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "project"))
import obj_gate  # noqa: E402

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


WORK = ROOT / ".tmp" / "obj_gate_test"
shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True, exist_ok=True)


def sec(idx: int, name: str, kind: str, size: int, flags: str = "A") -> str:
    """One `readelf -SW` row. 一行 `readelf -SW`。"""
    return f"  [{idx:2d}] {name:<18} {kind} 00000000 000034 {size:06x} 00 {flags:<3} 0 0 4"


def sym(idx: int, value: int, size: int, kind: str, bind: str, shndx: int, name: str) -> str:
    """One `readelf -sW` row. 一行 `readelf -sW`。"""
    return f"{idx:6d}: {value:08x} {size:5d} {kind} {bind} DEFAULT {shndx:4d} {name}"


def rel_text(name: str, target: str) -> str:
    """A `.rel.text` header plus one row that refers to `target`. 一个 `.rel.text` 段 + 一条指向 target 的行。"""
    return (f"Relocation section '{name}' at offset 0x00000000 contains 1 entries:\n"
            f" Offset     Info    Type            Sym.Value  Sym. Name\n"
            f"00000004  00000105 R_MIPS_HI16       00000000   {target}\n")


class FakeReadelf:
    """Answer `readelf -S/-s/-r` for one object path. 为一个对象路径回答 readelf 的三类查询。"""

    def __init__(self, sections: list[str], syms: list[str], rels: list[str]):
        self.sections = "\n".join(sections)
        self.syms = "\n".join(syms)
        self.rels = "\n".join(rels)

    def __call__(self, args, c_locale: bool = False) -> str:
        flag = args[0]
        if flag == "-SW":
            return self.sections
        if flag == "-sW":
            return self.syms
        if flag == "-rW":
            return self.rels
        return ""


def install(mapping: dict[str, FakeReadelf]) -> None:
    """Point obj_gate at the fake objects. 让 obj_gate 读假对象表。"""
    obj_gate.reset_cache()
    real = obj_gate.readelf_out

    def fake(args, c_locale: bool = False):
        obj = args[-1]
        f = mapping.get(obj)
        if f is None:
            return ""
        # The cache key includes the whole argv; use the fake's own answers per flag.
        return f(args, c_locale)

    obj_gate.readelf_out = fake


def gate(sym: str = "func_test", modes: dict[str, str] | None = None) -> list[str]:
    """Run the gate for one fake symbol. 对一个假符号跑闸门。"""
    obj_gate.configure(readelf="readelf", objdir=str(WORK / "obj"), srcdir="src",
                       modes=modes or {}, residual_dir=str(WORK / "residual"),
                       asm_cod_dir=str(ASM.parent))
    return obj_gate.check_one((sym, sym))


# Every path that `check_one` stats must exist (the gate reads objects, it does not create them).
(WORK / "obj").mkdir(parents=True, exist_ok=True)
(WORK / "residual").mkdir(parents=True, exist_ok=True)
(WORK / "obj" / "func_test.o").write_bytes(b"")
(WORK / "asm").mkdir(parents=True, exist_ok=True)
(WORK / "residual" / "func_test.o").write_bytes(b"")
ASM = WORK / "asm" / "func_test.o"
ASM.parent.mkdir(parents=True, exist_ok=True)
ASM.write_bytes(b"")
TEXT_ONLY = [sec(1, ".text", "PROGBITS", 0x10, "AX")]
TEXT_AND_RO = [sec(1, ".text", "PROGBITS", 0x10, "AX"), sec(2, ".rodata", "PROGBITS", 0x20)]
TARGET = [sym(1, 0, 0x10, "FUNC", "GLOBAL", 1, "func_test")]
REL_RO = [rel_text(".rel.text.func_test", ".rodata")]

print("[0] read_modes")
(WORK / "modes.tsv").write_text("func_a\tsrc_a\tdirect\nfunc_b\tsrc_b\tresidual\n#noise\n", encoding="utf-8")
m = obj_gate.read_modes(WORK / "modes.tsv")
check("read_modes maps sym -> mode", m == {"func_a": "direct", "func_b": "residual"}, repr(m))

print("[1] a C object with .text only passes")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
check("text only passes", gate() == [], repr(gate()))

print("[2] a referenced .rodata (string literal) is refused")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_AND_RO, TARGET + [sym(2, 0, 0x20, "OBJECT", "GLOBAL", 2, ".rodata")], REL_RO),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
msgs = gate()
check("string literal refused", any("non-empty allocatable section outside .text" in x and ".rodata" in x for x in msgs), repr(msgs))

print("[3] an unreferenced .rodata passes (P-52)")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_AND_RO, TARGET, []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
check("dead .rodata passes", gate() == [])

print("[4] .sdata with WEAK definitions passes (P2a)")
sdata_ok = [sec(1, ".text", "PROGBITS", 0x10, "AX"), sec(2, ".sdata", "PROGBITS", 0x8, "WA")]
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(
        sdata_ok, TARGET + [sym(2, 0, 8, "OBJECT", "WEAK", 2, "gp_sym")], [rel_text(".rel.text.func_test", "gp_sym")]),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
check("weak .sdata passes", gate() == [])

print("[5] .sdata with a GLOBAL symbol is refused")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(
        sdata_ok, TARGET + [sym(2, 0, 8, "OBJECT", "GLOBAL", 2, "gp_sym")], [rel_text(".rel.text.func_test", "gp_sym")]),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
check("global .sdata refused", any("weak coverage fails" in x for x in gate()))

print("[6] a referenced .bss object is refused")
bss = [sec(1, ".text", "PROGBITS", 0x10, "AX"), sec(2, ".bss", "NOBITS", 0x4, "WA")]
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(
        bss, TARGET + [sym(2, 0, 4, "OBJECT", "GLOBAL", 2, "static_var")], [rel_text(".rel.text.func_test", "static_var")]),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
check(".bss refused", any(".bss" in x for x in gate()))

print("[7] the target symbol must be defined in the C object")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, [], []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
check("undefined target refused", any("is not defined in" in x for x in gate()))

print("[8] the replaced asm object must hold .text only")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(ASM): FakeReadelf(TEXT_AND_RO, TARGET, []),
})
check("asm with .rodata refused", any("A full removal loses content" in x for x in gate()))

print("[9] residual mode")
(WORK / "residual" / "func_test.o").unlink()
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
})
msgs = gate(modes={"func_test": "residual"})
check("missing residual object refused", any("the residual object does not exist" in x for x in msgs), repr(msgs))
(WORK / "residual" / "func_test.o").write_bytes(b"")
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(WORK / "residual" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
})
msgs = gate(modes={"func_test": "residual"})
check("residual redefining the target refused", any("still defines the target symbol" in x for x in msgs), repr(msgs))
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET + [sym(9, 0, 4, "FUNC", "GLOBAL", 1, "sibling")], []),
    str(WORK / "residual" / "func_test.o"): FakeReadelf(TEXT_ONLY, [], []),
})
msgs = gate(modes={"func_test": "residual"})
check("residual losing a symbol refused", any("lost the symbol definitions" in x for x in msgs), repr(msgs))
install({
    str(WORK / "obj" / "func_test.o"): FakeReadelf(TEXT_ONLY, TARGET, []),
    str(ASM): FakeReadelf(TEXT_ONLY, TARGET + [sym(9, 0, 4, "FUNC", "GLOBAL", 1, "sibling")], []),
    str(WORK / "residual" / "func_test.o"): FakeReadelf(TEXT_ONLY, [sym(9, 0, 4, "FUNC", "GLOBAL", 1, "sibling")], []),
})
check("clean residual passes", gate(modes={"func_test": "residual"}) == [])

print()
if fails:
    print("FAILED: %d" % len(fails))
    sys.exit(1)
print("all obj_gate checks passed")
