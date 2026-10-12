#!/bin/bash
# Route B (baseline build) script. This script rebuilds the Japanese SLPS_258.19 byte for byte.
#
# The pipeline is the same as the US-version build script. Three items differ:
#   1. The target binary, the payload, and the configuration are the Japanese version
#      (SLPS_258.19).
#   2. The Japanese version has two PT_LOAD segments. The splat configuration therefore uses
#      two top-level segments (cod and dat). The symbol prefix of the second group in the
#      linker script is `dat_`, and the two linker script repairs use that name.
#   3. The payload extraction does not use `objcopy -O binary`. That command fills the
#      0x80 vaddr hole between the two segments with zeros and gives 9,305,064 bytes. The
#      script uses tools/project/extract_payload.py instead. That tool concatenates all
#      PT_LOAD segments and gives 9,304,936 bytes.
#
# Prerequisite runs:
#   .tmp/splatvenv/bin/splat split SLPS_258.19.yaml
#   python3 tools/project/gen_symbol_addrs_jp.py ...        (see tools/)
#
# Tool locations (outside the workspace, third-party or copyrighted, not in the repository):
#   ~/eecc/ps2binutils/mips-ps2-decompals-{as,objcopy}
#   ~/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd

# 路线 B（baseline build）构建脚本 —— **日版 SLPS_258.19** 的等价可重建基线。
#
# 与美版构建脚本的关系：流水线完全同构，差异只有三点——
#   1. 目标二进制/载荷/配置换成日版（SLPS_258.19）；
#   2. 日版有**两个 PT_LOAD 段**，splat 配置拆成两个 top-level segment（cod / dat），
#      因此链接脚本里第二组的符号前缀是 `dat_`，对应的两处链接脚本修补也跟着换名；
#   3. 载荷抽取不用 `objcopy -O binary`（它会把两段之间的 0x80 vaddr 空洞补零，
#      得到 9,305,064 B），改用 tools/project/extract_payload.py 按原版口径
#      「拼接全部 PT_LOAD」→ 9,304,936 B。
#
# 前置：已跑过
#   .tmp/splatvenv/bin/splat split SLPS_258.19.yaml
#   python3 tools/project/gen_symbol_addrs_jp.py ...             （见 tools/）
#
# 工具位置（工作区外，属第三方/版权二进制，不入库）：
#   ~/eecc/ps2binutils/mips-ps2-decompals-{as,objcopy}
#   ~/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
BINUTILS="${BINUTILS:-$HOME/eecc/ps2binutils}"
AS="$BINUTILS/mips-ps2-decompals-as"      # decompals fork: binutils 2.45 rejects $t4-$t7
LD="${LD:-$HOME/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/liutao/eecc/deb/root/usr/lib/x86_64-linux-gnu"

RET="${EE_GAME:-$HERE/orig/SLPS_258.19}"     # the Japanese retail ELF
ROM="$HERE/SLPS_258.19.rom"                 # the payload from the PT_LOAD concatenation (the reference for the payload check)
LDS="$HERE/build/SLPS_258.19.ld"
NAME="SLPS_258.19"

cd "$HERE"

echo "== 0/4 Patch macro.inc =="
# splat regenerates include/macro.inc at every split. Its `.internal` guard makes the
# .symtab from decompals-as report a wrong local symbol count. GNU ld then reports
# ".symtab local symbol at index N (>= sh_info of M)" and refuses the link.
# splat 每次 split 都会重生成 include/macro.inc，其中的 `.internal` 守卫会让 decompals-as
# 产出的 .symtab「local 计数与实际不符」，GNU ld 因此报错并拒绝链接。
if grep -q "_MACRO_INC_GUARD" include/macro.inc 2>/dev/null; then
    python3 - <<'PATCH'
p = 'include/macro.inc'
s = open(p, encoding='utf-8').read()
s = s.replace(""".ifndef _MACRO_INC_GUARD
.internal _MACRO_INC_GUARD
.set _MACRO_INC_GUARD, 1
""", "")
s = '\n'.join(l for l in s.split('\n') if l.strip() != '.endif')
open(p, 'w', encoding='utf-8').write(s)
print("  include guard removed")
PATCH
else
    echo "  macro.inc needs no repair"
fi

