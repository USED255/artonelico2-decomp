#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""签名推断原型：从 `jal <sym>` 调用点恢复被调用者的参数/返回类型，并可把签名替换进 m2c 草稿。

动机（2026-10-05，路线 B / task-3）：
  [docs/R16-F类结构阻塞分析.md](../docs/R16-F类结构阻塞分析.md) 的结论是：F 类 <80% 池
  「长度相近但指令选择/分配是另一份等价实现」，首差里 85% 落在栈帧/保存寄存器；
  其中一类**机械可修**的成因是**函数签名（参数/返回类型）推断错**——
  典型：`LibgccCommon_71` 被 m2c 推成 `u64` 参数（目标用 `srl`/`sw`，是 32 位），
  `func_00303730` 里变量被推成 unsigned（目标 `slti`，生成 `sltiu`）。
  m2c 只看**函数体内部**用法；本工具补上**调用点**这一路证据。

做什么：
  1. 扫 `routebjp/asm/cod/*.s` 里所有 `jal <sym>`（含 delay slot 的 noreorder 形态），
     按调用点回溯 `$a0`–`$a3` 是怎么被设置的，前向看 `$v0` 是怎么被用的；
  2. 输出**建议签名**（返回类型 + 每个参数类型 + 置信度 + 逐调用点证据）；
  3. `replace_signature()` / `suggest_and_replace()` 把建议**只改类型、不改参数名与个数**地
     写回 m2c 草稿（保证函数体里 `argN` 引用不被打断）。

证据分级：调用点证据是 `[实测]`（读自 asm）；推断出的类型是 `[推断]`。
工具本身不做正确性断言——是否命中由 objdiff 决定。

用法：
  python3 routebjp/tools/infer_sig.py scan <sym> [--json]
  python3 routebjp/tools/infer_sig.py scan-file <sym> <draft.c>      # 显示 建议 vs 现状 的差异
  python3 routebjp/tools/infer_sig.py apply <sym> <in.c> <out.c>     # 写替换后的草稿
  python3 routebjp/tools/infer_sig.py batch --classes F_branch_call,D2_multi_call [--limit N]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # routebjp/
REPO = ROOT.parent                                     # workspace root
ASM = ROOT / "asm" / "cod"
CACHE = REPO / ".tmp" / "sig-analysis" / "callsites.json"

# --- 汇编行解析 -------------------------------------------------------------
INSTR_RE = re.compile(r"^\s*/\*\s*(?:[0-9A-Fa-f]+\s+)+\*/\s*([a-z][a-z0-9._]*)\s*(.*)$")
LABEL_RE = re.compile(r"^\s*([.A-Za-z_][\w.]*)\s*:")
GLOB_RE = re.compile(r"^\s*(glabel|endlabel)\s+(\S+)")

# 写入 ops[0]（GPR 目标）的助记符；其余按「读 ops」处理
_WRITE0 = {
    "addiu", "addi", "addu", "add", "subu", "sub", "daddu", "dadd", "dsubu", "dsub",
    "and", "andi", "or", "ori", "nor", "xor", "xori", "lui", "sll", "srl", "sra",
    "dsll", "dsll32", "dsrl", "dsrl32", "dsra", "dsra32", "slt", "sltu", "slti", "sltiu",
    "lw", "lwu", "lb", "lbu", "lh", "lhu", "ld", "lwl", "lwr", "ldl", "ldr", "lq",
    "movz", "movn", "mfhi", "mflo", "mfc1", "cfc1", "mul", "madd", "maddu", "msub", "msubu",
    "max", "min", "plzcw", "pabsh", "por", "pand", "pxor", "pnor",
}
# 完全不写 GPR 的助记符（分支/跳转/存储/NOP/浮点搬运）
_NO_WRITE0 = {
    "sb", "sh", "sw", "sd", "sq", "swl", "swr", "sdl", "sdr",
    "beq", "bne", "beqz", "bnez", "beql", "bnel", "beqzl", "bnezl", "bltz", "bgez",
    "bltzl", "bgezl", "bltzal", "bgezal", "blez", "bgtz", "blezl", "bgtzl",
    "b", "j", "jr", "jalr", "jal", "nop", "sync", "break", "syscall",
    "mult", "multu", "div", "divu", "dmult", "dmultu", "ddiv", "ddivu",
    "mtc1", "ctc1", "mtc0", "ctc0", "mthi", "mtlo", "dmtc1", "dctc1",
    "c.eq.s", "c.lt.s", "c.le.s", "cop1", "cop2", "vcallms", "vadd", "vmul",
}

