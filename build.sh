#!/bin/bash
# 路线 B（M1）构建脚本 —— **日版 SLPS_258.19** 的等价可重建基线
#
# 与美版 routeb/build.sh 的关系：流水线完全同构，差异只有三点——
#   1. 目标二进制/载荷/配置换成日版（SLPS_258.19）；
#   2. 日版有**两个 PT_LOAD 段**，splat 配置拆成两个 top-level segment
#      （cod / dat），因此链接脚本里第二组的符号前缀是 `dat_`，
#      对应的两处链接脚本修补也跟着换名；
#   3. 载荷抽取不用 `objcopy -O binary`（它会把两段之间的 0x80 vaddr 空洞
#      补零，得到 9,305,064 B），改用 routebjp/tools/extract_payload.py
#      按原版口径「拼接全部 PT_LOAD」→ 9,304,936 B。
#
# 前置：已跑过
#   .tmp/splatvenv/bin/splat split SLPS_258.19.yaml      （在 routebjp/ 内）
#   python3 tools/gen_symbol_addrs_jp.py ...             （见 tools/）
#
# 工具位置（工作区外，属第三方/版权二进制，不入库）：
#   ~/eecc/ps2binutils/mips-ps2-decompals-{as,objcopy}
#   ~/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
BINUTILS="${BINUTILS:-$HOME/eecc/ps2binutils}"
AS="$BINUTILS/mips-ps2-decompals-as"      # decompals fork：binutils 2.45 拒绝 $t4-$t7
LD="${LD:-$HOME/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/liutao/eecc/deb/root/usr/lib/x86_64-linux-gnu"

RET="${EE_GAME:-$HERE/orig/SLPS_258.19}"     # 日版零售原版
ROM="$HERE/SLPS_258.19.rom"                 # 拼 PT_LOAD 得到的载荷（棘轮基准）
LDS="$HERE/build/SLPS_258.19.ld"
NAME="SLPS_258.19"

cd "$HERE"

echo "== 0/4 修补 macro.inc =="
# splat 每次 split 都会重生成 include/macro.inc，其中的 `.internal` 守卫会让
# decompals-as 产出的 .symtab「local 计数与实际不符」，GNU ld 报
#   ".symtab local symbol at index N (>= sh_info of M)" 并拒绝链接。
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
print("  已移除 include 守卫")
PATCH
else
    echo "  macro.inc 无需修补"
fi

echo "== 0b/4 对齐修正 =="
# splat 给每个代码子段加 `.align 3`（8 字节）。汇编器会把**段大小**补齐到该对齐，
# 于是 .init（36 B）被补成 40 B，其后所有地址偏移 4 字节。代码段按 4 字节对齐即可。
fixed=0
for f in $(find asm/cod -name '*.s'); do
    if grep -q '^\.align 3' "$f"; then
        sed -i 's/^\.align 3$/.align 2/' "$f"; fixed=$((fixed+1))
    fi
done
echo "  已修正 $fixed 个代码段的 .align"

echo "== 1/4 汇编 =="
mkdir -p build/asm/cod build/asm/data/cod build/asm/data/dat
export AS
# 不能加 -mabi=eabi：会置 eabi64 位（e_flags=0x20924001），原版是 0x20920001。
find asm -name '*.s' | sort > build/asm_list.txt
n=$(wc -l < build/asm_list.txt)
find asm -name '*.s' | sort | xargs -P "${JOBS:-4}" -I{} bash -c '
    o="build/asm/${1#asm/}"; o="${o%.s}.o"
    mkdir -p "$(dirname "$o")"
    "$AS" -EL -march=r5900 -I include -o "$o" "$1" 2>"$o.err" || { echo "汇编失败: $1" >&2; exit 1; }
    if [ -s "$o.err" ] && grep -q Error "$o.err"; then echo "有错误: $1" >&2; head -3 "$o.err" >&2; exit 1; fi
' _ {}
echo "  已汇编 $n 个 .s"

echo "== 1b/4 链接脚本对齐修补（日版：第二组前缀 dat_）=="
# 原版 .sdata 结束于 0x9DFBE8、.sbss 起始 0x9DFC00（32 字节对齐）。
# 同美版 P-04：ALIGN 必须在 NOLOAD 段**声明之前**；.sdata 末端对齐放宽到 8。
python3 - <<'PATCH'
p = 'build/SLPS_258.19.ld'
s = open(p, encoding='utf-8').read()
changed = []
if 'dat_bss_VRAM = ADDR(.dat_bss);' in s and '. = ALIGN(0x20);\n    dat_bss_VRAM' not in s:
    s = s.replace('    dat_bss_VRAM = ADDR(.dat_bss);',
                  '    . = ALIGN(0x20);\n    dat_bss_VRAM = ADDR(.dat_bss);')
    s = s.replace('        FILL(0x00000000);\n        . = ALIGN(., 32);\n        dat_SBSS_START = .;',
                  '        FILL(0x00000000);\n        dat_SBSS_START = .;')
    changed.append('dat_bss 前 ALIGN(0x20)')
old = """        . = ALIGN(., 16);
        dat_SDATA_END = .;"""
new = """        . = ALIGN(., 8);
        dat_SDATA_END = .;"""
if old in s:
    s = s.replace(old, new)
    changed.append('.sdata 末端对齐 16->8')
open(p, 'w', encoding='utf-8').write(s)
print("  已应用: %s" % (", ".join(changed) if changed else "无（可能已修补）"))
PATCH

echo "== 2/4 链接 =="
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
echo "  绝对地址定义: $(wc -l < build/defsyms.rsp) 条"

"$LD" -EL -m elf32ltsmip -T "$LDS" @build/defsyms.rsp -Map build/SLPS_258.19.map \
    -o build/SLPS_258.19.elf 2>build/ld.err || true
if [ ! -f build/SLPS_258.19.elf ]; then
    echo "  链接失败:"; grep -v "RWX" build/ld.err | head -10; exit 1; fi
echo "  链接完成: $(stat -c%s build/SLPS_258.19.elf) B"

echo "== 3/4 抽取载荷（拼接全部 PT_LOAD）=="
python3 tools/extract_payload.py build/SLPS_258.19.elf build/SLPS_258.19.bin

echo "== 4/4 比对 =="
python3 - "$ROM" build/SLPS_258.19.bin <<'PY'
import sys, struct, hashlib
ref, built = sys.argv[1:3]
r = open(ref, 'rb').read()
b = open(built, 'rb').read()
print("  重建 sha1 = %s (%d B)" % (hashlib.sha1(b).hexdigest(), len(b)))
print("  原版 sha1 = %s (%d B)" % (hashlib.sha1(r).hexdigest(), len(r)))
n = min(len(b), len(r))
same = sum(1 for i in range(0, n, 4) if b[i:i+4] == r[i:i+4])
tot = n // 4
print("  逐字一致  = %d / %d (%.2f%%)" % (same, tot, 100*same/max(tot,1)))
if b[:n] == r[:n] and len(b) == len(r):
    print("  >>> 载荷逐字节一致 <<<")
else:
    d = [i for i in range(0, n, 4) if b[i:i+4] != r[i:i+4]]
    print("  不一致字  = %d ; 首个 @0x%x" % (len(d), d[0] if d else -1))
    for i in d[:6]:
        print("     +0x%06x 重建=%08x 原版=%08x" % (i,
            struct.unpack_from('<I', b, i)[0], struct.unpack_from('<I', r, i)[0]))
PY
