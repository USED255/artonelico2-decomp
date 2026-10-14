#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ee-gcc-anchor —— bind a rule to the **shipped** ee-gcc 3.2 compiler binary.

## Why this tool exists

The shipped `ee-gcc 3.2-ee-040921` `cc1` is **not stripped and carries DWARF**. That makes the
factory binary a first-class source of evidence: a line number, a struct layout, or a floating
constant can be read straight out of it. Two things are true of the factory binary and are **not**
visible in a naive reading of mainline gcc-3.2.3 (measured 2026-10-14):

* `struct allocno` is **144 B** and its `HARD_REG_SET` member step is **24 B (192 bits)**, because
  the EE register file is wider (VU0 / ACC classes) than the mainline MIPS one;
* the binary embeds `config/mips/mips5900.c`, which mainline 3.2.3 does not have at all.

The same method also **corrects wrong beliefs about mainline itself**. Worked example: the shipped
`allocno_compare` multiplies by the double **10.0**, while a reading of the comment in
`global.c` ("Multiplying this by `10000/REG_FREQ_MAX`") suggests the factor is 1. Reading
`regs.h:79` settles it — mainline says `#define REG_FREQ_MAX 1000`, so `10000 / REG_FREQ_MAX == 10`
and the binary matches mainline exactly. **Read the `#define`, not the comment.**

So every rule in the handbook carries two anchors: `source_anchor` (mainline file and line) and
`binary_anchor` (symbol, address, constants). This tool produces the second one.

## What it reads

* `nm`          — symbol to address (`allocno_compare` at `0x081ab288`)
* `addr2line`   — address to `file:line` (`global.c:789`)
* `objdump -d --line-numbers` — instructions bound to source lines
* `objdump -s`  — raw bytes at an address, decoded as ints / floats
* `readelf --debug-dump=info` — struct layout (member offsets and declaration lines)

## Usage

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1

python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" addr 0x081ab288
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" selftest
```

`--cc1` defaults to `$EE_CC1`, then to the known local install path. `--json` prints machine
readable output. Exit codes: 0 = ok, 1 = assertion failed, 2 = usage / input error.

No game content is read or printed: this tool only touches the compiler binary.
"""

# 中文摘要
# ---------------------------------------------------------------------------
# 出厂 `ee-gcc 3.2-ee-040921` 的 `cc1` **未 strip 且带 DWARF**，因此可以直接读出行号、
# 结构布局与常量。出厂二进制有两件事与「朴素的 mainline 读法」不同（2026-10-14 实测）：
#   ① `struct allocno` 是 **144 B**，`HARD_REG_SET` 成员步长 **24 B（192 位）**（EE 寄存器类更宽）；
#   ② 二进制内嵌 `config/mips/mips5900.c`，mainline 3.2.3 没有这个文件。
# 同一套方法也能**纠正对 mainline 本身的错误印象**。实例：出厂 `allocno_compare` 乘的是
# double **10.0**，而读 `global.c` 注释（「Multiplying this by 10000/REG_FREQ_MAX」）会以为因子是 1。
# 读 `regs.h:79` 结清：mainline 就是 `#define REG_FREQ_MAX 1000` ⇒ `10000 / REG_FREQ_MAX == 10`，
# 二进制与 mainline **完全一致**。=> **读 `#define`，不要读注释**。
# 本工具只读编译器二进制，不碰游戏内容。

from __future__ import annotations

import argparse
import json
import os
import re
import struct as structlib
import subprocess
import sys
from pathlib import Path

DEFAULT_CC1 = os.environ.get(
    "EE_CC1",
    str(Path.home() / "eecc" / "ee-gcc3.2-040921" / "lib" / "gcc-lib" / "ee" / "3.2-ee-040921" / "cc1"),
)
# readelf prints localised section names and tags; force the C locale.
_C_ENV = {**os.environ, "LC_ALL": "C", "LANG": "C", "LANGUAGE": "C"}

