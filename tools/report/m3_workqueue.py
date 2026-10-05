#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 工作量分级队列：把主程序函数按"能不能用现有流水线做"分类，产出可并行的工作队列。

输入（默认日版主目标；--target us 切到美版参照）：
  <proj>/config/symbol_addrs.txt     函数名 + 地址 + 尺寸（Ghidra 边界）
  <proj>/asm/cod/<符号>.s            per-function 反汇编（用来判数据引用/跳转表/MMI）

分类维度：
  tier      尺寸档：trivial(<17B) / small(17–64) / medium(65–256) / large(257–1024) / huge(>1KB)
  data_ref  是否引用 .rodata/.data 里的符号（%hi/%lo 指向 D_*/jtbl_* 等非函数符号）
  jtbl      是否引用跳转表
  mmi       是否含 R5900 扩展指令（MMI / COP2 / LQ-SQ 等）
  hybrid_ok 旧口径：无 data_ref 且无 jtbl（**保守**，见下）
  eligible  新口径（2026-10-03 修正）：**真实机制**能否原位替换 =
            ①该 .s 不定义任何非 .text 段（否则 C/汇编产物放不下这些数据）
            ②无 %gp_rel（需要 -G，当前编译参数不可达）
            ③无跳转表引用（jtbl_*，需要 .rodata 原位放置）
            「引用**外部**数据符号（绝对 %hi/%lo）」不阻塞——C 里写 extern D_x 同样产出
            lui/%lo 绝对寻址（证据：M2 样板 baseelf_19 objdiff 100%，载荷棘轮绿）。
  gate      目标块能否被单独摘出：direct / residual / blocked_*（同 routebjp/tools/split_asm.py）

用法：
  python3 tools/report/m3_workqueue.py                     # 日版（默认），打印摘要
  python3 tools/report/m3_workqueue.py --target us         # 美版参照
  python3 tools/report/m3_workqueue.py --tsv out/evidence/jp_m3_workqueue.tsv
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# ⚠️ 2026-10-04 修正（P-31）：原先把 `mult/multu/div/divu/madd/msub/mfhi/mflo/mthi/mtlo`
#    也当成 MMI —— 但那些是**普通 MIPS I** 指令，游戏代码里到处都是，导致 2,741 个函数被误标成 G_mmi
#    （实测其中 1,865 个根本没有 MMI/COP2/lq/sq）。R5900 真正扩展的是**三操作数**形式
#    `mult $rd,$rs,$rt`（同理 madd/msub/div），所以这里只保留 R5900 扩展与打包/VU/COP2 记号，
#    三操作数形式由 r5900_muldiv() 单独判断。
MMI = re.compile(
    r"\b(lq|sq|pmaddw|pmsubw|pmadduw|pmultw|pmultuw|pdivw|pdivuw|pmfhi|pmflo|"
    r"psllh|psllw|psrlh|psrlw|psrah|psraw|paddh|paddw|psubh|psubw|pcgth|pcgtw|"
    r"pmaxh|pmaxw|pminh|pminw|pextlh|pextlw|pextuh|pextuw|pinth|pintoh|"
    r"pcpyh|pcpyld|pcpyud|pceqb|pceqh|pceqw|pabsh|pabsw|pinteh|pexch|pexcw|"
    r"pexeh|pexew|plzcw|prevh|prot3w|ppacb|ppach|ppacw|pext5|pmulth|pdivbw|"
    r"mfsa|mtsa|mtsab|mtsah|qfsrv|"
    r"mfc2|mtc2|cfc2|ctc2|qmfc2|qmtc2|vadd|vsub|vmul|vcallms|vcallmsr|vitof|vftoi|"
    r"lqc2|sqc2|vabs|vmax|vmin|vopmula|vopmsub|vnop|vrsqrt|vwaitq|vdiv|vsqrt)\b",
    re.I,
)
# R5900 的整数乘除扩展：`mult $rd,$rs,$rt`（三操作数）；两操作数的是普通 MIPS I
R5900_MULDIV = re.compile(r"^\s*(mult|multu|div|divu|madd|maddu|msub|msubu)\s+\$\d+\s*,\s*\$\d+\s*,\s*\$\d+",
                          re.M | re.I)


def r5900_muldiv(text: str) -> bool:
    return bool(R5900_MULDIV.search(text))
