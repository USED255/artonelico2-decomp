#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D 档（MMI 池中只用 ``lq/sq``，可含 ``por/pand/pxor/pnor`` 的 128 位搬运/逻辑）
的**向量形状合成**原型。

背景
----
- MMI 真池 = `class=G_mmi` 且不在 `routebjp/config/matched_symbols.txt`：803 个 / 530,384 B。
- 其中 **D 档 = 块内只有 `lq/sq`（＋`por/pand/pxor/pnor`）**：350 个 / 224,020 B（[R15]）。
- 机制已通（[P-22]）：`typedef int v4si __attribute__((mode(V4SI)));` 的 `*(v4si*)p`
  产 `lq`（`0x78820000`）、`*(v4si*)p = v` 产 `sq`（`0x7c850000`）。
- 但 m2c 草稿在 D 档中位只有 34.6%（[R15] §4），且 m2c 本身已经用 `s128` 表达 lq/sq。

本工具做什么
------------
1. 复算 D 池（块内判定，与 R15 的 350 / 224,020 B 对齐）；
2. 解析目标块的指令流，抽取 128 位访存/搬运**形状**：源/目标基址寄存器、偏移、
   经 `addiu`/`lui+addiu`/`addu`/`sll` 追溯出的 C 基址表达式、`lq`→`sq` 的寄存器配对；
3. 按形状直接生成候选 C（`*(v4si *)(DST) = *(v4si *)(SRC);` /
   `v4si v = *(v4si *)p; ... *(v4si *)q = v;`），把可判定的整数/内存/浮点/控制流一并翻译；
4. `batch`：串行编译（`-O2/-O1/-O3`，命中 100% 即停）→ objdiff 比对 → 写 JSON。

CLI
---
    python3 routebjp/tools/shape_lq_sq.py list
    python3 routebjp/tools/shape_lq_sq.py analyze <sym>
    python3 routebjp/tools/shape_lq_sq.py emit <sym> <outdir>
    python3 routebjp/tools/shape_lq_sq.py batch --samples 22 --max-compiles 67

证据等级：本工具输出的数字均为 `[实测]`。编译/比对串行执行并有硬上限（默认 60）。
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PROJ = REPO / "routebjp"
ASMDIR = PROJ / "asm" / "cod"
WORKQUEUE = REPO / "out/evidence/jp_m3_workqueue.tsv"
MATCHED = PROJ / "config" / "matched_symbols.txt"
GCC = Path(os.environ.get("GCC", str(Path.home() / "eecc/ee-gcc3.2-040921/bin/ee-gcc")))
AS = Path(os.environ.get("AS", str(Path.home() / "eecc/ps2binutils/mips-ps2-decompals-as")))
OBJDIFF = Path(os.environ.get("OBJDIFF", str(Path.home() / "eecc/objdiff-cli")))

VEC_POR = {"por", "pand", "pxor", "pnor"}
COP2Q = {"lqc2", "sqc2", "qmtc2", "qmfc2"}
COP2CTL = {"mfc2", "mtc2", "cfc2", "ctc2"}
VUMEM = {"lqd", "lqi", "sqd", "sqi", "ilw", "isw", "ilwr", "iswr"}
PACKED_OTHER = {
    "pabsh", "pabsw", "paddb", "paddh", "paddsb", "paddsh", "paddsw", "paddub", "padduh",
    "padduw", "paddw", "padsbh", "pceqb", "pceqh", "pceqw", "pcgtb", "pcgth", "pcgtw",
    "pcpyh", "pcpyld", "pcpyud", "pdivbw", "pdivuw", "pdivw", "pexch", "pexcw", "pexeh",
    "pexew", "pext5", "pextlb", "pextlh", "pextlw", "pextub", "pextuh", "pextuw", "phmadh",
    "phmsbh", "pinteh", "pinth", "plzcw", "pmaddh", "pmadduw", "pmaddw", "pmaxh", "pmaxw",
    "pmfhi", "pmfhl", "pmflo", "pminh", "pminw", "pmsubh", "pmsubw", "pmthi", "pmtlo",
    "pmulth", "pmultuw", "pmultw", "ppac5", "ppacb", "ppach", "ppacw", "prevh", "prot3w",
    "psllh", "psllvw", "psllw", "psrah", "psravw", "psraw", "psrlh", "psrlvw", "psrlw",
    "psubb", "psubh", "psubsb", "psubsh", "psubsw", "psubub", "psubuh", "psubuw", "psubw",
    "mfsa", "mtsa", "mtsab", "mtsah", "qfsrv",
}

PRE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
INS_RE = re.compile(r"/\*\s*[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s*\*/\s*([a-zA-Z0-9_.]+)\s*(.*)$")
LABEL_RE = re.compile(r"^\s*(\.L[0-9A-Fa-f]+)\s*:\s*$")


# ---------------------------------------------------------------- asm 解析

class Insn:
    __slots__ = ("m", "ops", "raw")

    def __init__(self, m, ops, raw):
        self.m = m
        self.ops = ops.strip()
        self.raw = raw

    def regs(self):
        return [int(x) for x in re.findall(r"\$(\d{1,2})\b", self.ops)]

    def __repr__(self):
        return f"{self.m} {self.ops}"


def block_bounds(sym):
    p = ASMDIR / f"{sym}.s"
    if not p.is_file():
        return p, None, None
    L = p.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = None
    for i, l in enumerate(L):
        if re.match(r"\s*glabel\s+" + re.escape(sym) + r"\s*$", l):
            gi = i
            break
    if gi is None:
        return p, None, None
    en = None
    for i in range(gi, len(L)):
        if re.match(r"\s*endlabel\s+" + re.escape(sym) + r"\s*$", L[i]):
            en = i
            break
    return p, gi, en


def parse_block(sym):
    """返回 (insns, labels) —— labels: .Lxxx -> 其后的第一条指令下标。"""
    p, gi, en = block_bounds(sym)
    if gi is None:
        return None, None
    L = p.read_text(encoding="utf-8", errors="replace").split("\n")
    end = en if en is not None else len(L)
    ins, labels = [], {}
    for l in L[gi:end + 1]:
        s = l.strip()
        mo = LABEL_RE.match(s)
        if mo:
            labels[mo.group(1)] = len(ins)
            continue
        mi = INS_RE.match(s)
        if mi:
            ins.append(Insn(mi.group(1).lower(), mi.group(2), s))
    return ins, labels


def target_s(sym):
    p, gi, en = block_bounds(sym)
    if gi is None or en is None:
        return None
    L = p.read_text(encoding="utf-8", errors="replace").split("\n")
    return PRE + "\n".join(L[gi:en + 1]) + "\n"


