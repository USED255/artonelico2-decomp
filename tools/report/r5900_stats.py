#!/usr/bin/env python3
"""R5900-aware instruction statistician for PS2 EE binaries.

capstone is NOT R5900 aware (it mis-decodes SPECIAL2/MMI, LQ/SQ and COP2
macro-mode), so all classification here is done from the raw 32-bit words
using the R5900 bit fields.  A mnemonic histogram built from those tables is
much closer to the real EE instruction mix than capstone's output; the
capstone comparison is printed as well so the difference is visible.

Usage: python3 r5900_stats.py <elf> <out.json>
"""
import struct, sys, json, collections, math, hashlib, os

SP_FUNCT = {0x00:'sll',0x02:'srl',0x03:'sra',0x04:'sllv',0x06:'srlv',0x07:'srav',
 0x08:'jr',0x09:'jalr',0x0a:'movz',0x0b:'movn',0x0c:'syscall',0x0d:'break',0x0f:'sync',
 0x10:'mfhi',0x11:'mthi',0x12:'mflo',0x13:'mtlo',0x14:'dsllv',0x16:'dsrlv',0x17:'dsrav',
 0x18:'mult',0x19:'multu',0x1a:'div',0x1b:'divu',0x1c:'dmult',0x1d:'dmultu',0x1e:'ddiv',0x1f:'ddivu',
 0x20:'add',0x21:'addu',0x22:'sub',0x23:'subu',0x24:'and',0x25:'or',0x26:'xor',0x27:'nor',
 0x28:'mfsa',0x29:'mtsa',0x2a:'slt',0x2b:'sltu',0x2c:'dadd',0x2d:'daddu',0x2e:'dsub',0x2f:'dsubu',
 0x30:'tge',0x31:'tgeu',0x32:'tlt',0x33:'tltu',0x34:'teq',0x36:'tne',
 0x38:'dsll',0x3a:'dsrl',0x3b:'dsra',0x3c:'dsll32',0x3e:'dsrl32',0x3f:'dsra32'}
REGIMM = {0x00:'bltz',0x01:'bgez',0x02:'bltzl',0x03:'bgezl',0x08:'tgei',0x09:'tgeiu',
 0x0a:'tlti',0x0b:'tltiu',0x0c:'teqi',0x0e:'tnei',0x10:'bltzal',0x11:'bgezal',
 0x12:'bltzall',0x13:'bgezall',0x18:'mtsab',0x19:'mtsah'}
SP2 = {0x00:'madd',0x01:'maddu',0x02:'mul',0x04:'plzcw',0x08:'madd1',0x09:'maddu1',
 0x10:'mfhi1',0x11:'mthi1',0x12:'mflo1',0x13:'mtlo1',
 0x20:'paddw',0x21:'psubw',0x22:'pcgtw',0x23:'pmaxw',0x24:'pcpyld',0x25:'pcpyud',
 0x26:'pand',0x27:'pxor',0x28:'pextlw',0x29:'ppacw',0x2a:'pnor',0x2b:'pextlh',
 0x2c:'pextlb',0x2d:'pextub',0x2e:'pextuw',0x30:'paddh',0x31:'psubh',0x32:'pcgth',
 0x33:'pmaxh',0x34:'pcpyh',0x35:'paddb',0x36:'psubb',0x37:'pcgtb',
 0x3c:'pexew',0x3d:'pexch',0x3e:'pexcw',0x3f:'pexoh'}
COP2_RS = {0x00:'mfc2',0x02:'cfc2',0x04:'mtc2',0x06:'ctc2',0x08:'bc2f/bc2t',
 0x10:'VU0-macro(rs=0x10)',0x11:'VU0-macro(rs=0x11)',0x12:'VU0-macro(rs=0x12)',
 0x13:'VU0-macro(rs=0x13)',0x14:'qpmi(rs=0x14)',0x15:'qmfc2(rs=0x15)',
 0x16:'qmtc2(rs=0x16)',0x17:'VU0-macro(rs=0x17)'}