# Anchors verified on 2026-10-14 against the shipped cc1 (see R33 §4.2).
KNOWN_ANCHORS = [
    ("allocno_compare", "global.c", 789, 0x081AB288,
     "global allocation priority order (allocno_compare)"),
    ("dump_conflicts", "global.c", 2265, 0x081AF134,
     "printer behind `;; N regs to allocate:`"),
    ("find_reg", "reload1.c", 1685, 0x08134570,
     "colouring / spill decision"),
    ("schedule_block", "haifa-sched.c", 2039, 0x081B15D8,
     "instruction scheduling"),
    ("dbr_schedule", "reorg.c", 3571, 0x081CD510,
     "delay-slot scheduling"),
]
KNOWN_STRUCT = ("allocno", 144)
# `allocno_compare` loads this double and multiplies by it: mainline's `10000 / REG_FREQ_MAX`
# with `REG_FREQ_MAX == 1000` (regs.h:79). Change the tool if a future toolchain changes it.
KNOWN_CONST = (0x0821E360, "double", 10.0)

_DIE_RE = re.compile(r"^\s*<(\d+)><([0-9a-f]+)>:\s+Abbrev Number:\s+\d+\s+\((\w+)\)")
_ATTR_RE = re.compile(r"^\s*<[0-9a-f]+>\s+(DW_AT_\w+)\s*:\s*(.*?)\s*$")
_PLUS_UCONST_RE = re.compile(r"DW_OP_plus_uconst:\s*(\d+)")
_DISASM_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(.*)$")


class ToolError(Exception):
    """A tool ran, but the input cannot be satisfied."""


def _run(cmd: list[str]) -> str:
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, env=_C_ENV, check=False)
    except FileNotFoundError as exc:  # binutils missing
        raise ToolError(f"command not found: {cmd[0]}") from exc
    if done.returncode != 0:
        raise ToolError(f"{' '.join(cmd[:2])} failed: {done.stderr.strip()[:200]}")
    return done.stdout


def require_cc1(path: str) -> Path:
    p = Path(path).expanduser()
    if not p.is_file():
        raise ToolError(
            f"cc1 not found: {p}\n"
            "pass --cc1, or set EE_CC1, or install the EE toolchain "
            "(the file lives at <toolchain>/lib/gcc-lib/ee/3.2-ee-040921/cc1)"
        )
    return p


# ---------------------------------------------------------------- symbols


def nm_symbols(cc1: Path) -> list[tuple[str, str, int]]:
    """Return `(name, type, address)` for every defined symbol. `-P` keeps the output stable."""
    out = _run(["nm", "-P", "--defined-only", str(cc1)])
    rows: list[tuple[str, str, int]] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            name, typ, value = parts[0], parts[1], parts[2]
            try:
                rows.append((name, typ, int(value, 16)))
            except ValueError:
                continue
    return rows


def lookup_symbol(rows: list[tuple[str, str, int]], name: str) -> list[tuple[str, str, int]]:
    return [r for r in rows if r[0] == name]


def symbol_at(rows: list[tuple[str, str, int]], addr: int) -> tuple[str, int] | None:
    """Nearest text symbol at or below `addr`."""
    best: tuple[str, int] | None = None
    for name, typ, value in rows:
        if typ not in ("T", "t"):
            continue
        if value <= addr and (best is None or value > best[1]):
            best = (name, value)
    return best


def addr2line(cc1: Path, addrs: list[int]) -> list[tuple[str, str]]:
    """Return `(function, file:line)` for each address, in order."""
    if not addrs:
        return []
    out = _run(["addr2line", "-f", "-e", str(cc1)] + [hex(a) for a in addrs])
    lines = out.splitlines()
    pairs = []
    for i in range(0, len(lines) - 1, 2):
        pairs.append((lines[i].strip(), lines[i + 1].strip()))
    while len(pairs) < len(addrs):
        pairs.append(("?", "?"))
    return pairs


def format_location(loc: str) -> str:
    """`/usr/local/sce/ee/gcc/build/gcc/../../src/gcc/global.c:789` -> `global.c:789`."""
    if loc in ("??", "?"):
        return loc
    m = re.match(r"^(.*):(\d+)$", loc)
    if not m:
        return loc
    path = m.group(1)
    tail = "/src/gcc/"
    if tail in path:
        path = path.split(tail, 1)[1]
    else:
        path = Path(path).name
    return f"{path}:{m.group(2)}"