# ---------------------------------------------------------------- D 池

def d_pool():
    matched = set()
    for l in MATCHED.read_text(encoding="utf-8", errors="replace").split("\n"):
        l = l.strip()
        if l and not l.startswith("#"):
            matched.add(l.split()[0])
    rows = list(csv.DictReader(open(WORKQUEUE, encoding="utf-8"), delimiter="\t"))
    out = []
    for r in rows:
        if r["class"] != "G_mmi" or r["name"] in matched:
            continue
        ins, _ = parse_block(r["name"])
        if ins is None:
            continue
        c = collections.Counter(i.m.split(".")[0] for i in ins)
        if c["lq"] + c["sq"] == 0:
            continue
        if any(c[k] for k in COP2Q | COP2CTL | VUMEM):
            continue
        if any(v for k, v in c.items() if k.startswith("v") and k not in ("lq", "sq")):
            continue
        if sum(c[k] for k in PACKED_OTHER):
            continue
        out.append({"name": r["name"], "addr": r["addr"], "size": int(r["size"]),
                    "insns": ins, "counts": dict(c)})
    return out


# ---------------------------------------------------------------- 形状抽取

def _imm(tok):
    tok = tok.strip()
    m = re.fullmatch(r"\(0x([0-9A-Fa-f]+)\s*&\s*0xFFFF\)", tok)
    if m:
        return int(m.group(1), 16)
    m = re.fullmatch(r"-?0x[0-9A-Fa-f]+|-?\d+", tok)
    if not m:
        return None
    return int(tok, 16) if ("0x" in tok or "0X" in tok) else int(tok)


def mem_operand(ops):
    """`Rt, off($rs)` / `Rt, %lo(SYM)($rs)` / `Rt, expr($rs)` → (sym|None, imm|None, base_reg)。"""
    if "," in ops:
        ops = ops.split(",", 1)[1]
    mo = re.search(r"\((\$(\d{1,2}))\)\s*$", ops)
    if not mo:
        return None
    base = int(mo.group(2))
    head = ops[:mo.start()].strip()
    ms = re.fullmatch(r"%lo\(([^)]+)\)", head)
    if ms:
        return ms.group(1).strip(), 0, base
    mi = _imm(head)
    if mi is not None:
        return None, mi, base
    return None, None, base


class V:
    """寄存器值的符号表示：kind=i(int) / p(pointer,expr+off) / g(全局地址) / f(float) / v(v4si)。"""
    __slots__ = ("kind", "expr", "off")

    def __init__(self, kind="i", expr=None, off=0):
        self.kind, self.expr, self.off = kind, expr, off

    def addr(self, extra=0):
        if self.kind in ("p", "g"):
            return self.expr, self.off + extra
        return None, extra


def _step(i, R):
    """更新寄存器符号状态（只求基址表达式，不求完整数据流）。"""
    m, ops, rs = i.m, i.ops, i.regs()
    if not rs:
        return
    if m in ("addiu", "daddiu"):
        if len(rs) < 2:
            return
        mlo = re.search(r"%lo\(([^)]+)\)", ops)
        if mlo:
            R[rs[0]] = V("g", mlo.group(1).strip(), 0)
            return
        imm = _imm(ops.split(",")[-1]) if ops.count(",") >= 2 else None
        if imm is None:
            mo = re.search(r",\s*(-?0x[0-9A-Fa-f]+|-?\d+)\s*$", ops)
            imm = _imm(mo.group(1)) if mo else None
        if rs[1] == 0:
            R[rs[0]] = V("i", str(imm) if imm is not None else None)
        elif imm is None:
            R[rs[0]] = V("i", None)
        else:
            b = R.get(rs[1], V())
            if b.kind in ("p", "g"):
                R[rs[0]] = V(b.kind, b.expr, b.off + imm)
            else:
                R[rs[0]] = V("i", None)
    elif m == "lui":
        s = re.search(r"%hi\(([^)]+)\)", ops)
        if s:
            R[rs[0]] = V("g", s.group(1).strip(), 0)
        else:
            v = re.search(r"\(0x([0-9A-Fa-f]+)\s*>>\s*16\)", ops)
            R[rs[0]] = V("i", ("0x" + v.group(1)) if v else None)
    elif m == "ori":
        a = re.search(r"\(0x([0-9A-Fa-f]+)\s*&\s*0xFFFF\)", ops)
        b = R.get(rs[1], V()) if len(rs) >= 2 else V()
        if a and b.kind == "i" and isinstance(b.expr, str) and b.expr.startswith("0x"):
            R[rs[0]] = V("i", "0x%X" % (int(b.expr, 16) | int(a.group(1), 16)))
        else:
            R[rs[0]] = V("i", None)
    elif m in ("addu", "daddu") and len(rs) >= 3:
        a, b = R.get(rs[1], V()), R.get(rs[2], V())
        if a.kind in ("p", "g") and b.kind == "i" and isinstance(b.expr, str) and b.expr.startswith("0x"):
            R[rs[0]] = V(a.kind, a.expr, a.off + int(b.expr, 16))
        elif b.kind in ("p", "g") and a.kind == "i" and isinstance(a.expr, str) and a.expr.startswith("0x"):
            R[rs[0]] = V(b.kind, b.expr, b.off + int(a.expr, 16))
        else:
            R[rs[0]] = V("i", None)
    elif m in ("lw", "ld", "lh", "lhu", "lb", "lbu", "mfc1", "mfhi", "mflo"):
        R[rs[0]] = V("i", None)
    elif m == "jal":
        R[2] = V("i", None)
    elif m in ("lq",):
        R[rs[0]] = V("v", None)
    elif m == "lwc1":
        pass
    else:
        # 其它写寄存器的指令：目标寄存器值未知
        if m not in ("sw", "sd", "sh", "sb", "swc1", "sq", "jr", "j", "b", "nop") and not m.startswith("b"):
            R[rs[0]] = V("i", None)


class VecShape:
    def __init__(self, kind, src, dst, tmp, off_src, off_dst, idx, fmt=None):
        self.kind = kind
        self.src, self.dst, self.tmp = src, dst, tmp
        self.off_src, self.off_dst = off_src, off_dst
        self.idx = idx
        self.fmt = fmt

    def as_dict(self):
        return {"kind": self.kind, "src": self.src, "dst": self.dst, "tmp": self.tmp,
                "off_src": self.off_src, "off_dst": self.off_dst, "insn_index": self.idx}


