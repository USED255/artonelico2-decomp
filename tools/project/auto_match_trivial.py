#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 trivial 档自动匹配器（日版主目标 SLPS_258.19）。

做什么
------
从 `out/evidence/jp_m3_workqueue.tsv`（由 tools/report/m3_workqueue.py 生成）里取出
**trivial（<17 B）且 hybrid_ok=1** 的函数，逐个读 `routebjp/asm/cod/<sym>.s`，
用少量**能逐条指令确定语义**的形状识别器反推出候选 C，然后：

  1. 把所有候选 C 合成一个 probe 文件，用 ee-gcc 3.2-ee-040921
     `-O2 -falign-functions=4 -ffunction-sections` 编译；
  2. 把同名函数从 per-function asm 抽成 target.s，用 mips-ps2-decompals-as 汇编；
  3. 一次 objdiff 逐符号比对，**只保留 match_percent == 100.0** 的；
  4. 对没匹配上的形状，换下一个候选变体再比（变体只改等价写法/语句顺序，不改语义）。

不做的事：不猜语义。识别不了的形状直接归入 `unrecognized`，拿不准的不生成。

用法
----
  python3 routebjp/tools/auto_match_trivial.py scan          # 只统计形状分布
  python3 routebjp/tools/auto_match_trivial.py run           # 生成+编译+objdiff（不落地）
  python3 routebjp/tools/auto_match_trivial.py apply         # 把 100% 的写入 src/matched + 清单
  python3 routebjp/tools/auto_match_trivial.py all           # scan + run + apply

幂等：已在 config/matched_symbols.txt 里的符号不会再尝试；apply 时重写清单中的
M3 段（标记之间），不动 M2 样板段。
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

from at2_paths import (  # noqa: E402  布局无关的路径解析（说明见 at2_paths.py 顶部）
    PROJECT_ROOT as ROOT,
    PRIVATE_ROOT,
    EVIDENCE_ROOT,
    WORK_ROOT,
    MATCHED_LIST,
    SRCDIR,
    FLAGS_TSV,
    ASMDIR,
    WORKQUEUE,
    GCC,
    AS,
    OBJDIFF,
)

REPO = PRIVATE_ROOT or ROOT          # 兼容旧名：私有工作面（.tmp/permvenv、out/evidence）
BUILDDIR = WORK_ROOT / "m2" / "m3pilot"
# 与 build_hybrid.sh 的 MATCHED_CFLAGS 完全一致：只有在这里 100% 的才会在混合构建里 100%
CFLAGS = ["-O2", "-falign-functions=4", "-ffunction-sections"]

# 编译档矩阵（P-32/P-40/轮次 64）：形状**在不同档位下可能才命中**。
# 后出现的 -O 覆盖前面的（gcc 取最后一个），所以额外标志一律排在 CFLAGS 之后。
# ⚠️ 2026-10-07：m2c 侧靠 -Os 多出 110 个、Ghidra 侧多出 40 个 ⇒ 形状库也必须扫全矩阵，
#    否则同一个漏档问题会在这里重演第三次。
FLAG_MATRIX = [[x if x.startswith("-") else "-" + x for x in item.split()] for item in (
    "Os", "O2", "O1", "O3", "O2 -G8", "O1 -G8", "O3 -G8",
    "O2 -fno-common", "O2 -fomit-frame-pointer", "O1 -fomit-frame-pointer", "O2 -fno-builtin",
)]


def flag_key(fs) -> str:
    return "".join(fs).replace("-", "")

M3_BEGIN = "# ---- M3 trivial 自动匹配（auto_match_trivial.py 生成，勿手改本段）----"
M3_END = "# ---- M3 段结束 ----"

A0, A1, A2, A3 = "$4", "$5", "$6", "$7"
V0, ZERO, GP, RA = "$2", "$0", "$28", "$31"
ARG_OF_REG = {A0: 0, A1: 1, A2: 2, A3: 3}
CARG = ["a", "b", "c", "d"]
PTR_ARGS = ["p"] + CARG          # 第一个参数固定叫 p（基址指针），其余 a,b,c
QPTR_ARGS = ["p", "q"] + CARG    # 两个指针 p,q，其余 a,b,c

# 载入/存储指令 -> C 访问类型
LOADS = {
    "lb": "signed char", "lbu": "unsigned char",
    "lh": "short", "lhu": "unsigned short",
    "lw": "int", "lwu": "unsigned int",
    "ld": "long long", "lwc1": "float",
}
STORES = {"sb": "char", "sh": "short", "sw": "int", "sd": "long long", "swc1": "float"}
# 形参类型：整型参数一律用 int（C 的窄类型实参需要截断，会多出 sll/sra 指令）
PARAM_T = {"sb": "int", "sh": "int", "sw": "int", "sd": "long long", "swc1": "float"}
TYPE_OF = {**LOADS, **STORES}    # 任意访存指令 -> C 访问类型
# 浮点参数寄存器 $f12,$f13,$f14 -> 第 1/2/3 个 float 形参
FARG_OF_REG = {"$f12": 0, "$f13": 1, "$f14": 2}


def ptr_val_name(reg):
    """基址指针占用 $4 后，$5/$6/$7 依次对应 C 形参 a/b/c。"""
    return CARG[ARG_OF_REG[reg] - 1]


# --------------------------------------------------------------------------
# 反汇编解析
# --------------------------------------------------------------------------
INS_RE = re.compile(r"/\*.*?\*/\s*(.*)$")


def glabels(sym: str):
    """asm/cod/<sym>.s 里出现的全部 glabel（有些文件含多个函数）。"""
    path = ASMDIR / f"{sym}.s"
    if not path.exists():
        return None
    return re.findall(r"^\s*glabel\s+(\S+)", path.read_text(encoding="utf-8",
                                                           errors="replace"), re.M)


def trailing_instructions(sym: str):
    """endlabel 之后、下一个 glabel 之前的指令条数（splat 的段内填充，如尾部 nop）。

    这些字节在 asm .o 的 .text 里真实存在；C 编译产物不会有，
    若把该 asm .o 整份摘掉，布局会短掉 4 字节 → sha1 不一致。故必须排除。
    """
    path = ASMDIR / f"{sym}.s"
    if not path.exists():
        return 0
    n, seen_end = 0, False
    for line in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        if re.match(r"\s*endlabel\s+", line):
            seen_end = True
            continue
        if re.match(r"\s*glabel\s+", line) and seen_end:
            break
        if seen_end and INS_RE.search(line.rstrip()):
            n += 1
    return n


def load_body(sym: str):
    """读 per-function .s，返回 (instructions, raw_hex_words)。"""
    path = ASMDIR / f"{sym}.s"
    if not path.exists():
        return None, None
    txt = path.read_text(encoding="utf-8", errors="replace")
    ins, hexes = [], []
    started = False
    for line in txt.split("\n"):
        if re.match(r"\s*glabel\s+", line):
            started = True
            continue
        if re.match(r"\s*endlabel\s+", line):
            break
        if not started:
            continue
        m = INS_RE.search(line.rstrip())
        if not m or not m.group(1).strip():
            continue
        h = re.search(r"/\*\s*([0-9A-Fa-f]+)\s+([0-9A-Fa-f]{8})\s*\*/", line)
        hexes.append(h.group(2) if h else None)
        ins.append(re.sub(r"\s+", " ", m.group(1).strip()))
    return ins, hexes


def split_ops(s: str):
    """'lw $2, 0x18($4)' -> ('lw', ['$2', '0x18($4)'])"""
    if " " not in s:
        return s, []
    mn, rest = s.split(" ", 1)
    return mn, [x.strip() for x in rest.split(",")]


