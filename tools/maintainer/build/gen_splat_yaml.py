#!/usr/bin/env python3
"""Write a splat config with per-function subsegments.

Background: a splat `asm` subsegment splits by section. The whole .text would
become one 780,000-line .s file. A per-function replacement workflow needs one
separate .s file for each function. DCDecomp lists each function as a
`type: asmtu` subsegment (see its config/ntsc/main.yaml).

This script writes those subsegments from the function bounds in
symbol_addrs.txt. The non-function ranges (.init/.fini/.vutext/data/rodata/...)
keep the original config.

Usage: python3 tools/maintainer/build/gen_splat_yaml.py <input yaml> <symbol_addrs> <output yaml>

生成带 per-function 子段的 splat 配置：splat 的 asm 子段按段切分，整个 .text
会变成一个 78 万行的 .s；逐函数替换为 C 的工作流需要每个函数一个独立 .s。
DCDecomp 的做法是把每个函数列成一个 type: asmtu 子段。
非函数区段（.init/.fini/.vutext/data/rodata/...）沿用原配置。
"""
import os, re, sys

TEXT_VADDR = 0x100000
TEXT_END = 0x36E028          # start of .init


def load_funcs(path):
    """Read the `type:func` entries from symbol_addrs: addr -> (name, size).

    从 symbol_addrs 读出 type:func 的 addr -> (name, size)。
    """
    out = {}
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^\s*(\S+)\s*=\s*(0x[0-9a-fA-F]+)\s*;\s*//\s*type:func\s+size:0x([0-9a-fA-F]+)', line)
        if m:
            out[int(m.group(2), 16)] = (m.group(1), int(m.group(3), 16))
    return out


def main():
    src_yaml, sym_path, out_yaml = sys.argv[1:4]
    funcs = load_funcs(sym_path)
    print("functions = %d" % len(funcs))

    lines = open(src_yaml, encoding='utf-8').read().split('\n')

    # Find the range after `subsegments:` up to the first line with a smaller
    # indent. Replace the whole range.
    #
    # 找到 `subsegments:` 之后、第一个缩进更浅的行之前的区间，整体替换。
    start = next(i for i, l in enumerate(lines) if re.match(r'^\s*subsegments:', l))
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        l = lines[end]
        if l.strip() and (len(l) - len(l.lstrip())) <= base_indent:
            break
        end += 1

    ind = ' ' * (base_indent + 2)
    new = ['%ssubsegments:' % (' ' * base_indent)]

    # 1) .text: one asmtu subsegment for each function
    in_text = sorted(a for a in funcs if TEXT_VADDR <= a < TEXT_END)
    # The header between the section start and the first function. It is usually
    # a small alignment block at 0x100000.
    if in_text and in_text[0] > TEXT_VADDR:
        new.append('%s- [0x0, asm, cod/head]   # header between the section start and the first function' % ind)
    for a in in_text:
        name = funcs[a][0]
        new.append('%s- {start: 0x%X, type: asmtu, name: cod/%s}' % (ind, a - TEXT_VADDR, name))
    # The tail padding between the last function end and .init.
    if in_text:
        last = in_text[-1]
        last_end = last + funcs[last][1]
        if last_end < TEXT_END:
            new.append('%s- [0x%X, asm, cod/tail]   # .text tail alignment and padding' % (ind, last_end - TEXT_VADDR))

    # 2) Non-function sections: copy them from the source config
    #    (.init/.fini/.vutext/data/rodata/...).
    # Skip the output of a previous run of this script. Without the skip, each
    # run doubles the range (measured: 10,950 -> 21,900 -> 32,850). The skip
    # rules are:
    #   - a `# .text` comment line (the whole .text section in the source)
    #   - an existing `type: asmtu` line
    #   - the head/tail placeholder segments of this script
    #
    # 非函数区段从原配置里照抄；同时跳过本脚本上一次生成的内容，否则重复运行会
    # 不断翻倍（实测 10,950 → 21,900 → 32,850）。
    skipped = 0
    for l in lines[start + 1:end]:
        if re.search(r'#\s*\.text', l) or 'type: asmtu' in l \
           or re.search(r'cod/(head|tail)\b', l):
            skipped += 1
            continue
        new.append(l)
    if skipped:
        print("skipped %d lines from the previous run (idempotent)" % skipped)

    lines[start:end] = new
    open(out_yaml, 'w', encoding='utf-8').write('\n'.join(lines))

    n_asmtu = sum(1 for l in new if 'type: asmtu' in l)
    print("asmtu subsegments = %d" % n_asmtu)
    print("wrote = %s" % out_yaml)


if __name__ == '__main__':
    main()
