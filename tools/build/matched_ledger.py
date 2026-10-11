#!/usr/bin/env python3
"""The only parser for `config/matched_symbols.txt`. The report generator and the incremental check share it.

Ledger format (see the file header comment):
    <symbol> [<source-basename>]        # <tag>          <- '#' starts an inline comment; the second column is optional
  * If the second column is absent, the source basename equals the symbol name.
  * One source file can provide several symbols. Several functions of one .c
    file can appear in the ledger.

Fix 2026-10-06: the incremental check used the whole line (comment and second
column included) as the symbol name. A ledger line with a comment never
matched. Then `make delta` skipped most functions, but it still reported "all
100 percent".

`config/matched_symbols.txt` 的唯一解析实现（报告生成器与增量检查共用）。

台账格式：`<symbol> [<source-basename>]  # <tag>`；`#` 起行内注释，第二列可省略。
省略第二列时源文件基名等于符号名；一个源文件可以提供多个符号。

2026-10-06 修复：此前增量检查把整行（含注释与第二列）当成符号名，
带注释的台账行一律匹配不上，`make delta` 会跳过绝大多数函数却仍报「全部 100%」。
"""
from __future__ import annotations
from pathlib import Path

STUB_PREFIX = "stub_"


def parse_ledger(path: Path) -> dict[str, tuple[str, str]]:
    """Return `{symbol: (source_basename, tag)}`. The tag is the inline comment after `#`, stripped.

    返回 `{symbol: (source_basename, tag)}`；tag = 行内注释去掉 `#` 后的原文（已 strip）。
    """
    out: dict[str, tuple[str, str]] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        body, _, comment = raw.partition("#")
        body = body.strip()
        if not body:
            continue
        parts = body.split()
        sym = parts[0]
        src = parts[1] if len(parts) > 1 else sym
        out[sym] = (src, comment.strip())
    return out


def entry_stats(path: Path) -> tuple[int, int, int]:
    """Return entry statistics: `(total entries, stub entries, distinct non-stub symbols)`.

    条目级统计：`(总条目, stub 条目, 去重后的非 stub 符号数)`。
    """
    total = stub = 0
    non_stub: set[str] = set()
    if not path.exists():
        return 0, 0, 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        body, _, comment = raw.partition("#")
        body = body.strip()
        if not body:
            continue
        total += 1
        if comment.strip().startswith(STUB_PREFIX):
            stub += 1
        else:
            non_stub.add(body.split()[0])
    return total, stub, len(non_stub)


def by_source(index: dict[str, tuple[str, str]]) -> dict[str, set[str]]:
    """Return source basename -> all symbols of that source. One source can hold several symbols.

    源文件基名 → 该源提供的全部符号（一个源可以多个符号）。
    """
    out: dict[str, set[str]] = {}
    for sym, (src, _tag) in index.items():
        out.setdefault(src, set()).add(sym)
    return out


def resolve_changed(index: dict[str, tuple[str, str]], changed_files: list[str],
                    path_prefix: str = "") -> tuple[set[str], list[str]]:
    """Map each changed matched source file to the symbols that need one-by-one comparison.

    * A match is `<sym>.c` against a symbol name, or against the source basename
      in the second ledger column. The two can differ.
    * An unregistered new file (neither a symbol name nor a source name) goes to
      `unregistered`. The caller counts it explicitly.

    把「改动过的匹配源文件」映射成「需要逐一比对的符号」。
    匹配规则：`<sym>.c` 命中符号名，或命中台账第二列的源基名。
    未登记的新文件返回在 unregistered 里，由调用方显式计数。
    """
    srcs = by_source(index)
    hit: set[str] = set()
    unregistered: list[str] = []
    for rel in changed_files:
        stem = Path(rel).stem
        found = set()
        if stem in index:
            found.add(stem)
        found |= srcs.get(stem, set())
        if found:
            hit |= found
        else:
            unregistered.append(rel)
    return hit, unregistered