# ---------------------------------------------------------------- disassembly


def disasm_annotated(cc1: Path, start: int, stop: int, max_lines: int = 400) -> list[str]:
    """`objdump -d --line-numbers` reduced to `address  bytes  mnemonic  ; file:line`."""
    out = _run([
        "objdump", "-d", "--line-numbers",
        f"--start-address={hex(start)}", f"--stop-address={hex(stop)}", str(cc1),
    ])
    rendered: list[str] = []
    current = ""
    for line in out.splitlines():
        if not line.strip():
            continue
        if line.startswith("/") and re.search(r":\d+$", line):
            current = format_location(line.strip())
            rendered.append(f"; {current}")
            continue
        m = _DISASM_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            raw = m.group(2).split()
            mnem = m.group(3).strip()
            shown = "".join(f"{b:>3}" for b in raw[:6])
            rendered.append(f"{addr:#010x} {shown:<20} {mnem}")
            if len(rendered) >= max_lines:
                rendered.append("; … (truncated; raise --disasm-bytes for more)")
                break
    return rendered


def read_bytes(cc1: Path, addr: int, count: int) -> bytes:
    out = _run([
        "objdump", "-s",
        f"--start-address={hex(addr)}", f"--stop-address={hex(addr + count)}", str(cc1),
    ])
    data = bytearray()
    for line in out.splitlines():
        m = re.match(r"^\s*([0-9a-f]{4,16})\s+((?:[0-9a-f]{2,16}\s+){1,8})", line)
        if not m:
            continue
        for group in m.group(2).split():
            data.extend(bytes.fromhex(group))
    return bytes(data[:count])


def decode_bytes(raw: bytes) -> dict:
    """Decode the first bytes as the integer and float views a formula may use."""
    view: dict = {"hex": raw.hex()}
    if len(raw) >= 4:
        view["int32"] = structlib.unpack_from("<i", raw, 0)[0]
        view["uint32"] = structlib.unpack_from("<I", raw, 0)[0]
        view["float32"] = structlib.unpack_from("<f", raw, 0)[0]
    if len(raw) >= 8:
        view["int64"] = structlib.unpack_from("<q", raw, 0)[0]
        view["double"] = structlib.unpack_from("<d", raw, 0)[0]
    return view


# ---------------------------------------------------------------- DWARF