# VU0 macro-mode "upper" opcode (bits 5:0) - the VU upper instruction opcode
VU_UPPER = {0x00:'VADD?/NOP',0x28:'VADD',0x29:'VSUB',0x2a:'VMUL',0x2b:'VMAX',0x2c:'VMINI',
 0x2d:'VMULq',0x2e:'VADDq',0x2f:'VMADDI',0x30:'VADDI',0x31:'VSUBI',0x32:'VMULI',
 0x33:'VMAXI',0x34:'VABS',0x35:'VMSUB',0x36:'VMSUBq',0x37:'VOPMSUB',0x38:'VIADD',
 0x39:'VISUB',0x3a:'VIADDI',0x3b:'VIAND',0x3c:'VIOR',0x3d:'VCALLMS',0x3e:'VCALLMSR',
 0x3f:'VADDq'}
OPC = {0x00:'SPECIAL',0x01:'REGIMM',0x02:'j',0x03:'jal',0x04:'beq',0x05:'bne',0x06:'blez',
 0x07:'bgtz',0x08:'addi',0x09:'addiu',0x0a:'slti',0x0b:'sltiu',0x0c:'andi',0x0d:'ori',
 0x0e:'xori',0x0f:'lui',0x10:'cop0',0x11:'cop1',0x12:'COP2',0x13:'cop1x/cop3',
 0x14:'beql',0x15:'bnel',0x16:'blezl',0x17:'bgtzl',0x18:'daddi',0x19:'daddiu',0x1a:'ldl',
 0x1b:'ldr',0x1c:'SPECIAL2/MMI',0x1d:'jalx',0x1e:'LQ',0x1f:'SQ',0x20:'lb',0x21:'lh',
 0x22:'lwl',0x23:'lw',0x24:'lbu',0x25:'lhu',0x26:'lwr',0x27:'lwu',0x28:'sb',0x29:'sh',
 0x2a:'swl',0x2b:'sw',0x2c:'sdl',0x2d:'sdr',0x2e:'swr',0x2f:'cache',0x30:'ll',0x31:'lwc1',
 0x32:'lwc2',0x33:'pref',0x34:'lld',0x35:'ldc1',0x36:'ldc2',0x37:'ld',0x38:'sc',0x39:'swc1',
 0x3a:'swc2',0x3b:'swc3',0x3c:'scd',0x3d:'sdc1',0x3e:'sdc2',0x3f:'sd'}

def entropy(b):
    c = collections.Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0.0

def decode(word):
    """return mnemonic string for a raw R5900 word"""
    op = word >> 26; rs = (word>>21)&0x1f; rt = (word>>16)&0x1f
    rd = (word>>11)&0x1f; sa = (word>>6)&0x1f; fn = word & 0x3f
    if op == 0x00: return SP_FUNCT.get(fn, 'SPECIAL:%02x' % fn)
    if op == 0x01: return REGIMM.get(rt, 'REGIMM:rt%02x' % rt)
    if op == 0x1c: return SP2.get(fn, 'SP2:%02x(sa%02x)' % (fn, sa))
    if op == 0x12:
        if rs & 0x10: return 'VU0MACRO:' + VU_UPPER.get(fn, '%02x' % fn) + '/lo%02x' % sa
        return COP2_RS.get(rs, 'COP2:rs%02x' % rs)
    return OPC.get(op, 'op%02x' % op)