def trace_shapes(ins):
    R = {r: V("i", None) for r in range(32)}
    R[0] = V("i", "0")
    for a in range(4):
        R[4 + a] = V("p", f"arg{a}", 0)
    shapes, pending = [], {}
    for k, i in enumerate(ins):
        if i.m in ("lq", "sq"):
            sym, off, base = mem_operand(i.ops)
            off = off if off is not None else 0
            b = R.get(base, V())
            if sym:
                src, so = sym, off
            elif b.kind in ("p", "g"):
                src, so = b.expr, b.off + off
            else:
                src, so = f"reg{base}", off
            rt = i.regs()[0]
            kind = i.m
            if i.m == "lq":
                shapes.append(VecShape("load", src, None, rt, so, None, k))
                pending[rt] = (src, so)
            elif rt == 0:
                shapes.append(VecShape("zero_store", None, src, 0, None, so, k))
            elif rt in pending:
                se, so2 = pending.pop(rt)
                shapes.append(VecShape("copy", se, src, rt, so2, so, k))
            else:
                shapes.append(VecShape("store", None, src, rt, None, so, k))
        else:
            _step(i, R)
    return shapes


# ---------------------------------------------------------------- 领域判定

INT_OK = {"addiu", "daddiu", "addu", "daddu", "ori", "andi", "xori", "lui", "sll", "srl", "sra",
          "dsll", "dsll32", "dsrl", "dsrl32", "dsra", "dsra32", "dsllv", "dsrlv", "sllv", "srlv", "srav", "and", "or",
          "xor", "nor", "subu", "dsubu", "slt", "sltu", "slti", "sltiu", "neg", "not",
          "movz", "movn", "negu", "mult", "multu", "div", "divu", "mfhi", "mflo", "break"}
MEM_OK = {"lw", "lwu", "sw", "ld", "sd", "lh", "lhu", "sh", "lb", "lbu", "sb", "lwl", "lwr", "swl", "swr"}
FP_OK = {"lwc1", "swc1", "mtc1", "mfc1", "mov.s", "add.s", "sub.s", "mul.s", "div.s",
         "neg.s", "abs.s", "sqrt.s", "cvt.s.w", "cvt.w.s", "trunc.w.s"}
CTL_OK = {"jr", "j", "jal", "nop", "beq", "bne", "beqz", "bnez", "b", "beql", "bnel", "beqzl",
          "bnezl", "bltz", "blez", "bgtz", "bgez", "bltzl", "blezl", "bgtzl", "bgezl"}
VEC_OK = {"lq", "sq"} | VEC_POR


def domain_check(ins, labels):
    if not ins:
        return "empty"
    has_branch = any(i.m.startswith("b") or i.m in ("beq", "bne") for i in ins)
    if len(ins) > 1200:
        return "too_large"
    for i in ins:
        m = i.m
        if m == "jalr":
            return "indirect_call"
        if m == "break":
            return "break"
        if m.startswith("bc1"):
            return "fpu_branch"
        if m not in INT_OK | MEM_OK | FP_OK | CTL_OK | VEC_OK:
            return "unsupported:" + m
    # 反向分支 = 循环
    for k, i in enumerate(ins):
        if i.m.startswith("b") or i.m in ("beq", "bne", "j"):
            for lab in re.findall(r"\.L[0-9A-Fa-f]+", i.ops):
                t = labels.get(lab)
                if t is not None and t <= k:
                    return "loop"
    # 嵌套分支（被跳过的区间里还有分支）会让简单 if-then 展开失效
    if has_branch:
        for k, i in enumerate(ins):
            if i.m.startswith("b") or i.m in ("beq", "bne"):
                for lab in re.findall(r"\.L[0-9A-Fa-f]+", i.ops):
                    t = labels.get(lab)
                    if t is None:
                        return "unresolved_label"
                    for j in range(k + 2, t):
                        if ins[j].m.startswith("b") or ins[j].m in ("beq", "bne"):
                            return "nested_branch"
                    for j in range(k + 1, t):
                        if ins[j].m == "j":
                            return "nested_tailcall"
                    if any(ins[j].m == "jr" and not ins[j].ops.startswith("$31")
                           for j in range(k, t)):
                        return "nested_indirect_jump"
    return None


# ---------------------------------------------------------------- C 生成

def _cint(v):
    return f"(-{-v})" if v < 0 else (str(v) if -9 <= v <= 9 else f"0x{v:x}")


