#!/usr/bin/env python3
"""生成日版（SLPS_258.19）路线 B 的 splat 配置（含 per-function asmtu 子段）。

为什么不用 `splat create_config` + tools/build/gen_splat_yaml.py 串起来：
  1. `tools/build/gen_splat_yaml.py` 的 `TEXT_END` 硬编码为**美版**的 .init 起点
     (0x36E028)；日版是 0x36C5E8。硬套会把 .init/.fini/.vutext 重复覆盖。
  2. 日版主程序有**两个 PT_LOAD 段**（美版只有一个）。splat 的 vram 由
     `most_parent.vram_start + start - most_parent.rom_start` 线性推出，
     而日版在第 2 段起始处 vram 比线性外推**多 0x80**（0x376000 -> 0x376080）。
     因此必须把配置拆成**两个 top-level segment**（cod / dat），各自带
     start+vram，才能让所有子段的 vram 精确对上原版地址。

本脚本从 ELF 节表/程序头**推导**全部布局（不写死地址），因此同一个脚本也能
在美版上生成与 `routeb/SLUS_217.88.yaml` 同构的配置（单段情形），便于自检。

用法:
  python3 gen_splat_yaml_jp.py <elf> <symbol_addrs.txt> <out.yaml> [--name NAME]
"""
import hashlib
import re
import struct
import sys

# 与 splat ps2elfinfo.ELF_SECTION_MAPPING 保持一致
SECT_MAP = {
    ".text": "asm", ".data": "data", ".rodata": "rodata", ".bss": "bss",
    ".sdata": "sdata", ".sbss": "sbss", ".gcc_except_table": "gcc_except_table",
    ".lit4": "lit4", ".lit8": "lit8", ".ctor": "ctor", ".vtables": "vtables",
    ".vutext": "textbin", ".vudata": "databin",
}
ALLOC = 0x2
EXEC = 0x4
WRITE = 0x1


def parse_elf(path):
    d = open(path, "rb").read()
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags,
     e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = \
        struct.unpack_from("<HHIIIIIHHHHHH", d, 16)
    phs = [struct.unpack_from("<IIIIIIII", d, e_phoff + i * 32) for i in range(e_phnum)]
    shs = [struct.unpack_from("<IIIIIIIIII", d, e_shoff + i * 40) for i in range(e_shnum)]
    shstr = d[shs[e_shstrndx][4]:shs[e_shstrndx][4] + shs[e_shstrndx][5]]
    secs = []
    for (n, t, f, a, o, s, l, inf, al, es) in shs:
        end = shstr.find(b"\0", n)
        nm = shstr[n:end].decode() if n else ""
        secs.append(dict(name=nm, type=t, flags=f, addr=a, off=o, size=s, align=al))
    return d, phs, secs


