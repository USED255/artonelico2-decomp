#!/usr/bin/env python3
"""生成 splat 用的 symbol_addrs.txt —— 把 Ghidra 的 10,951 个函数边界
与 .erx.lib 的 749 个命名锚点合并成 splat 能读的符号表。

为什么需要这个：splat 不读 ELF 的 symtab（本作也已被 strip），**边界完全靠
symbol_addrs.txt**。没有它，splat 只能把整个 .text 当成一坨，产不出 per-function .s。
社区没有现成的「Ghidra → splat 符号」通用工具（已核实 `ghidra-to-splat` 不存在），
所以自己写。

输出格式（splat 接受）：
    name = 0xADDR; // type:func size:0xNN
    name = 0xADDR; // type:label

命名优先级：.erx.lib 的库+槽名 > Ghidra 的 FUN_xxxxxxxx（转成 func_xxxxxxxx）

用法: python3 tools/build/gen_symbol_addrs.py [-o OUT]
默认输出: out/symbol_addrs.txt
"""
import os, re, sys, collections

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FUNCS = os.path.join(BASE, 'out/ghidra/SLUS_217.88.functions.tsv')
TABLES = os.path.join(BASE, 'out/evidence/hle_tables_SLUS.txt')
DEFAULT_OUT = os.path.join(BASE, 'out/symbol_addrs.txt')


def load_functions():
    """Ghidra 函数：addr -> (name, size_bytes)"""
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
    """`.erx.lib` 导出注册表：addr -> 主名（库_槽号）"""
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
        out_path = sys.argv[sys.argv.index('-o') + 1]

    funcs = load_functions()
    erx = load_erx_names()

    # 注意：splat 的 symbol_addrs 解析器要求「每行恰好一个分号」，
    # 因此**不能**写表头注释行——生成物必须是纯数据行。
    lines = []
    named = 0
    used = {}          # name -> 首次出现的地址；重名时加地址后缀去重
    for addr in sorted(funcs):
        gname, size = funcs[addr]
        if addr in erx:
            name = erx[addr]
            named += 1
        elif gname.startswith('FUN_'):
            name = 'func_%08x' % addr
        else:
            # Ghidra 恢复了真名（多为 HLE syscall 桩），保留
            name = gname
            named += 1
        # splat 不允许同名符号：Ghidra 会把同一个名字发给多个地址（如 RFU116_SetSyscall），
        # 这里给重复项加地址后缀。别名关系仍保留在 out/evidence/erx_symbols.tsv。
        if name in used:
            name = '%s_%08x' % (name, addr)
        used[name] = addr
        lines.append('%s = 0x%08x; // type:func size:0x%x' % (name, addr, size))

    # .erx.lib 里还有若干地址是 Ghidra 没识别为函数入口的。**不能**把它们写成
    # `type:label` —— splat 会输出成普通局部标签，夹在全局符号中间，导致 .symtab
    # 的 sh_info 与实际 local 数量不符，GNU ld 报
    # ".symtab local symbol at index N (>= sh_info of M)" 并拒绝链接。
    # 这些名字的完整清单保留在 out/evidence/erx_symbols.tsv，供人工命名参考。
    extra = [a for a in erx if a not in funcs]   # 仅用于统计，**不写入符号表**

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    print('函数符号      = %d' % len(funcs))
    print('  有真名/锚点 = %d (%.1f%%)' % (named, 100 * named / max(len(funcs), 1)))
    print('  仅占位      = %d' % (len(funcs) - named))
    print('额外 label    = %d' % len(extra))
    print('写出          = %s' % os.path.relpath(out_path, BASE))


if __name__ == '__main__':
    main()