class Emitter:
    """把目标块按「寄存器机器」逐条翻成 C；128 位访存/搬运走 v4si 形状。

    类型模型（目标：ee-gcc 3.2 一定能编译）：
      - 非参数寄存器：char *（访存基址）/ unsigned long（其它整数）；向量临时单独命名；
      - 参数 arg0..arg3：void *（访存基址）/ int（其它）；
      - 所有指针/整数混合运算都用 `(char *)(unsigned long)(E)` 形式显式转换；
      - $29 用局部字节缓冲 sb 代替（GCC 自建帧），帧内保存/恢复一律跳过。
    """

    def __init__(self, sym, ins, labels, prelude=True, variant="direct"):
        self.sym, self.ins, self.labels = sym, ins, labels
        self.prelude = prelude
        self.variant = variant        # direct / temp / ptr
        self.lines = []
        self.decl = collections.OrderedDict()
        self.externs = []
        self.ret_kind = None
        self.roles = {}
        self.used_args = set()
        self.ptr_val = {}
        self.pend = {}
        self.vreg = {}
        self.fp = {}
        self.n = 0
        self.stackbuf = False

    # ---- 类型推断
    def infer(self):
        membase = set()
        for i in self.ins:
            if i.m in ("lq", "sq") or i.m in MEM_OK:
                mo = mem_operand(i.ops)
                if mo:
                    membase.add(mo[2])
        for i in self.ins:
            rs = i.regs()
            if not rs:
                continue
            if i.m in INT_OK | MEM_OK and rs[0] not in self.roles and rs[0] not in membase:
                self.roles[rs[0]] = "i"
        for r in membase:
            self.roles[r] = "p"

    def rn(self, r):
        if r == 0:
            return "0"
        return f"arg{r-4}" if 4 <= r <= 7 else f"r{r}"

    def ensure(self, r):
        n = self.rn(r)
        if 4 <= r <= 7:
            return n, ("void *" if self.roles.get(r) == "p" else "int")
        ty = "char *" if self.roles.get(r) == "p" else "unsigned long"
        if n not in self.decl:
            self.decl[n] = (ty, None)
        return n, ty

    def oexpr(self, r):
        """整数上下文中的寄存器表达式（顺带声明只读寄存器）。"""
        if r == 0:
            return "0"
        self.ensure(r)
        if self.roles.get(r) == "p":
            return f"(unsigned long){self.rn(r)}"
        return self.rn(r)

    # ---- 地址
    def addr(self, ops):
        mo = mem_operand(ops)
        if mo is None:
            return None
        sym, off, base = mo
        off = off if off is not None else 0
        if sym:
            if sym not in self.externs:
                self.externs.append(sym)
            return f"((char *)({sym}) + {off})" if off else f"({sym})"
        b = self.ptr_val.get(base)
        if b is not None:
            e, o = b
            return f"((char *)(unsigned long)({e}) + {o + off})" if (o + off) else f"((char *)(unsigned long)({e}))"
        if base == 29:
            self.stackbuf = True
            return f"((char *)sb + {off})" if off else "((char *)sb)"
        self.ensure(base)
        return f"((char *)(unsigned long)({self.rn(base)}) + {off})" if off else f"((char *)(unsigned long)({self.rn(base)}))"

    # ---- 主翻译
    def emit(self):
        ins, labels = self.ins, self.labels
        k, n = 0, len(ins)
        while k < n:
            i = ins[k]
            m = i.m
            if m in ("nop", "jr"):
                k += 1
                continue
            if m in ("lq", "sq"):
                self.do_vec(k); k += 1; continue
            if m in MEM_OK:
                self.do_mem(k); k += 1; continue
            if m in INT_OK:
                self.do_int(k); k += 1; continue
            if m in VEC_POR:
                self.do_por(k); k += 1; continue
            if m in FP_OK:
                self.do_fp(k); k += 1; continue
            if m == "jal":
                self.do_call(k); k += 1; continue
            if m == "j":
                tgt = i.ops.split(",")[0].strip()
                if tgt and tgt not in self.externs:
                    self.externs.append(tgt)
                args = [f"arg{a}" for a in range(4) if (4 + a) in self.used_args]
                self.lines.append(f"return {tgt}({', '.join(args)});")
                k += 1; continue
            if m.startswith("b") or m in ("beq", "bne"):
                tgt = None
                for lab in re.findall(r"\.L[0-9A-Fa-f]+", i.ops):
                    tgt = labels.get(lab)
                if m == "b":
                    if k + 1 < n:
                        self.one(k + 1)
                    k = tgt if tgt is not None else k + 1
                    continue
                if k + 1 < n:
                    self.one(k + 1)
                cond = self.bcond(i)
                if cond is None or tgt is None or tgt <= k:
                    k += 1
                    continue
                self.lines.append(f"if (!({cond})) {{")
                for j in range(k + 2, tgt):
                    self.one(j)
                self.lines.append("}")
                k = tgt
                continue
            k += 1
        if not self.lines or not self.lines[-1].startswith("return"):
            if self.ret_kind == "int":
                self.ensure(2)
                self.lines.append("return r2;")
            else:
                self.lines.append("return;")
        return self.lines

    def one(self, j):
        i = self.ins[j]
        m = i.m
        if m in ("nop", "jr"):
            return
        if m in ("lq", "sq"):
            self.do_vec(j)
        elif m in MEM_OK:
            self.do_mem(j)
        elif m in INT_OK:
            self.do_int(j)
        elif m in VEC_POR:
            self.do_por(j)
        elif m in FP_OK:
            self.do_fp(j)
        elif m == "jal":
            self.do_call(j)

    def bcond(self, i):
        m, rs = i.m, i.regs()
        R = lambda r: self.oexpr(r)
        if m in ("beqz", "beqzl"):
            return f"{R(rs[0])} != 0"
        if m in ("bnez", "bnezl"):
            return f"{R(rs[0])} == 0"
        if m in ("beq", "beql"):
            return f"{R(rs[0])} != {R(rs[1])}"
        if m in ("bne", "bnel"):
            return f"{R(rs[0])} == {R(rs[1])}"
        if m == "bltz":
            return f"(long){R(rs[0])} >= 0"
        if m == "bgez":
            return f"(long){R(rs[0])} < 0"
        if m == "blez":
            return f"(long){R(rs[0])} > 0"
        if m == "bgtz":
            return f"(long){R(rs[0])} <= 0"
        return None

    def _poke(self, rt, base, off):
        if base == 0:
            self.ptr_val.pop(rt, None)
            return
        b = self.ptr_val.get(base)
        if b is not None:
            self.ptr_val[rt] = (b[0], b[1] + off)
        elif 4 <= base <= 7:
            self.ptr_val[rt] = (self.rn(base), off)
        else:
            self.ptr_val.pop(rt, None)

    def _castptr(self, e, o):
        s = f"(char *)(unsigned long)({e})"
        return f"{s} + {_cint(o)}" if o else s

    # ---- 整数 / 调用
    def do_int(self, k):
        i, m, ops, rs = self.ins[k], self.ins[k].m, self.ins[k].ops, self.ins[k].regs()
        if not rs:
            return
        rt = rs[0]
        if rt == 29 or (len(rs) > 1 and rs[1] == 29):
            return
        if m == "lui":
            sm = re.search(r"%hi\(([^)]+)\)", ops)
            if sm:
                sym = sm.group(1).strip()
                if sym not in self.externs:
                    self.externs.append(sym)
                self.ptr_val[rt] = (sym, 0)
                return
            v = re.search(r"\(0x([0-9A-Fa-f]+)\s*>>\s*16\)", ops)
            n, _ = self.ensure(rt)
            self.lines.append(f"{n} = 0x{v.group(1)};" if v else f"{n} = 0;")
            return
        if m in ("addiu", "daddiu"):
            if len(rs) < 2:
                return
            mo = re.search(r",\s*(-?0x[0-9A-Fa-f]+|-?\d+|\(0x[0-9A-Fa-f]+\s*&\s*0xFFFF\))\s*$", ops)
            imm = _imm(mo.group(1)) if mo else None
            if rs[1] == 0:
                self.ptr_val.pop(rt, None)
                n, ty = self.ensure(rt)
                if ty == "char *":
                    self.lines.append(f"{n} = (char *)(unsigned long){_cint(imm or 0)};")
                else:
                    self.lines.append(f"{n} = {_cint(imm or 0)};")
                return
            self._poke(rt, rs[1], imm or 0)
            n, ty = self.ensure(rt)
            b = self.ptr_val.get(rt)
            if b is not None:
                self.lines.append(f"{n} = {self._castptr(b[0], b[1])};")
            else:
                self.lines.append(f"{n} = {self.oexpr(rs[1])} + {_cint(imm or 0)};")
            return
        if m in ("addu", "daddu") and len(rs) >= 3:
            self.ptr_val.pop(rt, None)
            n, ty = self.ensure(rt)
            a, b = rs[1], rs[2]
            if a == 0:
                self.lines.append(f"{n} = {self.oexpr(b)};")
            elif b == 0:
                self.lines.append(f"{n} = {self.oexpr(a)};")
            elif ty == "char *" or self.roles.get(a) == "p" or self.roles.get(b) == "p":
                ptr = a if self.roles.get(a) == "p" else (b if self.roles.get(b) == "p" else a)
                oth = b if ptr == a else a
                self.lines.append(f"{n} = {self._castptr(self.rn(ptr), 0)} + {self.oexpr(oth)};")
            else:
                self.lines.append(f"{n} = {self.oexpr(a)} + {self.oexpr(b)};")
            return
        if m == "ori":
            n, _ = self.ensure(rt)
            imm = self.oexpr(rs[1]) if _imm(ops.split(",")[-1]) is None else _cint(_imm(ops.split(",")[-1]))
            if isinstance(imm, str) and imm.startswith("0x"):
                self.lines.append(f"{n} = {imm};")
            else:
                self.lines.append(f"{n} = {self.oexpr(rs[1])} | {imm};")
            return
        if m in ("andi", "xori"):
            n, _ = self.ensure(rt)
            op = "&" if m == "andi" else "^"
            self.lines.append(f"{n} = {self.oexpr(rs[1])} {op} {_cint(_imm(ops.split(',')[-1]) or 0)};")
            return
        if m in ("sll", "srl", "sra", "dsll", "dsll32", "dsrl", "dsrl32", "dsra", "dsra32"):
            n, _ = self.ensure(rt)
            if len(rs) >= 3:
                self.lines.append(f"{n} = {self.oexpr(rs[1])} << {self.oexpr(rs[2])};")
            else:
                self.lines.append(f"{n} = {self.oexpr(rs[1])} << {_imm(ops.split(',')[-1]) or 0};")
            return
        if m in ("sllv", "srlv", "srav", "dsllv", "dsrlv") and len(rs) >= 3:
            n, _ = self.ensure(rt)
            self.lines.append(f"{n} = {self.oexpr(rs[1])} << {self.oexpr(rs[2])};")
            return
        if m == "negu":
            n, _ = self.ensure(rt)
            self.lines.append(f"{n} = -{self.oexpr(rs[1])};")
            return
        if m in ("and", "or", "xor", "nor", "subu", "dsubu") and len(rs) >= 3:
            n, _ = self.ensure(rt)
            a, b = self.oexpr(rs[1]), self.oexpr(rs[2])
            if m == "nor":
                self.lines.append(f"{n} = ~({a} | {b});")
            else:
                op = {"and": "&", "or": "|", "xor": "^", "subu": "-", "dsubu": "-"}[m]
                self.lines.append(f"{n} = {a} {op} {b};")
            return
        if m in ("slt", "sltu") and len(rs) >= 3:
            n, _ = self.ensure(rt)
            self.lines.append(f"{n} = {self.oexpr(rs[1])} < {self.oexpr(rs[2])};")
            return
        if m in ("mult", "multu", "div", "divu", "mfhi", "mflo", "break"):
            return
        n, _ = self.ensure(rt)
        self.lines.append(f"{n} = 0;")

    def do_call(self, k):
        i = self.ins[k]
        tgt = i.ops.split(",")[0].strip()
        if tgt and tgt not in self.externs:
            self.externs.append(tgt)
        args = [f"arg{a}" for a in range(4) if (4 + a) in self.used_args]
        n, _ = self.ensure(2)
        self.lines.append(f"{n} = {tgt}({', '.join(args)});")
        for a in range(4):
            self.ptr_val.pop(4 + a, None)

    def do_mem(self, k):
        i, m, ops = self.ins[k], self.ins[k].m, self.ins[k].ops
        mo = mem_operand(ops)
        if mo is None:
            return
        base = mo[2]
        if base == 29:
            return
        data = i.regs()[0]
        if data == 29:
            return
        cty = {"lw": "int", "lwu": "unsigned int", "sw": "int", "ld": "long long",
               "sd": "long long", "lh": "short", "lhu": "unsigned short", "sh": "short",
               "lb": "signed char", "lbu": "unsigned char", "sb": "signed char",
               "lwl": "int", "lwr": "int", "swl": "int", "swr": "int"}[m]
        a = self.addr(ops)
        if m.startswith("s"):
            self.lines.append(f"*({cty} *)({a}) = ({cty})({self.oexpr(data)});" if data != 0
                              else f"*({cty} *)({a}) = 0;")
        else:
            n, _ = self.ensure(data)
            self.lines.append(f"{n} = (unsigned long)*({cty} *)({a});")

    def do_vec(self, k):
        i, m, ops = self.ins[k], self.ins[k].m, self.ins[k].ops
        rt = i.regs()[0]
        a = self.addr(ops)
        if m == "lq":
            self.n += 1
            v = f"vt{self.n}"
            self.decl[v] = ("v4si", None)
            if self.variant == "ptr":
                pv = f"px{self.n}"
                self.decl[pv] = ("char *", None)
                self.lines.append(f"{pv} = (char *)({a});")
                self.lines.append(f"{v} = *(v4si *)({pv});")
                self.pend[rt] = (v, pv, True)
            else:
                self.lines.append(f"{v} = *(v4si *)({a});")
                self.pend[rt] = (v, a, False)
            self.vreg[rt] = v
            return
        if rt == 0:
            self.lines.append(f'__asm__ volatile ("sq $0, 0(%0)" : : "r" ({a}));')
            return
        if rt in self.pend:
            v, sa, isptr = self.pend.pop(rt)
            v = self.vreg.get(rt, v)
            if self.variant == "direct" and not isptr and \
                    self.lines and self.lines[-1] == f"{v} = *(v4si *)({sa});":
                self.lines[-1] = f"*(v4si *)({a}) = *(v4si *)({sa});"
                self.decl.pop(v, None)
            elif self.variant == "ptr":
                pd = f"pd{self.n}"
                self.decl[pd] = ("char *", None)
                self.lines.append(f"{pd} = (char *)({a});")
                self.lines.append(f"*(v4si *)({pd}) = {v};")
            else:
                self.lines.append(f"*(v4si *)({a}) = {v};")
            return
        if rt in self.vreg:
            self.lines.append(f"*(v4si *)({a}) = {self.vreg[rt]};")
            return
        self.lines.append(f'__asm__ volatile ("sq %1, 0(%0)" : : "r" ({a}), "r" ({self.oexpr(rt)}));')

    def do_por(self, k):
        i = self.ins[k]
        rs = i.regs()
        rd = rs[0]
        if rd == 0:
            return
        self.n += 1
        v = f"vp{self.n}"
        self.decl[v] = ("v4si", None)
        a = rs[1] if len(rs) > 1 else 0
        b = rs[2] if len(rs) > 2 else 0
        if a == 0 and b == 0:
            self.lines.append(f'__asm__ volatile ("por %0, $0, $0" : "=r" ({v}));')
        elif a == 0:
            self.lines.append(f"{v} = {self.vget(b)};")
        elif b == 0:
            self.lines.append(f"{v} = {self.vget(a)};")
        else:
            self.lines.append(f"{v} = (v4si)__builtin_mips5900_por((v2di){self.vget(a)}, (v2di){self.vget(b)});")
        self.vreg[rd] = v

    def vget(self, r):
        if r in self.vreg:
            return self.vreg[r]
        return f"(v4si)(unsigned long)0" if r == 0 else f"*(v4si *)&{self.ensure(r)[0]}"

    def do_fp(self, k):
        i, m, ops = self.ins[k], self.ins[k].m, self.ins[k].ops
        fs = [int(x) for x in re.findall(r"\$f(\d{1,2})\b", ops)]
        if m == "lwc1":
            mo = mem_operand(ops)
            if mo and mo[2] == 29:
                return
            self.n += 1
            v = f"ft{self.n}"
            self.decl[v] = ("float", None)
            self.lines.append(f"{v} = *(float *)({self.addr(ops)});")
            self.fp[fs[0]] = v
            return
        if m == "swc1":
            mo = mem_operand(ops)
            if mo and mo[2] == 29:
                return
            self.lines.append(f"*(float *)({self.addr(ops)}) = {self.fp.get(fs[0], '0.0f')};")
            return
        if m == "mtc1":
            self.n += 1
            v = f"ft{self.n}"
            self.decl[v] = ("float", None)
            src = self.oexpr(i.regs()[0]) if i.regs() else "0"
            self.lines.append(f'__asm__ volatile ("mtc1 %1, %0" : "=f" ({v}) : "r" ({src}));')
            self.fp[fs[0]] = v
            return
        if m == "mfc1" and i.regs():
            n, _ = self.ensure(i.regs()[0])
            self.lines.append(f'__asm__ volatile ("mfc1 %0, %1" : "=r" ({n}) : "f" ({self.fp.get(fs[0], "0.0f")}));')
            return
        if m in ("add.s", "sub.s", "mul.s", "div.s") and len(fs) >= 3:
            op = {"add.s": "+", "sub.s": "-", "mul.s": "*", "div.s": "/"}[m]
            self.n += 1
            v = f"ft{self.n}"
            self.decl[v] = ("float", None)
            self.lines.append(f"{v} = {self.fp.get(fs[1], '0.0f')} {op} {self.fp.get(fs[2], '0.0f')};")
            self.fp[fs[0]] = v
            return
        if m in ("mov.s", "neg.s", "abs.s", "sqrt.s", "cvt.s.w", "cvt.w.s", "trunc.w.s") and len(fs) >= 2:
            self.fp[fs[0]] = self.fp.get(fs[1], "0.0f")
            return

    # ---- 组装
    def build(self):
        self.infer()
        self.ret_kind = "int" if any(
            i.m in INT_OK | MEM_OK and i.regs() and i.regs()[0] == 2
            and i.m not in ("sw", "sq", "sd", "sh", "sb") for i in self.ins) else None
        body = self.emit()
        blob = "\n".join(body)
        for a in range(4):
            if re.search(rf"\barg{a}\b", blob):
                self.used_args.add(4 + a)
        head = []
        if self.prelude:
            head += ["typedef int v4si __attribute__((mode(V4SI)));",
                     "typedef long long v2di __attribute__((mode(V2DI)));"]
        for e in self.externs:
            if e.startswith("D_"):
                head.append(f"extern unsigned char {e}[];")
            elif re.match(r"^[A-Za-z_]\w*$", e):
                head.append(f"extern int {e}();")
        args = []
        for a in range(4):
            if (4 + a) in self.used_args:
                ty = "void *" if self.roles.get(4 + a) == "p" else "int"
                args.append(f"{ty} arg{a}")
        rty = "int" if self.ret_kind == "int" else "void"
        out = head
        out.append(f"{rty} {self.sym}({', '.join(args) if args else 'void'}) {{")
        if self.stackbuf:
            out.append("    unsigned char sb[8192];")
        for nm, (ty, init) in self.decl.items():
            if nm.startswith("arg"):
                continue
            out.append(f"    {ty} {nm};")
        out += ["    " + l for l in body]
        out.append("}")
        return "\n".join(out) + "\n"


