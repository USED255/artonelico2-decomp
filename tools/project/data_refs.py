#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure the population that the mixed-build data gate excludes (O-01 (1)) and write a pool TSV.

Why this tool exists
--------------------
The gate refuses a C object that manufactures data the linker script cannot place. The
documented gap did not say **how many** functions that affects, so the work could not be
ranked. This tool answers it with the asm tree and the baseline link only: for every asm
block, list its `%lo(NAME)` data references, resolve NAME against the baseline symbol table,
and classify the bytes at that address as a string literal or other data.

The output is machine-derived (do not commit it): a TSV with one row per symbol.

Columns
  sym            the function
  matched        1 when `config/matched_symbols.txt` already has the symbol
  size           block size in bytes (4 x instruction lines)
  refs_total     every `%lo(NAME)` reference in the block
  refs_string    references whose bytes look like a printable, NUL-terminated string
  refs_other     references to other data (pointer tables, numeric arrays, ...)
  refs_gp        `%gp_rel(NAME)` references (the weak-definition path already handles these)
  refs_unknown   references that do not resolve in the baseline symbol table
  names          the first three referenced names, comma separated

Usage
  python3 tools/project/data_refs.py --asm-dir asm/cod --image build/SLPS_258.19.elf \\
      --ledger config/matched_symbols.txt --out .tmp/data_gate_pool.tsv [--summary]

量化混合构建数据闸门排除了多大一片（O-01 ①），并写出候选池 TSV。

为什么需要：闸门会拒收「自产数据」的 C 对象，但台账没写**影响多少个函数**，无法排优先级。
本工具只用 asm 树与基线链接回答：逐块列出 `%lo(NAME)` 数据引用，用基线符号表解出地址，
再按该地址的字节判断是字符串字面量还是其它数据。

产物是机器派生数据（不要入库）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data_patch as dp  # noqa: E402

GLABEL_RE = re.compile(r"^\s*glabel\s+(\S+)")
ALABEL_RE = re.compile(r"^\s*alabel\s+(\S+)")
ENDLABEL_RE = re.compile(r"^\s*endlabel\s+(\S+)")
INS_RE = re.compile(r"/\*.*?\*/\s+\S")
GP_RE = re.compile(r"%gp_rel\(\s*([A-Za-z_][A-Za-z0-9_.]*)")


def blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """[(symbol, start_line, end_line_exclusive)] for every glabel/alabel block.

    每个 glabel/alabel 块的 (符号, 起始行, 结束行(不含))。
    """
    starts: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = GLABEL_RE.match(line) or ALABEL_RE.match(line)
        if m:
            starts.append((m.group(1), i))
    out = []
    for k, (sym, i) in enumerate(starts):
        end = starts[k + 1][1] if k + 1 < len(starts) else len(lines)
        for j in range(i + 1, end):
            m = ENDLABEL_RE.match(lines[j])
            if m and m.group(1) == sym:
                end = j + 1
                break
        out.append((sym, i, end))
    return out


def looks_like_string(data: bytes) -> bool:
    """A printable, NUL-terminated byte run.

    The first version accepted any byte in 9..126, which made numeric tables and pointer arrays
    "strings" (measured: `D_003AE5E0` = `16 00 ...` and `jtbl_009009FC` = `2C 50 12 00` both
    passed). Control bytes below 0x20 are not text, so they are rejected now, and a NUL must
    appear inside the window (a byte run without a terminator is not a C string).

    可打印且以 NUL 结尾的字节串。
    第一版把 9..126 全算可打印，于是数字表和指针数组都被当成字符串（实测：`D_003AE5E0`
    = `16 00 ...`、`jtbl_009009FC` = `2C 50 12 00` 都通过了）。0x20 以下的控制字节不是文本，
    现在拒绝；同时要求 NUL 出现在窗口内（没有终止符的字节串不是 C 字符串）。
    """
    if not data:
        return False
    nul = data.find(b"\0")
    if nul < 0:
        return False                 # no terminator inside the window
    body = data[:nul]
    if not body:
        return False
    if len(body) < 4:
        return False                 # "`\rV" style struct prefixes are not text
    if not all(b == 10 or 0x20 <= b <= 0x7E for b in body):
        return False
    return any(0x21 <= b <= 0x7E for b in body)


def run(asm_dir: Path, image: Path, ledger: Path | None) -> list[dict]:
    """Classify every symbol's data references. 分类每个符号的数据引用。"""
    img = dp.Image(image)
    isyms = img.symbols()
    matched: set[str] = set()
    if ledger and ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                matched.add(line.split()[0])
    rows = []
    for p in sorted(asm_dir.glob("*.s")):
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        for sym, start, end in blocks(lines):
            body = lines[start:end]
            refs = [m.group(1) for line in body for m in dp.LO_RE.finditer(line)]
            gp = [m.group(1) for line in body for m in GP_RE.finditer(line)]
            size = 4 * sum(1 for line in body if INS_RE.search(line))
            strings = other = unknown = 0
            names = []
            for name in refs:
                hit = isyms.get(name)
                if hit is None:
                    unknown += 1
                    continue
                val, sz, typ, shndx = hit
                if typ == dp.STT_FUNC:
                    continue                      # a function address, not data
                if name.startswith("jtbl_"):
                    other += 1                # a jump table is data, never a literal
                    continue
                if len(names) < 3:
                    names.append(name)
                blob = img.read(val, max(1, min(sz or 256, 256))) or b""
                if looks_like_string(blob):
                    strings += 1
                else:
                    other += 1
            rows.append({"sym": sym, "matched": 1 if sym in matched else 0, "size": size,
                         "refs_total": len(refs), "refs_string": strings, "refs_other": other,
                         "refs_gp": len(gp), "refs_unknown": unknown, "names": ",".join(names)})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure the C-made-data population (O-01 (1))")
    ap.add_argument("--asm-dir", default="asm/cod")
    ap.add_argument("--image", default="build/SLPS_258.19.elf",
                    help="the baseline link (build.sh output): data symbols and bytes")
    ap.add_argument("--ledger", default="config/matched_symbols.txt")
    ap.add_argument("--out", default="")
    ap.add_argument("--summary", action="store_true", help="print the aggregate only, write no TSV")
    a = ap.parse_args()
    rows = run(Path(a.asm_dir), Path(a.image), Path(a.ledger) if a.ledger else None)
    unm = [r for r in rows if not r["matched"] and r["refs_total"]]
    str_unm = [r for r in unm if r["refs_string"]]
    print("symbols analysed: %d" % len(rows))
    print("unmatched with data references: %d (%d bytes)" % (len(unm), sum(r["size"] for r in unm)))
    print("  of which reference a string literal: %d (%d bytes)" % (len(str_unm), sum(r["size"] for r in str_unm)))
    print("  other-data only: %d" % (len(unm) - len(str_unm)))
    if not a.summary and a.out:
        cols = ["sym", "matched", "size", "refs_total", "refs_string", "refs_other", "refs_gp", "refs_unknown", "names"]
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            f.write("\t".join(cols) + "\n")
            for r in rows:
                f.write("\t".join(str(r[c]) for c in cols) + "\n")
        print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
