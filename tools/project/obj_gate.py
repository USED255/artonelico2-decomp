#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The mixed-build safety gate: a C object must not add a non-empty allocatable section outside `.text`.

Why this module exists
----------------------
The gate used to live inside `build_mixed.sh` as a Python heredoc. That made it unusable
anywhere else, so a candidate that `verify()` scored 100 could still be refused by CI
(P-135, measured 2026-10-16: `holds a non-empty allocatable section outside .text:
[('.rodata', 24, '')]`). The code below is the heredoc's logic, moved here unchanged; the
script and the candidate check now share **one** implementation.

Three rules (all three are load-bearing, do not relax them):

1. A C object must have no allocatable section with `size > 0` outside `.text*`, unless
   nothing in `.text*` refers to it. `/DISCARD/` drops such a section, and a referenced one
   would be **silently wrong code**, not a link error.
2. A replaced asm object must hold `.text` only. Removing it would lose data or bss.
3. Each symbol must really be defined in its C object.

P2a (2026-10-03) and the jtbl rule (2026-10-07, P-52) are the two deliberate exceptions;
see `bad_sections()`.

Usage (same arguments as the old heredoc):
  python3 tools/project/obj_gate.py --readelf <readelf> --objdir <dir> --srcdir <dir> \\
      --modes <residual.tsv> --residual-dir <dir> <sym>... -- <src>...

Library use:
  import obj_gate
  msgs = obj_gate.check_objects(syms, srcs, objdir=..., srcdir=..., modes_path=..., residual_dir=...)
  # empty list == the gate passes

混合构建安全闸门：C 对象不得在 `.text` 之外新增非空可分配段。

为什么独立成本模块
------------------
闸门原先写在 `build_mixed.sh` 的 Python heredoc 里，别处用不了 ⇒ `verify()` 给 100 的候选仍会被
CI 拒收（P-135，2026-10-16 实测：`holds a non-empty allocatable section outside .text:
[('.rodata', 24, '')]`）。下面的代码就是那段 heredoc 的逻辑原样搬出；构建脚本与候选复核从此
共用**同一份**实现。

三条规则都承重，别放宽：

1. C 对象里除 `.text*` 外不得有 `size > 0` 的可分配段，除非 `.text*` 没有任何重定位指向它。
   `/DISCARD/` 会丢掉这种段；被引用的那种则得到**静默错码**而不是链接错误。
2. 被替换的 asm 对象必须只有 `.text`，否则摘掉它会丢数据 / bss。
3. 每个符号必须真的在它的 C 对象里定义。

P2a（2026-10-03）与 jtbl 规则（2026-10-07，P-52）是两条刻意的例外，见 `bad_sections()`。

Self-test: python3 tools/check/test_obj_gate.py
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Set by `configure()`; the heredoc read these from `sys.argv`.
READELF = "readelf"
OBJDIR = ""
SRCDIR = ""
MODES = {}
RESIDDIR = ""
ASM_COD_DIR = "build/asm/cod"


def configure(*, readelf: str, objdir: str | Path, srcdir: str | Path,
              modes: dict[str, str], residual_dir: str | Path,
              asm_cod_dir: str | Path = "build/asm/cod") -> None:
    """Set the paths the gate needs. 设置闸门需要的路径。

    `asm_cod_dir` defaults to the build's own path; a test points it somewhere else.
    `asm_cod_dir` 默认就是构建里的路径；测试把它指到别处。
    """
    global READELF, OBJDIR, SRCDIR, MODES, RESIDDIR, ASM_COD_DIR
    READELF, OBJDIR, SRCDIR = str(readelf), str(objdir), str(srcdir)
    MODES, RESIDDIR, ASM_COD_DIR = dict(modes), str(residual_dir), str(asm_cod_dir)


def read_modes(path: str | Path) -> dict[str, str]:
    """Read `<sym>\\t<src>\\t<mode>` rows; return `{sym: mode}`. 读 residual.tsv 的 `{符号: 模式}`。"""
    modes: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3:
                modes[p[0]] = p[2]
    return modes