def emit_c(sym, ins, labels, prelude=True, variant="direct"):
    reason = domain_check(ins, labels)
    if reason:
        return None, reason
    em = Emitter(sym, ins, labels, prelude, variant)
    return em.build(), None


def refs_of(sym, ins):
    out = set()
    for i in ins:
        if i.m in ("jal", "j") and not i.ops.startswith("$"):
            t = i.ops.split(",")[0].strip()
            if t:
                out.add(t)
    return out


# ---------------------------------------------------------------- 编译 / 比对

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def compile_c(src, out, flags):
    return run([str(GCC), *flags, "-I", "include", "-c", "-o", str(out), str(src)], cwd=str(PROJ))


def build_target(sym, out):
    s = target_s(sym)
    if s is None:
        return None, "no_glabel_endlabel"
    out.mkdir(parents=True, exist_ok=True)
    (out / "target.s").write_text(s, encoding="utf-8")
    r = run([str(AS), "-EL", "-march=r5900", "-I", "include", "-o", str(out / "target.o"),
             str(out / "target.s")], cwd=str(PROJ))
    if r.returncode:
        return None, "as: " + r.stderr[-200:]
    return out / "target.o", None


def match(sym, tgt, cand, work):
    j = work / f"diff_{cand.stem}.json"
    r = run([str(OBJDIFF), "diff", "-1", str(tgt), "-2", str(cand), "-o", str(j),
             "--format", "json"], cwd=str(REPO))
    if r.returncode:
        return None, "objdiff rc=%d %s" % (r.returncode, r.stderr[-160:])
    data = json.loads(j.read_text())
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    return per.get(sym), None