_TY_INT = {"s8", "u8", "s16", "u16", "s32", "u32", "s64", "u64", "int", "uint",
           "short", "unsigned", "M2C_UNK", "M2C_UNK8", "M2C_UNK16", "M2C_UNK32", "M2C_UNK64"}
_TY_PTR = {"ptr", "u8*", "s8*", "void*", "void *", "s16*", "u16*", "s32*", "u32*", "char*"}
_TY_FLOAT = {"f32", "f64", "float", "double"}


def split_ops(s: str) -> list[str]:
    return [t.strip() for t in s.split(",") if t.strip()]


def regnum(tok: str) -> int | None:
    """`$4` / `$a0` → 寄存器号；不是寄存器返回 None。"""
    m = re.fullmatch(r"\$(\d{1,2})", tok)
    if m:
        n = int(m.group(1))
        return n if 0 <= n <= 31 else None
    m = re.fullmatch(r"\$([a-z]\w*)", tok)
    if not m:
        return None
    name = m.group(1)
    abi = {"zero": 0, "at": 1, "v0": 2, "v1": 3, "a0": 4, "a1": 5, "a2": 6, "a3": 7,
           "t0": 8, "t1": 9, "t2": 10, "t3": 11, "t4": 12, "t5": 13, "t6": 14, "t7": 15,
           "s0": 16, "s1": 17, "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23,
           "t8": 24, "t9": 25, "k0": 26, "k1": 27, "gp": 28, "sp": 29, "fp": 30, "s8": 30, "ra": 31}
    if name in abi:
        return abi[name]
    m2 = re.fullmatch(r"r(\d{1,2})", name)
    return int(m2.group(1)) if m2 else None


def base_reg(op: str) -> int | None:
    m = re.search(r"\(([^()]*)\)\s*$", op)
    return regnum(m.group(1).strip()) if m else None


def imm_of(op: str) -> int | None:
    op = op.strip()
    m = re.fullmatch(r"(-?)0x([0-9A-Fa-f]+)", op)
    if m:
        v = int(m.group(2), 16)
        return -v if m.group(1) else v
    m = re.fullmatch(r"(-?\d+)", op)
    return int(m.group(1)) if m else None


# --- 文件解析 ---------------------------------------------------------------
class Parsed:
    __slots__ = ("name", "items", "labels")

    def __init__(self, name: str, items: list[dict]):
        self.name = name
        self.items = items
        self.labels = {it["name"] for it in items if it.get("label")}


def parse_file(path: Path) -> Parsed:
    text = path.read_text(encoding="utf-8", errors="replace")
    items: list[dict] = []
    for i, line in enumerate(text.split("\n")):
        m = INSTR_RE.match(line)
        if m:
            ops = split_ops(m.group(2))
            items.append({"kind": "ins", "mnem": m.group(1).lower(), "ops": ops, "lineno": i + 1})
            continue
        g = GLOB_RE.match(line)
        if g:
            items.append({"kind": "glabel" if g.group(1) == "glabel" else "endlabel",
                          "name": g.group(2).strip(), "lineno": i + 1})
            continue
        l = LABEL_RE.match(line)
        if l and not line.strip().startswith("."):
            items.append({"kind": "label", "name": l.group(1), "lineno": i + 1})
        elif l:
            items.append({"kind": "label", "name": l.group(1), "lineno": i + 1})
    return Parsed(path.name, items)


# --- 索引：callee -> [(file, lineno)] --------------------------------------
def build_index(force: bool = False) -> dict[str, list]:
    if not force and CACHE.is_file():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    idx: dict[str, list] = {}
    for f in sorted(ASM.glob("*.s")):
        p = parse_file(f)
        for it in p.items:
            if it["kind"] == "ins" and it["mnem"] == "jal" and it["ops"]:
                tgt = it["ops"][0].strip()
                idx.setdefault(tgt, []).append([f.name, it["lineno"]])
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(idx, separators=(",", ":")), encoding="utf-8")
    return idx