def load_funcs(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*(\S+)\s*=\s*(0x[0-9a-fA-F]+)\s*;\s*//\s*type:func\s+size:0x([0-9a-fA-F]+)", line)
        if m:
            out[int(m.group(2), 16)] = (m.group(1), int(m.group(3), 16))
    return out


def rom_map(phs):
    """PT_LOAD -> [(vram_start, vram_end, rom_off, file_off, flags)]，按序拼接。"""
    out, rom = [], 0
    for (t, off, va, pa, fsz, msz, fl, al) in phs:
        if t != 1:
            continue
        out.append(dict(vstart=va, vend=va + fsz, vmem=va + msz,
                        rom=rom, foff=off, fsz=fsz, flags=fl))
        rom += fsz
    return out


def va2rom(loads, va):
    for L in loads:
        if L["vstart"] <= va < L["vmem"]:
            return L["rom"] + (va - L["vstart"])
    return None


def main():
    elf, sym_path, out_yaml = sys.argv[1:4]
    name = "SLPS_258.19"
    if "--name" in sys.argv:
        name = sys.argv[sys.argv.index("--name") + 1]

    d, phs, secs = parse_elf(elf)
    loads = rom_map(phs)
    rom_size = sum(L["fsz"] for L in loads)
    # yaml 的 sha1 必须等于 target_path（拼 PT_LOAD 得到的 rom）的 sha1
    rom_sha1 = hashlib.sha1(b"".join(d[L["foff"]:L["foff"] + L["fsz"]] for L in loads)).hexdigest()
    funcs = load_funcs(sym_path)

    alloc = [s for s in secs if (s["flags"] & ALLOC) and s["size"] > 0
             and s["type"] in (1, 8)]
    alloc.sort(key=lambda s: s["addr"])

    def splat_type(s):
        if s["name"] in SECT_MAP:
            return SECT_MAP[s["name"]]
        if s["type"] == 8:
            return "bss"
        if s["flags"] & EXEC:
            return "asm"
        if s["flags"] & WRITE:
            return "data"
        return "rodata"

    # 按 PT_LOAD 边界分组（美版 1 组；日版 2 组）
    groups = []
    for L in loads:
        gs = [s for s in alloc if L["vstart"] <= s["addr"] < L["vmem"]]
        if gs:
            groups.append((L, gs))
    names = ["cod", "dat"] + ["seg%d" % i for i in range(2, len(groups))]

    gp = None
    for s in secs:
        if s["name"] == ".reginfo" and s["size"] >= 0x18:
            # EE .reginfo：最后 4 字节是 gp 值（美版/日版实测均如此）
            gp = struct.unpack_from("<I", d, s["off"] + s["size"] - 4)[0]

    def gname(i):
        return names[i]

    # 链接脚本里的 gp 表达式：<group>_SDATA_START + 0x7FF0
    gp_expr = None
    for i, (L, gs) in enumerate(groups):
        if any(s["name"] == ".sdata" for s in gs):
            gp_expr = "%s_SDATA_START + 0x7FF0" % gname(i)
            break

    lines = []
    lines.append("# name: 魔塔大陆2 日版 (Ar tonelico II, Japan) -- 路线 B 可重建基线")
    lines.append("# 生成器: routebjp/tools/gen_splat_yaml_jp.py（从 ELF 节表/程序头推导）")
    lines.append("# sha1 = 拼接全部 PT_LOAD 段（与 build.sh 的载荷抽取口径一致）")
    lines.append("sha1: %s" % rom_sha1)
    lines.append("options:")
    lines.append("  basename: %s" % name)
    lines.append("  target_path: %s.rom" % name)
    lines.append("  elf_path: build/%s.elf" % name)
    lines.append("  base_path: .")
    lines.append("  platform: ps2")
    lines.append("  compiler: EEGCC")
    lines.append("")
    lines.append("  gp_value: 0x%08X" % gp)
    lines.append("  ld_gp_expression: %s" % gp_expr)
    lines.append("")
    lines.append("  ld_script_path: build/%s.ld" % name)
    lines.append("  ld_dependencies: True")
    lines.append("  ld_wildcard_sections: True")
    lines.append("  ld_bss_contains_common: True")
    lines.append("")
    lines.append("  create_asm_dependencies: True")
    lines.append("  disassemble_all: True")
    lines.append("  make_full_disasm_for_code: True")
    lines.append("")
    lines.append("  find_file_boundaries: False")
    lines.append("")
    lines.append("  o_as_suffix: True")
    lines.append("")
    lines.append("  symbol_addrs_path:")
    lines.append("    - config/symbol_addrs.txt")
    lines.append("  reloc_addrs_path:")
    lines.append("    - config/reloc_addrs.txt")
    lines.append("")
    lines.append("  extensions_path: tools/splat_ext")
    lines.append("")
    lines.append("  string_encoding: ASCII")
    lines.append("  data_string_encoding: ASCII")
    lines.append("  rodata_string_guesser_level: 2")
    lines.append("  data_string_guesser_level: 2")
    lines.append("")
    lines.append("  named_regs_for_c_funcs: False")
    lines.append("")
    lines.append("  # 数值寄存器名（$4 而非 $a0）：绕开 binutils 2.45 拒绝 $t4–$t7 的坑，")
    lines.append("  # 与美版一致（DCDecomp 同款 mips_abi_gpr: numeric）。")
    lines.append("  mips_abi_gpr: numeric")
    lines.append("")
    lines.append("  section_order:")
    lines.append("    - .text")
    lines.append("    - .data")
    lines.append("    - .rodata")
    lines.append("    - .sdata")
    lines.append("    - .sbss")
    lines.append("    - .bss")
    lines.append("")
    lines.append("  auto_link_sections:")
    lines.append("    - .data")
    lines.append("    - .rodata")
    lines.append("    - .sdata")
    lines.append("    - .sbss")
    lines.append("    - .bss")
    lines.append("")
    lines.append("segments:")

    for i, (L, gs) in enumerate(groups):
        gn = gname(i)
        rom_start = L["rom"]
        vram = L["vstart"]
        bss_size = sum(s["size"] for s in gs if s["type"] == 8)
        lines.append("  - name: %s" % gn)
        lines.append("    type: code")
        lines.append("    start: 0x%06X" % rom_start)
        lines.append("    vram: 0x%08X" % vram)
        lines.append("    bss_size: 0x%X" % bss_size)
        lines.append("    subalign: null")
        lines.append("    subsegments:")

        text = [s for s in gs if s["name"] == ".text"]
        if text:
            ts = text[0]
            tstart_va = ts["addr"]
            tend_va = ts["addr"] + ts["size"]
            in_text = sorted(a for a in funcs if tstart_va <= a < tend_va)
            if in_text and in_text[0] > tstart_va:
                lines.append("      - [0x%X, asm, %s/head]   # 段起点到首个函数之间的头部"
                             % (va2rom(loads, tstart_va), gn))
            elif not in_text:
                lines.append("      - [0x%X, asm, %s/head]" % (va2rom(loads, tstart_va), gn))
            for a in in_text:
                fn = funcs[a][0]
                lines.append("      - {start: 0x%X, type: asmtu, name: %s/%s}"
                             % (va2rom(loads, a), gn, fn))
            if in_text:
                last = in_text[-1]
                last_end = last + funcs[last][1]
                if last_end < tend_va:
                    lines.append("      - [0x%X, asm, %s/tail]   # .text 尾部对齐/填充区"
                                 % (va2rom(loads, last_end), gn))
        # .init/.fini/.vutext/.ctors/... 及数据/rodata/sdata/bss 节
        for s in gs:
            if s["name"] == ".text":
                continue
            st = splat_type(s)
            if s["type"] == 8:
                lines.append("      - { type: %s, vram: 0x%08X, name: %s/%08X } # %s"
                             % (st, s["addr"], gn, s["addr"], s["name"]))
            else:
                lines.append("      - [0x%X, %s, %s/%06X] # %s"
                             % (va2rom(loads, s["addr"]), st, gn, va2rom(loads, s["addr"]),
                                s["name"]))
    lines.append("  - [0x%X]" % rom_size)
    open(out_yaml, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("写出 %s" % out_yaml)
    print("组数 = %d ; 组名 = %s" % (len(groups), names[:len(groups)]))
    print("rom_size(拼 PT_LOAD) = 0x%X (%d B)" % (rom_size, rom_size))
    print("gp = 0x%08X ; ld_gp_expression = %s" % (gp, gp_expr))
    for i, (L, gs) in enumerate(groups):
        print("  [%s] rom 0x%06X vram 0x%08X bss 0x%X sections=%s"
              % (gname(i), L["rom"], L["vstart"], sum(s["size"] for s in gs if s["type"] == 8),
                 ",".join(s["name"] for s in gs)))


if __name__ == "__main__":
    main()
