#!/bin/bash
# 路线 B（M2.5 hybrid）构建脚本
# —— 「已 C 化函数由 C 编译产物提供，其余仍由 splat 的 asm 提供，全镜像重建仍逐字节一致」
#
# 与 build.sh 的关系（**刻意不改 build.sh**）：
#   * build.sh 是既有棘轮：10,938 个 .s → 全 asm 链接 → build/SLPS_258.19.bin。
#   * build_hybrid.sh 复用 build.sh 的产物（build/asm/*.o 与已打补丁的 build/SLPS_258.19.ld），
#     只改**链接输入**：
#       - direct  —— 清单符号的 asm .o 整份摘掉，在原位置换成 src/matched/<source>.c 编译出的 .o 的 .text*；
#       - residual—— 若该 .o 还含兄弟 glabel 或 endlabel 后的填充字节（P-15/P-16），则由
#                    tools/split_asm.py 摘出目标块、把其余内容原样汇编成 residual 对象，
#                    链接顺序为 [C 对象][residual 对象]，字节与原 .o 完全一致。
#     链接顺序不变 ⇒ 地址布局不变。产物写到 build/hybrid/，与 build/ 完全隔离；
#     build/SLPS_258.19.bin 仍是 build.sh 的产物，棘轮不受影响。
#
# 前置：
#   - 已跑过 `python -m splat split SLPS_258.19.yaml`（产出 asm/ 与 build/*.ld）
#   - 工作区外工具链：~/eecc/ee-gcc3.2-040921、~/eecc/ps2binutils、
#     ~/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd
#   - 若 build/ 下的 M1 产物缺失或不完整，本脚本会先调用一次 build.sh（约 5 分钟）。
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
BINUTILS="${BINUTILS:-$HOME/eecc/ps2binutils}"
GCC="${GCC:-$HOME/eecc/ee-gcc3.2-040921/bin/ee-gcc}"
LD="${LD:-$HOME/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/liutao/eecc/deb/root/usr/lib/x86_64-linux-gnu"
AS="$BINUTILS/mips-ps2-decompals-as"
OC="$BINUTILS/mips-ps2-decompals-objcopy"
READELF="$BINUTILS/mips-ps2-decompals-readelf"

RET="${EE_GAME:-$HERE/orig/SLPS_258.19}"          # 零售原版 ELF（参考）
ROM="$HERE/SLPS_258.19.rom"                      # 零售载荷（sha1 期望来源）
BASE_LDS="$HERE/build/SLPS_258.19.ld"            # build.sh 修补过的全 asm 链接脚本
# 可用 HYBRID_OUT / MATCHED_CFLAGS 覆盖：前者用于把负面对照写到别处（不污染正式产物），
# 后者用于验证编译参数确实是"承重"的（见 out/evidence/hybrid_build_result.txt 负面对照）。
OUTREL="${HYBRID_OUT:-build/hybrid}"
OUT="$HERE/$OUTREL"
MATCHED_CFLAGS="${MATCHED_CFLAGS:--O2 -falign-functions=4 -ffunction-sections}"
# 残差拆分（见 tools/split_asm.py 与 docs/KB/PITFALLS P-15/P-16）：
#   auto（默认）—— 目标符号所在 .s 若含兄弟 glabel 或 endlabel 后的填充，就把「除目标块以外的
#                  全部内容」原样汇编成 residual 对象，链接到 C 对象**之后**；否则走原 direct 路径。
#   0          —— 关闭残差拆分（负面对照；清单里若出现需要拆分的符号则报错退出）。
RESIDUAL="${HYBRID_RESIDUAL:-auto}"
LDS="$OUT/SLPS_258.19.ld"                        # hybrid 链接脚本
LIST="$HERE/config/matched_symbols.txt"
SRCDIR="$HERE/src/matched"
EXPECT_SHA1="7cc42d275750600d1f232b2632447f77205f3fc0"   # 日版零售载荷 sha1（棘轮期望）
# 先确认参考载荷本身没被换掉，再用它做比对
[ "$(sha1sum "$ROM" | cut -d' ' -f1)" = "$EXPECT_SHA1" ] || { echo "FAIL: $ROM 不是预期的日版载荷（sha1 不符）"; exit 1; }

