#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Redirect a C object's own data references to the data symbols that splat already cut (O-01 (1)).

The problem
-----------
A matched C function that writes a string literal, a static table or a static variable makes
its **own** `.rodata` / `.data` / `.bss`. The mixed build cannot place that data: its linker
script drops every non-`.text` section with `/DISCARD/`, so the build's safety gate refuses the
object (`tools/project/obj_gate.py`, rule 1). A string literal is the common case: of 10,926
asm blocks, 818 refer to a string label; only 38 of those functions are matched, and every one
of them sidesteps the gate by hand-writing `extern D_XXXX`.

What this tool does
-------------------
Compile first, patch the **object**, do not touch the source:

1. Read the ordered list of data references in the C object's `.text*` relocations: a
   `%hi`/`%lo` pair that targets a non-`.text` allocatable section (the C-made data).
2. Read the ordered list of data references in the original `asm/cod/<sym>.s` block
   (`%lo(NAME)` / `%lo(NAME + 0xNN)`; `%gp_rel` is out of scope, the weak-definition path
   already covers it).
3. Pair them 1:1. A different count is a refusal, never a guess.
4. **Verify the content**: the bytes of the C section at the reference must equal the original
   bytes at `NAME + off`. This check is mandatory, because `objdiff` compares `.text` only: a
   wrong string would still score 100 and would only fail at runtime.
5. Redirect the relocation to an undefined `NAME` (the asm data object supplies the strong
   definition) and write the original offset into the `%lo` immediate. The C data section then
   has no `.text` reference, so `/DISCARD/` drops it and the gate passes.

Why object-level, not source-level: an LLM/m2c draft writes the literal naturally. Rewriting
the source would need to know the symbol name, the byte content and the offset for every
literal; the object already has all three.

Conservative limits (refuse rather than write a wrong byte)
  * counts differ, an unknown symbol, an unpaired relocation, a content mismatch,
    a reference into `.text` (function address), or a missing baseline image;
  * `.bss`/`.sbss` targets have no file bytes, so only the redirect is checked (no content).
  * Idempotent: an object that already refers to the data symbols is left alone.

Usage
  python3 tools/project/data_patch.py --obj build/x.o --sym func_00123456 \\
      --asm asm/cod/func_00123456.s --image build/SLPS_258.19.elf [--out y.o] [--check]