DATA_REF = re.compile(r"%hi\((?!func_|entry|baseelf_|LibgccCommon_|LibcStdio_|LibcStdlib_|"
                      r"LibcString_|LibmFloat_|eekernel_|eetlb_|loadcore_|modload_|fileio_|"
                      r"eetimer_|libc_|libm_)([A-Za-z_][A-Za-z0-9_]*)\)")
JAL = re.compile(r"\bjal\b")
JMP = re.compile(r"(?<!ja)\bj\s")
SYM = re.compile(r"^(\S+)\s*=\s*(0x[0-9A-Fa-f]+)\s*;\s*//\s*type:(\w+)\s*size:0x([0-9A-Fa-f]+)")
SECTION = re.compile(r"^\s*\.section\s+(\S+)", re.M)


def real_eligible(text: str, jtbl: bool) -> bool:
    """真实机制判定：无非 .text 段 && 无 %gp_rel && 无跳转表。"""
    secs = {s.strip('"') for s in SECTION.findall(text)}
    if {s for s in secs if not s.startswith(".text")}:
        return False
    if "%gp_rel" in text:
        return False
    return not jtbl


# 难度画像（决定用哪条自动化流水线；见 docs/R11 长期计划 §2.2）
INS_RE = re.compile(r"/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
BRANCH_MN = {"b", "beq", "bne", "beqz", "bnez", "blez", "bgtz", "bltz", "bgez",
             "bgezal", "bltzal", "bgezl", "bgtzl", "blezl", "bltzl", "bc1",
             "beql", "bnel", "jr", "jalr"}


def classify(text: str, size: int, jtbl: bool, mmi: bool) -> str:
    """给未匹配函数一个「该走哪条流水线」的类别标签。"""
    if not text:
        return "no_asm"
    if mmi:
        return "G_mmi"
    if jtbl:
        return "jtbl"
    if "%gp_rel" in text:
        return "gp_rel"
    if size < 17:
        return "A_trivial"
    ops = []
    for line in text.splitlines():
        if INS_RE.search(line):
            body = line.split("*/", 1)[-1].strip()
            if body:
                ops.append(body.split(" ")[0].split(".", 1)[0])
    if not ops:
        return "unknown"
    branches = sum(1 for m in ops if m in BRANCH_MN and m != "jr")
    calls = sum(1 for m in ops if m in ("jal", "jalr"))
    if branches == 0 and calls == 0:
        return "B_straight"
    if branches == 0 and calls == 1:
        return "D_single_call"
    if branches == 0:
        return "D2_multi_call"
    if calls == 0:
        return "E_branch_only"
    return "F_branch_call"


def tier(size: int) -> str:
    if size < 17:
        return "trivial"
    if size <= 64:
        return "small"
    if size <= 256:
        return "medium"
    if size <= 1024:
        return "large"
    return "huge"


def scan_syms(path: Path):
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SYM.match(line)
        if m and m.group(3) == "func":
            out.append((m.group(1), int(m.group(2), 16), int(m.group(4), 16)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="jp", choices=["jp", "us"])
    ap.add_argument("--tsv", default="")
    args = ap.parse_args()

    proj = ROOT / ("routebjp" if args.target == "jp" else "routeb")
    syms = scan_syms(proj / "config" / "symbol_addrs.txt")
    if not syms:
        print(f"SKIP：{proj}/config/symbol_addrs.txt 不存在或为空")
        return 0

    # gate 判据复用 routebjp/tools/split_asm.py（日版才有；美版参照不给 gate）
    split_asm = None
    if args.target == "jp":
        sys.path.insert(0, str(proj / "tools"))
        try:
            import split_asm as _sa
            split_asm = _sa
        except ImportError:
            split_asm = None

    rows = []
    for name, addr, size in syms:
        f = proj / "asm" / "cod" / f"{name}.s"
        text = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""
        data_ref = bool(DATA_REF.search(text))
        jtbl = "jtbl_" in text
        mmi = bool(MMI.search(text)) or r5900_muldiv(text)
        rows.append({
            "name": name, "addr": addr, "size": size, "tier": tier(size),
            "data_ref": int(data_ref), "jtbl": int(jtbl), "mmi": int(mmi),
            "jal": len(JAL.findall(text)), "j": len(JMP.findall(text)),
            "has_asm": int(bool(text)),
            "eligible": int(bool(text) and real_eligible(text, jtbl)),
            "gate": (split_asm.analyze(name)["mode"] if split_asm and text else "-"),
            "class": classify(text, size, jtbl, mmi),
        })

    total = len(rows)
    tot_b = sum(r["size"] for r in rows)
    hybrid = [r for r in rows if not r["data_ref"] and not r["jtbl"]]
    elig = [r for r in rows if r["eligible"]]
    easy = [r for r in elig if not r["mmi"]]
    elig_clean = [r for r in elig if not str(r["gate"]).startswith("blocked")]
    print(f"== M3 工作量分级（{args.target.upper()}，{proj.name}/）==")
    print(f"  函数 {total:,} 个 / {tot_b:,} B")
    print(f"  旧口径 hybrid_ok（无 data_ref、无 jtbl）: {len(hybrid):,} 个 / "
          f"{sum(r['size'] for r in hybrid):,} B（{100*sum(r['size'] for r in hybrid)/tot_b:.1f}% 字节）")
    print(f"  **新口径 eligible（真实机制：无非 .text 段、无 gp_rel、无 jtbl）**: {len(elig):,} 个 / "
          f"{sum(r['size'] for r in elig):,} B（{100*sum(r['size'] for r in elig)/tot_b:.1f}% 字节）")
    print(f"    其中可安全拆分（gate != blocked_*）: {len(elig_clean):,} 个 / "
          f"{sum(r['size'] for r in elig_clean):,} B")
    print(f"  其中**不含 MMI/COP2** 的更easy池: {len(easy):,} 个 / "
          f"{sum(r['size'] for r in easy):,} B（{100*sum(r['size'] for r in easy)/tot_b:.1f}%）")
    print()
    print(f"  {'tier':<8}{'函数数':>8}{'字节':>12}{'可纳管':>8}{'带数据':>8}{'跳转表':>7}{'MMI/COP2':>9}")
    for t in ("trivial", "small", "medium", "large", "huge"):
        sub = [r for r in rows if r["tier"] == t]
        if not sub:
            continue
        print(f"  {t:<8}{len(sub):>8,}{sum(r['size'] for r in sub):>12,}"
              f"{sum(1 for r in sub if not r['data_ref'] and not r['jtbl']):>8,}"
              f"{sum(r['data_ref'] for r in sub):>8,}{sum(r['jtbl'] for r in sub):>7,}"
              f"{sum(r['mmi'] for r in sub):>9,}")
    print()
    print(f"  缺 asm 文件的函数（无法走 hybrid）: {sum(1 for r in rows if not r['has_asm']):,}")
    print()

    # 难度画像（未匹配函数走哪条流水线）——长期计划 §2.2 的仪表盘
    matched = set()
    ms = ROOT / ("routebjp" if args.target == "jp" else "routeb") / "config" / "matched_symbols.txt"
    if ms.is_file():
        for line in ms.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                matched.add(line.split()[0])
    rest = [r for r in rows if r["name"] not in matched]
    by: dict[str, list[int]] = {}
    for r in rest:
        k = r["class"]
        by.setdefault(k, [0, 0])
        by[k][0] += 1
        by[k][1] += r["size"]
    print(f"  未匹配 {len(rest):,} 个 / {sum(r['size'] for r in rest):,} B 的难度画像：")
    order = ["A_trivial", "B_straight", "D_single_call", "D2_multi_call", "E_branch_only",
             "F_branch_call", "G_mmi", "jtbl", "gp_rel", "no_asm", "unknown"]
    for k in order + sorted(set(by) - set(order)):
        if k in by:
            print(f"    {k:16s} {by[k][0]:6,} fns  {by[k][1]:10,d} B")
    print()

    if args.tsv:
        p = Path(args.tsv)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            fh.write("name\taddr\tsize\ttier\tdata_ref\tjtbl\tmmi\tjal\tj\thybrid_ok\teligible\tgate\tclass\n")
            for r in sorted(rows, key=lambda r: (r["tier"], r["addr"])):
                fh.write(f"{r['name']}\t0x{r['addr']:08x}\t{r['size']}\t{r['tier']}\t"
                         f"{r['data_ref']}\t{r['jtbl']}\t{r['mmi']}\t{r['jal']}\t{r['j']}\t"
                         f"{int(not r['data_ref'] and not r['jtbl'])}\t{r['eligible']}\t{r['gate']}\t{r['class']}\n")
        print(f"  队列已写出：{p}（机器派生，不入库）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