cd "$HERE"

echo "== 0/6 检查 M1 基线产物 =="
need_m1=0
[ -f build/asm_list.txt ] || need_m1=1
[ -f "$BASE_LDS" ] || need_m1=1
# build.sh 给链接脚本打的补丁标记（.cod_bss 之前的 32 字节对齐）
if [ -f "$BASE_LDS" ] && ! grep -q '\. = ALIGN(0x20);' "$BASE_LDS"; then need_m1=1; fi
n_asm=$(find build/asm -name '*.o' 2>/dev/null | wc -l)
n_lst=$(wc -l < build/asm_list.txt 2>/dev/null || echo 0)
[ "$n_asm" = "$n_lst" ] || need_m1=1
if [ "$need_m1" = 1 ]; then
    echo "  M1 产物缺失/不完整 → 先跑 build.sh（既有棘轮，约 5 分钟）"
    bash build.sh
else
    echo "  复用现有 build/asm（$n_asm 个 .o）与已打补丁的链接脚本"
fi

echo "== 1/6 读取已 C 化函数清单 =="
[ -f "$LIST" ] || { echo "缺少 $LIST" >&2; exit 1; }
SYMS=(); SRCS=()
while IFS= read -r line; do
    line="${line%%#*}"
    read -r sym src _rest <<< "$line" || true
    [ -z "${sym:-}" ] && continue
    [ -z "${src:-}" ] && src="$sym"
    SYMS+=("$sym"); SRCS+=("$src")
