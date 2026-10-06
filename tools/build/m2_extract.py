#!/usr/bin/env python3
"""从 splat 的 asm 里抽出指定函数，拼成一个用于 objdiff 对照的 target .s。

为什么需要：M1 的 splat 输出把整个 .text 放在一个 .s 里（78 万行）。
objdiff 是按**符号**比对的，所以只要把待 C 化的那几个函数抽到一个小 .s、
单独汇编成 target.o，就可以和 C 编译出的 base.o 逐符号对照。

用法: python3 tools/build/m2_extract.py <splat_asm_dir> <out.s> <符号名> [符号名...]
"""
import os, re, sys

def main():
    asm_dir, out_s = sys.argv[1], sys.argv[2]
    want = set(sys.argv[3:])
    if not want:
        print(__doc__); return 2

    # splat 的输出可能分成多个 .s，全部扫一遍
    files = []
    for root, _, fns in os.walk(asm_dir):
        for f in sorted(fns):
            if f.endswith('.s'):
                files.append(os.path.join(root, f))

    found = {}
    for path in files:
        lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
        cur, body, keep = None, [], False
        for l in lines:
            gm = re.match(r'\s*glabel\s+(\S+)', l)
            if gm:
                cur, body = gm.group(1), []
            if cur in want:
                keep = True
            if re.match(r'\s*endlabel\s+(\S+)', l):
                em = re.match(r'\s*endlabel\s+(\S+)', l)
                if em and em.group(1) in want:
                    found[em.group(1)] = '\n'.join(body)
                cur, body, keep = None, [], False
                continue
            if keep and cur:
                body.append(l.rstrip())
        # 实测有 54 个 glabel 位于文件末尾、splat 没写 endlabel（nonmatching 尾巴函数）：
        # 语义上它一直延伸到文件结束，这里补上，否则这些函数会被静默丢掉。
        if cur is not None and cur in want and cur not in found:
            found[cur] = '\n'.join(body)

    missing = want - set(found)
    if missing:
        print("未找到: %s" % ', '.join(sorted(missing)), file=sys.stderr)

    with open(out_s, 'w', encoding='utf-8') as f:
        f.write('.include "macro.inc"\n\n')
        f.write('.set noat\n.set noreorder\n\n.section .text, "ax"\n\n')
        for name in sys.argv[3:]:
            if name in found:
                f.write('glabel %s\n' % name)
                f.write(found[name] + '\n')
                f.write('endlabel %s\n\n' % name)
    print("抽出 %d 个函数 -> %s" % (len(found), out_s))
    return 0

if __name__ == '__main__':
    sys.exit(main())