# ---------------------------------------------------------------- CLI

def cmd_list(args):
    pool = d_pool()
    print(f"D 档：{len(pool)} 个 / {sum(p['size'] for p in pool)} B")
    kinds = collections.Counter()
    for p in pool:
        for s in trace_shapes(p["insns"]):
            kinds[s.kind] += 1
    print("形状计数:", dict(kinds))
    dom = collections.Counter()
    for p in pool:
        ins, labels = p["insns"], parse_block(p["name"])[1]
        r = domain_check(ins, labels)
        dom["in_domain" if r is None else r.split(":")[0]] += 1
    fn = collections.Counter()
    bd = collections.Counter()
    for p in pool:
        r = domain_check(p["insns"], parse_block(p["name"])[1])
        k = "in_domain" if r is None else r.split(":")[0]
        fn[k] += 1
        bd[k] += p["size"]
    tot = sum(bd.values())
    for k, _ in bd.most_common():
        print(f"  {k:20s} {fn[k]:4d} fn  {bd[k]:8d} B  ({100.0 * bd[k] / tot:5.1f}%)")


def cmd_analyze(args):
    ins, labels = parse_block(args.sym)
    if ins is None:
        print("no block")
        return 1
    for s in trace_shapes(ins):
        print(f"  {s.kind:10s} src={s.src}:{s.off_src} dst={s.dst}:{s.off_dst} tmp={s.tmp} idx={s.idx}")
    print("domain:", domain_check(ins, labels) or "in_domain")
    return 0