# --- 被调用者自身：arity + 内部类型线索 ------------------------------------
def callee_body(sym: str) -> list[dict] | None:
    f = ASM / f"{sym}.s"
    if not f.is_file():
        return None
    p = parse_file(f)
    out, inside = [], False
    for it in p.items:
        if it["kind"] == "glabel" and it["name"] == sym:
            inside = True
            continue
        if it["kind"] == "endlabel" and inside:
            break
        if inside:
            out.append(it)
    return out


def arity_and_hints(sym: str) -> tuple[int, dict]:
    """返回 (arity, hints)。arity = 在**被写之前**被读到的最大参数寄存器号+1。

    hints: {'signed':bool|None, 'wide64':bool, 'float':bool} —— 来自函数体内部的弱线索。
    """
    body = callee_body(sym)
    if body is None:
        return 0, {}
    written: set[int] = {0, 29, 30, 31}
    maxp = -1
    hint = {"signed": None, "wide64": False, "float": False}
    for it in body:
        if it["kind"] != "ins":
            continue
        mnem, ops = it["mnem"], it["ops"]
        # 读寄存器位置
        if mnem in _WRITE0:
            reads, dest = ops[1:], (ops[0] if ops else None)
        elif mnem in _NO_WRITE0:
            reads, dest = ops, (31 if mnem in ("jal", "jalr") else None)
        else:
            reads, dest = ops, (ops[0] if ops and regnum(ops[0]) is not None else None)
        for r in reads:
            n = regnum(r)
            if n is None:
                b = base_reg(r)
                if b is not None:
                    n = b
            if n is None:
                continue
            if 4 <= n <= 7 and n not in written:
                maxp = max(maxp, n)
            if n == 2:
                pass
            if mnem in ("bltz", "blez", "slt", "slti", "sra", "srav", "dsra32", "dsra") and n in (2, 4, 5, 6, 7):
                hint["signed"] = True
            if mnem in ("sltiu", "sltu", "srl", "srlv", "dsrl", "dsrl32", "lbu", "lhu") and n in (2, 4, 5, 6, 7):
                if hint["signed"] is None:
                    hint["signed"] = False
        if mnem in ("dsll", "dsll32", "dsrl", "dsrl32", "dsra", "dsra32", "daddiu", "daddu", "ld", "sd"):
            hint["wide64"] = True
        if mnem in ("mtc1", "cvt.s.w", "cvt.d.w", "lwc1", "swc1", "add.s", "sub.s", "mul.s", "div.s", "mov.s"):
            hint["float"] = True
        # 应用写入
        if dest is not None:
            n = regnum(dest) if isinstance(dest, str) else None
            if n is not None:
                written.add(n)
    # maxp 是**寄存器号**（4..7）；arity = 真正被读到的参数个数
    return (maxp - 3 if maxp >= 4 else 0), hint


# --- 调用点分析 -------------------------------------------------------------
def _is_barrier(it: dict) -> bool:
    if it["kind"] in ("label", "glabel", "endlabel"):
        return True
    m = it["mnem"]
    return m in {"j", "jal", "jalr", "jr", "b", "beq", "bne", "beqz", "bnez", "beql", "bnel",
                 "beqzl", "bnezl", "bltz", "bgez", "bltzl", "bgezl", "bltzal", "bgezal",
                 "blez", "bgtz", "blezl", "bgtzl"}


def _alias_info(items: list[dict], idx: int) -> tuple[str, str] | None:
    """判断 items[idx] 是否是 `dest = src` 的搬运；返回 (dest_reg, src_reg)。"""
    it = items[idx]
    m, ops = it["mnem"], it["ops"]
    if m in ("daddu", "addu", "or") and len(ops) >= 3 and regnum(ops[1]) == 0:
        return ops[0], ops[2]
    if m == "move" and len(ops) >= 2:
        return ops[0], ops[1]
    return None