# Memoised readelf. The gate reads the same object several times (`-SW` from `sections` and
# from `sym_bindings`, `-sW` from `sym_bindings` and `defined_syms`), which is about 2.3e4
# process starts for one run (1.1-1.5 ms each). The cache removes the duplicates; the worker
# pool below removes the serial part. Both keep the output byte for byte identical.
# 记忆化 readelf：闸门会反复读同一个对象（`sections` 与 `sym_bindings` 各跑一次 `-SW`，
# `sym_bindings` 与 `defined_syms` 各跑一次 `-sW`），一次运行约 2.3 万次进程启动
# （每次 1.1~1.5 ms）。缓存去掉重复，下面的线程池去掉串行部分；两者都保证输出逐字不变。
_readelf_cache: dict[tuple, str] = {}


def reset_cache() -> None:
    """Drop the memoised readelf output (tests and repeated runs). 清空 readelf 记忆化缓存。"""
    _readelf_cache.clear()


def readelf_out(args, c_locale: bool = False) -> str:
    key = (tuple(args), c_locale)
    hit = _readelf_cache.get(key)
    if hit is None:
        env = dict(os.environ, LC_ALL="C") if c_locale else None
        hit = subprocess.run([READELF, *args], capture_output=True, text=True, env=env).stdout
        _readelf_cache[key] = hit
    return hit


def sections(obj) -> list[tuple[str, int, str]]:
    """[(name, size, flags)] from `readelf -SW`. 段名 / 大小 / 标志。"""
    out = readelf_out(("-SW", obj))
    res = []
    for line in out.splitlines():
        parts = line.replace("[", " ").replace("]", " ").split()
        ti = None
        for i, t in enumerate(parts):
            if t in ("PROGBITS", "NOBITS", "MIPS_REGINFO", "MIPS_DEBUG"):
                ti = i
                break
        if ti is None or ti < 1:
            continue
        name = parts[ti - 1]
        size = int(parts[ti + 3], 16)
        # The readelf flags can contain lowercase letters (for example .sdata = "WAp").
        # A test for uppercase letters only would miss .sdata and .sbss. The gate would then
        # allow C-generated small data, and the link reports 'discarded section' later (P-24).
        flg = parts[ti + 5] if ti + 5 < len(parts) and re.fullmatch(r"[A-Za-z]+", parts[ti + 5]) else ""
        res.append((name, size, flg))
    return res


def defined_syms(obj) -> set[str]:
    """The defined FUNC and OBJECT symbol names. 已定义的 FUNC/OBJECT 符号名。"""
    out = readelf_out(("-sW", obj))
    names = set()
    for line in out.splitlines():
        p = line.split()
        if len(p) >= 8 and p[0].endswith(":") and p[3] in ("FUNC", "OBJECT") and p[6] != "UND":
            names.add(p[7].split("@")[0])
    return names


def sym_bindings(obj) -> list[tuple[str, str, str, int]]:
    """[(name, bind, secname, size)] of the defined FUNC and OBJECT symbols only.

    只含已定义的 FUNC/OBJECT。
    """
    sec_of = {}
    out = readelf_out(("-SW", obj))
    for line in out.splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)", line)
        if m:
            sec_of[m.group(1)] = m.group(2)
    res = []
    out = readelf_out(("-sW", obj))
    for line in out.splitlines():
        p = line.split()
        if len(p) >= 8 and p[0].endswith(":") and p[3] in ("FUNC", "OBJECT") and p[6] != "UND":
            try:
                size = int(p[2], 16)
            except ValueError:
                size = 0
            res.append((p[7].split("@")[0], p[4], sec_of.get(p[6], "?"), size))
    return res


def text_referenced(obj) -> set[str]:
    """Names that a relocation from a `.text*` section refers to (section symbols and normal symbols).

    2026-10-07 (jtbl pool): after tools/project/jtbl_patch.py redirects the %hi/%lo relocations
    of the C jump table to the existing jtbl_* symbols, no `.text*` relocation refers to the
    `.rodata` in the C object any more. /DISCARD/ therefore drops it, and it cannot change the
    code generation. The gate can allow it. The function counts `.rel.text*` only. A
    `.rel.rodata` section refers back to `.text`, so it does not count.

    2026-10-07（jtbl 池）：`tools/project/jtbl_patch.py` 把 C 自产跳转表的 `%hi/%lo`
    重定位改指到既有的 `jtbl_*` 符号后，C 对象里的 `.rodata` 就**没有任何 `.text*`
    重定位指向**了 ⇒ 它必然被 `/DISCARD/` 丢掉，不可能改变代码生成 ⇒ 可以放行。
    只统计 `.rel.text*`（`.rel.rodata` 是反过来引用 `.text`，不算）。
    """
    out = readelf_out(("-rW", obj), c_locale=True)
    refs, cur = set(), None
    for line in out.splitlines():
        if "R_MIPS_" not in line:
            m = re.search(r"\.rel\.[\w.]+", line)
            if m:
                cur = m.group(0)
            continue
        p = line.split()
        if len(p) >= 5 and cur and cur.startswith(".rel.text"):
            refs.add(p[4])
    return refs