done < "$LIST"
nsym=${#SYMS[@]}
[ "$nsym" -gt 0 ] || { echo "清单为空" >&2; exit 1; }
echo "  清单符号数 = $nsym"

echo "== 2/6 编译/汇编替换源（增量：源或标志不变则跳过）=="
mkdir -p "$OUT/obj"
# 每源额外编译标志（-O1 等；-O2 为默认）。见 config/source_flags.tsv 与 tools/auto_match_wrapper.py。
FLAGSFILE="$HERE/config/source_flags.tsv"
SRCTSV="$OUT/sources.tsv"
: > "$SRCTSV"
declare -A compiled=()
for i in "${!SYMS[@]}"; do
    src="${SRCS[$i]}"
    [ -n "${compiled[$src]:-}" ] && continue
    compiled[$src]=1
    if [ -f "$SRCDIR/$src.s" ]; then
        printf '%s\tas\t%s\n' "$src" "$SRCDIR/$src.s" >> "$SRCTSV"
    elif [ -f "$SRCDIR/$src.c" ]; then
        printf '%s\tcc\t%s\n' "$src" "$SRCDIR/$src.c" >> "$SRCTSV"
    else
        echo "缺少替换源: $SRCDIR/$src.{c,s}" >&2; exit 1
    fi
done
# shellcheck disable=SC2086
python3 "$HERE/tools/project/compile_sources.py" \
    --sources "$SRCTSV" --objdir "$OUT/obj" \
    --gcc "$GCC" --as "$AS" --include include \
    --cflags "$MATCHED_CFLAGS" --flags-file "$FLAGSFILE" \
    --jobs "${JOBS:-4}" ${HYBRID_NO_CACHE:+--no-cache} --label "源" || exit 1
echo "  源文件数 = ${#compiled[@]}"

echo "== 2b/6 残差拆分（多 glabel / 尾部填充；HYBRID_RESIDUAL=$RESIDUAL）=="
mkdir -p "$OUT/residual"
MODES="$OUT/residual.tsv"
python3 - "$HERE" "$OUT" "$RESIDUAL" "${SYMS[@]}" -- "${SRCS[@]}" <<'PY' || exit 1
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tools")
import split_asm

out_dir, flag = Path(sys.argv[2]), sys.argv[3]
rest = sys.argv[4:]
sep = rest.index('--')
syms, srcs = rest[:sep], rest[sep + 1:]

rows, blocked, need = [], [], []
for sym, src in zip(syms, srcs):
    info = split_asm.analyze(sym)
    m = info["mode"]
    if m.startswith("blocked"):
        blocked.append("%s: %s (%s)" % (sym, m, info.get("reason", "")))
        continue
    if m == "residual":
        need.append(sym)
        if flag != "0":
            split_asm.emit(sym, out_dir / "residual", info)
    rows.append("%s\t%s\t%s" % (sym, src, m))

if flag == "0" and need:
    print("  [FAIL] HYBRID_RESIDUAL=0，但以下符号所在 .s 需要残差拆分（会丢兄弟符号/尾部字节）：")
    for s in need[:15]:
        print("         " + s)
    sys.exit(1)
if blocked:
    print("  [FAIL] 以下符号无法安全拆分（跨块引用/块内兄弟标签等），须从清单移除：")
    for b in blocked[:20]:
        print("         " + b)
    sys.exit(1)
(out_dir / "residual.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("  残差对象 %d 个 / 直接替换 %d 个" % (len(need), len(rows) - len(need)))
PY
RESTSV="$OUT/residual_sources.tsv"
: > "$RESTSV"
while IFS=$'\t' read -r sym _src mode; do
    [ "${mode:-}" = "residual" ] || continue
    printf '%s\tas\t%s\n' "$sym" "$OUT/residual/$sym.residual.s" >> "$RESTSV"
done < "$MODES"
python3 "$HERE/tools/project/compile_sources.py" \
    --sources "$RESTSV" --objdir "$OUT/residual" \
    --gcc "$GCC" --as "$AS" --include include \
    --jobs "${JOBS:-4}" ${HYBRID_NO_CACHE:+--no-cache} --label "残差" || exit 1

echo "== 3/6 安全闸门：C 对象不得引入 .text 之外的非空可分配段 =="
# 1) 每个 C 对象里，除 .text* 外不得有 size>0 的可分配段（否则那些内容会被
#    /DISCARD/ 丢掉，得到的是"静默错码"而不是链接错误）。
# 2) 被替换掉的 asm 对象必须只有 .text（否则摘掉它会丢数据/丢 bss）。
# 3) 每个符号必须真的在它的 C 对象里定义。
python3 - "$READELF" "$OUT/obj" "$SRCDIR" "$MODES" "$OUT/residual" "${SYMS[@]}" -- "${SRCS[@]}" <<'PY'
import os, re, subprocess, sys
readelf = sys.argv[1]
objdir  = sys.argv[2]
srcdir  = sys.argv[3]
modes_f = sys.argv[4]
residdir = sys.argv[5]
rest = sys.argv[6:]
sep = rest.index('--')
syms, srcs = rest[:sep], rest[sep+1:]

modes = {}
for line in open(modes_f, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3:
        modes[p[0]] = p[2]

def sections(obj):
    out = subprocess.run([readelf, '-SW', obj], capture_output=True, text=True).stdout
    res = []
    for line in out.splitlines():
        parts = line.replace('[', ' ').replace(']', ' ').split()
        ti = None
        for i, t in enumerate(parts):
            if t in ('PROGBITS', 'NOBITS', 'MIPS_REGINFO', 'MIPS_DEBUG'):
                ti = i; break
        if ti is None or ti < 1:
            continue
        name = parts[ti-1]; size = int(parts[ti+3], 16)
        # ⚠️ readelf 的 flags 含小写（如 .sdata = "WAp"）：只认全大写会漏判 .sdata/.sbss，
        #    闸门就会放行「C 自产小数据」→ 直到链接期才报 'discarded section'（见 P-24）。
        flg = parts[ti+5] if ti+5 < len(parts) and re.fullmatch(r'[A-Za-z]+', parts[ti+5]) else ''
        res.append((name, size, flg))
    return res

def defined_syms(obj):
    out = subprocess.run([readelf, '-sW', obj], capture_output=True, text=True).stdout
    names = set()
    for line in out.splitlines():
        p = line.split()
        if len(p) >= 8 and p[0].endswith(':') and p[3] in ('FUNC', 'OBJECT') and p[6] != 'UND':
            names.add(p[7].split('@')[0])
    return names

def sym_bindings(obj):
    """[(name, bind, secname)]，只含已定义的 FUNC/OBJECT。"""
    sec_of = {}
    out = subprocess.run([readelf, '-SW', obj], capture_output=True, text=True).stdout
    for line in out.splitlines():
        m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)', line)
        if m:
            sec_of[m.group(1)] = m.group(2)
    res = []
    out = subprocess.run([readelf, '-sW', obj], capture_output=True, text=True).stdout
    for line in out.splitlines():
        p = line.split()
        if len(p) >= 8 and p[0].endswith(':') and p[3] in ('FUNC', 'OBJECT') and p[6] != 'UND':
            try:
                size = int(p[2], 16)
            except ValueError:
                size = 0
            res.append((p[7].split('@')[0], p[4], sec_of.get(p[6], '?'), size))
    return res

def bad_sections(obj):
    """C 对象里「不允许」的段。
    P2a（2026-10-03）：`.sdata*` / `.sbss*` **可以有条件放行** —— C 侧在这些段里 **weak 定义**
    小数据符号，用来拿到 `%gp_rel` 代码生成；这些段不在 hybrid 链接脚本里，会被 /DISCARD/ 丢掉，
    真实存储与地址仍由原 asm 数据对象提供（强定义胜出）。
    条件：该段内定义的**每一个符号都必须是 WEAK**，否则就是「C 自产数据」→ 仍然拒绝。
    """
    bad = []
    binds = sym_bindings(obj)          # [(name, bind, secname, size)]
    for (n, s, f) in sections(obj):
        if not ('A' in f and s > 0 and not n.startswith('.text')):
            continue
        if n.startswith(('.sdata', '.sbss')):
            # 只放行「整段都是 weak 定义」的小数据段：段大小必须等于其中 weak 符号大小之和。
            # 字符串字面量等没有具名符号（或只有 LOCAL 符号）⇒ 大小对不上 ⇒ 拒绝（P-24 的补丁）。
            weak = sum(x[3] for x in binds if x[2] == n and x[1] == 'WEAK')
            named = [x for x in binds if x[2] == n]
            nonweak = [x[0] for x in named if x[1] != 'WEAK']
            if weak != s or nonweak:
                bad.append((n, s, 'weak 覆盖不足(weak=%d/nonweak=%s)' % (weak, ','.join(nonweak[:3]) or '-')))
            continue
        bad.append((n, s, ''))
    return bad

def strict_bad_sections(obj):
    """严格版（asm / residual 对象用）：除 .text* 外不得有任何非空可分配段。"""
    return [(n, s) for (n, s, f) in sections(obj)
            if 'A' in f and s > 0 and not n.startswith('.text')]

fail = False
for sym, src in zip(syms, srcs):
    cobj = os.path.join(objdir, src + '.o')
    if not os.path.exists(cobj):
        print("  [FAIL] C 对象不存在: %s" % cobj); fail = True; continue
    bad = bad_sections(cobj)
    if bad:
        print("  [FAIL] %s 含 .text 之外的非空可分配段 %s（当前机制不会放置它们）" % (cobj, bad)); fail = True
    if sym not in defined_syms(cobj):
        print("  [FAIL] %s 未在 %s 中定义" % (sym, cobj)); fail = True

    aobj = 'build/asm/cod/%s.o' % sym
    if not os.path.exists(aobj):
        print("  [FAIL] 待替换的 asm 对象不存在: %s" % aobj); fail = True; continue
    # asm / residual 对象一律**严格**：除 .text 外不得有任何非空可分配段
    abad = strict_bad_sections(aobj)
    if abad:
        print("  [FAIL] %s 除 .text 外还有非空可分配段 %s；整份摘掉会丢内容" % (aobj, abad)); fail = True

    if modes.get(sym) == 'residual':
        robj = os.path.join(residdir, sym + '.o')
        if not os.path.exists(robj):
            print("  [FAIL] 残差对象不存在: %s" % robj); fail = True; continue
        rbad = strict_bad_sections(robj)
        if rbad:
            print("  [FAIL] %s 含 .text 之外的非空可分配段 %s" % (robj, rbad)); fail = True
        a_defs = defined_syms(aobj)
        r_defs = defined_syms(robj)
        if sym in r_defs:
            print("  [FAIL] 残差对象仍然定义目标符号 %s（C 对象会与它重定义）" % sym); fail = True
        expected = {n for n in a_defs if n not in (sym, sym + '.NON_MATCHING')}
        missing = sorted(expected - r_defs)
        if missing:
            print("  [FAIL] 残差对象丢了原对象的符号定义 %s（摘除会破坏链接）" % missing); fail = True
if fail:
    sys.exit(1)
print("  通过：%d 个 C 对象只提供 .text*；%d 个被替换的 asm 对象只含 .text；残差对象符号完整"
      % (len(syms), len(syms)))
PY

echo "== 4/6 生成 hybrid 链接脚本（原位替换，保持链接顺序）=="
python3 - "$BASE_LDS" "$LDS" "$OUT/obj" "$OUTREL" "$MODES" "${SYMS[@]}" -- "${SRCS[@]}" <<'PY'
import os, re, sys
base, out, objdir, outrel, modes_f = sys.argv[1:6]
rest = sys.argv[6:]
sep = rest.index('--')
syms, srcs = rest[:sep], rest[sep+1:]

modes = {}
for line in open(modes_f, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3:
        modes[p[0]] = p[2]

lines = open(base, encoding='utf-8').read().split('\n')
keep = []
repl = {}
for i, line in enumerate(lines):
    m = re.match(r'^(\s*)build/asm/cod/(\S+)\.o\(\.text\*\);\s*$', line)
    if m and m.group(2) in syms:
        sym = m.group(2)
        src = srcs[syms.index(sym)]
        repl[sym] = i
        keep.append('%s%s/obj/%s.o(.text*);' % (m.group(1), outrel, src))
        if modes.get(sym) == 'residual':
            # 目标符号是文件首个 glabel ⇒ 残差（兄弟块 + 尾部填充）紧随其后，顺序与原 .o 一致
            keep.append('%s%s/residual/%s.o(.text*);' % (m.group(1), outrel, sym))
        continue
    # 同一符号的 .data/.rodata/.sdata/.sbss/.bss 行：
    #   direct   —— 整份摘掉（asm .o 不再是链接输入）；
    #   residual —— 改指残差对象（它保留了原 .s 里除目标块以外的全部内容）。
    m2 = re.match(r'^(\s*)build/asm/cod/(\S+)\.o\((.*)\);\s*$', line)
    if m2 and m2.group(2) in syms:
        sym = m2.group(2)
        if modes.get(sym) == 'residual':
            keep.append('%s%s/residual/%s.o(%s);' % (m2.group(1), outrel, sym, m2.group(3)))
        continue
    keep.append(line)

missing = [s for s in syms if s not in repl]
if missing:
    print("  [FAIL] 链接脚本里找不到 .text* 行: %s" % ', '.join(missing), file=sys.stderr)
    sys.exit(1)
open(out, 'w', encoding='utf-8').write('\n'.join(keep))
n_res = sum(1 for s in syms if modes.get(s) == 'residual')
print("  已替换 %d 个符号的 .text* 行（其中 %d 个附带残差对象）-> %s" % (len(repl), n_res, out))
PY

echo "== 5/6 链接 =="
# 未定义符号（D_/func_0/.L）用绝对地址 --defsym 定义，与 build.sh 同一套规则。
# 第一遍「故意链接失败」只为收集未定义集合：在本机实测约 2m20s（11k 个对象、上万条未定义引用），
# 是整条 hybrid 流水线的最大单项开销。故先复用上一次的 defsyms.rsp 直接做第二遍；
# 只有第二遍真的失败（出现新的未定义符号）才回退到第一遍重新收集。
rm -f "$OUT/SLPS_258.19.elf"
link_pass2() {
    "$LD" -EL -m elf32ltsmip -T "$LDS" @"$OUT/defsyms.rsp" -Map "$OUT/SLPS_258.19.map" \
        -o "$OUT/SLPS_258.19.elf" 2>"$OUT/ld2.err"
}
collect_defsyms() {
    echo "  第一遍：收集未定义符号（约 2 分钟）"
    "$LD" -EL -m elf32ltsmip -T "$LDS" -o /dev/null 2>"$OUT/ld1.err" || true
    grep -oE "undefined reference to .[^'\'']+" "$OUT/ld1.err" 2>/dev/null \
        | sed "s/.*[\`']//;s/'//" | sort -u > "$OUT/undef.txt" || true
    : > "$OUT/defsyms.rsp"
    while read -r sym; do
        [ -z "$sym" ] && continue
        case "$sym" in
            func_0) echo "--defsym=func_0=0x0" >> "$OUT/defsyms.rsp" ;;
            D_*)    echo "--defsym=$sym=0x${sym#D_}" >> "$OUT/defsyms.rsp" ;;
            .L*)    echo "--defsym=$sym=0x${sym#.L}" >> "$OUT/defsyms.rsp" ;;
        esac
    done < "$OUT/undef.txt"
    echo "  绝对地址定义: $(wc -l < "$OUT/defsyms.rsp") 条"
}