echo "== 0b/4 Alignment repair =="
# splat adds `.align 3` (8 bytes) to each code subsegment. The assembler then pads the
# segment size to that alignment, so .init grows from 36 B to 40 B and every later address
# moves by 4 bytes. A code segment needs 4-byte alignment only.
# splat 给每个代码子段加 `.align 3`（8 字节）。汇编器会把**段大小**补齐到该对齐，
# 于是 .init（36 B）被补成 40 B，其后所有地址偏移 4 字节。代码段按 4 字节对齐即可。
# One tree walk instead of one process pair per file: `grep -rl` finds the 7,802 files that
# need the repair in one pass, then `xargs -P` rewrites them in parallel. On a 4 vCPU runner
# this turns ~28 s into ~3 s (measured: the per-file loop costs 19.7 s for the grep alone).
# 一次遍历代替「每文件两次进程启动」：`grep -rl` 一趟找出需要修的 7,802 个文件，
# 再用 `xargs -P` 并行改写。4 vCPU runner 上约 28 s → 约 3 s（实测：逐文件循环光 grep 就 19.7 s）。
mapfile -t -d '' align_files < <(grep -rlZ '^\.align 3' asm/cod --include='*.s')
if [ "${#align_files[@]}" -gt 0 ]; then
    printf '%s\0' "${align_files[@]}" \
        | xargs -0 -r -P "${JOBS:-4}" sed -i 's/^\.align 3$/.align 2/'
fi
echo "  fixed the .align of ${#align_files[@]} code segments"

echo "== 1/4 Assemble =="
mkdir -p build/asm/cod build/asm/data/cod build/asm/data/dat
export AS
# Do not add -mabi=eabi. It sets the eabi64 bit (e_flags=0x20924001), but the retail value is 0x20920001.
find asm -name '*.s' | sort > build/asm_list.txt
n=$(wc -l < build/asm_list.txt)
# `matching-gate` may restore the objects from the packaged snapshot (tools/ci/splat_snapshot.py,
# `asm` group). The tool verified every file against the manifest before writing it, so this
# only needs the count check; the flag comes from the workflow and is never set on a local run.
# The `.align` repair above still runs: the residual split and the per-function targets read the
# repaired sources under asm/.
# `matching-gate` 可能已从打包快照（tools/ci/splat_snapshot.py 的 `asm` 组）还原了对象：工具在写盘
# 前已逐文件核对过清单，所以这里只需核对数量；开关来自 workflow，本机构建永远不会带上它。
# 上面的 `.align` 修复照常执行：残差拆分与逐函数 target 都读 asm/ 里修好的源。
if [ "${BASELINE_ASM_PREBAKED:-0}" = "1" ] && [ "$(find build/asm -name '*.o' | wc -l)" = "$n" ]; then
    echo "  the snapshot restored $n .o files; the assembler is skipped"
else
    find asm -name '*.s' | sort | xargs -P "${JOBS:-4}" -I{} bash -c '
        o="build/asm/${1#asm/}"; o="${o%.s}.o"
        mkdir -p "$(dirname "$o")"
        "$AS" -EL -march=r5900 -I include -o "$o" "$1" 2>"$o.err" || { echo "assembly failed: $1" >&2; exit 1; }
        if [ -s "$o.err" ] && grep -q Error "$o.err"; then echo "errors found: $1" >&2; head -3 "$o.err" >&2; exit 1; fi
    ' _ {}
    echo "  assembled $n .s files"
fi

echo "== 1b/4 Linker script alignment repair (Japanese version, second group prefix dat_) =="
# The retail .sdata ends at 0x9DFBE8, and .sbss starts at 0x9DFC00 (32 bytes aligned).
# This is the same condition as the US version (P-04). The ALIGN statement must come
# before the NOLOAD section declaration. The .sdata end alignment relaxes to 8.
# 原版 .sdata 结束于 0x9DFBE8、.sbss 起始 0x9DFC00（32 字节对齐）。同美版 P-04：
# ALIGN 必须在 NOLOAD 段**声明之前**；.sdata 末端对齐放宽到 8。
python3 - <<'PATCH'
p = 'build/SLPS_258.19.ld'
s = open(p, encoding='utf-8').read()
changed = []
if 'dat_bss_VRAM = ADDR(.dat_bss);' in s and '. = ALIGN(0x20);\n    dat_bss_VRAM' not in s:
    s = s.replace('    dat_bss_VRAM = ADDR(.dat_bss);',
                  '    . = ALIGN(0x20);\n    dat_bss_VRAM = ADDR(.dat_bss);')
    s = s.replace('        FILL(0x00000000);\n        . = ALIGN(., 32);\n        dat_SBSS_START = .;',
                  '        FILL(0x00000000);\n        dat_SBSS_START = .;')
    changed.append('ALIGN(0x20) before dat_bss')