def bad_sections(obj) -> list[tuple[str, int, str]]:
    """Sections that a C object may not hold.

    P2a (2026-10-03): the gate can allow `.sdata*` and `.sbss*` under one condition. The C
    side defines small data symbols as WEAK in these sections, and that definition produces
    the `%gp_rel` code generation. These sections are not in the mixed build linker script, so
    /DISCARD/ drops them. The original asm data object still supplies the real storage and the
    address, because a strong definition wins.
    Condition: every symbol that the section defines must be WEAK. Otherwise the C side
    creates its own data, and the gate refuses it.
    2026-10-07 (jtbl, [P-52]): the gate also allows any non-`.text` allocatable section when no
    `.text*` relocation refers to it (neither a section symbol nor a symbol inside the section
    is named). /DISCARD/ drops it, and no code depends on it.
    Negative control: a `.rodata` section that holds a string literal is referred to by a
    `%hi/%lo` relocation from `.text`, so the gate still refuses it.

    C 对象里「不允许」的段。
    P2a（2026-10-03）：`.sdata*` / `.sbss*` **可以有条件放行** —— C 侧在这些段里 **weak 定义**
    小数据符号，用来拿到 `%gp_rel` 代码生成；这些段不在 mixed build 链接脚本里，会被 /DISCARD/ 丢掉，
    真实存储与地址仍由原 asm 数据对象提供（强定义胜出）。
    条件：该段内定义的**每一个符号都必须是 WEAK**，否则就是「C 自产数据」→ 仍然拒绝。
    2026-10-07（jtbl，[P-52]）：任何非 `.text` 可分配段，只要**没有任何 `.text*` 重定位指向它**
    （节符号或段内符号都没有被提到），同样放行 —— 它会被 /DISCARD/ 丢掉，且没有代码依赖它。
    负面对照：字符串字面量所在 `.rodata` 会被 `.text` 的 `%hi/%lo` 引用 ⇒ 仍然拒绝。
    """
    bad = []
    binds = sym_bindings(obj)          # [(name, bind, secname, size)]
    refs = text_referenced(obj)
    dead = set()
    for (n, s, f) in sections(obj):
        if not ("A" in f and s > 0 and not n.startswith(".text")):
            continue
        if n not in refs and not any(x[0] in refs for x in binds if x[2] == n):
            dead.add(n)
    for (n, s, f) in sections(obj):
        if not ("A" in f and s > 0 and not n.startswith(".text")):
            continue
        if n in dead:
            continue          # no .text* reference, so /DISCARD/ drops it, and the gate is safe
        if n.startswith((".sdata", ".sbss")):
            # Allow a small data section only when the whole section holds WEAK definitions.
            # The section size must equal the sum of the weak symbol sizes. A string literal has
            # no named symbol (or has LOCAL symbols only), so the sizes differ, and the gate
            # refuses it (the P-24 repair).
            weak = sum(x[3] for x in binds if x[2] == n and x[1] == "WEAK")
            named = [x for x in binds if x[2] == n]
            nonweak = [x[0] for x in named if x[1] != "WEAK"]
            if weak != s or nonweak:
                bad.append((n, s, "weak coverage fails (weak=%d/nonweak=%s)" % (weak, ",".join(nonweak[:3]) or "-")))
            continue
        bad.append((n, s, ""))
    return bad


def strict_bad_sections(obj) -> list[tuple[str, int]]:
    """The strict form for an asm object and a residual object: no non-empty allocatable section outside .text*.

    严格版（asm / residual 对象用）：除 .text* 外不得有任何非空可分配段。
    """
    return [(n, s) for (n, s, f) in sections(obj)
            if "A" in f and s > 0 and not n.startswith(".text")]


