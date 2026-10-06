#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 桩类自动生成器：syscall / break / 手写指令（日版主目标 SLPS_258.19）。

定位（与 auto_match_trivial.py 的区别）：
  * auto_match_trivial.py 是「从指令**反推** C」——形状识别 + 变体 + objdiff 裁决；
  * 本工具是「**逐条照抄**」——这些函数的语义由指令唯一确定（例如 `addiu $3,$0,N; syscall 0`
    里的 N 就是系统调用号），用 C 写不出 `syscall`/`break`/`mfc0` 这类指令，
    因此生成**手写汇编源** `src/matched/<sym>.s`，由 build_hybrid.sh 用 decompals-as 汇编
    （仍走同一套 hybrid 原位替换机制）。
  * 为什么不用「文件级 `__asm__` 的 .c」：实测 ee-gcc 3.2 对纯 asm TU 会在 `.text` 头部垫
    20 字节零字节（符号落在 0x14），这些字节会被一起放进镜像 → `.cod` 越界覆盖 `.dat`。
    改用 .s 后符号在偏移 0，`.text` 大小 = 指令字节数，逐字节可原位替换。
  证据口径单列：字节一致是 `[实测]`（objdiff 100% + 棘轮），语义是 `[已核实]`（指令唯一确定），
  **不得**把这一类算作「反推 C」——进度报告按 shape 分类分别计数。

判定与闸门：
  * 候选 = workqueue 里 `hybrid_ok=1`、未被 matched_symbols.txt 收录、且 split 模式可安全摘出的符号；
  * 桩形态 = 目标块含 syscall / break / 手写指令（mfc0/mtc0/ctc2/cfc2/vcallmsr/lq/sq/.word）；
  * 只有 objdiff == 100.0 才落地。

用法：
  python3 routebjp/tools/auto_match_stub.py scan [--tier trivial]
  python3 routebjp/tools/auto_match_stub.py run [--tier trivial] [--apply]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auto_match_trivial import (  # noqa: E402  复用同一批路径/工具链常量，避免口径漂移
    ROOT, REPO, WORK_ROOT, WORKQUEUE, ASMDIR, MATCHED_LIST, SRCDIR,
    GCC, AS, OBJDIFF, CFLAGS, split_mode, matched_in_list,
)

STUB_BEGIN = "# ---- M3 桩（syscall/break/手写指令；auto_match_stub.py 生成，勿手改本段）----"
STUB_END = "# ---- M3 桩段结束 ----"
BUILDDIR = WORK_ROOT / "m2" / "m3stub"
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
INS_RE = re.compile(r"/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
# 「无 C 等价」的手写指令（语义由指令唯一确定）
HAND_OPS = {"syscall", "break", "mfc0", "mtc0", "ctc2", "cfc2",
            "vcallms", "vcallmsr", "qmfc2", "qmtc2", "lq", "sq"}
# 允许出现在桩里的配平指令（返回/寄存器准备），不得含任何真实业务逻辑
PLUMB_OPS = {"nop", "jr", "addiu", "ori", "andi", "xori", "lui", "daddu", "move",
             "dsll32", "dsra32", "sll", "sra", "sltu", "sltiu"}
STUB_MAX_BYTES = 32   # 超过这个尺寸几乎必然是含 assert 的真实函数，不属于桩

TIERS = ("trivial", "small", "medium", "large", "huge")


def workqueue_rows(tier: str):
    """返回 [(sym, addr, size, data_ref, jtbl, mmi, hybrid_ok)]，按表头取列。"""
    lines = WORKQUEUE.read_text(encoding="utf-8").splitlines()
    idx = {k: i for i, k in enumerate(lines[0].split("\t"))}
    out = []
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) < len(idx) or p[idx["tier"]] != tier:
            continue
        out.append((p[idx["name"]], int(p[idx["addr"]], 16), int(p[idx["size"]]),
                    p[idx["data_ref"]] == "1", p[idx["jtbl"]] == "1",
                    p[idx["mmi"]] == "1", p[idx["hybrid_ok"]] == "1"))
    return out