def dwarf_dies(cc1: Path):
    """Stream `readelf --debug-dump=info` into `(level, tag, offset, attrs)` records."""
    proc = subprocess.Popen(
        ["readelf", "--debug-dump=info", str(cc1)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=_C_ENV,
    )
    assert proc.stdout is not None
    level = offset = 0
    tag = ""
    attrs: dict[str, str] = {}
    for line in proc.stdout:
        m = _DIE_RE.match(line)
        if m:
            if tag:
                yield level, tag, offset, attrs
            level, offset, tag, attrs = int(m.group(1)), m.group(2), m.group(3), {}
            continue
        m = _ATTR_RE.match(line)
        if m and tag:
            value = m.group(2)
            if m.group(1) == "DW_AT_name":
                value = _clean_name(value)
            attrs.setdefault(m.group(1), value)
    if tag:
        yield level, tag, offset, attrs
    proc.stdout.close()
    proc.wait()


def _clean_name(value: str) -> str:
    """`(indirect string, offset: 0x33dc2): allocno` and `(anonymous)` both reduce to the name."""
    text = value.strip()
    m = re.match(r"^\(indirect string, offset: 0x[0-9a-f]+\):\s*(.*)$", text)
    if m:
        return m.group(1).strip()
    return text


def dwarf_struct(cc1: Path, name: str) -> dict | None:
    """Return `{name, byte_size, decl_line, members[]}` for a named struct/union."""
    target_level = offset = None
    attrs: dict[str, str] = {}
    for level, tag, off, a in dwarf_dies(cc1):
        if target_level is not None:
            if level <= target_level:
                break
            if tag == "DW_TAG_member":
                loc = a.get("DW_AT_data_member_location", "")
                m = _PLUS_UCONST_RE.search(loc)
                members.append({
                    "name": a.get("DW_AT_name", "<anonymous>"),
                    "decl_line": _int_or_none(a.get("DW_AT_decl_line")),
                    "offset": int(m.group(1)) if m else _int_or_none(loc),
                })
            continue
        if tag in ("DW_TAG_structure_type", "DW_TAG_union_type") and a.get("DW_AT_name") == name:
            target_level, offset, attrs = level, off, a
            members = []
    if target_level is None:
        return None
    return {
        "name": name,
        "byte_size": _int_or_none(attrs.get("DW_AT_byte_size")),
        "decl_line": _int_or_none(attrs.get("DW_AT_decl_line")),
        "members": members,
    }


def _int_or_none(text: str | None) -> int | None:
    if text is None:
        return None
    m = re.search(r"\d+", text)
    return int(m.group(0)) if m else None


# ---------------------------------------------------------------- commands


def cmd_symbol(cc1: Path, rows, args: list[str], opts) -> tuple[dict, int]:
    name = require_arg(args, 0, "symbol <name>")
    hits = lookup_symbol(rows, name)
    if not hits:
        raise ToolError(f"symbol not found: {name}")
    result = {"symbol": name, "candidates": []}
    for _n, typ, addr in hits:
        func, loc = addr2line(cc1, [addr])[0]
        entry = {"type": typ, "addr": hex(addr), "function": func, "location": format_location(loc)}
        if opts.disasm:
            entry["disasm"] = disasm_annotated(cc1, addr, addr + opts.disasm)
        result["candidates"].append(entry)
    return result, 0


def cmd_addr(cc1: Path, rows, args: list[str], opts) -> tuple[dict, int]:
    addr = parse_addr(require_arg(args, 0, "addr <0xADDR>"))
    func, loc = addr2line(cc1, [addr])[0]
    near = symbol_at(rows, addr)
    result = {
        "addr": hex(addr), "function": func, "location": format_location(loc),
        "nearest_symbol": ({"name": near[0], "addr": hex(near[1])} if near else None),
    }
    if opts.disasm:
        result["disasm"] = disasm_annotated(cc1, addr, addr + opts.disasm)
    return result, 0


def cmd_struct(cc1: Path, _rows, args: list[str], _opts) -> tuple[dict, int]:
    name = require_arg(args, 0, "struct <name>")
    got = dwarf_struct(cc1, name)
    if got is None:
        raise ToolError(f"no struct/union named {name!r} in the DWARF of this cc1")
    return got, 0


def cmd_const(cc1: Path, _rows, args: list[str], opts) -> tuple[dict, int]:
    addr = parse_addr(require_arg(args, 0, "const <0xADDR>"))
    raw = read_bytes(cc1, addr, opts.bytes)
    if not raw:
        raise ToolError(f"no bytes at {hex(addr)} (not in an allocated section?)")
    return {"addr": hex(addr), "size": len(raw), **decode_bytes(raw)}, 0


def cmd_selftest(cc1: Path, rows, _args, _opts) -> tuple[dict, int]:
    checks: list[dict] = []
    failures = 0

    for name, want_file, want_line, want_addr, why in KNOWN_ANCHORS:
        hits = lookup_symbol(rows, name)
        addrs = [a for _n, _t, a in hits]
        ok_addr = want_addr in addrs
        loc = format_location(addr2line(cc1, [want_addr])[0][1]) if ok_addr else "n/a"
        ok_loc = loc == f"{want_file}:{want_line}"
        ok = ok_addr and ok_loc
        failures += 0 if ok else 1
        checks.append({
            "check": f"{name} -> {want_file}:{want_line} @ {hex(want_addr)}", "why": why,
            "ok": ok, "address_found": ok_addr, "resolved": loc,
        })

    got = dwarf_struct(cc1, KNOWN_STRUCT[0])
    ok = bool(got) and got.get("byte_size") == KNOWN_STRUCT[1]
    failures += 0 if ok else 1
    checks.append({
        "check": f"struct {KNOWN_STRUCT[0]} byte_size == {KNOWN_STRUCT[1]}",
        "ok": ok, "resolved": (got or {}).get("byte_size"),
    })

    raw = read_bytes(cc1, KNOWN_CONST[0], 8)
    value = decode_bytes(raw).get("double") if raw else None
    ok = value == KNOWN_CONST[2]
    failures += 0 if ok else 1
    checks.append({
        "check": f"double at {hex(KNOWN_CONST[0])} == {KNOWN_CONST[2]}",
        "ok": ok, "resolved": value,
    })

    return {"selftest": "pass" if failures == 0 else "fail",
            "failed": failures, "checks": checks}, (0 if failures == 0 else 1)


def require_arg(args: list[str], index: int, usage: str) -> str:
    if len(args) <= index or not args[index]:
        raise ToolError(f"missing argument; usage: ee-gcc-anchor.py {usage}")
    return args[index]


def parse_addr(text: str) -> int:
    try:
        return int(text, 16) if text.lower().startswith("0x") else int(text, 0)
    except ValueError as exc:
        raise ToolError(f"not an address: {text!r}") from exc


# ---------------------------------------------------------------- CLI

COMMANDS = {
    "symbol": (cmd_symbol, "symbol <name>      symbol -> address -> source line (+ optional disassembly)"),
    "addr": (cmd_addr, "addr <0xADDR>      address -> function -> source line"),
    "struct": (cmd_struct, "struct <name>    DWARF layout: byte size, member offsets, declaration lines"),
    "const": (cmd_const, "const <0xADDR>   decode the bytes at an address (int32 / uint32 / float / double)"),
    "selftest": (cmd_selftest, "selftest         assert the anchors this tool depends on"),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="ee-gcc-anchor",
        description="Read line numbers, struct layouts and constants out of the shipped ee-gcc cc1.",
    )
    ap.add_argument("--cc1", default=DEFAULT_CC1, help="path to cc1 (default: $EE_CC1 or the local install)")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--disasm", type=int, default=0,
                    help="for symbol/addr: also disassemble N bytes and bind instructions to source lines")
    ap.add_argument("--bytes", type=int, default=8, help="for const: how many bytes to read")
    ap.add_argument("command", choices=sorted(COMMANDS))
    ap.add_argument("args", nargs="*")
    opts = ap.parse_args(argv)

    func, _help = COMMANDS[opts.command]
    try:
        cc1 = require_cc1(opts.cc1)
        rows = nm_symbols(cc1) if opts.command != "struct" else []
        result, code = func(cc1, rows, opts.args, opts)
    except ToolError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if opts.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return code

    if opts.command == "selftest":
        for check in result["checks"]:
            mark = "ok  " if check["ok"] else "FAIL"
            extra = f"  ({check['resolved']})" if "resolved" in check else ""
            print(f"[{mark}] {check['check']}{extra}")
        print(f"selftest: {result['selftest']} ({result['failed']} failed)")
        return code
    if opts.command == "struct":
        print(f"struct {result['name']}  byte_size={result['byte_size']}  decl_line={result['decl_line']}")
        print(f"{'offset':>8}  {'line':>6}  member")
        for member in result["members"]:
            print(f"{str(member['offset']):>8}  {str(member['decl_line']):>6}  {member['name']}")
        return code
    if opts.command == "const":
        print(f"{result['addr']}  ({result['size']} B)  {result['hex']}")
        for key in ("int32", "uint32", "float32", "int64", "double"):
            if key in result:
                print(f"  {key:<8} {result[key]}")
        return code

    if "candidates" in result:
        for entry in result["candidates"]:
            print(f"{result['symbol']} [{entry['type']}] @ {entry['addr']}  ->  "
                  f"{entry['location']}  ({entry['function']})")
            for line in entry.get("disasm", []):
                print(f"    {line}")
    else:
        near = result["nearest_symbol"]
        suffix = f"  (nearest symbol: {near['name']} @ {near['addr']})" if near else ""
        print(f"{result['addr']}  ->  {result['location']}  ({result['function']}){suffix}")
        for line in result.get("disasm", []):
            print(f"    {line}")
    return code


if __name__ == "__main__":
    sys.exit(main())
