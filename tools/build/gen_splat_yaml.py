#!/usr/bin/env python3
"""生成带 per-function 子段的 splat 配置。

背景：splat 的 `asm` 子段按「段」切分——整个 .text 会变成一个 78 万行的 .s。
要做逐函数替换为 C 的工作流，需要每个函数一个独立 .s。DCDecomp 的做法是把
每个函数列成一个 `type: asmtu` 子段（见其 config/ntsc/main.yaml）。

本脚本按 symbol_addrs.txt 的函数边界生成这些子段，非函数区段（.init/.fini/
.vutext/data/rodata/...）沿用原配置。

用法: python3 tools/build/gen_splat_yaml.py <原yaml> <symbol_addrs> <输出yaml>
"""
import os, re, sys

TEXT_VADDR = 0x100000
TEXT_END = 0x36E028          # .init 起点


def load_funcs(path):
    """从 symbol_addrs 读出 type:func 的 addr -> (name, size)。"""
    out = {}
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^\s*(\S+)\s*=\s*(0x[0-9a-fA-F]+)\s*;\s*//\s*type:func\s+size:0x([0-9a-fA-F]+)', line)
        if m:
            out[int(m.group(2), 16)] = (m.group(1), int(m.group(3), 16))
    return out


def main():
    src_yaml, sym_path, out_yaml = sys.argv[1:4]
    funcs = load_funcs(sym_path)
    print("函数数 = %d" % len(funcs))

    lines = open(src_yaml, encoding='utf-8').read().split('\n')

    # 找到 `subsegments:` 之后、第一个非缩进更深的行之前的区间，整体替换
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

    # 1) .text：每个函数一个 asmtu 子段
    in_text = sorted(a for a in funcs if TEXT_VADDR <= a < TEXT_END)
    # 段起点到首个函数之间的头部（通常是 0x100000 处的少量对齐数据）
    if in_text and in_text[0] > TEXT_VADDR:
        new.append('%s- [0x0, asm, cod/head]   # 段起点到首个函数之间的头部' % ind)
    for a in in_text:
        name = funcs[a][0]
        new.append('%s- {start: 0x%X, type: asmtu, name: cod/%s}' % (ind, a - TEXT_VADDR, name))
    # 末个函数的结束地址到 .init 之间的尾部填充
    if in_text:
        last = in_text[-1]
        last_end = last + funcs[last][1]
        if last_end < TEXT_END:
            new.append('%s- [0x%X, asm, cod/tail]   # .text 尾部对齐/填充区' % (ind, last_end - TEXT_VADDR))

    # 2) 非函数区段：从原配置里照抄（.init/.fini/.vutext/data/rodata/...）
    # ⚠️ 必须同时跳过**本脚本上一次生成的内容**，否则重复运行会不断翻倍
    # （实测：10,950 → 21,900 → 32,850）。跳过规则：
    #   - `# .text` 注释行（原配置里的整段 .text）
    #   - 已存在的 `type: asmtu` 行
    #   - 本脚本生成的 head/tail 占位段
    skipped = 0
    for l in lines[start + 1:end]:
        if re.search(r'#\s*\.text', l) or 'type: asmtu' in l \
           or re.search(r'cod/(head|tail)\b', l):
            skipped += 1
            continue
        new.append(l)
    if skipped:
        print("跳过上一次生成的 %d 行（保证幂等）" % skipped)

    lines[start:end] = new
    open(out_yaml, 'w', encoding='utf-8').write('\n'.join(lines))

    n_asmtu = sum(1 for l in new if 'type: asmtu' in l)
    print("asmtu 子段 = %d" % n_asmtu)
    print("写出 = %s" % out_yaml)


if __name__ == '__main__':
    main()