MEM_RE = re.compile(r"^(0x[0-9A-Fa-f]+|%gp_rel\((\w+)\)|%lo\((\w+)\))\((\$\w+)\)$")


class Mem:
    __slots__ = ("mn", "reg", "off", "sym", "base", "kind")

    def __init__(self, mn, reg, addr):
        self.mn, self.reg = mn, reg
        self.base = self.off = self.sym = self.kind = None
        m = MEM_RE.match(addr)
        if not m:
            self.kind = "unknown"
            return
        if m.group(2):
            self.kind, self.sym = "gp", m.group(2)
        elif m.group(3):
            self.kind, self.sym = "lo", m.group(3)
        else:
            self.kind, self.off = "off", int(m.group(1), 16)
        self.base = m.group(4)


def parse_mem(s: str):
    mn, ops = split_ops(s)
    if mn not in LOADS and mn not in STORES:
        return None
    if len(ops) != 2:
        return None
    return Mem(mn, ops[0], ops[1])


def parse_imm(tok: str):
    try:
        return int(tok.strip(), 0)
    except ValueError:
        return None


def arglist(types, names):
    return ", ".join(f"{t} {n}" for t, n in zip(types, names))


def L(m: Mem, base="p"):
    """C 侧的访存表达式（load 或 store 左值）。"""
    return f"*({TYPE_OF[m.mn]} *)({base} + {m.off})"


def perm_variants(stmts, limit=6):
    """同一组语句的不同书写顺序（gcc 调度对顺序敏感）——语义等价。"""
    out = []
    for p in itertools.permutations(stmts):
        if p not in out:
            out.append(p)
        if len(out) >= limit:
            break
    return out


def wrap_void(sym, sig, variants_stmts):
    return [f"void {sym}({sig}) {{ " + " ".join(s) + " }" for s in variants_stmts]


