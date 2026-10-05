#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路线 C 调研 —— 可复现测量脚本（只读：不修改任何游戏文件）

用途：
  1) 从主程序 SLUS_217.88 解析资产清单（path 字符串池 + {name,id,size} 记录表）
  2) 统计 US 版英文文本量（注意：US 版英文以 **全角 Shift-JIS** 存储）
  3) 从 RPK.BIN 直接测量剧情文本量，并定位 .evd 数据区

用法：
  python3 tools/report/c_route_measure.py elf  <out/binaries/SLUS_217.88>
  python3 tools/report/c_route_measure.py erf  <out/binaries/erx>            # 目录，含 *.ERX
  python3 tools/report/c_route_measure.py rpk  <ISO> <RPK_LBA> <RPK_SIZE>

依赖：无（仅标准库）。RPK 扫描 662 MB 约 40 秒。
"""
import sys, os, re, json, struct, collections

# ---------------------------------------------------------------- helpers
FW_PAIR = b'[\x81-\x9f\xe0-\xef][\x40-\xfc]'
NAME_RUN = re.compile(b'(?<=\x00)((?:[\x20-\x7e]|' + FW_PAIR + b'){6,})(?=\x00)')


def is_fullwidth(ch):
    return '\uff01' <= ch <= '\uff5e' or ch == '\u3000'


def fw_count(t):
    return sum(1 for ch in t if is_fullwidth(ch))


def sjis_strings(buf, minbytes=6):
    """提取 NUL 结尾、含非 ASCII 的 Shift-JIS 串（US 版的英文是全角，必含非 ASCII）"""
    out, i, n = [], 0, len(buf)
    while i < n:
        j, s = i, bytearray()
        while j < n:
            c = buf[j]
            if c == 0:
                break
            if c < 0x80:
                s.append(c); j += 1
            elif 0x81 <= c <= 0x9f or 0xe0 <= c <= 0xef:
                if j + 1 < n and 0x40 <= buf[j + 1] <= 0xfc and buf[j + 1] != 0x7f:
                    s += buf[j:j + 2]; j += 2
                else:
                    break
            else:
                break
        if len(s) >= minbytes and buf[j:j + 1] == b'\x00' and any(c >= 0x80 for c in s):
            try:
                out.append((i, s.decode('shift_jis')))
            except UnicodeDecodeError:
                pass
            i = j + 1
        else:
            i = i + 1 if not s else j
    return out


def text_stats(pairs, label):
    chars = sum(len(t) for _, t in pairs)
    cr = sum(t.count('CR') for _, t in pairs)
    print('%-28s strings=%6d chars=%8d CR=%5d ~lines=%6d'
          % (label, len(pairs), chars, cr, len(pairs) + cr))
    return {'strings': len(pairs), 'chars': chars, 'cr': cr}


# ---------------------------------------------------------------- 1) ELF 清单
def elf_manifest(path):
    elf = open(path, 'rb').read()
    shoff, = struct.unpack_from('<I', elf, 0x20)
    shnum, shstrndx = struct.unpack_from('<HH', elf, 0x30)
    secs = []
    for i in range(shnum):
        o = shoff + i * 40
        secs.append(struct.unpack_from('<IIIIIIIIII', elf, o))
    for s in secs:
        if s[4] <= 0x70e300 < s[4] + s[5]:
            RO = (s[3], s[3] + s[5])          # .rodata vaddr 区间
        if s[4] <= 0x278a80 < s[4] + s[5]:
            DATA = (s[4], s[4] + s[5])        # .data 文件区间
    VA_OFF = 0xff000                          # vaddr = fileoff + 0xFF000（PT_LOAD off 0x1000 ↔ va 0x100000）

    def nm(n):
        if not (RO[0] <= n < RO[1]):
            return None
        o = n - VA_OFF
        z = elf.find(b'\x00', o, o + 16)
        if z < 0:
            return None
        b = elf[o:z]
        if not b or any(not (0x20 <= c < 0x7f) for c in b):
            return None
        return b.decode('ascii') if (b'/' in b or b'.' in b) else None

    vset = set()
    for i in range(DATA[0], DATA[1], 4):
        if nm(struct.unpack_from('<I', elf, i)[0]):
            vset.add(i)
    tables = []
    for p in sorted(vset):
        if (p - 12) in vset:
            continue
        recs, q = [], p
        while q in vset:
            n, x, y = struct.unpack_from('<III', elf, q)
            recs.append({'name': nm(n), 'id': x, 'size': y}); q += 12
        if len(recs) >= 4:
            tables.append((p, recs))
    return elf, tables


def cmd_elf(path):
    elf, tables = elf_manifest(path)
    print('== 记录表（{char* name; u32 id; u32 size}，12 B/条）==')
    for p, recs in tables:
        d = collections.Counter(r['name'].split('/')[0] for r in recs)
        print('  @%#x n=%5d Σsize=%d %s' % (p, len(recs), sum(r['size'] for r in recs), dict(d)))
    ev = [r for _, recs in tables for r in recs if r['name'].lower().endswith('.evd')]
    if ev:
        al = [(r['size'] + 2047) // 2048 * 2048 for r in ev]
        print('\n== .evd 语料 ==')
        print('  files=%d  Σsize=%d  Σalign2048=%d  min=%d max=%d'
              % (len(ev), sum(r['size'] for r in ev), sum(al),
                 min(r['size'] for r in ev), max(r['size'] for r in ev)))
    print('\n== 主程序英文文本（全角）==')
    run = re.compile(r'[\uff21-\uff3a\uff41-\uff5a\uff10-\uff19]{4,}')
    L = [(o, t) for o, t in sjis_strings(elf) if run.search(t)]
    print('  full-width strings=%d chars=%d' % (len(L), sum(len(t) for _, t in L)))
    prose = [(o, t) for o, t in L if '\u3000' in t and len(t) >= 12 and t.count('\u3000') >= 2]
    text_stats(prose, '  ELF prose-like')


# ---------------------------------------------------------------- 2) ERX
def cmd_erx(d):
    data = ['HKDATA', 'MKDATA', 'MIXMESS', 'QADATA', 'QVDATAE']
    btl = ['BTLS_M', 'BTLS_P', 'BTLS_PTS', 'BTLS_S', 'BTLS_TST']
    for grp, names in (('数据模块', data), ('战斗模块', btl)):
        pairs = []
        for f in names:
            p = os.path.join(d, f + '.ERX')
            if os.path.exists(p):
                pairs += [(0, t) for _, t in sjis_strings(open(p, 'rb').read())]
        print('== ERX %s ==' % grp)
        text_stats(pairs, '  ' + grp)


# ---------------------------------------------------------------- 3) RPK
def cmd_rpk(iso, lba, size):
    base = int(lba) * 2048
    f = open(iso, 'rb')
    CH, OVER = 1 << 24, 64
    f.seek(base); off, carry = 0, b''
    hits = []
    while off < size:
        d = carry + f.read(min(CH, size - off))
        for m in NAME_RUN.finditer(d):
            s = m.group(1)
            try:
                t = s.decode('shift_jis')
            except UnicodeDecodeError:
                continue
            if fw_count(t) < 6:
                continue
            hits.append((off + len(carry) + m.start(1), t))
        carry = d[-OVER:]; off += len(d) - OVER
    print('== RPK.BIN 全角文本 ==')
    print('  strings=%d chars=%d' % (len(hits), sum(len(t) for _, t in hits)))
    # 嵌入 ERX 模块区间（已核实的固定位置）
    E0, E1 = 0x1FD80000, 0x20226000
    for nm, a, b in (('  AFS 区 0..289MB', 0, 289280000),
                     ('  LZR 区 289..533MB', 289280000, E0),
                     ('  嵌入 ERX 区', E0, E1),
                     ('  .evd 区（余下）', E1, size)):
        sub = [t for o, t in hits if a <= o < b]
        print('%-22s strings=%6d chars=%8d' % (nm, len(sub), sum(len(t) for t in sub)))
    aft = [(o, t) for o, t in hits if o >= E1]
    if aft:
        lo, hi = min(o for o, _ in aft), max(o for o, _ in aft)
        print('  .evd 文本跨度 %#x..%#x = %d B' % (lo, hi, hi - lo))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    mode = sys.argv[1]
    if mode == 'elf':
        cmd_elf(sys.argv[2])
    elif mode == 'erx':
        cmd_erx(sys.argv[2])
    elif mode == 'rpk':
        cmd_rpk(sys.argv[2], sys.argv[3], int(sys.argv[4]))