def _prov_backward(items: list[dict], j: int, reg: int, depth: int = 0,
                   memo: dict | None = None) -> dict:
    """从 jal（items[j]）往前找 reg 的最近一次写入并分类。"""
    if depth > 6:
        return {"kind": "unk"}
    seen = 0
    i = j - 1
    while i >= 0 and seen < 40:
        it = items[i]
        if it["kind"] in ("label", "glabel"):
            break
        if it["kind"] == "ins" and _is_barrier(it):
            # 分支/jal：其 delay slot 在 i+1（已扫过）；jal 会定义 $2/$31
            if it["mnem"] == "jal" and it["ops"] and reg == 2:
                callee = it["ops"][0].strip()
                if re.fullmatch(r"[\w.]+", callee):
                    return {"kind": "ret", "callee": callee}
            if it["mnem"] == "jalr" and reg == 2:
                return {"kind": "ret", "callee": None}
            break
        if it["kind"] == "ins":
            m, ops = it["mnem"], it["ops"]
            n = len(ops)
            dest = None
            if m in _WRITE0 and n:
                dest = regnum(ops[0])
            elif m in ("jal", "jalr"):
                dest = 31 if reg == 31 else None
            if dest == reg:
                # 原地运算（dest == 源寄存器）：不终止回溯，继续往前找该寄存器的前一次写入
                if n >= 2 and regnum(ops[1]) == reg:
                    i -= 1
                    seen += 1
                    continue
                # 精确分类
                if m in ("addiu", "addi", "ori", "andi", "xori") and n >= 3:
                    s = regnum(ops[1])
                    imm = imm_of(ops[2])
                    if s == 0 and imm is not None:
                        return {"kind": "int", "value": imm, "signed": imm < 0, "width": 32}
                    if ops[2].startswith("%lo(") and i - 1 >= 0:
                        prev = items[i - 1]
                        if prev["kind"] == "ins" and prev["mnem"] == "lui" and prev["ops"]:
                            sym = re.sub(r"^%lo\(|\)$", "", ops[2].strip())
                            return {"kind": "addr", "sym": sym, "off": imm if imm is not None else 0}
                    if s is not None and 4 <= s <= 7:
                        return {"kind": "arith", "src": s, "op": m}
                    if s == 29 or s == 30:
                        return {"kind": "local"}
                    return {"kind": "int", "value": imm, "width": 32}
                if m == "lui" and n >= 2 and ops[1].startswith("%hi("):
                    sym = re.sub(r"^%hi\(|\)$", "", ops[1].strip())
                    return {"kind": "addr", "sym": sym, "off": 0}
                if m in ("lw", "lwu", "ld", "lq") and n >= 2:
                    b = base_reg(ops[1])
                    off = imm_of(ops[1].split("(")[0]) if "(" in ops[1] else None
                    kind = "ldst"
                    return {"kind": kind, "width": {"lw": 32, "lwu": 32, "ld": 64, "lq": 128}[m],
                            "base": b, "off": off}
                if m in ("lb", "lbu", "lh", "lhu") and n >= 2:
                    b = base_reg(ops[1])
                    return {"kind": "ldst", "width": {"lb": 8, "lbu": 8, "lh": 16, "lhu": 16}[m],
                            "base": b, "off": None, "unsigned": m in ("lbu", "lhu")}
                if m in ("sll", "srl", "sra", "dsll", "dsrl", "dsra", "dsll32", "dsrl32", "dsra32") and n >= 3:
                    return {"kind": "shift", "src": regnum(ops[1]), "unsigned": m.startswith(("srl", "dsrl"))}
                if m in ("mfhi", "mflo"):
                    return {"kind": "hiloint"}
                if m in ("mfc1", "cfc1"):
                    return {"kind": "floatbits"}
                if m in ("slt", "sltu", "slti", "sltiu"):
                    return {"kind": "cmp"}
                al = _alias_info(items, i)
                if al:
                    src = regnum(al[1])
                    if src is not None:
                        return {"kind": "alias", "src": src}
                return {"kind": "other", "mnem": m}
        i -= 1
        seen += 1
    return {"kind": "unk"}


