#!/usr/bin/env python3
"""Write symbol_addrs.txt for splat. Merge the Ghidra function bounds with the named anchors from .erx.lib.

Why the file is necessary: splat does not read the ELF symtab, and the retail
ELF is stripped. The function bounds come from symbol_addrs.txt only. Without
the file, splat treats the whole .text as one block and cannot write a
per-function .s file. No community tool converts Ghidra symbols to splat
symbols, so this script does the work.

Output format (splat accepts it):
    name = 0xADDR; // type:func size:0xNN
    name = 0xADDR; // type:label

Name priority: the .erx.lib library and slot name wins over the Ghidra
FUN_xxxxxxxx name (written as func_xxxxxxxx).

The Ghidra and .erx.lib inputs are private-side evidence. Keep their paths.

Usage: python3 tools/maintainer/build/gen_symbol_addrs.py [-o OUT]
Default output: out/symbol_addrs.txt

生成 splat 用的 symbol_addrs.txt：把 Ghidra 的函数边界与 .erx.lib 的命名锚点
合并成 splat 能读的符号表。splat 不读 ELF 的 symtab，没有这份文件就只能把
整个 .text 当成一坨，产不出 per-function .s。
输入 out/ghidra/** 与 out/evidence/** 属私有侧证据，路径保留不改。
命名优先级：.erx.lib 的库+槽名 > Ghidra 的 FUN_xxxxxxxx（转成 func_xxxxxxxx）。
"""
import collections
import os
import re
import sys
from pathlib import Path

# Make the shared tools in tools/project importable.  让 tools/project 的共享工具可被导入。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project"))
import at2_io  # noqa: E402  safe symbols / atomic writes

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FUNCS = os.path.join(BASE, 'out/ghidra/SLUS_217.88.functions.tsv')
TABLES = os.path.join(BASE, 'out/evidence/hle_tables_SLUS.txt')
DEFAULT_OUT = os.path.join(BASE, 'out/symbol_addrs.txt')


def load_functions():
    """Read Ghidra functions: addr -> (name, size_bytes).

    从 Ghidra 函数表读出 addr -> (name, size_bytes)。
    """
    out = {}
    for line in open(FUNCS, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) < 3 or p[0] == 'addr':
            continue
        try:
            out[int(p[0], 16)] = (p[1], int(p[2]))
        except ValueError:
            pass
    return out


def load_erx_names():
    """Read the `.erx.lib` export registry: addr -> primary name (library_slot).

    读 `.erx.lib` 导出注册表：addr -> 主名（库_槽号）。
    """
    cur, rows = None, []
    for line in open(TABLES, encoding='utf-8'):
        m = re.match(r'^=== library (\S+)', line)
        if m:
            cur = m.group(1); continue
        m = re.match(r'^\s+(\d+)\s+(0x[0-9a-f]+)\s+(\S+)', line)
        if m and cur and m.group(3) != 'none':
            rows.append((cur, int(m.group(1)), int(m.group(2), 16)))
    seen, out = set(), {}
    for lib, slot, addr in rows:
        if addr in seen:
            continue
        seen.add(addr)
        out[addr] = '%s_%d' % (lib, slot)
    return out


def main():
    out_path = DEFAULT_OUT
    if '-o' in sys.argv:
        i = sys.argv.index('-o')
        if i + 1 >= len(sys.argv):
            print("error: -o requires an output path", file=sys.stderr)
            return 2
        out_path = sys.argv[i + 1]

    funcs = load_functions()
    erx = load_erx_names()

    # The splat symbol_addrs parser requires exactly one semicolon on each line.
    # Therefore the output must hold data lines only. It cannot hold a header
    # comment.
    #
    # splat 的 symbol_addrs 解析器要求「每行恰好一个分号」，
    # 因此生成物必须是纯数据行，不能写表头注释行。
    lines = []
    named = 0
    unsafe = 0
    used = {}          # name -> first address; a duplicate name gets an address suffix
    for addr in sorted(funcs):
        gname, size = funcs[addr]
        if addr in erx:
            name = erx[addr]
            named += 1
        elif gname.startswith('FUN_'):
            name = 'func_%08x' % addr
        else:
            # Ghidra recovered the real name (mostly an HLE syscall stub). Keep it.
            name = gname
            named += 1
        # splat rejects two symbols with one name. Ghidra gives one name to
        # several addresses. Add an address suffix to the duplicate. The alias
        # list stays in out/evidence/erx_symbols.tsv.
        #
        # splat 不允许同名符号：Ghidra 会把同一个名字发给多个地址，
        # 这里给重复项加地址后缀，别名关系仍保留在 erx_symbols.tsv。
        if name in used:
            name = '%s_%08x' % (name, addr)
        try:
            # A malformed name would inject arbitrary text into symbol_addrs.txt (D4).
            # 名字不合法会把任意文本注入 symbol_addrs.txt（D4）。
            at2_io.safe_symbol(name, what="symbol")
        except ValueError as e:
            unsafe += 1
            print('  skip unsafe symbol: %s' % e, file=sys.stderr)
            continue
        used[name] = addr
        lines.append('%s = 0x%08x; // type:func size:0x%x' % (name, addr, size))

    # Some .erx.lib addresses are not function entries for Ghidra. Do not write
    # them as `type:label`. splat would emit a local label in the middle of the
    # global symbols. Then the .symtab sh_info would not match the real local
    # count, and GNU ld would report ".symtab local symbol at index N (>= sh_info
    # of M)" and refuse to link. The full list stays in
    # out/evidence/erx_symbols.tsv for manual naming.
    #
    # .erx.lib 里还有若干地址不是 Ghidra 识别的函数入口。不能写成 type:label，
    # 否则 splat 会输出夹在全局符号中间的局部标签，导致 .symtab 的 sh_info 与
    # 实际 local 数量不符，GNU ld 报错并拒绝链接。完整清单保留在
    # out/evidence/erx_symbols.tsv 供人工命名参考。
    extra = [a for a in erx if a not in funcs]   # statistics only; never written to the symbol table

    # The output can be the tracked config/symbol_addrs.txt; write it atomically (D12).
    # 输出可能是 tracked 的 config/symbol_addrs.txt，用原子写（D12）。
    at2_io.atomic_write_text(out_path, '\n'.join(lines) + '\n')

    print('function symbols   = %d' % len(funcs))
    print('  named or anchored = %d (%.1f%%)' % (named, 100 * named / max(len(funcs), 1)))
    print('  placeholder only  = %d' % (len(funcs) - named))
    print('extra labels       = %d' % len(extra))
    if unsafe:
        print('  unsafe rows skipped = %d' % unsafe)
    print('wrote              = %s' % os.path.relpath(out_path, BASE))
    return 0


if __name__ == '__main__':
    sys.exit(main())
