#!/usr/bin/env python3
"""Regression tests for the ledger parser and for the affected set of the delta check. The test needs no build.

This test covers the bugs that the project fixed on 2026-10-06:
  - A ledger line with an end-of-line comment or with a second column must be recognized.
    Before the fix, `make delta` treated the whole line as a symbol name and skipped
    2,678 of 2,688 entries.
  - An unregistered file must land in `unregistered`, and it must not disappear silently.
  - When a source file name differs from the symbol name, the source name must find the
    symbol. One source with several symbols must return all of them.

Usage: python3 tools/check/test_matched_ledger.py

台账解析与增量检查「受影响集合」的回归测试（纯 Python，不需要构建）。

覆盖 2026-10-06 修掉的 bug：
  · 带行内注释 / 带第二列的台账行必须能被识别（此前 `make delta` 把整行当符号名，2,678/2,688 被跳过）；
  · 未登记文件必须显式落在 unregistered，而不是静默消失；
  · 一个源文件名与符号名不同时，按源名也能找到符号；一个源多个符号要全部返回。
用法：python3 tools/check/test_matched_ledger.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "build"))
import matched_ledger as ml  # noqa: E402

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


# 1) Parsing: a comment, a second column, an empty line, and a comment-only line.
# 1) 解析：注释、第二列、空行、纯注释行。
tmp = ROOT / ".tmp" / "ledger_test"
tmp.mkdir(parents=True, exist_ok=True)
led = tmp / "matched_symbols.txt"
led.write_text("""# ledger: <symbol> [<source-basename>]   # <tag>
func_001b6030    # ret_bool
baseelf_15
LibcStdio_31\tLibcStdio_31_c\t# multi
# a full-line comment
func_multi_a   shared_src   # one
func_multi_b   shared_src   # one

""", encoding="utf-8")
idx = ml.parse_ledger(led)
check("a line with a comment resolves to a symbol", "func_001b6030" in idx, str(list(idx)[:3]))
check("the parser reads the comment as a tag", idx.get("func_001b6030", ("", ""))[1] == "ret_bool")
check("with no second column, the source name falls back to the symbol name", idx.get("baseelf_15") == ("baseelf_15", ""))
check("the second column gives a different source name", idx.get("LibcStdio_31", ("", ""))[0] == "LibcStdio_31_c")
check("entry count = 5", len(idx) == 5, str(len(idx)))
total, stub, distinct = ml.entry_stats(led)
check("entry statistics", (total, stub, distinct) == (5, 0, 5), f"{total},{stub},{distinct}")

# 2) The affected set.
# 2) 受影响集合。
hit, unr = ml.resolve_changed(idx, ["src/matched/func_001b6030.c"], "src/matched")
check("a ledger line with a comment hits (the old code failed here)", hit == {"func_001b6030"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/baseelf_15.c"], "src/matched")
check("a line with no second column hits", hit == {"baseelf_15"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/LibcStdio_31_c.c"], "src/matched")
check("the second-column source name hits", hit == {"LibcStdio_31"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/shared_src.c"], "src/matched")
check("one source with several symbols returns all of them", hit == {"func_multi_a", "func_multi_b"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/brand_new.c"], "src/matched")
check("an unregistered file lands in unregistered (it does not disappear)", hit == set() and unr == ["src/matched/brand_new.c"])

# 3) The real ledger: every registered C source must resolve to a symbol (the bug regression metric).
# 3) 真实台账：每个已登记的 C 源都必须能解析到符号（bug 回归指标）。
real = ROOT / "config" / "matched_symbols.txt"
ridx = ml.parse_ledger(real)
srcs = sorted((ROOT / "src" / "matched").glob("*.c"))
miss = [p.name for p in srcs if not ml.resolve_changed(ridx, [f"src/matched/{p.name}"], "src/matched")[0]]
check(f"the real ledger resolves {len(ridx)} symbols", len(ridx) > 2000, str(len(ridx)))
check(f"all {len(srcs)} .c files hit a symbol (missing {len(miss)})", not miss, str(miss[:5]))

print()
if fails:
    print(f"FAIL: {len(fails)} checks failed: {fails}")
    sys.exit(1)
print("all checks passed")