# --------------------------------------------------------------------------
# 形状识别器
# --------------------------------------------------------------------------
def recognizers():
    """返回 [(shape, matcher)]，matcher(ins, sym) -> (bodies, externs) 或 None"""
    R = []

    def reg(shape):
        def deco(fn):
            R.append((shape, fn))
            return fn
        return deco

    def tail(ins):
        """最后两条是 jr $31 + 延迟槽。"""
        return len(ins) >= 2 and ins[-2] == "jr $31"

    # ---------- 绝对寻址的全局数据访问（lui %hi(D) + %lo(D)）----------
    # 2026-10-03 新增：旧口径把「引用 .rodata/.data 符号」一律排除（workqueue 的 data_ref），
    # 但 C 里写 `extern int D_x;` 在无 -G 时同样产出 lui/%lo 绝对寻址 —— M2 样板 baseelf_19
    # 已实测 objdiff 100%（本文件即该形状）。真正阻塞的是 gp 相对寻址与跳转表，见
    # tools/report/m3_workqueue.py 的 eligible 口径。
    def _data_sym(tok):
        m = re.fullmatch(r"%(?:hi|lo)\((\w+)\)", tok)
        return m.group(1) if m else None

    def _lo_mem(tok):
        """%lo(D)($R) -> (D, $R)"""
        m = re.fullmatch(r"%lo\((\w+)\)\((\$\w+)\)", tok)
        return (m.group(1), m.group(2)) if m else (None, None)

    @reg("ret_data_load")
    def _retdl(ins, sym):
        core = [i for i in ins if i != "nop"]
        if len(core) != 3 or core[1] != "jr $31":
            return None
        a = split_ops(core[0])
        if a[0] != "lui" or len(a[1]) != 2:
            return None
        d = _data_sym(a[1][1])
        if not d:
            return None
        c = split_ops(core[2])
        if c[0] not in LOADS or len(c[1]) != 2 or c[1][0] != V0:
            return None
        dsym, base = _lo_mem(c[1][1])
        if dsym != d or base != a[1][0]:
            return None
        t = LOADS[c[0]]
        return [f"{t} {sym}(void) {{ return {d}; }}",
                f"{t} {sym}(void) {{ return *({t} *)&{d}; }}"], [(d, t)]

    @reg("ret_data_addr")
    def _retda(ins, sym):
        core = [i for i in ins if i != "nop"]
        if len(core) != 3 or core[1] != "jr $31":
            return None
        a = split_ops(core[0])
        if a[0] != "lui" or len(a[1]) != 2 or a[1][0] != V0:
            return None
        d = _data_sym(a[1][1])
        if not d:
            return None
        c = split_ops(core[2])
        if c[0] != "addiu" or len(c[1]) != 3 or c[1][0] != V0 or c[1][1] != V0:
            return None
        if _data_sym(c[1][2]) != d:
            return None
        return [f"int {sym}(void) {{ return (int)&{d}; }}",
                f"unsigned {sym}(void) {{ return (unsigned)&{d}; }}",
                f"long {sym}(void) {{ return (long)&{d}; }}"], [(d, "char")]

    @reg("store_data")
    def _std(ins, sym):
        core = [i for i in ins if i != "nop"]
        if len(core) != 3 or core[1] != "jr $31":
            return None
        a = split_ops(core[0])
        if a[0] != "lui" or len(a[1]) != 2:
            return None
        d = _data_sym(a[1][1])
        if not d:
            return None
        c = split_ops(core[2])
        if c[0] not in STORES or len(c[1]) != 2:
            return None
        dsym, base = _lo_mem(c[1][1])
        if dsym != d or base != a[1][0]:
            return None
        t, src = TYPE_OF[c[0]], c[1][0]
        if src == ZERO:
            return [f"void {sym}(void) {{ {d} = 0; }}"], [(d, t)]
        if src in ARG_OF_REG:
            i = ARG_OF_REG[src]
            return [f"void {sym}({arglist([PARAM_T[c[0]]] * (i + 1), CARG[:i + 1])}) "
                    f"{{ {d} = {CARG[i]}; }}"], [(d, t)]
        return None

    @reg("store_data_const")
    def _stdc(ins, sym):
        core = [i for i in ins if i != "nop"]
        if len(core) != 4 or core[2] != "jr $31":
            return None
        a = split_ops(core[0])
        if a[0] != "addiu" or len(a[1]) != 3 or a[1][1] != ZERO:
            return None
        k = parse_imm(a[1][2])
        if k is None:
            return None
        tmp = a[1][0]
        b = split_ops(core[1])
        if b[0] != "lui" or len(b[1]) != 2:
            return None
        d = _data_sym(b[1][1])
        if not d:
            return None
        c = split_ops(core[3])
        if c[0] not in STORES or len(c[1]) != 2 or c[1][0] != tmp:
            return None
        dsym, base = _lo_mem(c[1][1])
        if dsym != d or base != b[1][0]:
            return None
        return [f"void {sym}(void) {{ {d} = {k}; }}"], [(d, STORES[c[0]])]

    # ---------- 空函数 ----------
    @reg("empty")
    def _empty(ins, sym):
        if ins == ["jr $31", "nop"]:
            return [f"void {sym}(void) {{}}"], []
        return None

    # ---------- 常量返回 / 转发 ----------
    @reg("ret_const")
    def _retc(ins, sym):
        if len(ins) != 2 or ins[0] != "jr $31":
            return None
        mn, ops = split_ops(ins[1])
        if mn == "daddu" and ops == [V0, ZERO, ZERO]:
            return [f"int {sym}(void) {{ return 0; }}"], []
        if mn == "addiu" and len(ops) == 3 and ops[0] == V0 and ops[1] == ZERO:
            k = parse_imm(ops[2])
            if k is None:
                return None
            return [f"int {sym}(void) {{ return {k}; }}"], []
        return None

    @reg("ret_arg")
    def _reta(ins, sym):
        if len(ins) != 2 or ins[0] != "jr $31":
            return None
        mn, ops = split_ops(ins[1])
        if mn == "daddu" and len(ops) == 3 and ops[0] == V0 and ops[2] == ZERO:
            r = ops[1]
            if r not in ARG_OF_REG:
                return None
            i = ARG_OF_REG[r]
            return [f"int {sym}({arglist(['int'] * (i + 1), CARG[:i + 1])}) "
                    f"{{ return {CARG[i]}; }}"], []
        if mn == "addiu" and len(ops) == 3 and ops[0] == V0 and ops[1] in ARG_OF_REG:
            k = parse_imm(ops[2])
            if k is None:
                return None
            i = ARG_OF_REG[ops[1]]
            types = ["int"] * (i + 1)
            names = CARG[: i + 1]
            op = "+" if k >= 0 else "-"
            a = abs(k)
            variants = [
                f"int {sym}({arglist(types, names)}) {{ return {CARG[i]} {op} {a}; }}",
            ]
            # 地址运算写法（gcc 会直接把结果算进 $2）
            if k % 4 == 0:
                variants.append(
                    f"int {sym}({arglist(['int *'] * (i + 1), names)}) "
                    f"{{ return (int)&{CARG[i]}[{k // 4}]; }}")
            variants.append(
                f"char *{sym}({arglist(['char *'] * (i + 1), names)}) "
                f"{{ return {CARG[i]} {op} {a}; }}")
            return variants, []
        return None

    # ---------- 单个 load 返回（基址 = 第一个参数）----------
    @reg("ret_load_arg0")
    def _retl(ins, sym):
        if len(ins) != 2 or ins[0] != "jr $31":
            return None
        m = parse_mem(ins[1])
        if not m or m.mn not in LOADS or m.kind != "off" or m.base != A0 or m.reg != V0:
            return None
        t = LOADS[m.mn]
        return [f"{t} {sym}(char *p) {{ return {L(m)}; }}"], []

    # ---------- 单个 store（基址 = 第一个参数）----------
    @reg("store_arg0")
    def _st(ins, sym):
        if len(ins) != 2 or ins[0] != "jr $31":
            return None
        m = parse_mem(ins[1])
        if not m or m.mn not in STORES or m.kind != "off" or m.base != A0:
            return None
        t = STORES[m.mn]
        if m.reg == ZERO:
            return [f"void {sym}(char *p) {{ {L(m)} = 0; }}"], []
        if m.reg not in ARG_OF_REG or m.reg == A0:
            return None
        i = ARG_OF_REG[m.reg]
        types = ["char *"] + [PARAM_T[m.mn]] * i
        names = ["p"] + CARG[:i]
        body = f"void {sym}({arglist(types, names)}) {{ {L(m)} = {ptr_val_name(m.reg)}; }}"
        return [body], []

    # ---------- 浮点存取 ----------
    @reg("float_mem")
    def _fm(ins, sym):
        if len(ins) != 2 or ins[0] != "jr $31":
            return None
        m = parse_mem(ins[1])
        if not m or m.mn not in ("lwc1", "swc1") or m.kind != "off" or m.base != A0:
            return None
        if m.mn == "lwc1":
            if m.reg != "$f0":
                return None
            return [f"float {sym}(char *p) {{ return {L(m)}; }}"], []
        if m.reg not in FARG_OF_REG:
            return None
        i = FARG_OF_REG[m.reg]
        types = ["char *"] + ["float"] * (i + 1)
        names = ["p"] + CARG[:i + 1]
        return [f"void {sym}({arglist(types, names)}) {{ {L(m)} = {CARG[i]}; }}"], []

    # ---------- gp_rel：全局变量读写（纯 C 无法产生 gp_rel，见报告）----------
    @reg("gp_global")
    def _gp(ins, sym):
        if len(ins) != 2 or ins[0] != "jr $31":
            return None
        m = parse_mem(ins[1])
        if not m or m.kind != "gp" or m.base != GP:
            return None
        if m.mn in LOADS:
            if m.reg != V0:
                return None
            t = LOADS[m.mn]
            return [f"{t} {sym}(void) {{ return {m.sym}; }}"], [(m.sym, t)]
        t = STORES[m.mn]
        if m.reg == ZERO:
            return [f"void {sym}(void) {{ {m.sym} = 0; }}"], [(m.sym, t)]
        if m.reg not in ARG_OF_REG:
            return None
        i = ARG_OF_REG[m.reg]
        types = [t] * (i + 1)
        return [f"void {sym}({arglist(types, CARG[:i + 1])}) "
                f"{{ {m.sym} = {CARG[i]}; }}"], [(m.sym, t)]

    # ---------- 比较/布尔返回（含一次 load）----------
    @reg("ret_bool")
    def _bool(ins, sym):
        # 形态 A：load -> jr -> 比较
        if tail(ins) and len(ins) == 3:
            m = parse_mem(ins[0])
            if m and m.mn in LOADS and m.kind == "off" and m.base == A0 and m.reg == V0:
                mn, ops = split_ops(ins[2])
                if mn in ("sltu", "slt") and ops == [V0, ZERO, V0]:
                    cmp_ = "!= 0" if mn == "sltu" else "> 0"
                    return [f"int {sym}(char *p) {{ return {L(m)} {cmp_}; }}"], []
                if mn == "sltiu" and ops[:2] == [V0, V0]:
                    k = parse_imm(ops[2])
                    if k == 1:
                        return [f"int {sym}(char *p) {{ return {L(m)} == 0; }}",
                                f"int {sym}(char *p) {{ return !{L(m)}; }}"], []
                    if k is not None:
                        return [f"int {sym}(char *p) {{ return (unsigned){L(m)} < {k}; }}"], []
                if mn == "slt" and ops[:2] == [V0, V0] and ops[2] == ZERO:
                    return [f"int {sym}(char *p) {{ return {L(m)} < 0; }}"], []
        # 形态 B：load -> 变换 -> jr -> 比较
        if tail(ins) and len(ins) == 4:
            m = parse_mem(ins[0])
            mn1, o1 = split_ops(ins[1])
            mn2, o2 = split_ops(ins[3])
            if (m and m.mn in LOADS and m.kind == "off" and m.base == A0 and m.reg == V0):
                if mn1 == "xori" and o1[:2] == [V0, V0] and mn2 == "sltiu" and o2[:2] == [V0, V0]:
                    k, kk = parse_imm(o1[2]), parse_imm(o2[2])
                    if k is not None and kk == 1:
                        return [f"int {sym}(char *p) {{ return {L(m)} == {k}; }}"], []
                if mn1 == "addiu" and o1[:2] == [V0, V0] and mn2 == "sltiu" and o2[:2] == [V0, V0]:
                    d, n = parse_imm(o1[2]), parse_imm(o2[2])
                    if d is not None and n is not None:
                        # addiu 的立即数是有符号的：$2 = $2 + d
                        return [f"int {sym}(char *p) {{ return (unsigned)({L(m)} + ({d})) < {n}; }}",
                                f"int {sym}(char *p) {{ return (unsigned)({L(m)} - ({-d})) < {n}; }}"], []
                if mn1 == "lh" and mn2 == "srl":
                    pass
            # xori $2,$R,K ; jr ; sltiu $2,$2,1  （无 load）
            if mn1 == "xori" and len(o1) == 3 and o1[0] == V0 and o1[1] in ARG_OF_REG \
                    and mn2 == "sltiu" and o2[:2] == [V0, V0]:
                k, kk = parse_imm(o1[2]), parse_imm(o2[2])
                if k is not None and kk == 1:
                    i = ARG_OF_REG[o1[1]]
                    types = ["int"] * (i + 1)
                    return [f"int {sym}({arglist(types, CARG[:i + 1])}) "
                            f"{{ return {CARG[i]} == {k}; }}"], []
            # lbu/lb/lh: load -> 变换 -> jr -> 变换  （已覆盖上面）
        # 形态 C：slti $2,$4,K ; jr ; xori $2,$2,1   => a >= K
        if tail(ins) and len(ins) == 3:
            mn1, o1 = split_ops(ins[0])
            mn2, o2 = split_ops(ins[2])
            if mn1 == "slti" and len(o1) == 3 and o1[0] == V0 and o1[1] == A0 \
                    and mn2 == "xori" and o2[:2] == [V0, V0] and parse_imm(o2[2]) == 1:
                k = parse_imm(o1[2])
                if k is not None:
                    return [f"int {sym}(int a) {{ return a >= {k}; }}",
                            f"int {sym}(int a) {{ return (a < {k}) == 0; }}"], []
            if mn1 == "slti" and len(o1) == 3 and o1[0] == A0 and o1[1] == A0 \
                    and mn2 == "daddu" and o2 == [V0, A0, ZERO]:
                k = parse_imm(o1[2])
                if k is not None:
                    return [f"int {sym}(int a) {{ return a < {k}; }}"], []
            if mn1 == "andi" and len(o1) == 3 and o1[0] == V0 and o1[1] == A0 \
                    and mn2 == "xori" and o2[:2] == [V0, V0]:
                mk, xk = parse_imm(o1[2]), parse_imm(o2[2])
                if mk is not None and xk is not None:
                    return [f"int {sym}(unsigned a) {{ return (a & {mk}) ^ {xk}; }}"], []
        # 形态 D：lbu $2,o($4) ; andi $2,$2,M ; jr ; andi $2,$2,0xFF
        if tail(ins) and len(ins) == 4:
            m = parse_mem(ins[0])
            mn1, o1 = split_ops(ins[1])
            mn2, o2 = split_ops(ins[3])
            if m and m.mn == "lbu" and m.kind == "off" and m.base == A0 and m.reg == V0 \
                    and mn1 == "andi" and o1[:2] == [V0, V0] and mn2 == "andi" \
                    and o2[:2] == [V0, V0] and parse_imm(o2[2]) == 0xFF:
                mk = parse_imm(o1[2])
                if mk is not None:
                    return [f"int {sym}(char *p) {{ return (unsigned char)({L(m)} & {mk}); }}",
                            f"int {sym}(char *p) {{ return (unsigned short)({L(m)} & {mk}); }}"], []
        # 形态 E：lh $2,o($4) ; nor $2,$0,$2 ; jr ; srl $2,$2,31
        if tail(ins) and len(ins) == 4:
            m = parse_mem(ins[0])
            mn1, o1 = split_ops(ins[1])
            mn2, o2 = split_ops(ins[3])
            if m and m.mn in ("lh", "lw") and m.kind == "off" and m.base == A0 and m.reg == V0 \
                    and mn1 == "nor" and o1 == [V0, ZERO, V0] and mn2 == "srl" \
                    and o2[:2] == [V0, V0] and parse_imm(o2[2]) == 31:
                return [f"unsigned {sym}(char *p) {{ return (unsigned)(~{L(m)}) >> 31; }}",
                        f"int {sym}(char *p) {{ return {L(m)} >= 0; }}"], []
        return None

    # ---------- 双指针拷贝 / 索引 load / 索引 store ----------
    @reg("mem_two_ptr")
    def _two(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        m1, m2 = parse_mem(ins[0]), parse_mem(ins[2])
        if not m1 or not m2 or m1.kind != "off" or m2.kind != "off":
            return None
        if m1.mn in LOADS and m2.mn in STORES and m1.reg == m2.reg:
            if m1.base == A0 and m2.base == A1:
                t1, t2 = LOADS[m1.mn], STORES[m2.mn]
                return [f"{t1} {sym}(char *p, char *q) {{ {t1} v = {L(m1)}; "
                        f"*({t2} *)(q + {m2.off}) = v; return v; }}",
                        f"void {sym}(char *p, char *q) {{ "
                        f"*({t2} *)(q + {m2.off}) = {L(m1)}; }}"], []
        return None

    @reg("idx_load")
    def _idx(ins, sym):
        if not tail(ins) or len(ins) not in (3, 4):
            return None
        # 地址 = p + (i << S) [+ off]
        if len(ins) == 4:
            mn0, o0 = split_ops(ins[0])
            mn1, o1 = split_ops(ins[1])
            if mn0 != "sll" or len(o0) != 3 or mn1 != "addu" or len(o1) != 3:
                return None
            ireg, s = o0[1], parse_imm(o0[2])
            if ireg not in ARG_OF_REG or s is None:
                return None
            acc = o0[0]
            if o1[0] != acc or A0 not in o1[1:] or ireg not in o1[1:]:
                return None
            m = parse_mem(ins[3])
            if not m or m.mn not in LOADS or m.kind != "off" or m.reg != V0 or m.base != acc:
                return None
            ii = ARG_OF_REG[ireg]
            t = LOADS[m.mn]
            esz = {"lb": 1, "lbu": 1, "lh": 2, "lhu": 2, "lw": 4, "lwu": 4, "ld": 8}[m.mn]
            vs = []
            if m.off % esz == 0:
                vs.append(f"{t} {sym}({t} *p, int i) {{ return p[i + {m.off // esz}]; }}")
            vs.append(f"{t} {sym}(char *p, int i) "
                      f"{{ return *({t} *)(p + (i << {s}) + {m.off}); }}")
            return vs, []
        # 地址 = p + i
        mn0, o0 = split_ops(ins[0])
        m = parse_mem(ins[2])
        if mn0 != "addu" or len(o0) != 3 or m is None:
            return None
        if m.mn not in ("lb", "lh", "lw") or m.kind != "off" or m.reg != V0:
            return None
        if A0 not in o0[1:] or m.base not in o0[1:]:
            return None
        ireg = o0[1] if o0[2] == A0 else o0[2]
        if ireg not in ARG_OF_REG:
            return None
        t = LOADS[m.mn]
        return [f"{t} {sym}(char *p, int i) {{ return p[i + {m.off}]; }}",
                f"{t} {sym}(char *p, int i) {{ return *({t} *)(p + i + {m.off}); }}"], []

    @reg("idx_store")
    def _idxs(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        mn0, o0 = split_ops(ins[0])
        mn1, o1 = split_ops(ins[1])
        m = parse_mem(ins[3])
        if mn0 != "sll" or len(o0) != 3 or mn1 != "addu" or len(o1) != 3 or not m:
            return None
        ireg, s = o0[1], parse_imm(o0[2])
        if ireg not in ARG_OF_REG or s is None:
            return None
        if o1[0] != A0 or A0 not in o1[1:] or ireg not in o1[1:]:
            return None
        if m.mn not in STORES or m.kind != "off" or m.base != A0 or m.reg not in ARG_OF_REG:
            return None
        t = STORES[m.mn]
        return [f"void {sym}(char *p, {PARAM_T[m.mn]} {ptr_val_name(m.reg)}, int i) "
                f"{{ *({t} *)(p + (i << {s}) + {m.off}) = {ptr_val_name(m.reg)}; }}"], []

    # ---------- 字段自增/自减 / 指针追逐 ----------
    @reg("field_incdec")
    def _inc(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        m1, m2 = parse_mem(ins[0]), parse_mem(ins[3])
        mn, ops = split_ops(ins[1])
        if not m1 or not m2 or m1.mn not in LOADS or m2.mn not in STORES:
            return None
        if m1.kind != "off" or m2.kind != "off" or m1.base != A0 or m2.base != A0:
            return None
        if m1.mn != m2.mn or m1.off != m2.off or m1.reg != V0 or m2.reg != V0:
            return None
        if mn != "addiu" or len(ops) != 3 or ops[:2] != [V0, V0]:
            return None
        k = parse_imm(ops[2])
        if k is None:
            return None
        t = LOADS[m1.mn]
        op = "+" if k >= 0 else "-"
        a = abs(k)
        return [
            f"int {sym}(char *p) {{ {t} v = {L(m1)}; v = v {op} {a}; {L(m2)} = v; return v; }}",
            f"int {sym}(char *p) {{ return {L(m1)} {op}= {a}; }}",
        ], []

    @reg("ptr_chase")
    def _chase(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        m1, m2 = parse_mem(ins[0]), parse_mem(ins[2])
        if not m1 or not m2 or m1.mn not in LOADS or m2.mn not in LOADS:
            return None
        if m1.kind != "off" or m2.kind != "off" or m1.base != A0 or m2.base != m1.reg:
            return None
        if m2.reg != V0:
            return None
        t1 = LOADS[m1.mn]
        t2 = LOADS[m2.mn]
        return [f"{t2} {sym}(char *p) {{ return "
                f"*({t2} *)(*({t1} *)(p + {m1.off}) + {m2.off}); }}"], []

    # ---------- 两个内存操作（第二个在延迟槽）：store 对 ----------
    @reg("mem_pair")
    def _pair(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        ops = [parse_mem(ins[0]), parse_mem(ins[2])]
        if any(m is None or m.kind != "off" or m.base != A0 for m in ops):
            return None
        if any(m.mn not in STORES for m in ops):
            return None
        stmts = []
        for m in ops:
            t = STORES[m.mn]
            if m.reg == ZERO:
                stmts.append(f"*({t} *)(p + {m.off}) = 0;")
            elif m.reg in ARG_OF_REG:
                stmts.append(f"*({t} *)(p + {m.off}) = {ptr_val_name(m.reg)};")
            else:
                return None
        types = ["char *"] + [PARAM_T[ops[0].mn]] * 3
        return wrap_void(sym, arglist(types, PTR_ARGS), perm_variants(stmts)), []

    # ---------- 三个及以上 store（含常量）----------
    @reg("mem_multi_store")
    def _multi(ins, sym):
        if not tail(ins) or not (3 <= len(ins) <= 5):
            return None
        pre = [i for i in ins if i not in ("jr $31", "nop")]
        if len(pre) < 3:
            return None
        stmts, consts = [], {}
        for s in pre:
            mn, ops = split_ops(s)
            m = parse_mem(s)
            if m and m.kind == "off" and m.base == A0 and m.mn in STORES:
                t = STORES[m.mn]
                src = m.reg
                if src == ZERO:
                    stmts.append(f"*({t} *)(p + {m.off}) = 0;")
                elif src in ARG_OF_REG:
                    stmts.append(f"*({t} *)(p + {m.off}) = {ptr_val_name(src)};")
                elif src in consts:
                    stmts.append(f"*({t} *)(p + {m.off}) = {consts[src]};")
                else:
                    return None
            elif mn == "addiu" and len(ops) == 3 and ops[1] == ZERO:
                k = parse_imm(ops[2])
                if k is None:
                    return None
                consts[ops[0]] = k
            else:
                return None
        return wrap_void(sym, arglist(["char *", "int", "int", "int"], PTR_ARGS),
                         perm_variants(stmts)), []

    # ---------- 常量 store（单/双）----------
    @reg("const_store")
    def _cs(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        mn0, o0 = split_ops(ins[0])
        m1, m2 = parse_mem(ins[0]), parse_mem(ins[2])
        # addiu $T,$0,K ; jr ; store $T,off($4)
        if mn0 == "addiu" and len(o0) == 3 and o0[1] == ZERO:
            k = parse_imm(o0[2])
            if k is None or not m2 or m2.mn not in STORES or m2.kind != "off":
                return None
            if m2.base != A0 or m2.reg != o0[0]:
                return None
            t = STORES[m2.mn]
            return [f"void {sym}(char *p) {{ *({t} *)(p + {m2.off}) = {k}; }}"], []
        return None

    # ---------- store + 返回常量 ----------
    @reg("store_ret_const")
    def _src(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        m = parse_mem(ins[0])
        mn1, o1 = split_ops(ins[2])
        if not m or m.mn not in STORES or m.kind != "off":
            return None
        if mn1 != "addiu" or len(o1) != 3 or o1[:2] != [V0, ZERO]:
            return None
        k = parse_imm(o1[2])
        if k is None:
            return None
        t = STORES[m.mn]
        if m.base == A0:
            if m.reg == ZERO:
                stmt = f"*({t} *)(p + {m.off}) = 0;"
            elif m.reg in ARG_OF_REG:
                stmt = f"*({t} *)(p + {m.off}) = {ptr_val_name(m.reg)};"
            else:
                return None
            return [f"int {sym}(char *p, int a, int b, int c) {{ {stmt} return {k}; }}"], []
        if m.base == A1:
            if m.reg == ZERO:
                stmt = f"*({t} *)(q + {m.off}) = 0;"
            elif m.reg == A0:
                stmt = f"*({t} *)(q + {m.off}) = {t == 'int' and '0' or '0'};"
                return None
            else:
                return None
            return [f"int {sym}(char *p, char *q, int a, int b) {{ {stmt} return {k}; }}"], []
        return None

    # ---------- sw + 清零 + 返回 0 ----------
    @reg("store_zero_ret0")
    def _sz0(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        m = parse_mem(ins[0])
        mn1, o1 = split_ops(ins[2])
        if not m or m.mn not in STORES or m.kind != "off" or m.base != A0:
            return None
        if mn1 != "daddu" or o1 != [V0, ZERO, ZERO]:
            return None
        t = STORES[m.mn]
        if m.reg == ZERO:
            return [f"int {sym}(char *p) {{ *({t} *)(p + {m.off}) = 0; return 0; }}"], []
        if m.reg in ARG_OF_REG:
            return [f"int {sym}(char *p, int a, int b, int c) {{ "
                    f"*({t} *)(p + {m.off}) = {ptr_val_name(m.reg)}; return 0; }}"], []
        return None

    # ---------- 同一值写两处 + 返回 0（sw|daddu|jr|sw）----------
    @reg("two_store_same_ret0")
    def _tss(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        m1, m2 = parse_mem(ins[0]), parse_mem(ins[3])
        mn, ops = split_ops(ins[1])
        if not m1 or not m2 or m1.mn not in STORES or m2.mn not in STORES:
            return None
        if m1.kind != "off" or m2.kind != "off" or m1.base != A0 or m2.base != A0:
            return None
        if m1.reg != m2.reg or m1.mn != m2.mn:
            return None
        if mn != "daddu" or ops != [V0, ZERO, ZERO]:
            return None
        t = STORES[m1.mn]
        if m1.reg == ZERO:
            stmts = [f"*({t} *)(p + {m1.off}) = 0;", f"*({t} *)(p + {m2.off}) = 0;"]
        elif m1.reg in ARG_OF_REG:
            v = ptr_val_name(m1.reg)
            stmts = [f"*({t} *)(p + {m1.off}) = {v};", f"*({t} *)(p + {m2.off}) = {v};"]
        else:
            return None
        body = [f"int {sym}(char *p, int a, int b, int c) {{ " + " ".join(s)
                + " return 0; }" for s in perm_variants(stmts)]
        return body, []

    # ---------- addiu $4,$4,K ; store ; jr ; store ----------
    @reg("ptr_add_store")
    def _pas(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        mn0, o0 = split_ops(ins[0])
        if mn0 != "addiu" or len(o0) != 3 or o0[:2] != [A0, A0]:
            return None
        k = parse_imm(o0[2])
        if k is None:
            return None
        stmts = []
        for s in (ins[1], ins[3]):
            m = parse_mem(s)
            if not m or m.mn not in STORES or m.kind != "off" or m.base != A0:
                return None
            t = STORES[m.mn]
            if m.reg == ZERO:
                stmts.append(f"*({t} *)(p + {m.off}) = 0;")
            elif m.reg in ARG_OF_REG:
                stmts.append(f"*({t} *)(p + {m.off}) = {ptr_val_name(m.reg)};")
            else:
                return None
        vs = perm_variants(stmts)
        return [f"void {sym}(char *p, int a, int b, int c) {{ p += {k}; " + " ".join(s)
                + " }" for s in vs], []

    # ---------- load + store + jr + store（混合）----------
    @reg("load_mixed_stores")
    def _lms(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        m0, m1, m2 = parse_mem(ins[0]), parse_mem(ins[1]), parse_mem(ins[3])
        if not all((m0, m1, m2)):
            return None
        if any(m.kind != "off" or m.base != A0 for m in (m0, m1, m2)):
            return None
        if m0.mn not in LOADS or m1.mn not in STORES or m2.mn not in STORES:
            return None
        if m0.reg != V0 or m2.reg != V0:
            return None
        t0, t1, t2 = LOADS[m0.mn], STORES[m1.mn], STORES[m2.mn]
        if m1.reg == ZERO:
            a = f"*({t1} *)(p + {m1.off}) = 0;"
        elif m1.reg in ARG_OF_REG:
            a = f"*({t1} *)(p + {m1.off}) = {ptr_val_name(m1.reg)};"
        else:
            return None
        b = f"*({t2} *)(p + {m2.off}) = v;"
        return [f"{t0} {sym}(char *p, int a, int b, int c) {{ {t0} v = {L(m0)}; "
                f"{a} {b} return v; }}",
                f"void {sym}(char *p, int a, int b, int c) {{ {t0} v = {L(m0)}; "
                f"{a} {b} }}"], []

    # ---------- lbu + sh + jr + sb（临时寄存器版）----------
    @reg("lbu_copy_tmp")
    def _lct(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        m0, m1, m2 = parse_mem(ins[0]), parse_mem(ins[1]), parse_mem(ins[3])
        if not all((m0, m1, m2)) or any(m.kind != "off" or m.base != A0
                                         for m in (m0, m1, m2)):
            return None
        if m0.mn not in LOADS or m1.mn not in STORES or m2.mn not in STORES:
            return None
        if m1.reg != ZERO or m0.reg != m2.reg or m2.reg == V0:
            return None
        t0, t1, t2 = LOADS[m0.mn], STORES[m1.mn], STORES[m2.mn]
        return [f"void {sym}(char *p) {{ {t0} v = {L(m0)}; "
                f"*({t1} *)(p + {m1.off}) = 0; *({t2} *)(p + {m2.off}) = v; }}"], []

    # ---------- 简单算术一行 ----------
    @reg("ret_arith")
    def _ar(ins, sym):
        if not tail(ins) or len(ins) != 3:
            return None
        mn1, o1 = split_ops(ins[0])
        mn2, o2 = split_ops(ins[2])
        # subu $2,$4,$5 ; jr ; srl $2,$2,S
        if mn1 == "subu" and o1 == [V0, A0, A1] and mn2 == "srl" and o2[:2] == [V0, V0]:
            s = parse_imm(o2[2])
            if s is not None:
                return [f"unsigned {sym}(unsigned a, unsigned b) {{ return (a - b) >> {s}; }}",
                        f"int {sym}(int a, int b) {{ return (unsigned)(a - b) >> {s}; }}"], []
        # addiu $2,$0,K ; jr ; movz $2,$0,$R
        if mn1 == "addiu" and len(o1) == 3 and o1[:2] == [V0, ZERO] and mn2 == "movz" \
                and len(o2) == 3 and o2[0] == V0 and o2[1] == ZERO and o2[2] in ARG_OF_REG:
            k = parse_imm(o1[2])
            i = ARG_OF_REG[o2[2]]
            if k is not None:
                types = ["int"] * (i + 1)
                return [f"int {sym}({arglist(types, CARG[:i + 1])}) "
                        f"{{ return {CARG[i]} ? {k} : 0; }}",
                        f"int {sym}({arglist(types, CARG[:i + 1])}) "
                        f"{{ return {CARG[i]} == 0 ? 0 : {k}; }}"], []
        return None

    # ---------- 浮点三连 store ----------
    @reg("float_multi_store")
    def _fms(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        ms = [parse_mem(ins[0]), parse_mem(ins[1]), parse_mem(ins[3])]
        if any(m is None or m.mn != "swc1" or m.kind != "off" or m.base != A0 for m in ms):
            return None
        if any(m.reg not in FARG_OF_REG for m in ms):
            return None
        stmts = [f"*(float *)(p + {m.off}) = {CARG[FARG_OF_REG[m.reg]]};" for m in ms]
        sig = arglist(["char *", "float", "float", "float"], ["p", "a", "b", "c"])
        return [f"void {sym}({sig}) {{ " + " ".join(s) + " }"
                for s in perm_variants(stmts)], []

    # ---------- 移位/合并 store ----------
    @reg("shift_or_store")
    def _sos(ins, sym):
        if not tail(ins) or len(ins) != 4:
            return None
        mn0, o0 = split_ops(ins[0])
        mn1, o1 = split_ops(ins[1])
        m = parse_mem(ins[3])
        if mn0 != "sll" or len(o0) != 3 or mn1 != "or" or len(o1) != 3 or not m:
            return None
        if m.mn != "sw" or m.kind != "off" or m.base != A0 or m.reg != o0[0]:
            return None
        s = parse_imm(o0[2])
        if s is None or o0[1] not in ARG_OF_REG or o1[0] != o0[0] or o1[1] != o0[0] \
                or o1[2] not in ARG_OF_REG:
            return None
        i1, i2 = ARG_OF_REG[o0[1]], ARG_OF_REG[o1[2]]
        n = max(i1, i2) + 1
        types = ["char *"] + ["unsigned int"] * n
        names = ["p"] + CARG[:n]
        sig = arglist(types, names)
        return [f"void {sym}({sig}) {{ "
                f"*(unsigned int *)(p + {m.off}) = {CARG[i2]} | ({CARG[i1]} << {s}); }}",
                f"void {sym}({sig}) {{ {CARG[i1]} = ({CARG[i1]} << {s}) | {CARG[i2]}; "
                f"*(unsigned int *)(p + {m.off}) = {CARG[i1]}; }}"], []

    # ---------- 尾调用（j）----------
    @reg("tail_call_j")
    def _tail(ins, sym):
        if len(ins) != 2 or not ins[0].startswith("j "):
            return None
        target = ins[0].split(None, 1)[1]
        d = ins[1]
        if d == "nop":
            # 定义为旧式空参数表 `()`：同一 TU 内该符号可能被别的候选以多参尾调用
            return [f"void {sym}() {{ {target}(); }}",
                    f"int {sym}() {{ return {target}(); }}"], [(target, "func0")]
        mn, ops = split_ops(d)
        if mn == "addiu" and len(ops) == 3 and ops[0] in ARG_OF_REG:
            k = parse_imm(ops[2])
            if k is None:
                return None
            i = ARG_OF_REG[ops[0]]
            types = ["int"] * (i + 1)
            call_args = list(CARG[: i + 1])
            if ops[1] == ZERO:
                call_args[i] = str(k)
            elif ops[1] in ARG_OF_REG:
                j = ARG_OF_REG[ops[1]]
                call_args[i] = f"{CARG[j]} + {k}" if k >= 0 else f"{CARG[j]} - {abs(k)}"
            else:
                return None
            return [f"void {sym}({arglist(types, CARG[:i + 1])}) "
                    f"{{ {target}({', '.join(call_args)}); }}"], [(target, f"func{i+1}")]
        return None

    return R


# --------------------------------------------------------------------------
# 候选枚举
# --------------------------------------------------------------------------
def split_mode(sym: str) -> str:
    """该符号能否从 asm/cod/<sym>.s 里被单独摘出（direct/residual/blocked_*）。

    判定与 build_hybrid.sh 共用 tools/split_asm.py，避免两处口径漂移。
    """
    try:
        import split_asm
    except ImportError:                      # 允许从别的工作目录调用
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import split_asm
    return split_asm.analyze(sym)["mode"]


def candidate_symbols(tier: str = "trivial"):
    """从 workqueue 取指定 tier 且**真实可纳管**（eligible）的符号；无该列时退回 hybrid_ok。

    TSV 按**表头**取列：tools/report/m3_workqueue.py 追加列（gate/eligible）后本工具不需要改。
    """
    if not WORKQUEUE.exists():
        sys.exit(f"缺少 {WORKQUEUE}（先跑 python3 tools/report/m3_workqueue.py --tsv ...）")
    lines = WORKQUEUE.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    idx = {k: i for i, k in enumerate(header)}
    need = ("name", "addr", "size", "tier")
    if not all(k in idx for k in need):
        sys.exit(f"{WORKQUEUE} 表头缺少列：{[k for k in need if k not in idx]}")
    flag = "eligible" if "eligible" in idx else "hybrid_ok"
    out = []
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) < len(header):
            continue
        if p[idx["tier"]] != tier or p[idx[flag]] != "1":
            continue
        out.append((p[idx["name"]], int(p[idx["addr"]], 16), int(p[idx["size"]])))
    return out


def matched_in_list():
    syms = set()
    for line in MATCHED_LIST.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        syms.add(line.split()[0])
    return syms


def build_candidates(tier: str = "trivial"):
    recs = recognizers()
    cands = candidate_symbols(tier)
    already = matched_in_list()
    results = OrderedDict()
    stats = Counter()
    unrecognized = []
    for sym, addr, size in cands:
        ins, _ = load_body(sym)
        if ins is None:
            stats["no_asm"] += 1
            continue
        # 目标块必须能从 .s 里单独摘出来：
        #   direct   —— 文件只有该符号、无尾部填充，整份替换（原机制）；
        #   residual —— 有兄弟 glabel / 尾部填充，build_hybrid.sh 用 split_asm.py 把其余内容
        #               汇编成 residual 对象接在 C 对象之后（P-15/P-16 的解锁路径）；
        #   blocked_*—— 跨块引用、块内兄弟标签等，无法安全拆分，如实排除。
        mode = split_mode(sym)
        if mode.startswith("blocked"):
            stats[mode] += 1
            unrecognized.append((sym, addr, size, ins))
            continue
        if sym in already:
            stats["already_matched"] += 1
            continue
        hit = None
        for shape, fn in recs:
            try:
                r = fn(ins, sym)
            except Exception as e:      # 识别器 bug 不应中断整批
                print(f"  [warn] {shape} 识别 {sym} 抛异常: {e}", file=sys.stderr)
                r = None
            if r:
                hit = (shape, r)
                break
        if not hit:
            stats["unrecognized"] += 1
            unrecognized.append((sym, addr, size, ins))
            continue
        shape, (variants, externs) = hit
        stats[shape] += 1
        results[sym] = {
            "addr": addr, "size": size, "shape": shape, "tier": tier,
            "variants": variants, "externs": externs, "asm": ins,
        }
    return results, stats, unrecognized


# --------------------------------------------------------------------------
# 生成 probe / target，跑 objdiff
# --------------------------------------------------------------------------
def extern_decl(name, t):
    if t.startswith("func"):
        # 无原型声明：同一 TU 内该符号可能既是 0 参定义又被多参尾调用
        return "extern int %s();" % name
    return "extern %s %s;" % (t, name)


def write_probe(chosen, path):
    """chosen: {sym: (body, externs)}；写 probe.c。"""
    decls = OrderedDict()
    for sym, (body, externs) in chosen.items():
        for name, t in externs:
            decls.setdefault(name, extern_decl(name, t))
    parts = ["/* M3 trivial 自动匹配 probe（生成物，勿手改） */\n",
             "\n".join(decls.values()) + "\n"]
    for sym, (body, _) in chosen.items():
        parts.append(f"/* {sym} */\n{body}\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_target(syms, path):
    chunks = ['.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n']
    for sym in syms:
        p = ASMDIR / f"{sym}.s"
        txt = p.read_text(encoding="utf-8", errors="replace")
        body, started = [], False
        for line in txt.split("\n"):
            if re.match(r"\s*glabel\s+", line):
                started = True
            if started:
                body.append(line.rstrip())
            if re.match(r"\s*endlabel\s+", line):
                break
        chunks.append("\n".join(body) + "\n")
    path.write_text("\n".join(chunks), encoding="utf-8")


def run_objdiff(workdir: Path, chosen, tag: str):
    """编译 probe（**逐档**）+ 汇编 target + objdiff。

    返回 `({sym: 最高分}, {sym: 获胜档位})`。同一个 probe 只写一次、target 只汇编一次，
    每个档位各编译一次（单 TU，成本很低）。
    """
    probe = workdir / f"probe_{tag}.c"
    target_s = workdir / f"target_{tag}.s"
    target_o = workdir / f"target_{tag}.o"
    write_probe(chosen, probe)
    write_target(list(chosen.keys()), target_s)
    subprocess.run([AS, "-EL", "-march=r5900", "-I", str(ROOT / "include"),
                    "-o", str(target_o), str(target_s)], check=True, capture_output=True)
    best: dict[str, float] = {}
    best_flags: dict[str, str] = {}
    for fs in FLAG_MATRIX:
        base_o = workdir / f"base_{tag}_{flag_key(fs)}.o"
        diff = workdir / f"diff_{tag}_{flag_key(fs)}.json"
        c = subprocess.run([GCC, *CFLAGS, *fs, "-I", str(ROOT / "include"), "-c",
                            "-o", str(base_o), str(probe)], capture_output=True)
        if c.returncode:
            continue
        x = subprocess.run([OBJDIFF, "diff", "-1", str(target_o), "-2", str(base_o),
                            "-o", str(diff), "--format", "json"], capture_output=True)
        if x.returncode:
            continue
        try:
            d = json.loads(diff.read_text(encoding="utf-8"))
        except Exception:
            continue
        for s in d["left"]["symbols"]:
            if s.get("kind") != "SYMBOL_FUNCTION":
                continue
            mp = s.get("match_percent")
            if mp is None:
                continue
            mp = float(mp)
            if s["name"] not in best or mp > best[s["name"]]:
                best[s["name"]] = mp
                best_flags[s["name"]] = " ".join(fs)
    return best, best_flags


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def do_run(tier: str = "trivial", max_rounds: int = 4):
    results, stats, unrecognized = build_candidates(tier)
    print(f"== {tier}+hybrid_ok 候选：{sum(stats.values())} 个 ==")
    for k, v in stats.most_common():
        print(f"   {k:24s} {v}")

    BUILDDIR.mkdir(parents=True, exist_ok=True)
    winners, tried = {}, {}
    # 尾调用（j）单独逐个验证：同一 probe 里「某符号既是 0 参定义又被多参尾调用」在 C 里无解
    tail = OrderedDict((s, i) for s, i in results.items() if i["shape"] == "tail_call_j")
    remaining = OrderedDict((s, i) for s, i in results.items() if i["shape"] != "tail_call_j")
    rnd = 0
    while remaining and rnd < max_rounds:
        chosen = OrderedDict()
        for sym, info in remaining.items():
            vs = info["variants"]
            chosen[sym] = (vs[min(info.get("_vi", 0), len(vs) - 1)], info["externs"])
        per, pflags = run_objdiff(BUILDDIR, chosen, f"r{rnd}")
        n_ok, nxt = 0, OrderedDict()
        for sym, info in remaining.items():
            mp = per.get(sym)
            tried.setdefault(sym, []).append(mp)
            if mp == 100.0:
                info["_win_body"] = chosen[sym][0]
                info["_win_flags"] = pflags.get(sym, "")
                winners[sym] = info
                n_ok += 1
            else:
                info["_vi"] = info.get("_vi", 0) + 1
                if info["_vi"] < len(info["variants"]):
                    nxt[sym] = info
        print(f"== round {rnd}: 100% = {n_ok} / {len(remaining)} ==")
        remaining = nxt
        rnd += 1

    for sym, info in tail.items():
        for vi, body in enumerate(info["variants"]):
            per, pflags = run_objdiff(BUILDDIR, OrderedDict([(sym, (body, info["externs"]))]),
                                      f"tail_{sym}_{vi}")
            mp = per.get(sym)
            tried.setdefault(sym, []).append(mp)
            if mp == 100.0:
                info["_win_body"] = body
                info["_win_flags"] = pflags.get(sym, "")
                winners[sym] = info
                break
        else:
            print(f"   tail 未匹配: {sym} ({info['asm']})")

    fails = OrderedDict((s, i) for s, i in results.items() if s not in winners)
    return results, winners, fails, tried, stats, unrecognized


def shape_stats(winners, fails):
    ws = Counter(i["shape"] for i in winners.values())
    fs = Counter(i["shape"] for i in fails.values())
    return ws, fs


def do_apply(winners):
    """写 src/matched/<sym>.c 并把清单 M3 段**合并式**更新（已有条目保留，不整段重写）。"""
    SRCDIR.mkdir(parents=True, exist_ok=True)
    for sym, info in winners.items():
        a, sz, shape = info["addr"], info["size"], info["shape"]
        hdr = (f"/* {sym} @ 0x{a:08x} ({sz} B, {info.get('tier', 'trivial')}) : shape={shape}\n"
               f" * 由 routebjp/tools/auto_match_trivial.py 自动生成，"
               f"objdiff 100% 验证后再纳入 hybrid。 */\n")
        decls = "\n".join(extern_decl(n, t) for n, t in info["externs"])
        src = hdr + (decls + "\n\n" if decls else "") + info["_win_body"] + "\n"
        (SRCDIR / f"{sym}.c").write_text(src, encoding="utf-8")

    # 编译档必须落盘（键 = 清单第二列，即符号名，无扩展名；见 P-34），
    # 否则构建会用默认 -O2 重编 ⇒ 与验证时的档位不一致 ⇒ 载荷校验红。
    fmap: dict[str, str] = {}
    if FLAGS_TSV.is_file():
        for line in FLAGS_TSV.read_text(encoding="utf-8").splitlines():
            a = line.split("\t")
            if len(a) >= 2 and not line.lstrip().startswith("#"):
                fmap[a[0]] = a[1]
    for sym, info in winners.items():
        fl = (info.get("_win_flags") or "").strip()
        if fl and fl != "-O2":
            fmap[sym] = fl
        elif sym in fmap and (not fl or fl == "-O2"):
            del fmap[sym]
    FLAGS_TSV.write_text("\n".join(["# 格式：<source-basename>\t<extra-cflags>"]
                                    + [f"{k}\t{fmap[k]}" for k in sorted(fmap)]) + "\n",
                         encoding="utf-8")

    text = MATCHED_LIST.read_text(encoding="utf-8")
    pre = text.split(M3_BEGIN)[0].rstrip("\n") if M3_BEGIN in text else text.rstrip("\n")
    post = text.split(M3_END, 1)[1].lstrip("\n") if M3_END in text else ""

    # 合并已有 M3 条目（R9 的 286 个不能因为新一轮 apply 而丢失）
    existing: "OrderedDict[str, str]" = OrderedDict()
    if M3_BEGIN in text:
        seg = text.split(M3_BEGIN, 1)[1]
        seg = seg.split(M3_END, 1)[0] if M3_END in seg else seg
        for line in seg.split("\n"):
            line = line.split("#", 1)
            sym = line[0].strip()
            if not sym:
                continue
            existing[sym] = line[1].strip() if len(line) > 1 else ""
    n_before = len(existing)
    for sym, info in winners.items():
        existing[sym] = info["shape"]

    lines = [pre, "", M3_BEGIN]
    for sym in sorted(existing):
        c = existing[sym]
        lines.append(f"{sym}    # {c}" if c else sym)
    lines.append(M3_END)
    body = "\n".join(lines)
    if post:
        body = body.rstrip("\n") + "\n" + post
    MATCHED_LIST.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
    print(f"apply: 写入 {len(winners)} 个 C 源；清单 M3 段 {n_before} -> {len(existing)} 条")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run",
                    choices=["scan", "run", "apply", "all"])
    ap.add_argument("--apply", action="store_true", help="run 之后直接落地")
    ap.add_argument("--max-rounds", type=int, default=4)
    ap.add_argument("--tier", default="trivial",
                    choices=["trivial", "small", "medium", "large", "huge"],
                    help="候选尺寸档（默认 trivial，与 R9 口径一致）")
    args = ap.parse_args()

    if args.mode == "scan":
        results, stats, unrec = build_candidates(args.tier)
        for k, v in stats.most_common():
            print(f"{k:24s} {v}")
        return 0

    results, winners, fails, tried, stats, unrecognized = do_run(args.tier, args.max_rounds)
    for sym, info in winners.items():
        info.setdefault("_win_body", info["variants"][0])

    ws, fs = shape_stats(winners, fails)
    print("\n== 形状统计（成功/失败）==")
    for shape in sorted(set(list(ws) + list(fs))):
        print(f"   {shape:22s} 成功 {ws.get(shape,0):4d} / 失败 {fs.get(shape,0):4d}")
    n_try = len(results)
    print(f"\n== 汇总：尝试 {n_try}，100% 匹配 {len(winners)}，"
          f"成功率 {100.0*len(winners)/max(n_try,1):.1f}% ==")

    out = BUILDDIR / ("result.json" if args.tier == "trivial" else f"result_{args.tier}.json")
    out.write_text(json.dumps({
        "tier": args.tier,
        "n_candidates": n_try,
        "n_matched": len(winners),
        "shapes_matched": dict(ws),
        "shapes_failed": dict(fs),
        "matched": {s: {"addr": i["addr"], "size": i["size"], "shape": i["shape"],
                        "body": i["_win_body"]} for s, i in winners.items()},
        "failed": {s: {"addr": i["addr"], "size": i["size"], "shape": i["shape"],
                       "asm": i["asm"], "tried": tried.get(s, [])}
                   for s, i in fails.items()},
        "unrecognized": [{"sym": s, "addr": a, "size": z, "asm": ins}
                         for s, a, z, ins in unrecognized],
        "scan_stats": dict(stats),
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"结果 JSON -> {out}")

    if args.apply or args.mode == "all":
        do_apply(winners)
    return 0


if __name__ == "__main__":
    sys.exit(main())
