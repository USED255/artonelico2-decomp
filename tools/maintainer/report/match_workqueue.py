#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write the matching batch workload queue. Group main-program functions by "can the current pipeline do it".

The queue supports parallel work.

Input (the Japanese main target by default; --target us selects the US reference):
  <proj>/config/symbol_addrs.txt     function name, address, and size (Ghidra bounds)
  <proj>/asm/cod/<symbol>.s          per-function disassembly (for data references, jump tables, MMI)

Classification:
  tier      size band: trivial(<17 B) / small(17-64) / medium(65-256) / large(257-1024) / huge(>1 KB)
  data_ref  the code references a symbol in .rodata/.data (%hi/%lo points to D_*, jtbl_*, or another non-function symbol)
  jtbl      the code references a jump table
  mmi       the code holds R5900 extension instructions (MMI / COP2 / LQ-SQ and others)
  hybrid_ok old rule: no data_ref and no jtbl (conservative; see below)
  eligible  new rule (corrected 2026-10-03): an in-place replacement works if
            1. the .s file defines no section other than .text, else the C or asm object cannot hold the data,
            2. the code holds no %gp_rel, which needs -G and the current compile flags cannot reach,
            3. the code references no jump table (jtbl_*), which needs in-place .rodata.
            A reference to an EXTERNAL data symbol (absolute %hi/%lo) does not block the replacement.
            C code with `extern D_x` gives the same lui/%lo absolute addressing.
            Evidence: the per-function compare sample baseelf_19 is objdiff 100 percent, and the payload check is green.
  gate      can the pipeline extract the target block alone: direct / residual / blocked_*
            (the same rule as routebjp/tools/split_asm.py)