def target_block(sym: str) -> list[str] | None:
    """目标块（glabel..endlabel）的**全部行**原文（含 glabel/endlabel，用于 objdiff 的 target）。"""
    p = ASMDIR / f"{sym}.s"
    if not p.is_file():
        return None
    lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = None
    for i, l in enumerate(lines):
        if re.match(r"\s*glabel\s+", l):
            gi = i
            break
    if gi is None:
        return None
    en = None
    for i in range(gi, len(lines)):
        if re.match(r"\s*endlabel\s+", lines[i]):
            en = i
            break
    if en is None:
        return None
    return lines[gi:en + 1]


def body_ins(sym: str) -> list[str] | None:
    """目标块里的指令行原文（含缩进与行尾注释），用于照抄进 __asm__。"""
    block = target_block(sym)
    if block is None:
        return None
    return [l for l in block if INS_RE.search(l)]



def classify(sym: str) -> str | None:
    """判定为桩的条件（**从严**，避免把含 assert 的真实函数当成桩批量转写）：

      1. 尺寸 ≤ STUB_MAX_BYTES；
      2. 至少含一条「无 C 等价」的手写指令（syscall/break/mfc0/...）；
      3. 块内**每条**指令都属于 手写指令 ∪ 配平指令（不含任何真实业务逻辑）。
    """
    body = body_ins(sym)
    if not body:
        return None
    ops = []
    for l in body:
        txt = l.split("*/", 1)[-1].strip()
        if not txt:
            continue
        # 去掉 .ni/.i 之类协处理器后缀（ctc2.ni / cfc2.ni 仍是手写 VU 指令）
        ops.append(re.sub(r"\s+", " ", txt).split(" ")[0].split(".", 1)[0])
    if not ops or len(ops) * 4 > STUB_MAX_BYTES:
        return None
    if not any(o in HAND_OPS for o in ops):
        return None
    if not all(o in HAND_OPS or o in PLUMB_OPS for o in ops):
        return None
    text = "\n".join(body)
    if re.search(r"\bsyscall\b", text):
        return "stub_syscall"
    if re.search(r"\bbreak\b", text):
        return "stub_break"
    return "stub_hand"


def s_source(sym: str, addr: int, size: int, shape: str, body: list[str]) -> str:
    """手写汇编源（逐条照抄，注释保留原文）。"""
    hdr = (f"/* {sym} @ 0x{addr:08x} ({size} B) : shape={shape}\n"
           f" * 由 routebjp/tools/auto_match_stub.py **逐条照抄**原反汇编生成（非反推 C）。\n"
           f" * 语义：syscall/break 的立即数在指令里唯一确定；objdiff 100% 后再纳入 hybrid。\n"
           f" * 证据口径：字节一致 [实测]；语义 [已核实]。 */\n")
    out = ['.set noat', '.set noreorder', '', '.section .text, "ax"', '', '.align 2',
           f'.globl {sym}', f'.type {sym}, @function', '', f'{sym}:']
    for l in body:
        out.append("    " + l.strip())
    out.append('')
    out.append(f'.size {sym}, .-{sym}')
    return hdr + "\n".join(out) + "\n"