def _prov_forward_v0(items: list[dict], j: int) -> dict:
    """jal 之后 $v0 怎么用（跳过 delay slot）。"""
    i = j + 2
    seen = 0
    while i < len(items) and seen < 16:
        it = items[i]
        if it["kind"] in ("label", "glabel", "endlabel"):
            return {"use": "label_boundary"}
        if it["kind"] == "ins":
            m, ops = it["mnem"], it["ops"]
            if m == "jal" and ops:
                return {"use": "ret"}
            if m in _WRITE0 and ops and regnum(ops[0]) == 2:
                return {"use": "overwritten"}
            # $2 出现在哪里
            positions = []
            for k, o in enumerate(ops):
                if regnum(o) == 2:
                    positions.append(k)
                elif base_reg(o) == 2:
                    positions.append(("base", k))
            if positions:
                if m in ("beqz", "bnez", "beq", "bne") or m.startswith(("bltz", "bgez", "blez", "bgtz")):
                    return {"use": "test"}
                if m in ("lw", "lb", "lbu", "lh", "lhu", "sw", "sb", "sh", "sd", "ld", "lq", "sq"):
                    if any(isinstance(p, tuple) for p in positions):
                        return {"use": "deref", "width": 32}
                    return {"use": "store"}
                if m in ("daddu", "addu", "or") and positions == [1]:
                    return {"use": "alias_arg", "src": 2}
                if m in ("slt", "sltu", "slti", "sltiu", "andi", "ori", "and", "or", "addiu", "addu", "daddu",
                         "sll", "srl", "sra", "subu", "nor", "xor"):
                    return {"use": "arith"}
                return {"use": "other"}
            if _is_barrier(it):
                return {"use": "barrier"}
        i += 1
        seen += 1
    return {"use": "unused"}


def _type_of_prov(prov: dict, memo: dict, depth: int) -> tuple[str, float]:
    """把调用点证据投影成一个类型 + 置信度。"""
    k = prov.get("kind")
    if k == "int":
        return ("s32", 0.8)
    if k == "addr":
        return ("void *", 0.7)
    if k == "ldst":
        w = prov.get("width", 32)
        if prov.get("unsigned"):
            return ({8: "u8", 16: "u16", 32: "u32"}.get(w, "u32"), 0.5)
        return ({8: "s8", 16: "s16", 32: "s32", 64: "s64"}.get(w, "s32"), 0.5)
    if k == "shift":
        return ("u32" if prov.get("unsigned") else "s32", 0.4)
    if k == "cmp":
        return ("s32", 0.4)
    if k == "hiloint":
        return ("s32", 0.3)
    if k == "floatbits":
        return ("f32", 0.4)
    if k == "arith":
        return ("s32", 0.5)
    if k == "ret":
        callee = prov.get("callee")
        if callee and depth < 3 and callee not in memo:
            r = infer(callee, memo=memo, depth=depth + 1)
            if r:
                memo[callee] = r
                return (r["ret"], 0.6)
        return ("s32", 0.4)
    if k == "local":
        return ("s32", 0.5)
    if k == "other":
        return ("s32", 0.3)
    return ("unk", 0.0)


def _ret_type_from_use(use: dict) -> tuple[str, float]:
    u = use.get("use")
    if u == "test":
        return ("s32", 0.7)
    if u == "deref":
        return ("void *", 0.7)
    if u == "store":
        return ("s32", 0.5)
    if u == "arith":
        return ("s32", 0.5)
    if u == "alias_arg":
        return ("s32", 0.4)
    if u == "unused":
        return ("s32", 0.1)
    return ("unk", 0.0)


def _merge(types: list[tuple[str, float]]) -> tuple[str, float, bool]:
    """按置信度加权合并；返回 (type, confidence, conflicting)。"""
    types = [(t, c) for t, c in types if c > 0 and t != "unk"]
    if not types:
        return ("unk", 0.0, False)
    score: dict[str, float] = {}
    for t, c in types:
        score[t] = score.get(t, 0.0) + c
    # 指针 vs 整数 冲突标记
    ptr = sum(v for k, v in score.items() if "ptr" in k or k.endswith("*"))
    ints = sum(v for k, v in score.items() if k in _TY_INT or k in ("f32", "f64"))
    best = max(score, key=lambda k: score[k])
    total = sum(score.values())
    conflict = ptr > 0 and ints > 0
    return (best, min(1.0, score[best] / max(1e-9, len(types))), conflict)


