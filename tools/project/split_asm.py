#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 hybrid 残差拆分工具：让「一个 asm .o 里的**某个**符号」可以被 C 单独替换。

背景（见 docs/R9 与 P-15/P-16）：
  * splat 产出的 asm/cod/<sym>.s 里可能含**多个** glabel/alabel（兄弟函数入口）；
  * endlabel 之后可能有填充指令（几乎都是 nop）。
  现有 build_hybrid.sh 按「一符号 = 一个 asm .o」整份摘除，会连带丢掉兄弟定义或尾部字节。
  本工具在**不改 build.sh、不改 .s 内容语义**的前提下，把目标符号的代码块从原文件里摘出来，
  其余内容（前导 + 兄弟块 + 尾部填充 + 其它指令行）逐行原样保留为「残差 .s」，
  由 build_hybrid.sh 汇编成 residual 对象放在 C 对象之后，从而保持链接顺序与全部字节。

模式判定（目标符号必须是文件里**第一个** glabel，实测 10,923 个符号 0 例外）：
  direct           文件只有该符号、endlabel 后没有指令        -> 不产残差，走现有路径
  residual         有兄弟符号，或有尾部填充                  -> 产 <sym>.residual.s（+ <sym>.target.s）
  blocked_*        无 glabel / 非首 glabel / 块内有兄弟标签 /
                   残差汇编报错（跨块 .L 引用等）            -> 排除该符号，如实报告

用法：
  python3 routebjp/tools/split_asm.py split <symbol> <outdir>   # 写 target/residual.s，打印模式
  python3 routebjp/tools/split_asm.py verify --all [--jobs 4]   # 穷举：target+residual 必须还原原 .o 的 .text
  python3 routebjp/tools/split_asm.py stats [--jobs 4]          # 只统计各模式数量
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # routebjp/
REPO = ROOT.parent
ASMDIR = ROOT / "asm" / "cod"
BUILD_ASM = ROOT / "build" / "asm" / "cod"
CHECK_DIR = ROOT / "build" / "hybrid" / "splitcheck"   # 派生数据，不入库

BINUTILS = Path(os.environ.get("BINUTILS", str(Path.home() / "eecc" / "ps2binutils")))
AS = BINUTILS / "mips-ps2-decompals-as"
OBJCOPY = BINUTILS / "mips-ps2-decompals-objcopy"

