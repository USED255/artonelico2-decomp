#!/usr/bin/env python3
"""Parse the `.erx.lib` export registry and the `.erx.stub` import table of the main program (PS2 EE ELF).

Background: the main program of this game has no symbols (`.mdebug`=0, no `.symtab`). The
`.erx.lib` section is the **export registry** that the GUST/ERX mechanism leaves. It gives
"library name + version -> a set of function addresses". It is the only ready source of
naming anchors. The 749 anchors of the US route B come from it (see the comments in
tools/build/gen_symbol_addrs.py).

Format (this script derives it from the US version by measurement. The JP structure is
byte-identical. See `[verified]` in out/evidence/jp_routeb_m1_result.txt):

    .erx.lib record (one record per library):
      +0x00  u32 magic0 = 'eRxL' (0x4C785265 LE)
      +0x04  u32 magic1 = 'iB\\0A' (0x41004269 LE)
      +0x08  u32 0
      +0x0C  u32 0
      +0x10  u32 name_va   -> points to the library name string in .rodata
      +0x14  u32 version   (0x101, 0x102, ...)
      +0x18  u32 0
      +0x1C  u32 0
      +0x20  u32 funcs[n]  (n = (next record offset - this record offset - 0x20 - 4) / 4)
      The last 4 bytes are 0 fill. The next record follows (or the section ends).
     The next record = the next position of magic0.

    .erx.stub record (32 bytes each):
      +0x00 magic0 'sRx$' (0x24785273 LE)  +0x04 magic1 '\\0BuT' (0x54754200 LE)
      +0x08 u32 0  +0x0C u32 0
      +0x10 name_va  +0x14 version  +0x18 a  +0x1C b

Usage: python3 erx_tables.py <elf> <out.json> [out.txt]

解析主程序的 `.erx.lib` 导出注册表与 `.erx.stub` 导入表（PS2 EE ELF）。

背景：本作主程序无符号（`.mdebug`=0、无 `.symtab`），`.erx.lib` 是 GUST/ERX 机制
留下的**导出注册表**——它给出「库名 + 版本 → 一组函数地址」，是唯一现成的命名锚点
来源。美版路线 B 的 749 个锚点就是这么来的（见 tools/build/gen_symbol_addrs.py 的注释）。

格式（本脚本对美版实测反推，日版结构逐字节同构；`[已核实]` 见 out/evidence/
jp_routeb_m1_result.txt）：

    .erx.lib 记录（每条库一条）：
      +0x00  u32 magic0 = 'eRxL' (0x4C785265 LE)
      +0x04  u32 magic1 = 'iB\\0A' (0x41004269 LE)
      +0x08  u32 0
      +0x0C  u32 0
      +0x10  u32 name_va   -> 指向 .rodata 里的库名字符串
      +0x14  u32 version   (0x101, 0x102, ...)
      +0x18  u32 0
      +0x1C  u32 0
      +0x20  u32 funcs[n]  (n = (下一条记录偏移 - 本记录偏移 - 0x20 - 4) / 4)
      末尾 4 字节 0 填充，随后是下一条记录（或节结束）
    下一条记录 = 下一次出现 magic0 的位置。

    .erx.stub 记录（每条 32 字节）：
      +0x00 magic0 'sRx$' (0x24785273 LE)  +0x04 magic1 '\\0BuT' (0x54754200 LE)
      +0x08 u32 0  +0x0C u32 0
      +0x10 name_va  +0x14 version  +0x18 a  +0x1C b

用法: python3 erx_tables.py <elf> <out.json> [out.txt]
"""
import json
import struct
import sys

MAGIC_LIB = b"eRxLiB\x00A"
MAGIC_STUB = b"sRx$\x00BuT"
LIB_HDR = 0x20          # Record header size
LIB_TAIL = 4            # Zero fill at the end of each record
STUB_REC = 32


def parse_elf(path):
    d = open(path, "rb").read()
    e = struct.unpack_from("<HHIIIIIHHHHHH", d, 16)
    shoff, shnum, shstrndx = e[5], e[11], e[12]
    shs = [struct.unpack_from("<IIIIIIIIII", d, shoff + i * 40) for i in range(shnum)]
    shstr = d[shs[shstrndx][4]:shs[shstrndx][4] + shs[shstrndx][5]]
    secs = {}
    for (n, t, f, a, o, s, l, inf, al, es) in shs:
        end = shstr.find(b"\0", n)
        nm = shstr[n:end].decode() if n else ""
        secs[nm] = dict(addr=a, off=o, size=s)
    return d, secs


SEGMAPS = []


def cstr(d, va):
    """Read a vaddr as a NUL-terminated ASCII string.

    The JP version has two LOAD segments, so a lookup through the section table is the most
    reliable method.

    把 vaddr 读成 NUL 结尾 ASCII 串。日版有两段 LOAD，用节表反查最稳。
    """
    for base, off, size in SEGMAPS:
        if base <= va < base + size:
            o = off + (va - base)
            end = d.find(b"\0", o, o + 128)
            if end > o:
                return d[o:end].decode("ascii", "replace")
    return "<bad va 0x%x>" % va


