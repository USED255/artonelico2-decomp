#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""jtbl 对象修补：把 C 对象里**自产跳转表**的引用改指到 splat 既有的 `jtbl_*` 数据符号。

## 为什么需要

`switch` 在 ee-gcc 3.2 下会自产 `.rodata` 跳转表（实测 `-Os`：32 B，8 条 `R_MIPS_32`），
代码用 `lui/addiu %hi/%lo(<.rodata>)` 引用它。但本作数据段里**本来就有**这张表
（splat 切出符号，如 `jtbl_00965B58`），C 再产一份就是重复定义/地址错位（P-23），
hybrid 的安全闸门也会拒收（`.rodata` 是非 `.text` 可分配段）。

实测（`func_001d7154`，2026-10-07）：真实 `switch` 草稿 objdiff **99.5%**，
唯一差异就是这两条 `%hi/%lo` 的**重定位目标**（指向 C 自己的 `.rodata` 而非 `jtbl_00965B58`）。
本工具把它们改成引用一个**未定义**符号 `jtbl_XXXX`（真身由原 asm 数据对象提供），
并把被改指指令的 16 位立即数清零（去掉节内 addend）⇒ C 的 `.rodata` 变成**无人引用**的段，
可被链接脚本 `/DISCARD/` 丢掉，而代码字节与原版完全一致。

## 保守边界（宁可不做，也不静默错码）

* 只处理 **立即数 == 0** 的引用（表在 `.rodata` 偏移 0）；一个函数里有多张表、或表后还有
  字符串常量时立即数不为 0 ⇒ **报错退出**。
* 只改 `.text*` 段的重定位；`.rel.rodata`（表项自身的 `R_MIPS_32`）不动（整段会被丢弃）。
* 幂等：目标符号已以 UND 存在时复用，不重复追加。

用法：
  python3 tools/project/jtbl_patch.py --obj build/x.o --table jtbl_00965B58 [--out y.o]
  python3 tools/project/jtbl_patch.py --obj x.o --table jtbl_X --check
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

SHT_SYMTAB, SHT_REL = 2, 9
STT_SECTION = 3
SHN_UNDEF = 0
R_MIPS_HI16, R_MIPS_LO16 = 5, 6