old = """        . = ALIGN(., 16);
        dat_SDATA_END = .;"""
new = """        . = ALIGN(., 8);
        dat_SDATA_END = .;"""
if old in s:
    s = s.replace(old, new)
    changed.append('.sdata end alignment 16 -> 8')
open(p, 'w', encoding='utf-8').write(s)
print("  applied: %s" % (", ".join(changed) if changed else "none (the script probably repaired it already)"))
PATCH

# `matching-gate` fast lane. The mixed build only needs the assembled objects (build/asm) and
# the repaired linker script, so a pure-source pull request can stop here. The mixed payload is
# still compared against the retail payload, so the image stays verified byte for byte; only the
# separate "the pure-asm baseline also rebuilds the retail image" assertion is skipped (that one
# keeps running on every push to main). Guarded by the caller (decomp_build.py --stage fast).
# `matching-gate` 的快路：混合构建只需要 build/asm 的装配产物与修好的链接脚本，纯源码 PR 可以
# 到此为止。混合载荷仍与零售载荷比对，镜像依旧逐字节验证；只跳过「纯汇编基线也能重建零售镜像」
# 这条独立断言（它在每次 main push 上照跑）。由调用方（decomp_build.py --stage fast）控制。
if [ "${BASELINE_ASSEMBLE_ONLY:-0}" = "1" ]; then
    echo "== 2/4-4/4 skipped (BASELINE_ASSEMBLE_ONLY=1): the asm baseline is assembled, the link and the payload check are skipped =="
    exit 0
fi

echo "== 2/4 Link =="
rm -rf build/stage; mkdir -p build/stage
"$LD" -EL -m elf32ltsmip -T "$LDS" -o /dev/null 2>build/ld.err || true
grep -oE "undefined reference to .[^'\'']+" build/ld.err 2>/dev/null \
    | sed "s/.*[\`']//;s/'//" | sort -u > build/undef.txt || true
: > build/defsyms.rsp
while read -r sym; do
    [ -z "$sym" ] && continue
    case "$sym" in
        func_0) echo "--defsym=func_0=0x0" >> build/defsyms.rsp ;;
        D_*)    echo "--defsym=$sym=0x${sym#D_}" >> build/defsyms.rsp ;;
        .L*)    echo "--defsym=$sym=0x${sym#.L}" >> build/defsyms.rsp ;;
    esac
done < build/undef.txt
echo "  absolute address definitions: $(wc -l < build/defsyms.rsp)"

"$LD" -EL -m elf32ltsmip -T "$LDS" @build/defsyms.rsp -Map build/SLPS_258.19.map \
    -o build/SLPS_258.19.elf 2>build/ld.err || true
if [ ! -f build/SLPS_258.19.elf ]; then
    echo "  link failed:"; grep -v "RWX" build/ld.err | head -10; exit 1; fi
echo "  link done: $(stat -c%s build/SLPS_258.19.elf) B"

echo "== 3/4 Extract the payload (concatenate all PT_LOAD segments) =="
python3 tools/project/extract_payload.py build/SLPS_258.19.elf build/SLPS_258.19.bin

echo "== 4/4 Compare =="
python3 - "$ROM" build/SLPS_258.19.bin <<'PY'
import sys, struct, hashlib
ref, built = sys.argv[1:3]
r = open(ref, 'rb').read()
b = open(built, 'rb').read()
print("  rebuilt sha1 = %s (%d B)" % (hashlib.sha1(b).hexdigest(), len(b)))
print("  retail sha1  = %s (%d B)" % (hashlib.sha1(r).hexdigest(), len(r)))
n = min(len(b), len(r))
same = sum(1 for i in range(0, n, 4) if b[i:i+4] == r[i:i+4])
tot = n // 4
print("  word-identical = %d / %d (%.2f%%)" % (same, tot, 100*same/max(tot,1)))
if b[:n] == r[:n] and len(b) == len(r):
    print("  >>> the payload is byte-identical <<<")
else:
    d = [i for i in range(0, n, 4) if b[i:i+4] != r[i:i+4]]
    print("  different words = %d, first at 0x%x" % (len(d), d[0] if d else -1))
    for i in d[:6]:
        print("     +0x%06x rebuilt=%08x retail=%08x" % (i,
            struct.unpack_from('<I', b, i)[0], struct.unpack_from('<I', r, i)[0]))
PY
