#!/usr/bin/env python3
"""把主程序 .erx.lib 导出注册表转成 decomp 项目可用的符号表。

背景：SLUS_217.88 被完全 strip（.mdebug=0、无 .symtab），10,951 个函数里 99.3% 是 FUN_*。
但 .erx.lib 是一张**导出注册表**：21 个库 / 1,109 个槽位 / 749 个唯一函数地址。
本脚本把它转成符号表，给 749 个函数至少一个"库+槽号"级别的名字，作为人工命名的起点。

输入：out/evidence/hle_tables_SLUS.txt（由 tools/research/imports.py 生成）
输出：
  out/evidence/erx_symbols.tsv   地址 / 主名 / 全部别名 / 是否 Ghidra 函数入口
  out/evidence/symbols.txt       decomp 项目风格：`<addr_hex> <name>`（主名）

用法: python3 tools/build/export_symbols.py
"""
import re, os, json, collections

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TABLES = os.path.join(BASE, 'out/evidence/hle_tables_SLUS.txt')
FUNCS = os.path.join(BASE, 'out/ghidra/SLUS_217.88.functions.tsv')
OUT_TSV = os.path.join(BASE, 'out/evidence/erx_symbols.tsv')
OUT_SYM = os.path.join(BASE, 'out/evidence/symbols.txt')

# 这些库是"游戏自身向外暴露的 API"，命名时给更显眼的前缀
GAME_LIBS = {'baseelf'}


def parse_tables(path):
    """返回 [(lib, slot, addr, kind)]，跳过 none 槽位。"""
    libs = []
    cur = None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^=== library (\S+)\s+version=(\S+)\s+slots=(\d+)', line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r'^\s+(\d+)\s+(0x[0-9a-f]+)\s+(\S+)', line)
        if m and cur is not None:
            slot, addr, kind = int(m.group(1)), int(m.group(2), 16), m.group(3)
            if kind != 'none':
                libs.append((cur, slot, addr, kind))
    return libs


def parse_func_entries(path):
    s = set()
    if not os.path.exists(path):
        return s
    for line in open(path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3 and p[0] != 'addr':
            try:
                s.add(int(p[0], 16))
            except ValueError:
                pass
    return s


def main():
    rows = parse_tables(TABLES)
    entries = parse_func_entries(FUNCS)

    by_addr = collections.OrderedDict()
    for lib, slot, addr, kind in rows:
        by_addr.setdefault(addr, []).append((lib, slot, kind))

    def primary(addr):
        """选主名：游戏自身 API 优先，其次按 (库名, 槽号) 排序取第一个。"""
        owners = by_addr[addr]
        game = [o for o in owners if o[0] in GAME_LIBS]
        pick = (game or sorted(owners))[0]
        return pick[0], pick[1]

    os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
    with open(OUT_TSV, 'w', encoding='utf-8') as f:
        f.write('addr\tslot\tprimary_name\tis_func_entry\tn_aliases\taliases\n')
        for addr in sorted(by_addr):
            lib, slot = primary(addr)
            aliases = ';'.join('%s:%d' % (l, s) for l, s, _ in sorted(by_addr[addr]))
            f.write('0x%08x\t%d\t%s_%d\t%s\t%d\t%s\n' % (
                addr, slot, lib, slot, 'yes' if addr in entries else 'no',
                len(by_addr[addr]), aliases))

    with open(OUT_SYM, 'w', encoding='utf-8') as f:
        f.write('# 由 tools/build/export_symbols.py 生成 —— 来源：主程序 .erx.lib 导出注册表\n')
        f.write('# 格式: <vaddr_hex> <name>   （同名多槽位时保留主名，别名见 erx_symbols.tsv）\n')
        for addr in sorted(by_addr):
            lib, slot = primary(addr)
            f.write('0x%08x %s_%d\n' % (addr, lib, slot))

    # ---- 统计 ----
    stats = collections.Counter()
    for lib, slot, addr, kind in rows:
        stats[lib] += 1
    print('读入槽位        = %d' % len(rows))
    print('唯一函数地址    = %d' % len(by_addr))
    print('其中 Ghidra 函数入口 = %d' % sum(1 for a in by_addr if a in entries))
    print('库数            = %d' % len(stats))
    print()
    print('--- 唯一地址数 top 10 库 ---')
    per = collections.Counter()
    seen = set()
    for lib, slot, addr, kind in sorted(rows):
        if (lib, addr) not in seen:
            seen.add((lib, addr)); per[lib] += 1
    for lib, n in per.most_common(10):
        print('  %-16s %d' % (lib, n))
    print()
    print('已写出:')
    print('  %s' % os.path.relpath(OUT_TSV, BASE))
    print('  %s' % os.path.relpath(OUT_SYM, BASE))


if __name__ == '__main__':
    main()
