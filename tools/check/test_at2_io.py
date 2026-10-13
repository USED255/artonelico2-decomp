#!/usr/bin/env python3
"""Tests for tools/project/at2_io.py. No toolchain, no build, no network.

These helpers guard the R30 findings D8 (repo-derived names escaping the output directory) and
D12 (in-place rewrites of tracked files). The test pins the accept/reject rule and the atomic
write contract, including the "failure leaves the old content alone" path.

Usage: python3 tools/check/test_at2_io.py

at2_io.py 的测试（不需要工具链/构建/网络）。守护 R30 的 D8（仓库派生名字逃出输出目录）与
D12（就地改写 tracked 文件）：固定白名单规则与原子写契约，含「失败不动旧内容」这条。
用法：python3 tools/check/test_at2_io.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "project"))
import at2_io as aio  # noqa: E402

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


WORK = ROOT / ".tmp" / "at2_io_test"
shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True, exist_ok=True)

print("[1] symbol_ok accepts plain symbol names")
for name in ("func_00100000", "baseelf_15", "LibcStdio_31_c", "jtbl_00965B58", "_x", "a.b", "A1"):
    check(f"ok: {name!r}", aio.symbol_ok(name))

print("[2] symbol_ok rejects everything that can escape a path or a source line")
for name in ("", "a/b", "../x", "..", "a b", "a)b", "a;b", "日本", ".hidden", "a\tb",
             'a"b', "a'b", "a#b", "a,b", None, 7, "a\\b"):
    check(f"reject: {name!r}", not aio.symbol_ok(name))

print("[3] safe_symbol raises a clear ValueError")
try:
    aio.safe_symbol("../evil", what="ledger symbol")
    check("safe_symbol refuses a traversal name", False, "no error")
except ValueError as exc:
    check("safe_symbol refuses a traversal name", "ledger symbol" in str(exc) and "evil" in str(exc),
          str(exc))

print("[4] safe_child stays inside the root")
root = WORK / "repo" / "src" / "matched"
root.mkdir(parents=True, exist_ok=True)
p = aio.safe_child(root, "func_00100000", ".c")
check("a plain name resolves below the root", p == (root / "func_00100000.c").resolve(), str(p))
for name, suffix in (("..", "/x.c"), ("../evil", ".c"), ("a/b", ".c"), ("", ".c")):
    try:
        aio.safe_child(root, name, suffix)
        check(f"safe_child refuses {name!r}{suffix!r}", False, "no error")
    except ValueError:
        check(f"safe_child refuses {name!r}{suffix!r}", True)

# A symlinked component inside the root must not be usable to escape it.
outside = WORK / "outside"
outside.mkdir(parents=True, exist_ok=True)
link = root / "link"
if not link.exists():
    os.symlink(outside, link)
try:
    aio.safe_child(root, "link", "/escaped.c")
    check("safe_child refuses a symlinked escape", False, "no error")
except ValueError:
    check("safe_child refuses a symlinked escape", True)

print("[5] atomic_write_text writes whole content and leaves no temporary file")
dst = WORK / "a" / "b" / "file.txt"
aio.atomic_write_text(dst, "first\n")
check("parents are created", dst.read_text(encoding="utf-8") == "first\n")
aio.atomic_write_text(dst, "second\n")
check("an existing file is replaced", dst.read_text(encoding="utf-8") == "second\n")
leftovers = [q.name for q in dst.parent.iterdir() if q.name.startswith(".file.txt")]
check("no temporary file is left behind", not leftovers, str(leftovers))

print("[6] a failing write leaves the previous content untouched")
victim = WORK / "victim.txt"
aio.atomic_write_text(victim, "keep me\n")
try:
    aio.atomic_write_bytes(victim / "child", b"x")   # parent is a file -> mkdir/replace fails
    check("a write under a file path fails", False, "no error")
except OSError:
    check("a write under a file path fails", True)
check("the previous content survives", victim.read_text(encoding="utf-8") == "keep me\n")
check("no temporary file is left by the failure",
      not [q.name for q in victim.parent.iterdir() if q.name.startswith(".child")])

print("[7] atomic_copy copies bytes")
src = WORK / "src.bin"
src.write_bytes(b"\x00\x01\x02")
cp = WORK / "copy.bin"
aio.atomic_copy(src, cp)
check("the copy is byte-identical", cp.read_bytes() == b"\x00\x01\x02")

print("[8] guarded_json_load never raises")
good = WORK / "good.json"
good.write_text(json.dumps({"a": 1}), encoding="utf-8")
bad = WORK / "bad.json"
bad.write_text("{not json", encoding="utf-8")
check("a valid file parses", aio.guarded_json_load(good) == {"a": 1})
check("a broken file returns None", aio.guarded_json_load(bad) is None)
check("a missing file returns None", aio.guarded_json_load(WORK / "nope.json") is None)

shutil.rmtree(WORK, ignore_errors=True)

print(f"\n{len(fails)} failed" if fails else "\nall at2_io tests passed")
sys.exit(1 if fails else 0)
