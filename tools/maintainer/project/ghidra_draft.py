#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ghidra pseudo C -> compilable draft (experiment tool for P1a and gate G1).

Background: `routebjp/build/ghidra/SLPS_258.19.decomp.c` (9.9 MB, 10,919 functions) is
pseudo C from Ghidra 12.1.4 and the R5900 language. The long-term plan section 4/P1a asks
for a measurement: can pseudo C serve as a matching draft? This tool extracts the pseudo C
of one function, adds a minimal shim, and maps `FUN_xxxxxxxx` back to our symbol names. It
writes `<sym>.draft.c` for compile and objdiff scoring by
`tools/project/p1a_pseudoc_probe.py`.

Rule (honest class):
  * A successful compile proves only that the syntax and the types are usable.
  * Only objdiff == 100 counts as a match. Pseudo C is a **draft**, so the tool makes no
    meaning claim from it.

Usage:
  python3 tools/project/ghidra_draft.py list | emit <sym> <outdir>

Ghidra 伪 C → 可编译草稿（P1a / 闸门 G1 的实验工具）。

背景：`routebjp/build/ghidra/SLPS_258.19.decomp.c`（9.9 MB，10,919 个函数）是 Ghidra 12.1.4
+ R5900 语言的伪 C。长期计划 §4/P1a 要求实测：「伪 C 能否作为匹配草稿」。
本工具把单个函数的伪 C 抽出来、补最小 shim、把 `FUN_xxxxxxxx` 改回我们的符号名，
输出 `<sym>.draft.c`，供 `tools/project/p1a_pseudoc_probe.py` 编译 + objdiff 打分。

判据（诚实口径）：
  * 编译通过 = 语法/类型层可用；
  * objdiff == 100 才算「匹配」；伪 C 是**草稿**，不据此断言语义。

用法：
  python3 tools/project/ghidra_draft.py list | emit <sym> <outdir>