GLABEL = re.compile(r"^\s*glabel\s+(\S+)")
ALABEL = re.compile(r"^\s*alabel\s+(\S+)")
JLABEL = re.compile(r"^\s*jlabel\s+(\S+)")
NONMATCH = re.compile(r"^\s*nonmatching\s+(\S+?)\s*,")
ENDLABEL = re.compile(r"^\s*endlabel\s+(\S+)")
LABEL_DEF = re.compile(r"^\s*([.\w]+):\s*$")
INS = re.compile(r"/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
TOKEN = re.compile(r"[.\w]+")


def _defs_and_refs(lines: list[str]) -> tuple[set[str], set[str]]:
    """返回（本文件里定义的标签名集合, 被指令引用的标识符集合）。"""
    defs: set[str] = set()
    refs: set[str] = set()
    for l in lines:
        m = LABEL_DEF.match(l)
        if m:
            defs.add(m.group(1))
            continue
        m = GLABEL.match(l) or ALABEL.match(l) or JLABEL.match(l)
        if m:
            defs.add(m.group(1))
            continue
        m = NONMATCH.match(l)
        if m:
            defs.add(m.group(1))
            continue
        if INS.search(l):
            body = l.split("*/", 1)[-1]
            refs |= set(TOKEN.findall(body))
    return defs, refs

PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").split("\n")


def analyze(sym: str, asm_dir: Path = ASMDIR) -> dict:
    """判定单个符号的拆分模式；不写盘、不汇编（汇编错误由 verify/assemble 阶段发现）。"""
    p = asm_dir / f"{sym}.s"
    if not p.is_file():
        return {"mode": "blocked_no_asm", "reason": f"缺少 {p}"}
    lines = read_lines(p)

    gl = [(i, GLABEL.match(l).group(1)) for i, l in enumerate(lines) if GLABEL.match(l)]
    al = [(i, ALABEL.match(l).group(1)) for i, l in enumerate(lines) if ALABEL.match(l)]
    if not gl:
        return {"mode": "blocked_no_glabel", "reason": "文件里没有 glabel"}
    if gl[0][1] != sym:
        return {"mode": "blocked_not_first", "reason": f"首 glabel 是 {gl[0][1]}，不是 {sym}"}

    gi = gl[0][0]
    start = gi
    j = gi - 1
    while j >= 0 and lines[j].strip() == "":
        j -= 1
    if j >= 0:
        m = NONMATCH.match(lines[j])
        if m and m.group(1) == sym:
            start = j

    end = None
    for k in range(gi, len(lines)):
        if ENDLABEL.match(lines[k]):
            end = k
            break
    if end is None:
        return {"mode": "blocked_no_endlabel", "reason": "块内没有 endlabel"}

    # 块内不得定义别的全局函数符号（alabel/嵌套 glabel）——摘除会丢掉它们的定义
    inner = [n for i, n in gl + al if start <= i <= end and n != sym]
    if inner:
        return {"mode": "blocked_inner_label", "reason": "块内有兄弟标签: " + ", ".join(inner)}

    outer = [n for i, n in gl + al if not (start <= i <= end)]

    after = lines[end + 1:]
    has_rest = any(INS.search(l) or GLABEL.match(l) or ALABEL.match(l) for l in after)
    mode = "residual" if has_rest else "direct"

    info = {
        "mode": mode,
        "start": start,
        "end": end,
        "lines": lines,
        "path": p,
        "siblings": [n for i, n in gl + al if i > end],
        "outer_labels": outer,
        "tail_ins": sum(1 for l in after if INS.search(l)),
    }

    if mode == "residual":
        # 跨块引用：目标块引用残差里的标签，或残差引用目标块里的标签。
        # 两种情况在「C 替换 + 残差对象」的真实链接里都无法表达（C 写不出跨对象 .L 分支），
        # 必须排除；否则 objcopy 逐字节比对也只会看到未解析的重定位。
        b_defs, b_refs = _defs_and_refs(lines[start:end + 1])
        o_defs, o_refs = _defs_and_refs(lines[:start] + lines[end + 1:])
        cross_out = sorted((b_refs & o_defs) - b_defs)
        cross_in = sorted((o_refs & b_defs) - o_defs)
        if cross_out or cross_in:
            info["mode"] = "blocked_cross_ref"
            info["reason"] = ("跨块引用: "
                              + ("目标块->残差 " + ",".join(cross_out) if cross_out else "")
                              + ("; " if cross_out and cross_in else "")
                              + ("残差->目标块 " + ",".join(cross_in) if cross_in else ""))
    return info


def emit(sym: str, outdir: Path, info: dict | None = None) -> dict:
    """写 <sym>.target.s / <sym>.residual.s；返回 analyze 结果（含写入路径）。"""
    info = info or analyze(sym)
    if info["mode"] not in ("direct", "residual"):
        return info
    if info["mode"] == "direct":
        return info
    lines, start, end = info["lines"], info["start"], info["end"]
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / f"{sym}.target.s"
    residual = outdir / f"{sym}.residual.s"
    target.write_text(PREAMBLE + "\n".join(lines[start:end + 1]) + "\n", encoding="utf-8")
    residual.write_text("\n".join(lines[:start] + lines[end + 1:]), encoding="utf-8")
    info["target_s"] = target
    info["residual_s"] = residual
    return info


def assemble(src: Path, obj: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(AS), "-EL", "-march=r5900", "-I", "include", "-o", str(obj), str(src)],
        cwd=str(ROOT), capture_output=True, text=True,
    )


def text_bytes(obj: Path, out: Path) -> bytes | None:
    r = subprocess.run([str(OBJCOPY), "-O", "binary", "--only-section=.text",
                        str(obj), str(out)], capture_output=True, text=True)
    if r.returncode != 0 or not out.is_file():
        return None
    return out.read_bytes()