def infer(sym: str, memo: dict | None = None, depth: int = 0) -> dict | None:
    """推断 sym 的签名。返回 {ret, params:[{i,type,conf,evidence}], arity, hints, callsites}。"""
    if memo is None:
        memo = {}
    if sym in memo:
        return memo[sym]
    idx = build_index()
    sites = idx.get(sym, [])
    arity, hints = arity_and_hints(sym)
    if not sites:
        r = {"sym": sym, "ret": "s32", "params": [{"i": i, "type": "unk", "conf": 0.0, "evidence": []}
                                                  for i in range(arity)],
             "arity": arity, "hints": hints, "callsites": 0, "ret_evidence": []}
        memo[sym] = r
        return r
    # 限制分析调用点数量，避免极热门函数开销过大
    sites = sites[:24]
    votes: dict[int, list] = {i: [] for i in range(max(arity, 1))}
    ret_votes: list = []
    for fname, lineno in sites:
        p = parse_file(ASM / fname)
        items = p.items
        j = next((k for k, it in enumerate(items)
                  if it["kind"] == "ins" and it["lineno"] == lineno), None)
        if j is None:
            continue
        for i in range(max(arity, 1)):
            reg = 4 + i
            prov = _prov_backward(items, j, reg, depth=depth, memo=memo)
            t, c = _type_of_prov(prov, memo, depth)
            votes[i].append((t, c, {"file": fname, "line": lineno, "prov": prov,
                                    "type": t, "conf": round(c, 3)}))
        use = _prov_forward_v0(items, j)
        t, c = _ret_type_from_use(use)
        ret_votes.append((t, c, {"file": fname, "line": lineno, "use": use,
                                 "type": t, "conf": round(c, 3)}))
    params = []
    for i in range(max(arity, 1)):
        v = votes[i]
        t, c, conflict = _merge([(a, b) for a, b, _ in v])
        params.append({"i": i, "type": t, "conf": round(c, 3), "conflict": conflict,
                       "evidence": [x[2] for x in v[:6]], "n_votes": len(v)})
    rt, rc, _ = _merge([(a, b) for a, b, _ in ret_votes])
    r = {"sym": sym, "ret": rt, "ret_conf": round(rc, 3), "params": params, "arity": arity,
         "hints": hints, "callsites": len(sites), "ret_evidence": [x[2] for x in ret_votes[:6]]}
    memo[sym] = r
    return r


# --- 草稿签名的读取与替换 ---------------------------------------------------
DEF_RE_TMPL = r"(?m)^([ \t]*)([A-Za-z_][\w \t\*]*?)\b{sym}\s*\(([^()]*)\)\s*\{{"


def current_signature(src: str, sym: str) -> dict | None:
    m = re.search(DEF_RE_TMPL.format(sym=re.escape(sym)), src)
    if not m:
        return None
    ret = m.group(2).strip()
    raw_args = m.group(3).strip()
    # `f(void)` 是零参数；不要把它当成一个名叫 void 的参数（否则替换后变 `f(s32 void)`）
    args = [] if raw_args in ("", "void") else [a.strip() for a in raw_args.split(",") if a.strip()]
    parsed = []
    for a in args:
        mm = re.match(r"^(.*?)\b(\w+)\s*(\[\s*\])?$", a)
        if mm:
            parsed.append({"raw": a, "type": mm.group(1).strip(), "name": mm.group(2)})
        else:
            parsed.append({"raw": a, "type": a, "name": f"arg{len(parsed)}"})
    return {"ret": ret, "args": parsed, "span": m.span(), "head": m.group(0)}


def replace_signature(src: str, sym: str, ret: str | None, arg_types: list[str] | None) -> tuple[str, list]:
    """只改类型（保留参数名与个数），返回 (新源码, 变更列表)。"""
    cur = current_signature(src, sym)
    if cur is None:
        raise ValueError(f"草稿里找不到 {sym} 的定义")
    changes = []
    new_ret = ret or cur["ret"]
    if new_ret != cur["ret"]:
        changes.append(("ret", cur["ret"], new_ret))
    new_args = []
    for i, a in enumerate(cur["args"]):
        t = a["type"]
        if arg_types and i < len(arg_types) and arg_types[i] and arg_types[i] != "unk":
            t = arg_types[i]
        if t != a["type"]:
            changes.append((f"arg{i}", a["type"], t))
        new_args.append(f"{t} {a['name']}")
    head = f"{new_ret} {sym}({', '.join(new_args)}) {{"
    src2 = src[:cur["span"][0]] + head + src[cur["span"][1]:]
    return src2, changes