def run_objdiff(sym: str, work: Path) -> float | None:
    block = target_block(sym)
    if not block:
        return None
    d = work / sym
    d.mkdir(parents=True, exist_ok=True)
    (d / "target.s").write_text(PREAMBLE + "\n".join(block) + "\n", encoding="utf-8")
    t_o, c_o, dj = d / "t.o", d / "c.o", d / "diff.json"
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(t_o), str(d / "target.s")],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(c_o), str(d / "probe.s")],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    r = subprocess.run([OBJDIFF, "diff", "-1", str(t_o), "-2", str(c_o), "-o", str(dj), "--format", "json"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    data = json.loads(dj.read_text(encoding="utf-8"))
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    return per.get(sym)


def stub_section_syms() -> set:
    """本工具自己写进清单的桩段符号（重跑时要重新验证，不能当成「已匹配」跳过）。"""
    if not MATCHED_LIST.is_file():
        return set()
    text = MATCHED_LIST.read_text(encoding="utf-8")
    if STUB_BEGIN not in text:
        return set()
    seg = text.split(STUB_BEGIN, 1)[1]
    seg = seg.split(STUB_END, 1)[0] if STUB_END in seg else seg
    return {l.split("#", 1)[0].strip() for l in seg.split("\n") if l.split("#", 1)[0].strip()}


def candidates(tier: str):
    already = matched_in_list() - stub_section_syms()
    out = []
    for sym, addr, size, data_ref, jtbl, mmi, ok in workqueue_rows(tier):
        if sym in already or not ok:
            continue
        shape = classify(sym)
        if not shape:
            continue
        mode = split_mode(sym)
        if mode.startswith("blocked"):
            continue
        out.append({"sym": sym, "addr": addr, "size": size, "shape": shape, "split": mode})
    return out


def do_apply(winners: dict):
    SRCDIR.mkdir(parents=True, exist_ok=True)
    for sym, info in winners.items():
        (SRCDIR / f"{sym}.s").write_text(
            s_source(sym, info["addr"], info["size"], info["shape"], info["body"]), encoding="utf-8")
    text = MATCHED_LIST.read_text(encoding="utf-8")
    base = text.split(STUB_BEGIN)[0].rstrip("\n") if STUB_BEGIN in text else text.rstrip("\n")
    existing: "OrderedDict[str, str]" = OrderedDict()
    if STUB_BEGIN in text:
        seg = text.split(STUB_BEGIN, 1)[1]
        seg = seg.split(STUB_END, 1)[0] if STUB_END in seg else seg
        for line in seg.split("\n"):
            a = line.split("#", 1)
            s = a[0].strip()
            if s:
                existing[s] = a[1].strip() if len(a) > 1 else ""
    n0 = len(existing)
    for sym, info in winners.items():
        existing[sym] = info["shape"]
    out = [base, "", STUB_BEGIN]
    for sym in sorted(existing):
        out.append(f"{sym}    # {existing[sym]}" if existing[sym] else sym)
    out.append(STUB_END)
    MATCHED_LIST.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"apply: 写入 {len(winners)} 个桩 .s 源；清单桩段 {n0} -> {len(existing)} 条")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["scan", "run"])
    ap.add_argument("--tier", default="trivial", choices=TIERS)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cands = candidates(args.tier)
    if args.mode == "scan":
        from collections import Counter
        c = Counter(i["shape"] for i in cands)
        print(f"== {args.tier} 桩候选：{len(cands)} 个 ==")
        for k, v in c.most_common():
            print(f"   {k:16s} {v}")
        return 0

    BUILDDIR.mkdir(parents=True, exist_ok=True)
    winners, fails = OrderedDict(), OrderedDict()
    for info in cands:
        sym = info["sym"]
        body = body_ins(sym)
        if not body:
            fails[sym] = info
            continue
        src = s_source(sym, info["addr"], info["size"], info["shape"], body)
        d = BUILDDIR / sym
        d.mkdir(parents=True, exist_ok=True)
        (d / "probe.s").write_text(src, encoding="utf-8")
        mp = run_objdiff(sym, BUILDDIR)
        if mp == 100.0:
            info["body"] = body
            info["match"] = mp
            winners[sym] = info
        else:
            info["match"] = mp
            fails[sym] = info

    print(f"== {args.tier} 桩：尝试 {len(cands)}，objdiff 100% = {len(winners)} ==")
    by_shape: dict[str, list[int]] = {}
    for i in winners.values():
        by_shape.setdefault(i["shape"], [0, 0])[0] += 1
    for i in fails.values():
        by_shape.setdefault(i["shape"], [0, 0])[1] += 1
    for k in sorted(by_shape):
        print(f"   {k:16s} 成功 {by_shape[k][0]:4d} / 失败 {by_shape[k][1]:4d}")

    out_json = BUILDDIR / ("result.json" if args.tier == "trivial" else f"result_{args.tier}.json")
    out_json.write_text(json.dumps({
        "tier": args.tier,
        "n_candidates": len(cands),
        "n_matched": len(winners),
        "matched": {s: {k: i[k] for k in ("addr", "size", "shape", "split", "match")}
                    for s, i in winners.items()},
        "failed": {s: {k: i[k] for k in ("addr", "size", "shape", "split", "match")}
                   for s, i in fails.items()},
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"结果 JSON -> {out_json}")
    if args.apply:
        do_apply(winners)
    return 0


if __name__ == "__main__":
    sys.exit(main())