def cmd_emit(args):
    ins, labels = parse_block(args.sym)
    if ins is None:
        print("no block")
        return 1
    c, reason = emit_c(args.sym, ins, labels)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if c is None:
        (outdir / f"{args.sym}.shape.txt").write_text(f"OUT_OF_DOMAIN: {reason}\n")
        print(f"{args.sym}: OUT_OF_DOMAIN {reason}")
        return 2
    (outdir / f"{args.sym}.shape.c").write_text(c)
    print(f"{args.sym}: emitted -> {outdir / (args.sym + '.shape.c')}")
    return 0


def pick_samples(pool, n):
    ps = sorted(pool, key=lambda p: (p["size"], p["name"]))
    tiny = [p for p in ps if p["size"] <= 64]
    mid = [p for p in ps if 64 < p["size"] <= 256]
    big = [p for p in ps if p["size"] > 256]
    want_t = round(n * 0.36)
    want_m = round(n * 0.36)
    want_b = n - want_t - want_m
    out = []
    for lst, k in ((tiny, want_t), (mid, want_m), (big, want_b)):
        k = min(k, len(lst))
        if k <= 0:
            continue
        step = len(lst) / k
        out += [lst[int(i * step)] for i in range(k)]
    return out


FLAGSETS = [("O2", ["-O2", "-falign-functions=4", "-ffunction-sections"]),
            ("O1", ["-O1", "-falign-functions=4", "-ffunction-sections"]),
            ("O3", ["-O3", "-falign-functions=4", "-ffunction-sections"])]