def context_source(sym: str, src: str, memo: dict | None = None) -> tuple[str, dict]:
    """生成 m2c `--context` 用的函数声明（推断结果写进声明，m2c 会据此**重生成函数体**）。

    这是比 `suggest_and_replace()` 更「正确」的用法：只改定义行的类型不会重推函数体，
    而 `--context` 会让 m2c 按给定签名重新推断内部表达式/指令选择。
    """
    r = infer(sym, memo=memo) or {}
    cur = current_signature(src, sym)
    if cur is None:
        return "", r
    ret = r.get("ret") if r.get("ret") not in (None, "unk") else cur["ret"]
    args = []
    for i, a in enumerate(cur["args"]):
        p = next((x for x in r.get("params", []) if x["i"] == i), None)
        t = p["type"] if p and p["type"] != "unk" and p["conf"] >= 0.4 else a["type"]
        args.append(f"{t} {a['name']}")
    body = ", ".join(args) if args else "void"
    return f"{ret} {sym}({body});", r


def suggest_and_replace(sym: str, src: str, memo: dict | None = None) -> tuple[str, list, dict]:
    """推断 → 替换草稿签名。返回 (新源码, 变更列表, 推断结果)。"""
    r = infer(sym, memo=memo) or {}
    cur = current_signature(src, sym)
    if cur is None:
        return src, [], r
    ret = r.get("ret") if r.get("ret") not in (None, "unk") else None
    types = []
    for i, a in enumerate(cur["args"]):
        p = next((x for x in r.get("params", []) if x["i"] == i), None)
        t = p["type"] if p and p["type"] != "unk" and p["conf"] >= 0.4 else None
        types.append(t)
    src2, ch = replace_signature(src, sym, ret, types)
    return src2, ch, r


def type_class(t: str) -> tuple:
    """把一个类型归一成「对 codegen 有意义的等价类」。"""
    if not t:
        return ("unk",)
    s = t.replace("*", " *").replace("  ", " ").strip().lower()
    if "*" in s:
        base = s.replace("*", "").strip()
        size = 1 if base in ("void", "u8", "s8", "char", "undefined1", "byte", "code", "undefined") else \
               2 if base in ("s16", "u16", "undefined2") else \
               4 if base in ("s32", "u32", "int", "uint", "undefined4", "m2c_unk", "m2c_unk32") else \
               8 if base in ("s64", "u64", "undefined8", "m2c_unk64") else 4
        return ("ptr", size)
    if s in ("void",):
        return ("void",)
    if s in ("f32", "float"):
        return ("f", 32)
    if s in ("f64", "double"):
        return ("f", 64)
    if s in ("s128", "u128"):
        return ("i", 128, "u")
    uns = s in ("u8", "u16", "u32", "u64", "uint", "unsigned", "undefined1", "undefined2",
                "undefined4", "undefined8", "byte", "code")
    base = s.rstrip("0123456789")
    bits = 32
    for n in (8, 16, 32, 64):
        if s.endswith(str(n)):
            bits = n
            break
    if s.startswith("m2c_unk"):
        bits = 32
    if s in ("int", "short", "long"):
        bits = {"int": 32, "short": 16, "long": 32}[s]
    return ("i", bits, "u" if uns else "s")


def is_effective(changes: list) -> tuple[bool, bool]:
    """返回 (有参数级有效变更, 有返回级有效变更)。"""
    ea = er = False
    for k, o, n in changes:
        if type_class(o) == type_class(n):
            continue
        if k == "ret":
            # void <-> 32 位 int 在 ee-gcc 下一般不改代码生成，单列不计有效
            if {type_class(o), type_class(n)} == {("void",), ("i", 32, "s")}:
                continue
            if {type_class(o), type_class(n)} == {("void",), ("i", 32, "u")}:
                continue
            er = True
        else:
            ea = True
    return ea, er


