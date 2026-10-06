#!/usr/bin/env python3
"""台账解析与增量检查「受影响集合」的回归测试（纯 Python，不需要构建）。

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


# 1) 解析：注释、第二列、空行、纯注释行
tmp = ROOT / ".tmp" / "ledger_test"
tmp.mkdir(parents=True, exist_ok=True)
led = tmp / "matched_symbols.txt"
led.write_text("""# 台账：<symbol> [<source-basename>]   # <tag>
func_001b6030    # ret_bool
baseelf_15
LibcStdio_31\tLibcStdio_31_c\t# multi
# 整行注释
func_multi_a   shared_src   # one
func_multi_b   shared_src   # one

""", encoding="utf-8")
idx = ml.parse_ledger(led)
check("带注释的行能解析出符号", "func_001b6030" in idx, str(list(idx)[:3]))
check("注释被当作 tag", idx.get("func_001b6030", ("", ""))[1] == "ret_bool")
check("无第二列时源名回退为符号名", idx.get("baseelf_15") == ("baseelf_15", ""))
check("第二列给出不同源名", idx.get("LibcStdio_31", ("", ""))[0] == "LibcStdio_31_c")
check("条目数 = 5", len(idx) == 5, str(len(idx)))
total, stub, distinct = ml.entry_stats(led)
check("条目级统计", (total, stub, distinct) == (5, 0, 5), f"{total},{stub},{distinct}")

# 2) 受影响集合
hit, unr = ml.resolve_changed(idx, ["src/matched/func_001b6030.c"], "src/matched")
check("带注释的台账行能命中（旧代码在此失败）", hit == {"func_001b6030"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/baseelf_15.c"], "src/matched")
check("无第二列的行能命中", hit == {"baseelf_15"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/LibcStdio_31_c.c"], "src/matched")
check("按第二列源名命中", hit == {"LibcStdio_31"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/shared_src.c"], "src/matched")
check("一个源多个符号全部返回", hit == {"func_multi_a", "func_multi_b"}, str(hit))
hit, unr = ml.resolve_changed(idx, ["src/matched/brand_new.c"], "src/matched")
check("未登记文件落入 unregistered（不静默）", hit == set() and unr == ["src/matched/brand_new.c"])

# 3) 真实台账：每个已登记的 C 源都必须能解析到符号（bug 回归指标）
real = ROOT / "config" / "matched_symbols.txt"
ridx = ml.parse_ledger(real)
srcs = sorted((ROOT / "src" / "matched").glob("*.c"))
miss = [p.name for p in srcs if not ml.resolve_changed(ridx, [f"src/matched/{p.name}"], "src/matched")[0]]
check(f"真实台账解析出 {len(ridx)} 个符号", len(ridx) > 2000, str(len(ridx)))
check(f"{len(srcs)} 个 .c 全部能命中符号（缺失 {len(miss)}）", not miss, str(miss[:5]))

print()
if fails:
    print(f"❌ {len(fails)} 项失败：{fails}")
    sys.exit(1)
print("✅ 全部通过")
