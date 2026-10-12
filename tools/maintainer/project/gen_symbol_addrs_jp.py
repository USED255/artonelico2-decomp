#!/usr/bin/env python3
"""Generate symbol_addrs.txt for splat (version independent).

This script uses the same logic as tools/maintainer/build/gen_symbol_addrs.py.
Only the two input paths are parameters. One copy of the code serves the US
version (regression self-test) and the JP version (main target of this task).

    Input 1: Ghidra function list <name>.functions.tsv  (addr / name / size_bytes ...)
    Input 2: .erx.lib export registry text (made by tools/maintainer/project/erx_tables.py)

Name priority: the library_slot name from `.erx.lib` wins over the Ghidra name
FUN_xxxxxxxx (which becomes func_xxxxxxxx).
An address in `.erx.lib` that is not a function entry gets **no** `type:label`
entry (see P-06).

Self-test: run this script on the US input. The output must be byte-identical to
routeb/config/symbol_addrs.txt.

生成 splat 用的 symbol_addrs.txt（版本无关）。

与 tools/maintainer/build/gen_symbol_addrs.py 的逻辑完全一致，只把两个输入路径参数化，
以便同一份代码服务美版（回归自检）与日版（本次主目标）：

    输入 1: Ghidra 函数清单 <name>.functions.tsv  (addr / name / size_bytes ...)
    输入 2: .erx.lib 导出注册表文本（tools/maintainer/project/erx_tables.py 生成）

命名优先级：`.erx.lib` 的 库_槽号 > Ghidra 的 FUN_xxxxxxxx（转 func_xxxxxxxx）。
`.erx.lib` 里非函数入口的地址**不写入** `type:label`（见 P-06）。

自检：用美版输入跑本脚本，输出应与 routeb/config/symbol_addrs.txt 逐字节一致。

用法: python3 gen_symbol_addrs_jp.py <functions.tsv> <hle_tables.txt> <out.txt>
"""
import re
import sys


def load_functions(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) < 3 or p[0] == "addr":
            continue
        try:
            out[int(p[0], 16)] = (p[1], int(p[2]))
        except ValueError:
            pass
    return out


def load_erx_names(path):
    """Return addr -> primary name (library_slot) from the `.erx.lib` export registry.

    Keep the first occurrence of each address.

    `.erx.lib` 导出注册表：addr -> 主名（库_槽号），按首次出现去重。
    """
    cur, rows = None, []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^=== library (\S+)", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^\s+(\d+)\s+(0x[0-9a-f]+)\s+(\S+)", line)
        if m and cur and m.group(3) != "none":
            rows.append((cur, int(m.group(1)), int(m.group(2), 16)))
    seen, out = set(), {}
    for lib, slot, addr in rows:
        if addr in seen:
            continue
        seen.add(addr)
        out[addr] = "%s_%d" % (lib, slot)
    return out


def main():
    funcs_path, tables_path, out_path = sys.argv[1:4]
    funcs = load_functions(funcs_path)
    erx = load_erx_names(tables_path)

    lines = []
    named = 0
    used = {}
    for addr in sorted(funcs):
        gname, size = funcs[addr]
        if addr in erx:
            name = erx[addr]
            named += 1
        elif gname.startswith("FUN_"):
            name = "func_%08x" % addr
        else:
            name = gname
            named += 1
        if name in used:
            name = "%s_%08x" % (name, addr)
        used[name] = addr
        lines.append("%s = 0x%08x; // type:func size:0x%x" % (name, addr, size))

    extra = [a for a in erx if a not in funcs]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("function symbols   = %d" % len(funcs))
    print("  named/anchor     = %d (%.1f%%)" % (named, 100 * named / max(len(funcs), 1)))
    print("  placeholder only = %d" % (len(funcs) - named))
    print("erx unique addrs   = %d (not in the Ghidra function list = %d)" % (len(erx), len(extra)))
    print("written            = %s" % out_path)


if __name__ == "__main__":
    main()