# --- CLI --------------------------------------------------------------------
def _fmt_sig(r: dict, cur: dict | None = None) -> str:
    args = ", ".join(f"{p['type']} arg{p['i']}" for p in r.get("params", [])) or "void"
    return f"{r.get('ret', 's32')} {r['sym']}({args})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["scan", "scan-file", "apply", "ctx", "batch"])
    ap.add_argument("sym", nargs="?")
    ap.add_argument("infile", nargs="?")
    ap.add_argument("outfile", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--classes", default="F_branch_call,D2_multi_call")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    if a.cmd == "scan":
        r = infer(a.sym)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            print(f"建议签名: {_fmt_sig(r)}   （调用点 {r['callsites']} 个，arity={r['arity']}，体线索={r['hints']}）")
            for p in r["params"]:
                print(f"  $a{p['i']}: {p['type']:6s} conf={p['conf']:.2f}"
                      f"{' ***冲突***' if p.get('conflict') else ''}")
                for e in p["evidence"]:
                    print(f"      {e['file']}:{e['line']}  {e['prov']}")
            print(f"  $v0 -> {r['ret']} (conf={r.get('ret_conf')})")
            for e in r["ret_evidence"]:
                print(f"      {e['file']}:{e['line']}  {e['use']}")
        return 0

    if a.cmd == "scan-file":
        src = Path(a.infile).read_text(encoding="utf-8")
        src2, ch, r = suggest_and_replace(a.sym, src)
        cur = current_signature(src, a.sym)
        print(f"现状: {cur['ret']} {a.sym}({', '.join(x['raw'] for x in cur['args'])})")
        print(f"建议: {_fmt_sig(r)}")
        print("变更: " + (", ".join(f"{k}: {o} -> {n}" for k, o, n in ch) if ch else "(无)"))
        return 0

    if a.cmd == "apply":
        src = Path(a.infile).read_text(encoding="utf-8")
        src2, ch, _ = suggest_and_replace(a.sym, src)
        Path(a.outfile).write_text(src2, encoding="utf-8")
        print(f"{a.sym}: {len(ch)} 处类型变更 -> {a.outfile}")
        for k, o, n in ch:
            print(f"  {k}: {o} -> {n}")
        return 0

    if a.cmd == "ctx":
        src = Path(a.infile).read_text(encoding="utf-8")
        decl, r = context_source(a.sym, src)
        print(decl)
        return 0

    # batch：对池做一次离线普查
    res_path = REPO / "routebjp" / "build" / "m2c" / "batch" / "result.json"
    wq = {}
    for line in (REPO / "out" / "evidence" / "jp_m3_workqueue.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        p = line.split("\t")
        if len(p) > 12:
            wq[p[0]] = {"size": int(p[2]), "class": p[12]}
    want = set(a.classes.split(","))
    rows = []
    for r in json.loads(res_path.read_text(encoding="utf-8")):
        w = wq.get(r["sym"])
        if not w or w["class"] not in want:
            continue
        if r.get("match") is None or r["match"] >= 80:
            continue
        rows.append(r)
    rows.sort(key=lambda r: r["sym"])
    if a.limit:
        rows = rows[:a.limit]
    memo: dict = {}
    out = []
    for r in rows:
        sym = r["sym"]
        p = ROOT / "build" / "m2c" / "batch" / sym / f"{sym}.m2c.c"
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        try:
            _, ch, inf = suggest_and_replace(sym, src, memo=memo)
        except Exception as e:  # noqa: BLE001
            out.append({"sym": sym, "match": r["match"], "err": str(e)})
            continue
        out.append({"sym": sym, "class": wq[sym]["class"], "size": wq[sym]["size"], "match": r["match"],
                    "flags": r.get("flags"), "changes": [[k, o, n] for k, o, n in ch],
                    "n_changes": len(ch), "eff_arg": is_effective(ch)[0], "eff_ret": is_effective(ch)[1],
                    "suggest": _fmt_sig(inf), "callsites": inf.get("callsites"),
                    "cur": (lambda c: f"{c['ret']} ({', '.join(a['raw'] for a in c['args'])})"
                            if c else None)(current_signature(src, sym))})
    dst = CACHE.parent / "batch_scan.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n_ch = sum(1 for x in out if x.get("n_changes"))
    n_ea = sum(1 for x in out if x.get("eff_arg"))
    n_er = sum(1 for x in out if x.get("eff_ret"))
    n_any = sum(1 for x in out if x.get("eff_arg") or x.get("eff_ret"))
    print(f"扫描 {len(out)} 个符号：名义变更 {n_ch}（{100.0*n_ch/max(1,len(out)):.1f}%），"
          f"有效参数变更 {n_ea}，有效返回变更 {n_er}，任一有效 {n_any}"
          f"（{100.0*n_any/max(1,len(out)):.1f}%）-> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