Private pipeline compatibility, do not rename: the file name jp_m3_workqueue.tsv,
the column name hybrid_ok, and the private layout path routebjp/**.

Usage:
  python3 tools/report/match_workqueue.py                     # Japanese target (default), print a summary
  python3 tools/report/match_workqueue.py --target us         # US reference
  python3 tools/report/match_workqueue.py --tsv out/evidence/jp_m3_workqueue.tsv

matching batch 工作量分级队列：把主程序函数按「能不能用现有流水线做」分类，
产出可并行的工作队列。
输入是 proj/config/symbol_addrs.txt（Ghidra 边界）与 asm/cod/<符号>.s（反汇编）。
分类维度见英文段：tier 尺寸档、data_ref 数据引用、jtbl 跳转表、mmi R5900 扩展指令、
hybrid_ok 旧口径、eligible 新口径、gate 目标块能否单独摘出。

私有流水线兼容，勿改名：jp_m3_workqueue.tsv 文件名、hybrid_ok 列名、
私有布局路径 routebjp/**。改了会打断正在跑的匹配流水线。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# Fix 2026-10-04 (P-31): the first version treated `mult/multu/div/divu/madd/msub/
# mfhi/mflo/mthi/mtlo` as MMI. Those are plain MIPS I instructions and occur
# everywhere. 2,741 functions were marked G_mmi by mistake; 1,865 of them hold
# no MMI/COP2/lq/sq instruction at all. The real R5900 extension is the
# three-operand form `mult $rd,$rs,$rt` (also madd/msub/div). Therefore the
# pattern below keeps the R5900 extension marks and the packed/VU/COP2 marks
# only. r5900_muldiv() checks the three-operand form separately.
#
# 2026-10-04 修正（P-31）：原先把 mult/multu/div/divu/madd/msub/mfhi/mflo/mthi/mtlo
# 也当成 MMI，但那些是普通 MIPS I 指令，导致 2,741 个函数被误标成 G_mmi
# （其中 1,865 个根本没有 MMI/COP2/lq/sq）。R5900 真正扩展的是三操作数形式
# mult $rd,$rs,$rt，所以这里只保留 R5900 扩展与打包/VU/COP2 记号，
# 三操作数形式由 r5900_muldiv() 单独判断。
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
# The integer multiply and divide extension of the R5900: `mult $rd,$rs,$rt`
# (three operands). The two-operand form is plain MIPS I.
#
# R5900 的整数乘除扩展是多操作数形式 `mult $rd,$rs,$rt`；两操作数的是普通 MIPS I。
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
    """Real rule: no section other than .text, no %gp_rel, and no jump table.

    真实机制判定：无非 .text 段、无 %gp_rel、无跳转表。
    """
    secs = {s.strip('"') for s in SECTION.findall(text)}
    if {s for s in secs if not s.startswith(".text")}:
        return False
    if "%gp_rel" in text:
        return False
    return not jtbl


# Difficulty profile. The profile selects the automation pipeline for one
# function. See the long-term plan (private repository note R11 section 2.2).
#
# 难度画像（决定用哪条自动化流水线；见私有仓库长期计划 R11 §2.2）。
INS_RE = re.compile(r"/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
BRANCH_MN = {"b", "beq", "bne", "beqz", "bnez", "blez", "bgtz", "bltz", "bgez",
             "bgezal", "bltzal", "bgezl", "bgtzl", "blezl", "bltzl", "bc1",
             "beql", "bnel", "jr", "jalr"}


def classify(text: str, size: int, jtbl: bool, mmi: bool) -> str:
    """Give an unmatched function the label of the pipeline that fits it.

    给未匹配函数一个「该走哪条流水线」的类别标签。
    """
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
    # The example TSV name is a private pipeline name. Keep it. See the module docstring.
    ap.add_argument("--tsv", default="")
    args = ap.parse_args()

    proj = ROOT / ("routebjp" if args.target == "jp" else "routeb")
    syms = scan_syms(proj / "config" / "symbol_addrs.txt")
    if not syms:
        print(f"SKIP: {proj}/config/symbol_addrs.txt is missing or empty")
        return 0

    # Reuse the gate rule from routebjp/tools/split_asm.py. The Japanese target
    # has the file. The US reference gives no gate.
    #
    # gate 判据复用 routebjp/tools/split_asm.py（日版才有；美版参照不给 gate）。
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
    hybrid_ok = [r for r in rows if not r["data_ref"] and not r["jtbl"]]
    elig = [r for r in rows if r["eligible"]]
    easy = [r for r in elig if not r["mmi"]]
    elig_clean = [r for r in elig if not str(r["gate"]).startswith("blocked")]
    print(f"== matching batch workload tiers ({args.target.upper()}, {proj.name}/) ==")
    print(f"  functions {total:,} / {tot_b:,} B")
    print(f"  old rule hybrid_ok (no data_ref, no jtbl): {len(hybrid_ok):,} / "
          f"{sum(r['size'] for r in hybrid_ok):,} B ({100*sum(r['size'] for r in hybrid_ok)/tot_b:.1f}% of bytes)")
    print(f"  new rule eligible (real mechanism: no non-.text section, no gp_rel, no jtbl): {len(elig):,} / "
          f"{sum(r['size'] for r in elig):,} B ({100*sum(r['size'] for r in elig)/tot_b:.1f}% of bytes)")
    print(f"    of which safe to split (gate != blocked_*): {len(elig_clean):,} / "
          f"{sum(r['size'] for r in elig_clean):,} B")
    print(f"    of which without MMI/COP2 (the easier pool): {len(easy):,} / "
          f"{sum(r['size'] for r in easy):,} B ({100*sum(r['size'] for r in easy)/tot_b:.1f}%)")
    print()
    print(f"  {'tier':<8}{'functions':>10}{'bytes':>12}{'in scope':>9}{'data':>8}{'jtbl':>7}{'MMI/COP2':>9}")
    for t in ("trivial", "small", "medium", "large", "huge"):
        sub = [r for r in rows if r["tier"] == t]
        if not sub:
            continue
        print(f"  {t:<8}{len(sub):>10,}{sum(r['size'] for r in sub):>12,}"
              f"{sum(1 for r in sub if not r['data_ref'] and not r['jtbl']):>9,}"
              f"{sum(r['data_ref'] for r in sub):>8,}{sum(r['jtbl'] for r in sub):>7,}"
              f"{sum(r['mmi'] for r in sub):>9,}")
    print()
    print(f"  functions without an asm file (the mixed build cannot replace them): {sum(1 for r in rows if not r['has_asm']):,}")
    print()

    # Difficulty profile of the unmatched functions. This is the dashboard of
    # the long-term plan (private repository note R11 section 2.2).
    #
    # 难度画像（未匹配函数走哪条流水线）——私有仓库长期计划 R11 §2.2 的仪表盘。
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
    print(f"  difficulty profile of {len(rest):,} unmatched functions / {sum(r['size'] for r in rest):,} B:")
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
            # The column name hybrid_ok is a private pipeline name. Do not rename it.
            fh.write("name\taddr\tsize\ttier\tdata_ref\tjtbl\tmmi\tjal\tj\thybrid_ok\teligible\tgate\tclass\n")
            for r in sorted(rows, key=lambda r: (r["tier"], r["addr"])):
                fh.write(f"{r['name']}\t0x{r['addr']:08x}\t{r['size']}\t{r['tier']}\t"
                         f"{r['data_ref']}\t{r['jtbl']}\t{r['mmi']}\t{r['jal']}\t{r['j']}\t"
                         f"{int(not r['data_ref'] and not r['jtbl'])}\t{r['eligible']}\t{r['gate']}\t{r['class']}\n")
        print(f"  queue written: {p} (machine-derived, not tracked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