def cmd_batch(args):
    pool = d_pool()
    dom = []
    reasons = collections.Counter()
    rbytes = collections.Counter()
    for p in pool:
        ins, labels = p["insns"], parse_block(p["name"])[1]
        r = domain_check(ins, labels)
        if r is None:
            dom.append(p)
        else:
            reasons[r.split(":")[0]] += 1
            rbytes[r.split(":")[0]] += p["size"]
    print("D 档全池：%d 个 / %d B；形状域内 %d 个 / %d B (%.1f%% fn, %.1f%% B)"
          % (len(pool), sum(p["size"] for p in pool), len(dom), sum(p["size"] for p in dom),
             100.0 * len(dom) / len(pool), 100.0 * sum(p["size"] for p in dom) / sum(p["size"] for p in pool)))
    print("域外主因:", ", ".join("%s %d fn/%d B" % (k, reasons[k], rbytes[k]) for k, _ in reasons.most_common()))
    samples = pick_samples(dom, args.samples)
    work = REPO / ".tmp/lqsq/work/batch"
    work.mkdir(parents=True, exist_ok=True)
    used = 0
    results = []
    print(f"样本 {len(samples)} 个；编译上限 {args.max_compiles}")
    for p in samples:
        sym, size = p["name"], p["size"]
        ins, labels = p["insns"], parse_block(p["name"])[1]
        shapes = trace_shapes(ins)
        c, reason = emit_c(sym, ins, labels)
        rec = {"sym": sym, "size": size, "n_shapes": len(shapes),
               "shape_kinds": dict(collections.Counter(s.kind for s in shapes)),
               "domain": "in" if c is not None else reason,
               "best": None, "by_flag": {}, "note": None}
        if c is None:
            rec["note"] = "no_candidate"
            results.append(rec)
            print(f"  {sym:16s} {size:6d}B OUT_OF_DOMAIN({reason})")
            continue
        src = work / f"{sym}.c"
        src.write_text(c)
        tgt, terr = build_target(sym, work / sym)
        if tgt is None:
            rec["note"] = "target:" + str(terr)
            results.append(rec)
            print(f"  {sym:16s} TARGET FAIL {terr}")
            continue
        if used + 3 > args.max_compiles:
            rec["note"] = "budget_exhausted"
            results.append(rec)
            print("  [budget exhausted]")
            break
        used += 3
        best = None
        for fl, fls in FLAGSETS:
            o = work / f"{sym}.{fl}.o"
            r = compile_c(src, o, fls)
            if r.returncode:
                rec["by_flag"][fl] = "cc_fail:" + r.stderr.strip().split("\n")[0][:90]
                continue
            mp, merr = match(sym, tgt, o, work)
            rec["by_flag"][fl] = mp
            if mp is not None and (best is None or mp > best[0]):
                best = (mp, fl)
            if mp == 100.0:
                break
        rec["best"] = best
        results.append(rec)
        print(f"  {sym:16s} {size:6d}B {rec['shape_kinds']} best={best} {rec['by_flag']}")
    (work / "batch_result.json").write_text(json.dumps(results, indent=1))
    ok = [r for r in results if r["best"]]
    hit100 = [r for r in ok if r["best"][0] == 100.0]
    ge80 = [r for r in ok if r["best"][0] >= 80.0]
    print("\n=== 汇总 ===")
    print(f"样本 {len(results)}；有候选 {sum(1 for r in results if r['domain'] == 'in')}；"
          f"有评分 {len(ok)}；100% {len(hit100)}；≥80% {len(ge80)}")
    print(f"编译次数 {used}/{args.max_compiles}")
    if ok:
        vals = sorted(r["best"][0] for r in ok)
        print("best 中位 %.2f 均值 %.2f 最小 %.2f 最大 %.2f" %
              (vals[len(vals) // 2], sum(vals) / len(vals), vals[0], vals[-1]))
        bc = collections.Counter(r["best"][1] for r in ok)
        print("最佳档位分布:", dict(bc))
    return 0


def write_target_multi(syms, path):
    """把多个 glabel..endlabel 块拼成一个目标 .s（仓库 auto_match_trivial.py 同款做法）。"""
    chunks = [PRE.rstrip("\n")]
    for sym in syms:
        p, gi, en = block_bounds(sym)
        if gi is None or en is None:
            continue
        L = p.read_text(encoding="utf-8", errors="replace").split("\n")
        chunks.append("\n".join(L[gi:en + 1]))
    path.write_text("\n".join(chunks) + "\n", encoding="utf-8")


def cmd_combined(args):
    """合并单 TU 批量：N 个候选合成一个 .c，每档只调用 ee-gcc 1 次。"""
    pool = d_pool()
    dom, reasons, rbytes = [], collections.Counter(), collections.Counter()
    for p in pool:
        ins, labels = p["insns"], parse_block(p["name"])[1]
        r = domain_check(ins, labels)
        if r is None:
            dom.append(p)
        else:
            reasons[r.split(":")[0]] += 1
            rbytes[r.split(":")[0]] += p["size"]
    allbytes = sum(p["size"] for p in pool)
    print("D 档全池：%d 个 / %d B" % (len(pool), allbytes))
    print("形状域内：%d 个 / %d B (%.1f%% fn, %.1f%% B)"
          % (len(dom), sum(p["size"] for p in dom), 100.0 * len(dom) / len(pool),
             100.0 * sum(p["size"] for p in dom) / allbytes))
    print("域外主因：" + ", ".join("%s %d fn/%dB" % (k, reasons[k], rbytes[k])
                                 for k, _ in reasons.most_common()))
    names = [p["name"] for p in dom]
    S = set(names)
    callers = [n for n in names if refs_of(n, parse_block(n)[0]) & S]
    names = [n for n in names if n not in callers]
    if args.samples and args.samples < len(names):
        keep = {p["name"] for p in pick_samples([p for p in dom if p["name"] in set(names)], args.samples)}
        names = [n for n in names if n in keep]
    print("合并 TU：%d 个符号；因同 TU 内互相调用而排除 %d 个：%s"
          % (len(names), len(callers), ",".join(callers)))
    work = REPO / ".tmp/lqsq/work/combined"
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, n in enumerate(names):
        ins, labels = parse_block(n)
        c, _ = emit_c(n, ins, labels, prelude=(i == 0))
        parts.append(f"/* {n} */\n{c}")
    probe = work / "probe.c"
    probe.write_text("\n".join(parts), encoding="utf-8")
    tgt_s = work / "target.s"
    write_target_multi(names, tgt_s)
    tgt_o = work / "target.o"
    r = run([str(AS), "-EL", "-march=r5900", "-I", "include", "-o", str(tgt_o), str(tgt_s)],
            cwd=str(PROJ))
    if r.returncode:
        print("AS FAIL", r.stderr[-400:])
        return 1
    res = {n: {} for n in names}
    used = 0
    for fl, fls in FLAGSETS:
        if used + 1 > args.max_compiles:
            print("[budget exhausted]")
            break
        used += 1
        o = work / f"probe.{fl}.o"
        rr = compile_c(probe, o, fls)
        if rr.returncode:
            print(f"{fl}: CC FAIL {rr.stderr.strip().splitlines()[0][:160] if rr.stderr.strip() else ''}")
            for n in names:
                res[n][fl] = None
            continue
        mp, err = match_multi(tgt_o, o, work / f"diff.{fl}.json")
        if mp is None:
            print(f"{fl}: objdiff fail {err}")
            continue
        for n in names:
            res[n][fl] = mp.get(n)
        got = sum(1 for n in names if mp.get(n) is not None)
        print(f"{fl}: 评分 {got}/{len(names)}；100% {sum(1 for n in names if mp.get(n)==100.0)}")
    out = []
    for n in names:
        vals = {k: v for k, v in res[n].items() if v is not None}
        best = max(vals.values()) if vals else None
        bestf = max(vals, key=vals.get) if vals else None
        out.append({"sym": n, "size": next(p["size"] for p in dom if p["name"] == n),
                    "by_flag": vals, "best": best, "best_flag": bestf})
    (work / "combined_result.json").write_text(json.dumps(out, indent=1))
    ok = [r for r in out if r["best"] is not None]
    print("\n=== 合并 TU 汇总（%d 符号，%d 次 ee-gcc）===" % (len(names), used))
    print("有评分 %d；100%% %d；≥90%% %d；≥80%% %d"
          % (len(ok), sum(1 for r in ok if r["best"] == 100.0),
             sum(1 for r in ok if r["best"] >= 90), sum(1 for r in ok if r["best"] >= 80)))
    if ok:
        vals = sorted(r["best"] for r in ok)
        print("best 中位 %.2f 均值 %.2f 最小 %.2f 最大 %.2f"
              % (vals[len(vals)//2], sum(vals)/len(vals), vals[0], vals[-1]))
        bc = collections.Counter(r["best_flag"] for r in ok)
        print("最佳档位分布:", dict(bc))
    return 0


def match_multi(tgt, cand, jpath):
    r = run([str(OBJDIFF), "diff", "-1", str(tgt), "-2", str(cand), "-o", str(jpath),
             "--format", "json"], cwd=str(REPO))
    if r.returncode:
        return None, r.stderr[-200:]
    data = json.loads(jpath.read_text())
    return {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
            if s.get("kind") == "SYMBOL_FUNCTION"}, None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    a = sub.add_parser("analyze"); a.add_argument("sym"); a.set_defaults(func=cmd_analyze)
    a = sub.add_parser("emit"); a.add_argument("sym"); a.add_argument("outdir"); a.set_defaults(func=cmd_emit)
    a = sub.add_parser("batch")
    a.add_argument("--samples", type=int, default=22)
    a.add_argument("--max-compiles", type=int, default=60)
    a.set_defaults(func=cmd_batch)
    a = sub.add_parser("combined")
    a.add_argument("--samples", type=int, default=0, help="0 = 全部形状域内样本")
    a.add_argument("--max-compiles", type=int, default=3)
    a.set_defaults(func=cmd_combined)
    args = ap.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
