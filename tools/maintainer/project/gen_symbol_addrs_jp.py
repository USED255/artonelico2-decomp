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
from pathlib import Path

# Make the shared tools in tools/project importable.  让 tools/project 的共享工具可被导入。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project"))
import at2_io  # noqa: E402  safe symbols / atomic writes


def load_functions(path):
    """Return (addr -> (name, size_bytes), number of malformed rows).

    A malformed row (a non-hex address or a non-integer size) is counted, not silently
    swallowed; `main` reports the count at the end.

    返回 (addr -> (name, size_bytes), 解析失败行数)。

    解析失败的行（地址非十六进制 / size 非整数）会被计数而不是悄悄吞掉，`main` 最后
    统一报告。
    """
    out = {}
    skipped = 0
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) < 3 or p[0] == "addr":
            continue
        try:
            out[int(p[0], 16)] = (p[1], int(p[2]))
        except ValueError:
            skipped += 1
    return out, skipped


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
    if len(sys.argv) < 4:
        print("usage: python3 gen_symbol_addrs_jp.py <functions.tsv> <hle_tables.txt> <out.txt>",
              file=sys.stderr)
        return 2
    funcs_path, tables_path, out_path = sys.argv[1:4]
    funcs, skipped_rows = load_functions(funcs_path)
    erx = load_erx_names(tables_path)

    lines = []
    named = 0
    unsafe = 0
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
        try:
            # A malformed name would inject arbitrary text into the symbol table (D4).
            # 名字不合法会把任意文本注入符号表（D4）。
            at2_io.safe_symbol(name, what="symbol")
        except ValueError as e:
            unsafe += 1
            print("  skip unsafe symbol: %s" % e, file=sys.stderr)
            continue
        used[name] = addr
        lines.append("%s = 0x%08x; // type:func size:0x%x" % (name, addr, size))

    extra = [a for a in erx if a not in funcs]
    # The output can be a tracked config/symbol_addrs.txt; write it atomically (D12).
    # 输出可能是 tracked 的 config/symbol_addrs.txt，用原子写（D12）。
    at2_io.atomic_write_text(out_path, "\n".join(lines) + "\n")

    print("function symbols   = %d" % len(funcs))
    print("  named/anchor     = %d (%.1f%%)" % (named, 100 * named / max(len(funcs), 1)))
    print("  placeholder only = %d" % (len(funcs) - named))
    if skipped_rows:
        print("  malformed input rows skipped = %d" % skipped_rows)
    if unsafe:
        print("  unsafe symbols skipped       = %d" % unsafe)
    print("erx unique addrs   = %d (not in the Ghidra function list = %d)" % (len(erx), len(extra)))
    print("written            = %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