def build_seg_maps(secs):
    """Build the (vaddr_base, file_off, size) list from the section table for cstr.

    用节表构造 (vaddr_base, file_off, size) 列表，供 cstr 使用。
    """
    del SEGMAPS[:]
    for nm, s in secs.items():
        if s["size"] and s["off"] and s["addr"]:
            SEGMAPS.append((s["addr"], s["off"], s["size"]))


def parse_lib(d, secs):
    s = secs[".erx.lib"]
    start, size = s["off"], s["size"]
    offs = []
    i = start
    while True:
        j = d.find(MAGIC_LIB, i, start + size)
        if j < 0:
            break
        offs.append(j)
        i = j + 4
    libs = []
    for k, o in enumerate(offs):
        nxt = offs[k + 1] if k + 1 < len(offs) else start + size
        name_va, ver = struct.unpack_from("<II", d, o + 0x10)
        n = (nxt - o - LIB_HDR - LIB_TAIL) // 4
        funcs = list(struct.unpack_from("<%dI" % n, d, o + LIB_HDR))
        libs.append(dict(off=o, name=cstr(d, name_va), name_va=name_va,
                         ver=ver, funcs=funcs))
    return libs


def parse_stub(d, secs):
    s = secs[".erx.stub"]
    out = []
    for k in range(s["size"] // STUB_REC):
        o = s["off"] + k * STUB_REC
        name_va, ver, a, b = struct.unpack_from("<IIII", d, o + 0x10)
        out.append(dict(name=cstr(d, name_va), name_va=name_va, ver=ver, a=a, b=b))
    return out


def scan_hle_stubs(d, secs):
    """Scan for the canonical 16-byte HLE stub: addiu $v1,$zero,n ; syscall 12 ; jr $ra ; nop

    扫描规范的 16 字节 HLE 桩: addiu $v1,$zero,n ; syscall 12 ; jr $ra ; nop
    """
    stubs = {}
    for nm in (".text", ".init", ".fini"):
        s = secs.get(nm)
        if not s:
            continue
        for i in range(s["off"], s["off"] + s["size"] - 16, 4):
            w = struct.unpack_from("<I", d, i)[0]
            if w == 0x0000000C:
                prev, nxt, after = struct.unpack_from("<III", d, i - 4)[0:3]
                if (prev & 0xFFFF0000) == 0x24030000 and nxt == 0x03E00008 and after == 0:
                    stubs[s["addr"] + (i - s["off"]) - 4] = prev & 0xFFFF
    return stubs


def main():
    elf, out_json = sys.argv[1], sys.argv[2]
    out_txt = sys.argv[3] if len(sys.argv) > 3 else None
    d, secs = parse_elf(elf)
    build_seg_maps(secs)
    libs = parse_lib(d, secs)
    stub = parse_stub(d, secs)
    hle = scan_hle_stubs(d, secs)

    lines = ["PS2 %s -- ERX native library registry (.erx.lib) with resolved addresses"
             % elf.split("/")[-1],
             "legend: index | target vaddr | kind (hle-stub = `li $v1,n; syscall 12` trap"
             " / native = real code / none = placeholder 0)",
             ""]
    n_uniq_all = set()
    for L in libs:
        rows = []
        n_stub = n_real = n_none = 0
        for idx, fp in enumerate(L["funcs"]):
            if fp == 0:
                cat = "none"; n_none += 1
            elif fp in hle:
                cat = "hle-stub"; n_stub += 1
            else:
                cat = "native"; n_real += 1
            if fp:
                n_uniq_all.add(fp)
            rows.append((idx, fp, cat))
        lines.append("=== library %-14s version=0x%08x  slots=%d  hle-stub=%d native=%d none=%d"
                     % (L["name"], L["ver"], len(L["funcs"]), n_stub, n_real, n_none))
        for idx, fp, cat in rows:
            lines.append("  %5d  0x%08x  %-8s" % (idx, fp, cat))
        lines.append("")
        L["rows"] = [dict(idx=i, addr=a, cat=c) for i, a, c in rows]
        L["n_stub"], L["n_native"], L["n_none"] = n_stub, n_real, n_none

    uniq_slots = sum(1 for L in libs for f in L["funcs"] if f)
    print("libraries        = %d" % len(libs))
    print("total slots      = %d" % sum(len(L["funcs"]) for L in libs))
    print("non-empty slots  = %d" % uniq_slots)
    print("unique func addrs = %d" % len(n_uniq_all))
    print("HLE stubs (global scan) = %d" % len(hle))
    print("library names    = %s" % ", ".join(L["name"] for L in libs))
    print("unique addr range = %s" % ("0x%06x .. 0x%06x" % (min(n_uniq_all), max(n_uniq_all))
                                      if n_uniq_all else "n/a"))
    json.dump(dict(stub=stub, libs=libs, hle_stubs=len(hle),
                   n_unique_funcs=len(n_uniq_all)), open(out_json, "w"), indent=1)
    print("-> %s" % out_json)
    if out_txt:
        open(out_txt, "w").write("\n".join(lines) + "\n")
        print("-> %s" % out_txt)


if __name__ == "__main__":
    main()
