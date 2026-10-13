#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strict helpers shared by the tools: safe names, safe child paths, atomic writes.

Why this module exists
----------------------
Several tools turn a **repo-derived name** into a filesystem path: a symbol from
`config/symbol_addrs.txt` or the workqueue, a ledger line, or a jump-table name. A name that
holds `/` or `..` escapes the directory the tool meant to write to (R30 finding D8); the same
names are interpolated into generated C and into the linker script. Several other tools
rewrite tracked files in place, so a crash or a kill truncates them (R30 findings D12).

Both are avoidable with a small, shared rule set. `tools/maintainer/project/auto_match_*`,
`tools/project/*` and `tools/report/*` import this module, so there is one implementation.

工具共用的严格助手：安全名字、安全子路径、原子写。

为什么需要：多个工具把**仓库派生的名字**（`symbol_addrs.txt`/工作队列的符号、台账行、
jtbl 表名）拼成文件路径；含 `/` 或 `..` 的名字会逃出目标目录（R30 D8）；同一个名字还会被插进
生成的 C 与链接脚本。另一些工具就地改写 tracked 文件，崩溃或被杀会截断文件（R30 D12）。
两条都能用一套共用规则堵住；`auto_match_*`、`tools/project/*`、`tools/report/*` 都 import 本模块。

Self-test: python3 tools/check/test_at2_io.py
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

# A symbol name we are willing to turn into a path component. This is deliberately stricter
# than "valid C identifier": it forbids `/`, `..`, spaces, quotes, `)` and non-ASCII, which are
# exactly the characters that break out of a path or a generated source line.
# 只接受可安全作为路径分量的符号名：比「合法 C 标识符」更严，禁掉 `/`、`..`、空白、引号、`)` 与非 ASCII。
SYMBOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


def symbol_ok(name: object) -> bool:
    """True when `name` is a plain symbol name that is safe as one path component."""
    return isinstance(name, str) and bool(SYMBOL_RE.match(name))


def safe_symbol(name: str, *, what: str = "symbol") -> str:
    """Return `name` when it is safe; raise ValueError otherwise.

    合法则原样返回，否则抛 ValueError（消息里带原始值与规则）。
    """
    if not symbol_ok(name):
        raise ValueError(
            f"unsafe {what} name: {name!r} (expected a match of {SYMBOL_RE.pattern})")
    return name


def safe_child(root: Path, name: str, suffix: str = "", *, what: str = "symbol") -> Path:
    """Return the path `root/<name><suffix>`, proven to stay inside `root`.

    Raises ValueError for an unsafe name or a path that resolves outside `root` (for example
    through a symlinked component).

    返回 `root/<name><suffix>`，并证明它仍在 `root` 之内；名字不安全或解析后越界即抛 ValueError。
    """
    safe_symbol(name, what=what)
    base = Path(root).resolve()
    cand = (base / f"{name}{suffix}").resolve()
    if cand != base and base not in cand.parents:
        raise ValueError(f"{what} {name!r} escapes {base}")
    return cand


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write `data` to `path` through a same-directory temporary file and os.replace().

    同目录临时文件 + os.replace()：要么看到旧内容，要么看到完整的新内容。
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_text(path: Path, text: str) -> None:
    """`atomic_write_bytes` for UTF-8 text."""
    atomic_write_bytes(path, text.encode("utf-8"))


def atomic_copy(src: Path, dst: Path) -> None:
    """Copy a file atomically (read once, then one atomic replace)."""
    atomic_write_bytes(dst, Path(src).read_bytes())


def guarded_json_load(path: Path):
    """Return the parsed JSON, or None when the file is missing or not valid JSON.

    解析失败返回 None（调用方据此把该条当「没有评分」跳过，而不是让整批抛异常）。
    """
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