def check_one(pair) -> list[str]:
    """The failure messages of one symbol. The work is independent per symbol, so a pool can run it.

    单个符号的失败消息。逐符号独立，可放进线程池。
    """
    sym, src = pair
    msgs = []
    cobj = os.path.join(OBJDIR, src + ".o")
    if not os.path.exists(cobj):
        msgs.append("  [FAIL] the C object does not exist: %s" % cobj)
        return msgs
    bad = bad_sections(cobj)
    if bad:
        msgs.append("  [FAIL] %s holds a non-empty allocatable section outside .text: %s (the current mechanism does not place them)" % (cobj, bad))
    if sym not in defined_syms(cobj):
        msgs.append("  [FAIL] %s is not defined in %s" % (sym, cobj))

    aobj = os.path.join(ASM_COD_DIR, "%s.o" % sym)
    if not os.path.exists(aobj):
        msgs.append("  [FAIL] the asm object to replace does not exist: %s" % aobj)
        return msgs
    # The gate treats an asm object and a residual object strictly: no non-empty allocatable section outside .text.
    abad = strict_bad_sections(aobj)
    if abad:
        msgs.append("  [FAIL] %s holds a non-empty allocatable section outside .text: %s. A full removal loses content." % (aobj, abad))

    if MODES.get(sym) == "residual":
        robj = os.path.join(RESIDDIR, sym + ".o")
        if not os.path.exists(robj):
            msgs.append("  [FAIL] the residual object does not exist: %s" % robj)
            return msgs
        rbad = strict_bad_sections(robj)
        if rbad:
            msgs.append("  [FAIL] %s holds a non-empty allocatable section outside .text: %s" % (robj, rbad))
        a_defs = defined_syms(aobj)
        r_defs = defined_syms(robj)
        if sym in r_defs:
            msgs.append("  [FAIL] the residual object still defines the target symbol %s (the C object would redefine it)" % sym)
        expected = {n for n in a_defs if n not in (sym, sym + ".NON_MATCHING")}
        missing = sorted(expected - r_defs)
        if missing:
            msgs.append("  [FAIL] the residual object lost the symbol definitions of the original object: %s (removal breaks the link)" % missing)
    return msgs


def check_objects(syms, srcs, *, readelf, objdir, srcdir, modes_path, residual_dir,
                  asm_cod_dir: str | Path = "build/asm/cod", jobs: int | None = None) -> list[str]:
    """Run the gate over the pairs; return every failure message in input order.

    对全部 (符号, 源) 跑闸门；按输入顺序返回失败消息（空 = 通过）。
    """
    configure(readelf=readelf, objdir=objdir, srcdir=srcdir,
              modes=read_modes(modes_path), residual_dir=residual_dir, asm_cod_dir=asm_cod_dir)
    gate_jobs = max(1, int(jobs or os.environ.get("GATE_JOBS") or (os.cpu_count() or 4)))
    out: list[str] = []
    with ThreadPoolExecutor(max_workers=gate_jobs) as pool:
        # `map` keeps the input order, so the messages print in the same order as the serial loop did.
        # `map` 保序，打印顺序与改造前的串行循环一致。
        for msgs in pool.map(check_one, zip(syms, srcs)):
            out.extend(msgs)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Mixed-build safety gate: no non-.text allocatable section from C")
    ap.add_argument("--readelf", required=True)
    ap.add_argument("--objdir", required=True)
    ap.add_argument("--srcdir", required=True)
    ap.add_argument("--modes", required=True, help="residual.tsv (<sym>\\t<src>\\t<mode>)")
    ap.add_argument("--residual-dir", required=True)
    ap.add_argument("--asm-cod-dir", default="build/asm/cod")
    ap.add_argument("pairs", nargs=argparse.REMAINDER,
                    help="<sym>... -- <src>... (the same shape as the old heredoc)")
    a = ap.parse_args()
    rest = a.pairs
    if "--" not in rest:
        print("usage: obj_gate.py ... <sym>... -- <src>...", file=sys.stderr)
        return 2
    sep = rest.index("--")
    syms, srcs = rest[:sep], rest[sep + 1:]
    if len(syms) != len(srcs):
        print("the symbol and source lists differ in length (%d vs %d)" % (len(syms), len(srcs)), file=sys.stderr)
        return 2
    msgs = check_objects(syms, srcs, readelf=a.readelf, objdir=a.objdir, srcdir=a.srcdir,
                         modes_path=a.modes, residual_dir=a.residual_dir)
    for m in msgs:
        print(m)
    if msgs:
        return 1
    print("  passed: %d C objects supply .text* only, %d replaced asm objects hold .text only, the residual objects keep all symbols"
          % (len(syms), len(syms)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