if [ -f "$OUT/defsyms.rsp" ]; then
    link_pass2 || true
    if [ ! -f "$OUT/SLPS_258.19.elf" ]; then
        echo "  缓存 defsyms 不足（清单变了或出现新未定义符号）→ 重新收集"
        collect_defsyms
        link_pass2 || true
    else
        echo "  复用缓存 defsyms（$(wc -l < "$OUT/defsyms.rsp") 条），跳过第一遍"
    fi
else
    collect_defsyms
    link_pass2 || true
fi
if [ ! -f "$OUT/SLPS_258.19.elf" ]; then
    echo "  链接失败:"; grep -v "RWX" "$OUT/ld2.err" | head -20 >&2; exit 1
fi
echo "  ELF: $(stat -c%s "$OUT/SLPS_258.19.elf") B"

echo "== 6/6 抽取载荷 + sha1 比对 =="
# ⚠️ 日版有 2 个 PT_LOAD 且中间有 0x80 空洞：objcopy -O binary 会补零（9,305,064 B ≠ 9,304,936 B）
#    必须与 build.sh 同一口径：按程序头拼接 PT_LOAD
python3 "$HERE/tools/project/extract_payload.py" "$OUT/SLPS_258.19.elf" "$OUT/SLPS_258.19.bin"
python3 - "$ROM" "$OUT/SLPS_258.19.bin" "$EXPECT_SHA1" "$OUT/SLPS_258.19.map" "$OUTREL" "${SYMS[@]}" <<'PY'
import hashlib, sys
rom, built, expect = sys.argv[1:4]
mapfile = sys.argv[4]
outrel = sys.argv[5]
syms = sys.argv[6:]
b = open(built, 'rb').read()
r = open(rom, 'rb').read()
hb, hr = hashlib.sha1(b).hexdigest(), hashlib.sha1(r).hexdigest()
n = min(len(b), len(r))
same = sum(1 for i in range(0, n, 4) if b[i:i+4] == r[i:i+4])
print("  重建 sha1 = %s (%d B)" % (hb, len(b)))
print("  零售 sha1 = %s (%d B)" % (hr, len(r)))
print("  期望 sha1 = %s" % expect)
print("  逐字一致  = %d / %d (%.2f%%)" % (same, n//4, 100*same/max(n//4, 1)))

# 从 map 里取每个符号的最终地址 + 提供者对象（C 铁证）
# 单遍扫描：map 有 37 万行、850 个符号，原先「每个符号全表扫一遍」实测要 43 秒。
print("  -- 清单符号的来源（link map 证据）--")
want = set(syms)
found = {}
provider = "?"
with open(mapfile, encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if (outrel + '/obj/') in line or 'build/asm/cod/' in line:
            provider = line.strip()
            continue
        p = line.split()
        if len(p) == 2 and p[0].startswith('0x') and p[1] in want and p[1] not in found:
            if int(p[0], 16) != 0:
                found[p[1]] = (p[0], provider)
for s in syms:
    addr, prov = found.get(s, (None, None))
    print("    %-18s %-12s <- %s" % (s, addr or '?', prov or '?'))

ok = (hb == expect and hb == hr and len(b) == len(r) and b == r)
print("  >>> %s <<<" % ("逐字节一致，hybrid 构建通过" if ok else "不一致：hybrid 构建失败"))
sys.exit(0 if ok else 1)
PY