def main():
    elf, out = sys.argv[1], sys.argv[2]
    d = open(elf, 'rb').read()
    h = hashlib.md5(d).hexdigest()
    e = None
    for c in ('out/evidence/elf_SLUS.json', 'out/evidence/elf_SLPS.json'):
        if os.path.exists(c) and json.load(open(c))['md5'] == h:
            e = json.load(open(c)); break
    assert e, 'no matching elf json'
    secs = {s['name']: s for s in e['shdrs'] if not s.get('truncated')}

    res = {}
    for sname in ('.text', '.init', '.fini', '.vutext'):
        s = secs.get(sname)
        if not s or s['size'] == 0: continue
        blob = d[s['offset']:s['offset']+s['size']]
        n = len(blob)//4
        opch = collections.Counter(); mne = collections.Counter()
        sp = collections.Counter(); sp2 = collections.Counter(); sp2sa = collections.Counter()
        cop2 = collections.Counter(); cop2fn = collections.Counter(); cop2lo = collections.Counter()
        regimm = collections.Counter()
        jal_targets = collections.Counter()
        indirect = 0; jr_ra = 0
        micro_upload = 0
        for i in range(n):
            w = struct.unpack_from('<I', blob, i*4)[0]
            op = w >> 26
            opch[OPC.get(op, 'op%02x' % op)] += 1
            m = decode(w); mne[m] += 1
            if op == 0x00:
                fn = w & 0x3f; sp[SP_FUNCT.get(fn, 'SPECIAL:%02x' % fn)] += 1
                if fn == 0x08:
                    if ((w>>21)&0x1f) == 31: jr_ra += 1
                    else: indirect += 1
                if fn in (0x18,0x19,0x1a,0x1b): pass
            elif op == 0x01:
                regimm[REGIMM.get((w>>16)&0x1f, 'REGIMM:%02x' % ((w>>16)&0x1f))] += 1
            elif op == 0x1c:
                fn = w & 0x3f; sa = (w>>6)&0x1f
                sp2[SP2.get(fn, 'SP2:%02x' % fn)] += 1
                sp2sa[(fn, sa)] += 1
            elif op == 0x12:
                rs = (w>>21)&0x1f; fn = w & 0x3f; sa = (w>>6)&0x1f
                if rs & 0x10:
                    cop2['VU0-macro'] += 1
                    cop2fn[VU_UPPER.get(fn, 'upper%02x' % fn)] += 1
                    cop2lo['lo%02x' % sa] += 1
                else:
                    cop2[COP2_RS.get(rs, 'rs%02x' % rs)] += 1
            elif op == 0x03:
                jal_targets[((w & 0x03ffffff) << 2) | (s['addr'] & 0xf0000000)] += 1
            if op == 0x0f and ((w & 0xffff) == 0x1100):
                micro_upload += 1
        # capstone comparison
        from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN
        md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 | CS_MODE_LITTLE_ENDIAN)
        cs_mne = collections.Counter(); cs_n = 0
        pos = 0
        while pos < len(blob):
            got = list(md.disasm(blob[pos:pos+4], s['addr']+pos))
            if got:
                cs_mne[got[0].mnemonic] += 1; cs_n += 1
            pos += 4
        res[sname] = dict(vaddr=s['addr'], size=s['size'], words=n, entropy=entropy(blob),
                          opcode=dict(opch), mnemonic=dict(mne), special=dict(sp),
                          special2=dict(sp2), cop2=dict(cop2),
                          cop2_vu_upper=dict(cop2fn), cop2_vu_lower=dict(cop2lo),
                          regimm=dict(regimm), jr_ra=jr_ra, jr_indirect=indirect,
                          micro_upload_lui=0, capstone_mnemonic=dict(cs_mne),
                          capstone_decoded=cs_n, capstone_undecoded=n-cs_n,
                          distinct_jal_targets=len(jal_targets))
        print('\n================ %s  vaddr=0x%06x size=0x%x words=%d entropy=%.4f' % (
            sname, s['addr'], s['size'], n, entropy(blob)))
        print('  R5900 mnemonic histogram (top 22 of %d distinct):' % len(mne))
        for k, v in mne.most_common(22):
            print('     %-22s %7d  %5.2f%%' % (k, v, 100.0*v/n))
        print('  opcode class histogram:')
        for k, v in opch.most_common(14):
            print('     %-22s %7d  %5.2f%%' % (k, v, 100.0*v/n))
        if sname == '.text':
            print('  SPECIAL funct (top 20):')
            for k, v in sp.most_common(20): print('     %-22s %7d' % (k, v))
            print('  SPECIAL2/MMI funct:')
            for k, v in sp2.most_common(30): print('     %-22s %7d' % (k, v))
            print('  SPECIAL2 (funct,sa) pairs:')
            for k, v in sp2sa.most_common(20): print('     funct=0x%02x sa=0x%02x %12d' % (k[0], k[1], v))
            print('  COP2 rs classes:')
            for k, v in cop2.most_common(12): print('     %-22s %7d' % (k, v))
            print('  COP2 VU0-macro upper opcodes:')
            for k, v in cop2fn.most_common(25): print('     %-22s %7d' % (k, v))
            print('  COP2 VU0-macro lower(field) opcodes:')
            for k, v in cop2lo.most_common(10): print('     %-22s %7d' % (k, v))
        print('  control flow: jr $ra=%d  jr other=%d  distinct jal targets=%d' % (
            jr_ra, indirect, len(jal_targets)))
        print('  capstone(MIPS64) decoded=%d undecoded=%d (%.2f%% not decoded)' % (
            cs_n, n-cs_n, 100.0*(n-cs_n)/n))
        print('  capstone top-10:', cs_mne.most_common(10))
    json.dump(res, open(out, 'w'), indent=1)
    print('\n-> %s' % out)

if __name__ == '__main__':
    main()