"""

# Private layout names (routebjp/build/ghidra, routebjp/build/hybrid, routebjp/build/mixed), do not rename.  私有布局名（routebjp/build/ghidra、routebjp/build/hybrid、routebjp/build/mixed），勿改名。

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from at2_paths import PROJECT_ROOT as ROOT, PRIVATE_ROOT, WORK_ROOT, ASMDIR  # noqa: E402  layout independent

REPO = PRIVATE_ROOT or ROOT
DECOMP = WORK_ROOT / "ghidra" / "SLPS_258.19.decomp.c"
SYMADDRS = ROOT / "config" / "symbol_addrs.txt"

MARK = re.compile(r"^//==== ([0-9a-fA-F]{8}) (\S+) ====", re.M)

SHIM = r"""/* Minimal shim for Ghidra pseudo C (experiment only; not a final type recovery) */
typedef unsigned char      undefined;
typedef unsigned char      undefined1;
typedef unsigned short     undefined2;
typedef unsigned int       undefined4;
typedef unsigned long long undefined8;
typedef unsigned int       uint;
typedef unsigned long      ulong;
typedef unsigned short     ushort;
typedef unsigned char      uchar;
typedef long long          longlong;
typedef unsigned long long ulonglong;
typedef unsigned char      byte;
typedef unsigned char      code;
typedef unsigned char      bool;
typedef struct { int a[3]; } int3;
typedef struct { unsigned int a[3]; } uint3;
#define true 1
#define false 0
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
#define CONCAT44(a,b) (((unsigned long long)(a) << 32) | (unsigned int)(b))
#define CONCAT13(a,b) ((((unsigned int)(a)) << 24) | ((unsigned int)(b) & 0xffffff))
#define CONCAT22(a,b) ((((unsigned int)(a)) << 16) | ((unsigned int)(b) & 0xffff))
#define SUB41(a,b) ((unsigned int)(a))
#define SUB42(a,b) ((unsigned int)(a))
#define ZEXT14(a)  ((unsigned int)(unsigned char)(a))
#define ZEXT24(a)  ((unsigned int)(unsigned short)(a))
#define ZEXT48(a)  ((unsigned long long)(unsigned int)(a))
#define SEXT14(a)  ((int)(signed char)(a))
#define SEXT24(a)  ((int)(short)(a))
#define SEXT48(a)  ((long long)(int)(a))
#define LOWER(x)   ((unsigned int)(x))
#define HIDWORD(x) ((unsigned int)((unsigned long long)(x) >> 32))
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int  syscall(int);
"""

IDENT_FUN = re.compile(r"\bFUN_([0-9a-fA-F]{8})\b")
# Ghidra global symbol names (case is kept; the forms include _DAT_, _PTR_, and PTR_s_<text>_<addr>)
# Ghidra 全局符号名（保留大小写；含 _DAT_/_PTR_/PTR_s_<text>_<addr> 等形态）
IDENT_GLOB = re.compile(r"\b(_?(?:DAT|PTR|UNK|LAB)_[A-Za-z0-9_]+)\b")


_DECOMP_CACHE = None
_NAMES_CACHE = None
_DATA_CACHE = None
_GP_CACHE = None

# Directive in asm/data -> (C type, has an initial value)  伪指令 -> (C 类型, 是否有初值)
DIRECTIVE_TYPE = {
    ".word": ("unsigned int", True),
    ".short": ("unsigned short", True),
    ".byte": ("unsigned char", True),
    ".float": ("float", True),
    ".double": ("double", True),
    ".dword": ("unsigned long long", True),
}


def gp_value():
    """Read `_gp` from the link map of the baseline build or the mixed build.

    Use the value to turn the Ghidra `fGp<off>` form into a data symbol address.

    从 baseline build / mixed build 的 link map 里取 `_gp`，用于把 Ghidra 的 `fGp<off>` 还原成数据符号地址。
    """
    global _GP_CACHE
    if _GP_CACHE is not None:
        return _GP_CACHE
    # "hybrid" is a private repo layout name, do not rename. "mixed" is the output
    # directory of build_mixed.sh in the public repo.
    # "hybrid" 是私有仓库布局名，勿改名；"mixed" 是公开仓库 build_mixed.sh 的产物目录。
    for p in (WORK_ROOT / "mixed" / "SLPS_258.19.map",
              WORK_ROOT / "hybrid" / "SLPS_258.19.map",     # private layout name, do not rename
              WORK_ROOT / "SLPS_258.19.map"):
        if p.is_file():
            for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r'\s*0x([0-9a-fA-F]+)\s+_gp\b', l)
                if m:
                    _GP_CACHE = int(m.group(1), 16)
                    return _GP_CACHE
    _GP_CACHE = 0
    return 0


def fgp_to_sym(text: str) -> str:
    """Ghidra writes an unresolved gp offset as `fGp<8 hex digits>`. This function uses _gp to
    compute the address and returns the `D_<ADDR>` name.

    Ghidra 对「未解析的 gp 偏移」写作 `fGp<8 位 hex>`；用 _gp 反算地址得到 `D_<ADDR>`。
    """
    gp = gp_value()
    if not gp:
        return text

    def repl(m):
        off = int(m.group(1), 16)
        off = off - 0x100000000 if off >= 0x80000000 else off
        return "D_%08X" % ((gp + off) & 0xFFFFFFFF)

    # The Ghidra prefix changes with the access type: fGp(float), uGp(unsigned), iGp(int),
    # cGp, sGp, and more. This code converts all of them with the rule "gp plus a signed
    # 16-bit offset" to D_<ADDR>. The directive in asm/data decides the type.
    # Ghidra 的前缀随访问类型变化：fGp(float)/uGp(unsigned)/iGp(int)/cGp/sGp/…，
    # 统一按「gp + 有符号 16 位偏移」还原成 D_<ADDR>（类型以 asm/data 的伪指令为准）。
    return re.sub(r"\b[a-zA-Z]Gp([0-9a-fA-F]{4,8})\b", repl, text)


def data_index():
    """Scan asm/data and return {symbol: (section name, directive, initial value or None)}.

    A `.space N` entry (.sbss) has no initial value. N==4 gives unsigned int. N==8 gives
    unsigned long long. Any other N gives None and the candidate is skipped.

    扫描 asm/data，得到 {符号: (段名, 伪指令, 初值文本 或 None)}。

    `.space N`（.sbss）没有初值：N==4 -> unsigned int，N==8 -> unsigned long long，其它 -> None（该候选跳过）。
    """
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE
    idx = {}
    for f in (ROOT / "asm" / "data").rglob("*.s"):
        sec = None
        lines = f.read_text(encoding="utf-8", errors="replace").split("\n")
        for i, l in enumerate(lines):
            m = re.match(r'^\s*\.section\s+([.\w]+)', l)
            if m:
                sec = m.group(1)
                continue
            m = re.match(r'^\s*dlabel\s+(\S+)', l)
            if not m:
                continue
            sym = m.group(1)
            if sec is None:
                continue
            # Find the first data directive in the block  找块内第一条数据伪指令
            for j in range(i + 1, min(i + 8, len(lines))):
                mm = re.search(r'\*/\s*\.(\w+)\s*(.*)$', lines[j])
                if not mm:
                    mm = re.match(r'^\s*\.(\w+)\s*(.*)$', lines[j])
                if mm:
                    idx[sym] = (sec, "." + mm.group(1), mm.group(2).strip())
                    break
    _DATA_CACHE = idx
    return idx


def weak_def_c(sym: str) -> str | None:
    """Write a small data symbol as a weak definition. This form gives %gp_rel code output.

    The linker discards the section itself with /DISCARD/.

    把小数据符号写成「weak 定义」，用于拿到 %gp_rel 代码生成（段本身会被 /DISCARD/ 丢弃）。
    """
    info = data_index().get(sym)
    if not info:
        return None
    sec, directive, arg = info
    secname = sec.split(",")[0].strip()
    if directive == ".space" or arg == "":
        try:
            n = int(arg, 16) if str(arg).lower().startswith("0x") else int(arg)
        except ValueError:
            return None
        ty = {4: "unsigned int", 8: "unsigned long long"}.get(n)
        if ty is None:
            return None
        return f'{ty} {sym} __attribute__((section("{secname}"), weak));'
    ty, has_init = DIRECTIVE_TYPE.get(directive, (None, False))
    if ty is None:
        return None
    val = arg.split()[0].rstrip(";") if arg else ""
    numeric = re.fullmatch(r"-?(0[xX][0-9A-Fa-f]+|\d+)(\.\d+)?([eE][-+]?\d+)?", val or "")
    if not has_init or not val or not numeric:
        # A symbol initial value (for example `.word func_0`) cannot be a literal. The
        # linker discards the section anyway. This code needs only a compile and a gp_rel
        # output, so it omits the initial value.
        # 初值是符号（如 `.word func_0`）时不能直接当字面量；段本来就会被 /DISCARD/ 丢弃，
        # 这里只求「能编译且给出 gp_rel 代码生成」，所以省略初值。
        return f'{ty} {sym} __attribute__((section("{secname}"), weak));'
    return f'{ty} {sym} __attribute__((section("{secname}"), weak)) = {val};'



def load_decomp():
    """Parse the 9.9 MB pseudo C file (cached; a fresh parse per function is far too slow in a batch).

    解析 9.9 MB 伪 C（带缓存；批量跑时每个函数都重新解析会慢到不可用）。
    """
    global _DECOMP_CACHE
    if _DECOMP_CACHE is None:
        txt = DECOMP.read_text(encoding="utf-8", errors="replace")
        marks = [(m.start(), m.group(1).lower(), m.group(2)) for m in MARK.finditer(txt)]
        index = {addr: (start, marks[i + 1][0] if i + 1 < len(marks) else len(txt))
                 for i, (start, addr, _n) in enumerate(marks)}
        _DECOMP_CACHE = (txt, index)
    return _DECOMP_CACHE


def name_map():
    """Return addr (lower hex, 8 digits) -> our symbol name (cached).

    addr(lower hex, 8) -> 我们的符号名（带缓存）。
    """
    global _NAMES_CACHE
    if _NAMES_CACHE is not None:
        return _NAMES_CACHE
    out = {}
    for line in SYMADDRS.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(\S+)\s*=\s*0x([0-9A-Fa-f]{8})", line)
        if m:
            out[m.group(2).lower()] = m.group(1)
    _NAMES_CACHE = out
    return out


def body_of(sym: str):
    txt, index = load_decomp()
    want = sym.split("_")[-1].lower()
    rng = index.get(want)
    if rng is None:
        return None
    return txt[rng[0]:rng[1]].strip()


def our_name(gh: str) -> str:
    """Map a Ghidra global symbol name to the splat naming.

    splat writes a data symbol as `D_<8 upper hex digits>` (asm uses `%hi(D_009E5A2C)`).
    Ghidra writes `DAT_009e5a2c`, `_DAT_009dfc58`, or `PTR_s_..._008077e8`.
    The names **must agree**. If they do not, the relocation target of the C object is
    `DAT_...` and the target assembly is `D_...`. objdiff then reports a difference, and
    the link fails because the --defsym rules do not hold `DAT_*`.

    把 Ghidra 的全局符号名映射到 splat 的命名。

    splat 用 `D_<8 位大写 hex>` 表示数据符号（asm 里就是 `%hi(D_009E5A2C)`），
    Ghidra 写 `DAT_009e5a2c` / `_DAT_009dfc58` / `PTR_s_..._008077e8`。
    **必须统一**：否则 C 对象的重定位目标是 `DAT_...`，而目标汇编是 `D_...`，
    objdiff 直接判不等，链接期也会因为 `DAT_*` 不在 --defsym 规则里而失败。
    """
    m = re.fullmatch(r"_?(?:DAT|UNK|LAB)_([0-9a-fA-F]{6,8})", gh)
    if m:
        return "D_" + m.group(1).upper().zfill(8)
    m = re.fullmatch(r"PTR_[A-Za-z0-9_]*?_([0-9a-fA-F]{6,8})", gh)
    if m:
        return "D_" + m.group(1).upper().zfill(8)
    m = re.fullmatch(r"PTR_([A-Za-z0-9_]+)", gh)
    if m:
        return gh          # A PTR_ name with no address suffix: keep it. The link reports the error.
    return gh


def emit(sym: str, outdir: Path, gprel_syms: set | None = None) -> Path | None:
    body = body_of(sym)
    if body is None:
        return None
    names = name_map()
    funs = {a.lower() for a in IDENT_FUN.findall(body)}
    # First rewrite all symbols (FUN_ -> our name, DAT_/PTR_ -> D_<HEX>, fGp<off> -> D_<ADDR>).
    # Then collect the global symbols that need a declaration or a definition from the
    # result. Without this order, a symbol from an fGp conversion gets no declaration and
    # the compile reports "undeclared".
    # ⚠️ 先做全部符号改写（FUN_ → 我们的名字、DAT_/PTR_ → D_<HEX>、fGp<off> → D_<ADDR>），
    #    再据此收集「需要声明/定义」的全局符号——否则 fGp 还原出来的符号不会被声明（编译报 undeclared）。
    text = body
    text = IDENT_FUN.sub(lambda m: names.get(m.group(1).lower(), "func_" + m.group(1).lower()), text)
    text = IDENT_GLOB.sub(lambda m: our_name(m.group(1)), text)
    text = fgp_to_sym(text)
    # Global symbols: (1) the DAT_/PTR_/UNK_/LAB_ mapped names from the original body;
    # (2) every D_<8 upper hex digits> name in the converted text. Both the fGp conversion
    # and our_name produce that form. IDENT_GLOB does not match the D_ prefix, so this code
    # collects it separately.
    # 全局符号：① 原体里的 DAT_/PTR_/UNK_/LAB_ 映射名；② 映射后文本里出现的 D_<8 位大写 HEX>
    # （fGp 还原 + our_name 产物都是这个形态；IDENT_GLOB 不认 D_ 前缀，必须单独收）
    globs = {our_name(g) for g in IDENT_GLOB.findall(body)}
    globs |= set(re.findall(r"\bD_[0-9A-F]{8}\b", text))
    decls = []
    for a in sorted(funs):
        if a == sym.split("_")[-1].lower():
            continue
        decls.append(f"extern int {names.get(a, 'func_' + a)}();")
    # Declare a global variable as a scalar in the Ghidra usage form. `DAT_x = v` needs an
    # left value. `&DAT_x` and `(&DAT_x)[i]` also work.
    # 全局变量按 Ghidra 的用法声明成标量（`DAT_x = v` 需要左值；`&DAT_x`/`(&DAT_x)[i]` 同样可用）
    gprel = {s for s in (gprel_syms or set()) if our_name(s) in globs or s in globs}
    for g in sorted(globs):
        if g.startswith("PTR_"):
            continue
        if gprel and g in {our_name(s) for s in gprel}:
            d = weak_def_c(g)
            if d:
                decls.append(d)
                continue
        decls.append(f"extern unsigned int {g};")
    # The Ghidra function head `void FUN_x(void)` is renamed. The return type keeps the Ghidra decision.
    # Ghidra 的函数头 `void FUN_x(void)` 已改名；返回类型保持 Ghidra 判断
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / f"{sym}.draft.c"
    p.write_text(SHIM + "\n" + "\n".join(decls) + "\n\n" + text + "\n", encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "emit"])
    ap.add_argument("sym", nargs="?")
    ap.add_argument("outdir", nargs="?")
    args = ap.parse_args()
    if args.cmd == "list":
        txt, index = load_decomp()
        names = name_map()
        print(f"pseudo C functions {len(index)}; mapped to a known symbol {sum(1 for a in index if a in names)}")
        return 0
    if not args.sym or not args.outdir:
        print("emit needs <sym> <outdir>", file=sys.stderr)
        return 2
    p = emit(args.sym, Path(args.outdir))
    if p is None:
        print(f"{args.sym}: no matching address in the pseudo C")
        return 1
    print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
