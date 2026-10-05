#!/usr/bin/env python3
"""Disassembly statistics for the PS2 EE (R5900) main program.

- linear sweep of every executable PROGBITS section with capstone (MIPS32/MIPS3)
- raw-opcode (bits 31:26) histogram, independent of the disassembler, so that
  R5900-only extensions are counted even if capstone does not know them:
      opcode 0x12 = COP2  (VU0 macro mode when rs bit4 == 0 -> VU0)
      opcode 0x1C = SPECIAL2 (MMI: paddw/psubw/pcpyld/pmpyh/...)
      opcode 0x1E = LQ, opcode 0x1F = SQ  (128-bit MMI loads/stores)
      opcode 0x1B = SPECIAL3
- histogram of capstone mnemonics, jal/jr conventions, jump tables
- byte entropy per section (obfuscation / compression check)
- invalid-instruction ratio

Usage: python3 disasm_stats.py <elf> <out.json>
"""
import struct, sys, json, collections, math

SEG_OFF, SEG_VA = 0x1000, 0x100000

def va2off(v): return v - SEG_VA + SEG_OFF

def entropy(b):
    if not b: return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def main():
    elf, out = sys.argv[1], sys.argv[2]
    d = open(elf, 'rb').read()
    ej = json.load(open(elf.replace('.', '_').replace('out_', 'out/') + '.json')) if False else None
    # find json next to elf
    import os
    for cand in ('out/evidence/elf_SLUS.json', 'out/evidence/elf_SLPS.json'):
        if os.path.exists(cand):
            e = json.load(open(cand))
            if e['md5'] == __import__('hashlib').md5(d).hexdigest():
                ej = e; break
    if ej is None:
        raise SystemExit('cannot find matching elf json')
    secs = [s for s in ej['shdrs'] if not s.get('truncated')]

    from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_MIPS3, CS_MODE_LITTLE_ENDIAN
    md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_MIPS3 | CS_MODE_LITTLE_ENDIAN)

    OPNAME = {0x00:'SPECIAL',0x01:'REGIMM(bltz..)',0x02:'j',0x03:'jal',0x04:'beq',
              0x05:'bne',0x06:'blez',0x07:'bgtz',0x08:'addi',0x09:'addiu',0x0a:'slti',
              0x0b:'sltiu',0x0c:'andi',0x0d:'ori',0x0e:'xori',0x0f:'lui',0x10:'COP0',
              0x11:'COP1',0x12:'COP2/VU0',0x13:'COP1X/COP3',0x14:'beql',0x15:'bnel',
              0x16:'blezl',0x17:'bgtzl',0x18:'daddi',0x19:'daddiu',0x1a:'ldl',
              0x1b:'SPECIAL3/ldr',0x1c:'SPECIAL2(MMI)',0x1d:'jalx',0x1e:'LQ',0x1f:'SQ',
              0x20:'lb',0x21:'lh',0x22:'lwl',0x23:'lw',0x24:'lbu',0x25:'lhu',
              0x26:'lwr',0x27:'lwu',0x28:'sb',0x29:'sh',0x2a:'swl',0x2b:'sw',
              0x2c:'sdl',0x2d:'sdr',0x2e:'swr',0x2f:'cache',0x30:'ll',0x31:'lwc1',
              0x32:'lwc2',0x33:'pref/lwc3',0x34:'lld',0x35:'ldc1',0x36:'ldc2',
              0x37:'ld',0x38:'sc',0x39:'swc1',0x3a:'swc2',0x3b:'swc3',0x3c:'scd',
              0x3d:'sdc1',0x3e:'sdc2',0x3f:'sd'}
    SPECIAL2_MMI = {0x00:'madd',0x01:'maddu',0x02:'mul',0x04:'plzcw',0x08:'madd1',
                    0x09:'maddu1',0x20:'paddw',0x21:'psubw',0x24:'pcpyld',0x25:'pcpyud',
                    0x26:'pand',0x27:'pxor',0x28:'pextlw',0x29:'ppacw',0x2a:'pnor',
                    0x2b:'pextlh',0x2c:'pextlb',0x2d:'pextub',0x2e:'pextuw',
                    0x30:'paddh',0x31:'psubh',0x34:'pcpyh',0x35:'paddb',0x36:'psubb',
                    0x3c:'pexew',0x3d:'pexch',0x3e:'pexcw',0x3f:'pexoh'}

    stats = {}
    for sname in ('.text', '.init', '.fini'):
        s = next((x for x in secs if x['name'] == sname), None)
        if not s: continue
        o, sz = s['offset'], s['size']
        blob = d[o:o+sz]
        opc = collections.Counter()
        mne = collections.Counter()
        invalid = 0
        n = sz // 4
        for i in range(0, n*4, 4):
            w = struct.unpack_from('<I', blob, i)[0]
            opc[(w >> 26) & 0x3f] += 1
        # capstone
        for ins in md.disasm(blob, s['addr']):
            mne[ins.mnemonic] += 1
        decoded = sum(mne.values())
        invalid = n - decoded
        stats[sname] = dict(vaddr=s['addr'], size=sz, words=n,
                            entropy=entropy(blob),
                            opcode_hist={OPNAME.get(k, 'op%d' % k): v for k, v in opc.most_common()},
                            mnemonic_hist=mne.most_common(60),
                            decoded=decoded, invalid=invalid,
                            invalid_pct=100.0*invalid/n if n else 0)
        print('=== %s  vaddr=0x%06x size=0x%x words=%d entropy=%.4f' % (
            sname, s['addr'], sz, n, stats[sname]['entropy']))
        print('  decoded=%d  invalid/undef=%d (%.2f%%)' % (decoded, invalid, stats[sname]['invalid_pct']))
        print('  -- opcode(31:26) histogram --')
        tot = n or 1
        for k, v in opc.most_common(20):
            print('     %-16s %8d  %5.2f%%' % (OPNAME.get(k, 'op%d' % k), v, 100.0*v/tot))
        print('  -- MMI/SPECIAL2 sub-funct histogram --')
        sub = collections.Counter()
        for i in range(0, n*4, 4):
            w = struct.unpack_from('<I', blob, i)[0]
            if (w >> 26) == 0x1c:
                sub[SPECIAL2_MMI.get(w & 0x3f, 'sp2:%02x' % (w & 0x3f))] += 1
        for k, v in sub.most_common(20):
            print('     %-16s %8d' % (k, v))
        print('  -- top 25 capstone mnemonics --')
        for k, v in mne.most_common(25):
            print('     %-16s %8d  %5.2f%%' % (k, v, 100.0*v/max(decoded,1)))
        # call convention
        print('  -- control flow --')
        for name in ('jal', 'jalr', 'jr', 'j', 'b', 'beq', 'bne', 'bal', 'bc1f', 'bc1t'):
            if mne.get(name): print('     %-16s %8d' % (name, mne[name]))
        stats[sname]['opcode_hist_raw'] = {OPNAME.get(k, 'op%d' % k): v for k, v in opc.items()}
        stats[sname]['mmi_subfunct'] = dict(sub)
    json.dump(stats, open(out, 'w'), indent=1)
    print('\n-> %s' % out)

if __name__ == '__main__':
    main()