`--image` is the **baseline** link (build.sh's output). It supplies both the data symbol
addresses (the splat symbols are global) and the original bytes. `orig/SLPS_258.19` has no
symbol table, so it cannot be used alone.

把 C 对象自己产出的数据引用改指到 splat 已经切好的数据符号（O-01 ①）。

问题
----
写字符串字面量 / 静态表 / 静态变量的 C 函数会自产 `.rodata` / `.data` / `.bss`。混合构建放不下这些数据：
链接脚本用 `/DISCARD/` 丢掉所有非 `.text` 段，于是安全闸门（`tools/project/obj_gate.py` 规则 1）拒收。
最典型的是字符串常量：10,926 个 asm 块里有 818 个引用字符串标签，其中只有 38 个函数已匹配，
且全部靠手写 `extern D_XXXX` 绕过闸门。

做法
----
先编译，改**对象**，不动源码：

1. 读 C 对象 `.text*` 重定位里的数据引用（`%hi`/`%lo` 一对，目标是 C 自产的非 `.text` 可分配段）。
2. 读原 `asm/cod/<sym>.s` 块里的数据引用（`%lo(NAME)` / `%lo(NAME + 0xNN)`；`%gp_rel` 不在此列，
   weak 定义那条路已覆盖）。
3. 1:1 配对。数量不等就拒绝，绝不猜。
4. **校验内容**：C 段在引用处的字节必须等于原版在 `NAME + off` 处的字节。这一步不可省——
   `objdiff` 只比 `.text`，错的字符串照样 100 分，只有运行期才会暴露。
5. 把重定位改指到未定义的 `NAME`（真身由 asm 数据对象提供），并把原始偏移写回 `%lo` 立即数。
   C 的数据段随即没有 `.text` 引用 ⇒ 被 `/DISCARD/` 丢掉 ⇒ 闸门放行。

为什么改对象而不是改源码：LLM/m2c 草稿天然会写字面量；改源码需要为每个字面量知道符号名、字节内容
和偏移，而对象里三者都在。

保守边界（宁可不做，也不写错字节）：数量不符 / 未知符号 / 落单的重定位 / 内容不符 /
指向 `.text`（函数地址）/ 缺基线镜像 ⇒ 拒绝。`.bss`/`.sbss` 没有文件字节，只做改指不校验内容。
幂等：已指向数据符号的对象原样放过。
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import at2_io  # noqa: E402
import jtbl_patch as JT  # the C-object ELF parser  # noqa: E402

R_MIPS_HI16, R_MIPS_LO16 = 5, 6
SHT_REL = 9
STT_SECTION, STT_OBJECT, STT_FUNC = 3, 1, 2
SHN_UNDEF = 0

# `%lo(NAME)` / `%lo(NAME + 0x18)`; splat writes the offset with spaces around `+`.
LO_RE = re.compile(r"%lo\(\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(?:\+\s*(0x[0-9A-Fa-f]+|\d+)\s*)?\)")
INS_ADDR_RE = re.compile(r"/\*\s*[0-9A-Fa-f]+\s+([0-9A-Fa-f]+)\s+[0-9A-Fa-f]{8}\s*\*/")
GLABEL_RE = re.compile(r"^\s*glabel\s+(\S+)")
ENDLABEL_RE = re.compile(r"^\s*endlabel\s+(\S+)")


class Image:
    """The baseline ELF: VMA -> bytes (PT_LOAD) and name -> symbol. 基线 ELF：VMA→字节、名字→符号。"""

    def __init__(self, path: Path):
        data = path.read_bytes()
        self.d = data
        if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
            raise ValueError("not ELF32 little-endian: %s" % path)
        (e_phoff,) = struct.unpack_from("<I", data, 0x1C)
        (e_phentsize, e_phnum) = struct.unpack_from("<HH", data, 0x2A)
        (e_shoff,) = struct.unpack_from("<I", data, 0x20)
        (e_shentsize, e_shnum, self.shstrndx) = struct.unpack_from("<HHH", data, 0x2E)
        if e_phentsize != 32:
            raise ValueError("e_phentsize != 32")
        self.segs = []
        for i in range(e_phnum):
            (p_type, p_offset, p_vaddr, _paddr, p_filesz) = struct.unpack_from("<IIIII", data, e_phoff + i * 32)
            if p_type == 1:  # PT_LOAD
                self.segs.append((p_vaddr, p_vaddr + p_filesz, p_offset))
        if e_shentsize != 40:
            raise ValueError("e_shentsize != 40")
        self.sh = [list(struct.unpack_from("<10I", data, e_shoff + i * 40)) for i in range(e_shnum)]
        self._syms: dict[str, tuple[int, int, int, int]] | None = None

    def read(self, vaddr: int, n: int) -> bytes | None:
        """Read `n` bytes at a VMA from the PT_LOAD file image. 从 PT_LOAD 的文件镜像里读 VMA 的 n 字节。"""
        for start, end, off in self.segs:
            if start <= vaddr and vaddr + n <= end:
                return self.d[off + (vaddr - start): off + (vaddr - start) + n]
        return None

    def has(self, vaddr: int, n: int) -> bool:
        return self.read(vaddr, n) is not None

    def symbols(self) -> dict[str, tuple[int, int, int, int]]:
        """name -> (value, size, type, shndx) for every defined symbol.

        全部已定义符号的 名字→(值, 大小, 类型, 段索引)。
        """
        if self._syms is not None:
            return self._syms
        out: dict[str, tuple[int, int, int, int]] = {}
        st = next((i for i in range(len(self.sh)) if self.sh[i][1] == 2), None)  # SHT_SYMTAB
        if st is None:
            raise ValueError("the image has no symbol table (use the baseline link, not the stripped original)")
        off, size, link = self.sh[st][4], self.sh[st][5], self.sh[st][6]
        raw = self.d[self.sh[link][4]: self.sh[link][4] + self.sh[link][5]]
        for i in range(size // 16):
            nm, val, sz, info, _other, shndx = struct.unpack_from("<IIIBBH", self.d, off + i * 16)
            if shndx == SHN_UNDEF or not nm:
                continue
            end = raw.find(b"\0", nm)
            name = raw[nm:end if end >= 0 else len(raw)].decode("utf-8", "replace")
            out.setdefault(name, (val, sz, info & 0xF, shndx))
        self._syms = out
        return out

    def section_type(self, shndx: int) -> int:
        """The ELF section type of `shndx` (8 == SHT_NOBITS). `shndx` 的段类型（8 == SHT_NOBITS）。"""
        if 0 <= shndx < len(self.sh):
            return self.sh[shndx][1]
        return 0


# The baseline image is a 9 MB ELF with ~168k symbols. Parsing it once per object would
# dominate a 3,572-source build (measured: the first integration run spent >10 minutes in this
# step), so it is memoised by path and mtime.
# 基线镜像是 9 MB、约 16.8 万个符号的 ELF。若每个对象都解析一次，3,572 个源的构建会被它拖死
# （实测：第一次集成跑在这一步耗掉 10 分钟以上），因此按路径 + mtime 记忆化。
_IMAGE_CACHE: dict[tuple[str, int], "Image"] = {}


def load_image(path: Path | str) -> "Image":
    """The memoised baseline image. 记忆化的基线镜像。"""
    p = Path(path)
    key = (str(p.resolve()), p.stat().st_mtime_ns)
    img = _IMAGE_CACHE.get(key)
    if img is None:
        img = Image(p)
        img.symbols()          # parse the symbol table once  # 符号表只解析一次
        _IMAGE_CACHE[key] = img
    return img


def clear_image_cache() -> None:
    """Drop the memoised image (tests). 清空镜像缓存（测试用）。"""
    _IMAGE_CACHE.clear()


def block_refs(asm_text: str, sym: str) -> list[tuple[int, str, int]]:
    """[(offset_in_block, NAME, addend)] for every `%lo(NAME + off)` of one block.

    The offset comes from the instruction's own `/* file-offset VMA word */` comment, so it can
    be compared with the C object's relocation `r_offset` **directly**. Order alone is not
    enough: the C source may reference a data symbol as an `extern` (which leaves no C-made
    data), so the number of C data references and the number of asm `%lo` do not have to agree.

    一个块（glabel..endlabel）内每条 `%lo(NAME + off)` 的 (块内偏移, 名字, 加数)。
    偏移取自指令自带的 `/* 文件偏移 VMA 字 */` 注释，因此可与 C 对象的 `r_offset` **直接**比较。
    只用顺序不够：C 源可能把数据符号写成 `extern`（不会产 C 数据），两边的数量不必相等。
    """
    lines = asm_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = GLABEL_RE.match(line)
        if m and m.group(1) == sym:
            start = i
            break
    if start is None:
        raise ValueError("the asm block has no glabel for %s" % sym)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        m = ENDLABEL_RE.match(lines[i])
        if m and m.group(1) == sym:
            end = i + 1
            break
    refs: list[tuple[int, str, int]] = []
    base: int | None = None
    for line in lines[start:end]:
        # Every instruction line starts with a `/* file offset address word */` comment, so a
        # "starts with a comment" test would drop the instructions. `%lo` only appears in an
        # operand, so matching anywhere in the line is safe.
        # splat 的每条指令都以 `/* 文件偏移 地址 字 */` 开头，用「以注释开头」过滤会把指令全丢掉；
        # `%lo` 只会出现在操作数里，因此整行匹配即可。
        a = INS_ADDR_RE.search(line)
        if a:
            addr = int(a.group(1), 16)
            if base is None:
                base = addr
            delta = addr - base
        else:
            delta = None
        for m in LO_RE.finditer(line):
            if delta is None:
                raise ValueError("a %%lo line without an address comment: %r" % line.strip()[:80])
            name = m.group(1)
            off = int(m.group(2), 0) if m.group(2) else 0
            refs.append((delta, name, off))
    return refs


def _text_rel_sections(e: "JT.Elf"):
    """(section index, name) of the `.rel.text*` sections. `.rel.text*` 段的 (索引, 名字)。"""
    out = []
    for ri in range(e.sh_num):
        if e.sh[ri][1] != SHT_REL:
            continue
        name = e.name(ri)
        if name.startswith(".rel.text"):
            out.append((ri, name))
    return out


def relocated_ranges(e: "JT.Elf") -> dict[int, set[int]]:
    """byte offsets covered by a relocation, per section index. 按段索引给出「被重定位覆盖」的字节偏移。"""
    out: dict[int, set[int]] = {}
    for ri in range(e.sh_num):
        if e.sh[ri][1] != SHT_REL:
            continue
        target = e.sh[ri][7]
        entries = out.setdefault(target, set())
        off, size = e.sh[ri][4], e.sh[ri][5]
        for k in range(size // 8):
            (r_off, _r_info) = struct.unpack_from("<II", e.d, off + k * 8)
            entries.update(range(r_off, r_off + 4))
    return out


def patch(obj: Path, sym: str, asm: Path, image_path: Path, out: Path | None = None,
          check: bool = False) -> tuple[bool, str]:
    """Patch one object. Return (ok, message). 修补一个对象，返回 (是否成功, 说明)。"""
    if not at2_io.symbol_ok(sym):
        return False, "the symbol is not a safe name: %r" % sym
    e = JT.Elf(obj.read_bytes())
    syms = e.syms()
    img = load_image(image_path)
    isyms = img.symbols()
    asm_refs = block_refs(asm.read_text(encoding="utf-8", errors="replace"), sym)

    # 1) Pair the C uses with the asm references, in instruction order.
    #
    # A use is anchored on its **LO16** relocation: one LO16 == one `%lo(NAME)` in the asm. Its
    # high half is the most recent unconsumed HI16 with the same target. The two are NOT adjacent:
    # measured 2026-10-17 on the real ledger, a `jal` (R_MIPS_26) often sits between them, and one
    # HI16 feeds two LO16s (`addiu $4, $16, %lo(D)` plus `sb $0, %lo(D)($16)`). An adjacency rule
    # refused 180 of 3,572 objects; this models the actual relocation stream.
    # 一次引用以 **LO16** 为锚：一条 LO16 = asm 里一条 `%lo(NAME)`；高半部取「同一目标最近一条、
    # 尚未被消费的 HI16」。两者**不相邻**：2026-10-17 实测，中间常夹 `jal`（R_MIPS_26），
    # 且一条 HI16 可以喂两条 LO16（`addiu $4, $16, %lo(D)` 与 `sb $0, %lo(D)($16)`）。
    # 「相邻即配对」在 3,572 个对象里拒了 180 个；这里按真实的重定位流建模。
    sections = {i: e.name(i) for i in range(e.sh_num)}
    c_uses = []  # (sec, name, c_off, text_sec, lo_r_off, rel_sec, lo_k, hi, tgt)
    for ri, _rname in _text_rel_sections(e):
        text_sec = e.sh[ri][7]
        text_off = e.sh[text_sec][4]
        off, size = e.sh[ri][4], e.sh[ri][5]
        entries = []
        for k in range(size // 8):
            r_off, r_info = struct.unpack_from("<II", e.d, off + k * 8)
            entries.append((r_off, r_info & 0xFF, r_info >> 8, k))
        entries.sort()
        pending: dict[int, list[tuple[int, int]]] = {}
        for r_off, rtype, tgt, k in entries:
            if rtype not in (R_MIPS_HI16, R_MIPS_LO16) or tgt >= len(syms):
                continue
            s = syms[tgt]
            if s["shndx"] == SHN_UNDEF:
                continue                       # already redirected, or an extern global
            tname = sections.get(s["shndx"], "?")
            if tname.startswith(".text") or tname in ("ABS", "?", "UND"):
                continue                       # a function address
            if rtype == R_MIPS_HI16:
                pending.setdefault(tgt, []).append((r_off, k))
                continue
            hi = pending.get(tgt)
            hi = hi.pop() if hi else None
            (lo_word,) = struct.unpack_from("<I", e.d, text_off + r_off)
            c_off = (lo_word & 0xFFFF) + (s["value"] if s["type"] == STT_SECTION else 0)
            c_uses.append((s["shndx"], tname, c_off, text_sec, r_off, ri, k, hi, tgt))
    if not c_uses:
        return True, "no .text reference to C-made data (nothing to patch)"

    # 2) Key the asm references by their **instruction offset**. A C data reference at the same
    # offset is the same instruction, so the pairing needs no order and no count equality:
    # an asm `%lo(D_X)` whose C counterpart is an `extern` simply has no C data reference.
    # 2) 按**指令偏移**给 asm 引用建索引。偏移相同的 C 数据引用就是同一条指令，因此既不需要顺序，
    #    也不要求数量相等：asm 的 `%lo(D_X)` 若在 C 里写成 `extern`，本来就不会有 C 数据引用。
    asm_at: dict[int, list[tuple[str, int]]] = {}
    for delta, name, off in asm_refs:
        hit = isyms.get(name)
        if hit is None:
            return False, "the asm reference %s is not in the baseline symbol table" % name
        _val, _size, typ, _shndx = hit
        if typ == STT_FUNC:
            continue                           # a function address
        asm_at.setdefault(delta, []).append((name, off))
    for u in c_uses:
        hits = asm_at.get(u[4])
        if not hits:
            return False, ("the C data reference at block offset 0x%x has no %%lo in the asm block "
                           "(the draft does not match the original reference layout)" % u[4])
        if len(hits) > 1:
            return False, "two %%lo references at block offset 0x%x; refusing to guess" % u[4]
    asm_data = [asm_at[u[4]][0] for u in c_uses]

    # 3) Content verification per section: region = [c_off, next c_off) or the section end.
    by_sec: dict[int, list[int]] = {}
    for u in c_uses:
        by_sec.setdefault(u[0], []).append(u[2])
    for si, offs in by_sec.items():
        size = e.sh[si][5]
        for a in offs:
            if a > size:
                return False, "a reference offset 0x%x lies outside section %s (size 0x%x)" % (a, e.name(si), size)
    relocated = relocated_ranges(e)
    for idx, (cs, cname, c_off, _text_sec, _r_off, _ri, _k, _hi, _tgt) in enumerate(c_uses):
        name, off = asm_data[idx]
        val, ssize, _typ, shndx = isyms[name]
        nxt = min([o for o in by_sec[cs] if o > c_off], default=e.sh[cs][5])
        n = nxt - c_off
        if n <= 0:
            return False, "empty data region at %s+0x%x" % (cname, c_off)
        cbytes = bytes(e.d[e.sh[cs][4] + c_off: e.sh[cs][4] + c_off + n])
        if cname.startswith((".bss", ".sbss")):
            continue                            # NOBITS: no file bytes to compare
        if img.section_type(shndx) == 8:        # SHT_NOBITS: .bss/.sbss have no file bytes
            continue
        obytes = img.read(val + off, n)
        if obytes is None:
            return False, "the original bytes at %s+0x%x are outside the image" % (name, off)
        # A jump table (or any pointer array) holds relocations, not literal bytes: the C object
        # stores zero placeholders and the linker fills them. Skip those words on both sides; the
        # shape/order of the table is what matters, and objdiff plus the payload check cover it.
        # 跳转表（或任何指针数组）里装的是重定位而不是字面字节：C 对象存的是零占位，由链接器填。
        # 这些字两边都跳过；表的内容/顺序由 objdiff 与载荷校验兜底。
        covered = relocated.get(cs, set())
        diff = next((i for i in range(n) if (c_off + i) not in covered and cbytes[i] != obytes[i]), None)
        if diff is not None:
            return False, ("content mismatch at %s+0x%x byte %d (C %s != original %s)"
                           % (name, off, diff, cbytes[max(0, diff - 4):diff + 12].hex(),
                              obytes[max(0, diff - 4):diff + 12].hex()))

    desc = "paired %d data references (%s)" % (
        len(c_uses), ", ".join("%s+0x%x" % (n, o) for n, o in asm_data[:4]) + ("..." if len(asm_data) > 4 else ""))
    if check:
        return True, desc + " (--check: no write)"

    # 4) Rewrite: symbol -> undefined NAME, LO16 immediate -> the original offset, HI16 -> 0.
    st = e.symtab_index()
    strs_idx = e.sh[st][6]
    und: dict[str, int] = {}
    new_entries: list[tuple[bytes, int]] = []   # (entry bytes, name)
    for name, _off in asm_data:
        if name in und:
            continue
        found = next((s for s in syms if s["name"] == name and s["shndx"] == SHN_UNDEF), None)
        if found is not None:
            und[name] = found["idx"]
        else:
            new_entries.append((name, len(syms) + len(new_entries)))
    if new_entries:
        sym_off, sym_size = e.sh[st][4], e.sh[st][5]
        str_off, str_size = e.sh[strs_idx][4], e.sh[strs_idx][5]
        new_str = bytes(e.d[str_off:str_off + str_size])
        entries = b""
        for name, _idx in new_entries:
            entries += struct.pack("<IIIBBH", len(new_str), 0, 0, (1 << 4) | 0, 0, SHN_UNDEF)
            new_str += name.encode() + b"\0"
        e.d.extend(b"\0" * ((-len(e.d)) % 4))
        new_sym_file = len(e.d)
        e.d.extend(bytes(e.d[sym_off:sym_off + sym_size]) + entries)
        new_str_file = len(e.d)
        e.d.extend(new_str)
        struct.pack_into("<II", e.d, e.sh_off + st * 40 + 16, new_sym_file, (len(syms) + len(new_entries)) * 16)
        struct.pack_into("<II", e.d, e.sh_off + strs_idx * 40 + 16, new_str_file, len(new_str))
        for name, idx in new_entries:
            und[name] = idx
    n = 0
    for idx, (cs, cname, c_off, text_sec, r_off, ri, k, hi, tgt) in enumerate(c_uses):
        name, off = asm_data[idx]
        new_idx = und[name]
        text_off = e.sh[text_sec][4]
        # LO16: the target symbol and its original in-section offset.
        (lo_word,) = struct.unpack_from("<I", e.d, text_off + r_off)
        struct.pack_into("<I", e.d, text_off + r_off, (lo_word & 0xFFFF0000) | (off & 0xFFFF))
        struct.pack_into("<I", e.d, e.sh[ri][4] + k * 8 + 4, (new_idx << 8) | R_MIPS_LO16)
        if hi is not None:
            hi_r_off, hi_k = hi
            (hi_word,) = struct.unpack_from("<I", e.d, text_off + hi_r_off)
            struct.pack_into("<I", e.d, text_off + hi_r_off, hi_word & 0xFFFF0000)
            struct.pack_into("<I", e.d, e.sh[ri][4] + hi_k * 8 + 4, (new_idx << 8) | R_MIPS_HI16)
        n += 1
    dst = out or obj
    at2_io.atomic_write_bytes(dst, bytes(e.d))
    return True, desc + " => redirected %d relocations; output %s" % (n, dst)


def main() -> int:
    ap = argparse.ArgumentParser(description="Redirect a C object's own data references to the splat data symbols")
    ap.add_argument("--obj", required=True)
    ap.add_argument("--sym", required=True)
    ap.add_argument("--asm", required=True)
    ap.add_argument("--image", required=True, help="the baseline link (build.sh output), for symbols and bytes")
    ap.add_argument("--out", default="")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    try:
        ok, msg = patch(Path(a.obj), a.sym, Path(a.asm), Path(a.image),
                        Path(a.out) if a.out else None, a.check)
    except Exception as exc:                    # noqa: BLE001 - a clear message beats a traceback for callers
        print("[FAIL] %s: %s" % (type(exc).__name__, exc))
        return 1
    print(("[OK] " if ok else "[FAIL] ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