def verify_one(sym: str, work: Path) -> tuple[str, str]:
    """返回 (status, detail)；status ∈ ok / direct / blocked / FAIL。"""
    info = analyze(sym)
    if info["mode"] == "direct":
        return "direct", ""
    if info["mode"].startswith("blocked"):
        return "blocked", info["mode"] + ": " + info.get("reason", "")
    info = emit(sym, work, info)
    t_s, r_s = info["target_s"], info["residual_s"]
    d = work / sym
    d.mkdir(parents=True, exist_ok=True)
    t_o, r_o = d / "t.o", d / "r.o"
    rt = assemble(t_s, t_o)
    if rt.returncode != 0:
        return "blocked", "target 汇编失败: " + rt.stderr.strip().splitlines()[-1][:160]
    rr = assemble(r_s, r_o)
    if rr.returncode != 0:
        return "blocked", "residual 汇编失败: " + rr.stderr.strip().splitlines()[-1][:160]
    orig_o = BUILD_ASM / f"{sym}.o"
    if not orig_o.is_file():
        return "blocked", f"缺少原对象 {orig_o}"
    tb = text_bytes(t_o, d / "t.bin")
    rb = text_bytes(r_o, d / "r.bin")
    ob = text_bytes(orig_o, d / "o.bin")
    if tb is None or rb is None or ob is None:
        return "blocked", "objcopy 取 .text 失败"
    if tb + rb != ob:
        return "FAIL", (f"字节不符: target {len(tb)} + residual {len(rb)} = {len(tb) + len(rb)} "
                        f"!= 原 {len(ob)}")
    return "ok", f"{len(tb)}+{len(rb)}={len(ob)}"


def all_symbols() -> list[str]:
    return sorted(p.name[:-2] for p in ASMDIR.glob("*.s"))


def cmd_split(args) -> int:
    info = emit(args.symbol, Path(args.outdir))
    if info["mode"] in ("direct", "residual"):
        print(f"{args.symbol}\t{info['mode']}\tsiblings={len(info.get('siblings', []))}"
              f"\ttail_ins={info.get('tail_ins', 0)}")
        return 0
    print(f"{args.symbol}\t{info['mode']}\t{info.get('reason', '')}")
    return 3


def cmd_verify(args) -> int:
    syms = all_symbols() if args.all else [s.strip() for s in args.symbols]
    if args.limit:
        syms = syms[:args.limit]
    CHECK_DIR.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    ok = fail = 0
    reasons: dict[str, int] = {}
    fails: list[str] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for sym, (st, detail) in zip(syms, ex.map(lambda s: verify_one(s, CHECK_DIR), syms)):
            counts[st] = counts.get(st, 0) + 1
            if st == "ok":
                ok += 1
            elif st == "FAIL":
                fail += 1
                fails.append(f"{sym}: {detail}")
            elif st == "blocked":
                key = detail.split(":", 1)[0]
                reasons[key] = reasons.get(key, 0) + 1
    print(f"== split verify：共 {len(syms)} 个符号 ==")
    for k, v in sorted(counts.items()):
        print(f"   {k:10s} {v}")
    if reasons:
        print("   -- blocked 原因 --")
        for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
            print(f"      {k:28s} {v}")
    if fails:
        print("   -- FAIL（前 20 条）--")
        for f in fails[:20]:
            print("      " + f)
    print(f"结论：{'✅ 全部通过' if fail == 0 else f'❌ {fail} 个失败'}")
    return 0 if fail == 0 else 1


def cmd_stats(args) -> int:
    syms = all_symbols()
    counts: dict[str, int] = {}
    reasons: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for st, detail in ex.map(lambda s: (lambda i: (i["mode"], i.get("reason", "")))(analyze(s)), syms):
            counts[st] = counts.get(st, 0) + 1
            if st.startswith("blocked"):
                reasons[detail] = reasons.get(detail, 0) + 1
    print(f"== split 模式统计（{len(syms)} 个符号）==")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"   {k:22s} {v}")
    for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])[:10]:
        print(f"      {k[:70]:70s} {v}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("split"); sp.add_argument("symbol"); sp.add_argument("outdir"); sp.set_defaults(fn=cmd_split)
    vp = sub.add_parser("verify"); vp.add_argument("symbols", nargs="*"); vp.add_argument("--all", action="store_true")
    vp.add_argument("--jobs", type=int, default=4); vp.add_argument("--limit", type=int, default=0)
    vp.set_defaults(fn=cmd_verify)
    tp = sub.add_parser("stats"); tp.add_argument("--jobs", type=int, default=4); tp.set_defaults(fn=cmd_stats)
    args = ap.parse_args()
    if args.cmd == "verify" and not args.all and not args.symbols:
        print("verify 需要 --all 或符号列表", file=sys.stderr)
        return 2
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