class Elf:
    def __init__(self, data: bytes):
        if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
            raise ValueError("不是 ELF32 little-endian")
        self.d = bytearray(data)
        (self.sh_off,) = struct.unpack_from("<I", self.d, 0x20)
        self.sh_entsize, self.sh_num, self.sh_strndx = struct.unpack_from("<HHH", self.d, 0x2E)
        if self.sh_entsize != 40:
            raise ValueError("e_shentsize != 40（非标准 ELF32）")
        self.sh = [list(struct.unpack_from("<10I", self.d, self.sh_off + i * 40))
                   for i in range(self.sh_num)]

    @staticmethod
    def _str_at(raw: bytes, off: int) -> str:
        """按偏移取字符串。⚠️ GAS 会做**字符串后缀共享**：`sh_name`/`st_name` 可能指向
        另一条字符串的中间（实测 `.text.func_001d7154` 落在 `.rel.text.func_001d7154` 内部），
        所以不能用 split('\\0') 建立的「只认串首」字典。"""
        end = raw.find(b"\0", off)
        return raw[off:end if end >= 0 else len(raw)].decode("utf-8", "replace")

    def _shstr(self) -> bytes:
        h = self.sh[self.sh_strndx]
        return bytes(self.d[h[4]:h[4] + h[5]])

    def name(self, idx: int) -> str:
        return self._str_at(self._shstr(), self.sh[idx][0])

    def symtab_index(self) -> int:
        return next(i for i in range(self.sh_num) if self.sh[i][1] == SHT_SYMTAB)

    def syms(self) -> list[dict]:
        st = self.symtab_index()
        off, size, link = self.sh[st][4], self.sh[st][5], self.sh[st][6]
        strs = self.sh[link]
        raw = bytes(self.d[strs[4]:strs[4] + strs[5]])
        out = []
        for i in range(size // 16):
            nm, val, sz, info, other, shndx = struct.unpack_from("<IIIBBH", self.d, off + i * 16)
            out.append({"idx": i, "name": self._str_at(raw, nm) if nm else "", "value": val,
                        "size": sz, "bind": info >> 4, "type": info & 0xF, "shndx": shndx})
        return out


def patch(obj: Path, table: str, out: Path | None = None, check: bool = False) -> tuple[bool, str]:
    e = Elf(obj.read_bytes())
    syms = e.syms()
    rodata = next((i for i in range(e.sh_num) if e.name(i) == ".rodata"), None)
    if rodata is None:
        return False, "对象里没有 .rodata（不需要修补？）"
    secsym = next((s for s in syms if s["type"] == STT_SECTION and s["shndx"] == rodata), None)
    if secsym is None:
        return False, "找不到 .rodata 的节符号"
    hits = []
    for ri in range(e.sh_num):
        if e.sh[ri][1] != SHT_REL or not e.name(e.sh[ri][7]).startswith(".text"):
            continue
        off, size, info = e.sh[ri][4], e.sh[ri][5], e.sh[ri][7]
        for k in range(size // 8):
            r_off, r_info = struct.unpack_from("<II", e.d, off + k * 8)
            if (r_info >> 8) != secsym["idx"]:
                continue
            tgt_off = e.sh[info][4] + r_off
            (word,) = struct.unpack_from("<I", e.d, tgt_off)
            hits.append((ri, k, r_off, r_info & 0xFF, tgt_off, word & 0xFFFF))
    if not hits:
        return False, "没有指向 .rodata 的 .text 重定位（可能已修补过）"
    bad = [h for h in hits if h[5] != 0]
    if bad:
        return False, ("引用的表不在 .rodata 偏移 0（立即数 %s）⇒ 该函数有多张表或混有常量，本工具保守拒做"
                       % ", ".join(hex(h[5]) for h in bad[:4]))
    desc = "找到 %d 条 .text→.rodata 重定位：%s" % (
        len(hits), ", ".join("R_MIPS_%s@+0x%x" % ({R_MIPS_HI16: "HI16", R_MIPS_LO16: "LO16"}.get(h[3], h[3]), h[2])
                             for h in hits))
    if check:
        return True, desc + "（--check：未写入）"

    st = e.symtab_index()
    strs_idx = e.sh[st][6]
    existing = next((s for s in syms if s["name"] == table and s["shndx"] == SHN_UNDEF), None)
    if existing is not None:
        new_idx = existing["idx"]
    else:
        sym_off, sym_size = e.sh[st][4], e.sh[st][5]
        str_off, str_size = e.sh[strs_idx][4], e.sh[strs_idx][5]
        new_str_tab = bytes(e.d[str_off:str_off + str_size]) + table.encode() + b"\0"
        entry = struct.pack("<IIIBBH", str_size, 0, 0, (1 << 4) | 0, 0, SHN_UNDEF)
        new_idx = sym_size // 16
        e.d.extend(b"\0" * ((-len(e.d)) % 4))
        new_sym_file = len(e.d)
        e.d.extend(bytes(e.d[sym_off:sym_off + sym_size]) + entry)
        new_str_file = len(e.d)
        e.d.extend(new_str_tab)
        struct.pack_into("<II", e.d, e.sh_off + st * 40 + 16, new_sym_file, (new_idx + 1) * 16)
        struct.pack_into("<II", e.d, e.sh_off + strs_idx * 40 + 16, new_str_file, len(new_str_tab))

    n = 0
    for ri, k, r_off, rtype, tgt_off, imm in hits:
        r_info_off = e.sh[ri][4] + k * 8 + 4
        struct.pack_into("<I", e.d, r_info_off, (new_idx << 8) | rtype)
        (word,) = struct.unpack_from("<I", e.d, tgt_off)
        struct.pack_into("<I", e.d, tgt_off, word & 0xFFFF0000)
        n += 1
    dst = out or obj
    dst.write_bytes(bytes(e.d))
    return True, desc + " ⇒ 已改写 %d 条重定位指向 %s（立即数清零）；输出 %s" % (n, table, dst)


def main() -> int:
    ap = argparse.ArgumentParser(description="把 C 自产跳转表的引用改指到既有 jtbl_* 符号")
    ap.add_argument("--obj", required=True)
    ap.add_argument("--table", required=True, help="splat 里的表符号名，如 jtbl_00965B58")
    ap.add_argument("--out", default="")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ok, msg = patch(Path(a.obj), a.table, Path(a.out) if a.out else None, a.check)
    print(("[OK] " if ok else "[FAIL] ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
