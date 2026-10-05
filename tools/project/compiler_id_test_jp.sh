#!/bin/bash
# M0 编译器身份判决实验 —— **日版 SLPS_258.19**
#
# 这是 tools/research/compiler_id_test.sh 的日版移植：判别原理完全相同（见该脚本头部注释），
# 只把 (a) 目标 ELF 换成日版、(b) 目标函数地址换成一组的日版对应物。
#
# 判别点：读全局变量的地址暂存寄存器
#   ee-gcc 2.96 -G0 -> lui $v1 ; lw $v0,lo($v1)
#   ee-gcc 3.2-040921 -G0 -> lui $t7 ; lw $v0,lo($t7)
#
# 日版对照函数（由 .erx.lib baseelf 槽位对齐得到）：
#   baseelf_15 @0x1F5D20  ->  jr $ra ; lh $v0,24($a0)   （对照组，两版应一致）
#   baseelf_19 @0x1E0F60  ->  lui $t7,0x7b ; jr $ra ; lw $v0,-3376($t7)  （判别点）
set -u
EECC="${EECC:-$HOME/eecc}"
OD="${OD:-$HOME/ps2dev/ee/bin/mips64r5900el-ps2-elf-objdump}"
W="$(cd "$(dirname "$0")/.." && pwd)"
ELF="$W/../out/binaries/SLPS_258.19"
TMP="$(mktemp -d "$W/../.tmp/m0jp.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/probe.c" <<'EOF'
struct S { char pad[24]; short v; };
short f1(struct S *p){ return p->v; }        /* 不受版本影响，作对照组 */
extern int gv;
int  f2(void){ return gv; }                  /* <-- 判别点：地址暂存寄存器 */
EOF

echo "=== 对照组 f1（两版应一致，日版 @0x1F5D20 = jr ra ; lh v0,24(a0)）==="
echo "=== 判别点 f2（2.96 用 \$v1 或 \$gp；3.2 用 \$t7）==="
for v in 2.96 3.2-040921; do
    GCC="$EECC/ee-gcc$v/bin/ee-gcc"
    [ -x "$GCC" ] || { echo "  缺少 $GCC，跳过"; continue; }
    echo "--- ee-gcc $($GCC --version 2>&1 | head -1) ---"
    for g in 0 8; do
        "$GCC" -O2 -G$g -c -o "$TMP/p.o" "$TMP/probe.c" 2>/dev/null
        printf "  -G%-2s  f1: " "$g"
        "$OD" -d "$TMP/p.o" | sed -n '/<f1>:/,/^$/p' | grep -E '^\s+[0-9a-f]+:' \
            | sed 's/^ *[0-9a-f]*:\t[0-9a-f]*\t//' | tr '\n' '|'
        printf "   f2: "
        "$OD" -d "$TMP/p.o" | sed -n '/<f2>:/,/^$/p' | grep -E '^\s+[0-9a-f]+:' \
            | sed 's/^ *[0-9a-f]*:\t[0-9a-f]*\t//' | tr '\n' '|'
        echo
    done
done

echo
echo "=== 日版目标二进制实测 ==="
printf "  f1 @0x1F5D20 : "
"$OD" -d --start-address=0x1f5d20 --stop-address=0x1f5d28 "$ELF" | sed -n '/>:/,$p' \
    | grep -E '^\s+[0-9a-f]+:' | sed 's/^ *[0-9a-f]*:\t[0-9a-f]*\t//' | tr '\n' '|'
echo
printf "  f2 @0x1E0F60 : "
"$OD" -d --start-address=0x1e0f60 --stop-address=0x1e0f6c "$ELF" | sed -n '/>:/,$p' \
    | grep -E '^\s+[0-9a-f]+:' | sed 's/^ *[0-9a-f]*:\t[0-9a-f]*\t//' | tr '\n' '|'
echo
echo
echo "=== 日版 .text 全局地址暂存寄存器直方图（复现判决的统计依据）==="
python3 - "$ELF" <<'PY'
import struct, collections, sys
d = open(sys.argv[1], 'rb').read()
# 日版 .text: vaddr 0x100000, size 0x26C5E8, file off 0x1000
W = struct.unpack_from('<%dI' % (0x26C5E8 // 4), d, 0x1000)
op = lambda w: w >> 26
rs = lambda w: (w >> 21) & 0x1f
rt = lambda w: (w >> 16) & 0x1f
LOAD = {0x20, 0x21, 0x23, 0x24, 0x25, 0x27, 0x37, 0x31}
STORE = {0x28, 0x29, 0x2b, 0x3f, 0x39}
NM = {1:'at',2:'v0',3:'v1',8:'t0',9:'t1',10:'t2',11:'t3',12:'t4',13:'t5',14:'t6',
      15:'t7',24:'t8',25:'t9',16:'s0',28:'gp',29:'sp',30:'fp',31:'ra'}
c = collections.Counter()
for i, w in enumerate(W):
    if op(w) != 0x0f or rt(w) not in NM: continue
    reg = rt(w)
    for j in range(i + 1, min(i + 5, len(W))):
        if (op(W[j]) in LOAD or op(W[j]) in STORE) and rs(W[j]) == reg:
            c[NM[reg]] += 1; break
tot = sum(c.values())
for k, v in c.most_common(6):
    print("  $%-3s %6d  (%.1f%%)" % (k, v, 100 * v / tot))
print("  ---- ee-gcc 2.96 -> $v1 ; ee-gcc 3.2-040921 -> $t7")
PY
