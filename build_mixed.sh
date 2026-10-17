#!/bin/bash
# Route B (mixed build) script.
# -- "The C output provides the matched functions. The asm from splat provides the other
#     functions. The full image is still byte-identical after the rebuild."
#
# Relation to build.sh (this script deliberately does not change build.sh):
#   * build.sh is the existing baseline build: 10,938 .s files -> a full asm link ->
#     build/SLPS_258.19.bin.
#   * build_mixed.sh reuses the output of build.sh (build/asm/*.o and the repaired
#     build/SLPS_258.19.ld). It changes the **link input** only:
#       - direct   -- the script removes the whole asm .o of a ledger symbol and puts the
#                     .text* of the object from src/matched/<source>.c at the same position;
#       - residual -- when that .o still holds a sibling glabel or filler bytes after the
#                     endlabel (P-15/P-16), tools/split_asm.py extracts the target block and
#                     assembles the rest into a residual object unchanged. The link order is
#                     [C object][residual object], and the bytes equal the original .o.
#     The link order does not change, so the address layout does not change. The script writes
#     the result to build/mixed/, away from build/. build/SLPS_258.19.bin stays the output of
#     build.sh, and the payload check is not affected.
#
# Prerequisites:
#   - `python -m splat split SLPS_258.19.yaml` has run (it writes asm/ and build/*.ld)
#   - Toolchain outside the workspace: ~/eecc/ee-gcc3.2-040921, ~/eecc/ps2binutils,
#     ~/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd
#   - When the baseline build output under build/ is absent or incomplete, this script calls
#     build.sh once (about 5 minutes).

# 路线 B（mixed build）构建脚本。
# —— 「已 C 化函数由 C 编译产物提供，其余仍由 splat 的 asm 提供，全镜像重建仍逐字节一致」
#
# 与 build.sh 的关系（**刻意不改 build.sh**）：
#   * build.sh 是既有 baseline build：10,938 个 .s → 全 asm 链接 → build/SLPS_258.19.bin。
#   * build_mixed.sh 复用 build.sh 的产物（build/asm/*.o 与已打补丁的 build/SLPS_258.19.ld），
#     只改**链接输入**：
#       - direct  —— 清单符号的 asm .o 整份摘掉，在原位置换成 src/matched/<source>.c 编译出的 .o 的 .text*；
#       - residual—— 若该 .o 还含兄弟 glabel 或 endlabel 后的填充字节（P-15/P-16），则由
#                    tools/split_asm.py 摘出目标块、把其余内容原样汇编成 residual 对象，
#                    链接顺序为 [C 对象][residual 对象]，字节与原 .o 完全一致。
#     链接顺序不变 ⇒ 地址布局不变。产物写到 build/mixed/，与 build/ 完全隔离；
#     build/SLPS_258.19.bin 仍是 build.sh 的产物，载荷检查不受影响。
#
# 前置：
#   - 已跑过 `python -m splat split SLPS_258.19.yaml`（产出 asm/ 与 build/*.ld）
#   - 工作区外工具链：~/eecc/ee-gcc3.2-040921、~/eecc/ps2binutils、
#     ~/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd
#   - 若 build/ 下的 baseline build 产物缺失或不完整，本脚本会先调用一次 build.sh（约 5 分钟）。
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
BINUTILS="${BINUTILS:-$HOME/eecc/ps2binutils}"
GCC="${GCC:-${EE_GCC:-$HOME/eecc/ee-gcc3.2-040921/bin/ee-gcc}}"
GCC_CRI="${GCC_CRI:-${EE_GCC_CRI:-$HOME/eecc/ee-gcc2.96/bin/ee-gcc}}"   # CRI sections (ADXT 10.03 / ADXRT 3100, R17 section 4.2)
CCMAP="$HERE/config/compiler_map.tsv"                    # the compiler of each source: <source><TAB>game|cri
LD="${LD:-$HOME/eecc/deb/root/usr/bin/mips-linux-gnu-ld.bfd}"
# The ld from the Debian package needs its own shared libraries. Do not hard-code a personal home
# directory: `LD_LIBDIR` (or `EE_LIBDIR`) names it, the default follows `$HOME`, and an absent
# directory is simply not appended (R30 finding B1).
# Debian 包里那份 ld 需要它自己的共享库。不要写死某个人的家目录：`LD_LIBDIR`（或 `EE_LIBDIR`）指定，
# 缺省跟随 `$HOME`，目录不存在就不追加（R30 B1）。
LD_LIBDIR="${EE_LIBDIR:-${LD_LIBDIR:-$HOME/eecc/deb/root/usr/lib/x86_64-linux-gnu}}"
[ -d "$LD_LIBDIR" ] || LD_LIBDIR=""
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}${LD_LIBRARY_PATH:+:}${LD_LIBDIR}"
AS="$BINUTILS/mips-ps2-decompals-as"
OC="$BINUTILS/mips-ps2-decompals-objcopy"
READELF="$BINUTILS/mips-ps2-decompals-readelf"

RET="${EE_GAME:-$HERE/orig/SLPS_258.19}"          # the retail ELF (reference)
ROM="$HERE/SLPS_258.19.rom"                      # the retail payload (the source of the expected sha1)
BASE_LDS="$HERE/build/SLPS_258.19.ld"            # the full-asm linker script that build.sh repaired
# Override HYBRID_OUT or MATCHED_CFLAGS when you need to. HYBRID_OUT writes a negative control
# to another directory and keeps the official output clean. MATCHED_CFLAGS proves that the
# compiler flags carry the result (see the negative control in the private evidence file
# out/evidence/hybrid_build_result.txt).
# 可用 HYBRID_OUT / MATCHED_CFLAGS 覆盖：前者用于把负面对照写到别处（不污染正式产物），
# 后者用于验证编译参数确实是「承重」的（见私有证据 out/evidence/hybrid_build_result.txt 的负面对照）。
OUTREL="${HYBRID_OUT:-build/mixed}"
# Private pipeline compatibility. The HYBRID_* variables keep their historical names. The private
# repository keeps its own output directory matching-jp/build/hybrid and its own evidence file name
# out/evidence/hybrid_build_result.txt. Do not rename any of them.
# 私有流水线兼容，勿改名：HYBRID_* 变量沿用历史名；私有仓库的产物目录 matching-jp/build/hybrid
# 与私有证据文件名 hybrid_build_result.txt 也不改名。
OUT="$HERE/$OUTREL"
MATCHED_CFLAGS="${MATCHED_CFLAGS:--O2 -falign-functions=4 -ffunction-sections}"
# Residual split (see tools/split_asm.py and private note P-15/P-16):
#   auto (default) -- when the .s of the target symbol holds a sibling glabel or filler after
#                    the endlabel, the script assembles everything except the target block into
#                    a residual object and links it after the C object. Otherwise the script
#                    uses the original direct path.
#   0              -- disable the residual split (negative control). The script stops with an
#                    error when the ledger holds a symbol that needs the split.
# 残差拆分（见 tools/split_asm.py 与私有笔记 P-15/P-16）：
#   auto（默认）—— 目标符号所在 .s 若含兄弟 glabel 或 endlabel 后的填充，就把「除目标块以外的
#                  全部内容」原样汇编成 residual 对象，链接到 C 对象**之后**；否则走原 direct 路径。
#   0          —— 关闭残差拆分（负面对照；清单里若出现需要拆分的符号则报错退出）。
RESIDUAL="${HYBRID_RESIDUAL:-auto}"
LDS="$OUT/SLPS_258.19.ld"                        # the mixed build linker script
LIST="$HERE/config/matched_symbols.txt"
SRCDIR="$HERE/src/matched"
# Jump table patch table. The script uses the file only when the file exists and is not empty.
# The patch redirects the C-generated `.rodata` table to the existing splat symbol. See
# tools/project/jtbl_patch.py.
# 跳转表修补表（<符号>\t<jtbl_符号>）：只在文件存在且非空时启用。C 侧真 `switch` 自产的
# `.rodata` 表会被改指到 splat 既有符号，见 tools/project/jtbl_patch.py。
JTBLTABLES="${JTBLTABLES:-$HERE/config/jtbl_tables.tsv}"
[ -s "$JTBLTABLES" ] || JTBLTABLES=""
EXPECT_SHA1="7cc42d275750600d1f232b2632447f77205f3fc0"   # the sha1 of the Japanese retail payload (the expected value for the payload check)
# First confirm that the reference payload is the expected one. Then use it for the comparison.
[ "$(sha1sum "$ROM" | cut -d' ' -f1)" = "$EXPECT_SHA1" ] || { echo "FAIL: $ROM is not the expected Japanese payload (sha1 mismatch)"; exit 1; }

cd "$HERE"

echo "== 0/6 Check the baseline build output =="
need_m1=0
[ -f build/asm_list.txt ] || need_m1=1
[ -f "$BASE_LDS" ] || need_m1=1
# the repair mark that build.sh writes into the linker script (the 32-byte alignment before .cod_bss)
if [ -f "$BASE_LDS" ] && ! grep -q '\. = ALIGN(0x20);' "$BASE_LDS"; then need_m1=1; fi
n_asm=$(find build/asm -name '*.o' 2>/dev/null | wc -l)
n_lst=$(wc -l < build/asm_list.txt 2>/dev/null || echo 0)
[ "$n_asm" = "$n_lst" ] || need_m1=1
if [ "$need_m1" = 1 ]; then
    echo "  the baseline build output is absent or incomplete. Run build.sh first (about 5 minutes)."
    bash build.sh
else
    echo "  reuse the existing build/asm ($n_asm .o files) and the repaired linker script"
fi

echo "== 1/6 Read the matched function ledger =="
[ -f "$LIST" ] || { echo "missing $LIST" >&2; exit 1; }
# A ledger name becomes `src/matched/<src>.{c,s}`, an object name and a row of the generated
# linker script. Refuse anything that is not a plain symbol name BEFORE anything is written, so a
# crafted ledger cannot escape the directory or inject linker-script text (R30 finding B5).
# 台账里的名字会变成 `src/matched/<src>.{c,s}`、对象名与生成链接脚本的一行。任何写盘之前先拒绝
# 不是普通符号名的输入：被构造的台账因此无法逃出目录或注入链接脚本文本（R30 B5）。
valid_name() { [[ "$1" =~ ^[A-Za-z_][A-Za-z0-9_.]*$ ]]; }
SYMS=(); SRCS=()
nline=0
while IFS= read -r line; do
    nline=$((nline + 1))
    line="${line%%#*}"
    read -r sym src _rest <<< "$line" || true
    [ -z "${sym:-}" ] && continue
    [ -z "${src:-}" ] && src="$sym"
    if ! valid_name "$sym" || ! valid_name "$src"; then
        echo "FAIL: $LIST line $nline: unsafe symbol/source name (sym='$sym' src='$src');" >&2
        echo "      expected [A-Za-z_][A-Za-z0-9_.]* (letters, digits, '_' and '.')" >&2
        exit 1
    fi
    SYMS+=("$sym"); SRCS+=("$src")
done < "$LIST"
nsym=${#SYMS[@]}
[ "$nsym" -gt 0 ] || { echo "the ledger is empty" >&2; exit 1; }
echo "  ledger symbols = $nsym"

echo "== 2/6 Compile or assemble the replacement sources (incremental: skip when the source and the flags do not change) =="
mkdir -p "$OUT/obj"
# Extra compiler flags for one source (-O1 and others; -O2 is the default). See
# config/source_flags.tsv and tools/maintainer/project/auto_match_wrapper.py.
FLAGSFILE="$HERE/config/source_flags.tsv"
SRCTSV="$OUT/sources.tsv"
: > "$SRCTSV"
# <source><TAB><symbol> for the data patch. The ledger may name a source differently from the
# symbol, so the mapping is explicit (compile_sources keys objects by the source basename).
# 数据改指用的 <源码><TAB><符号>。台账允许源码名与符号名不同，所以映射显式给出
# （compile_sources 用源码基名做对象名）。
SYMTSV="$OUT/symbols.tsv"
: > "$SYMTSV"
declare -A compiled=()
for i in "${!SYMS[@]}"; do
    src="${SRCS[$i]}"
    [ -n "${compiled[$src]:-}" ] && continue
    compiled[$src]=1
    # `${SYMS[$i]}`, not `$sym`: `sym` still holds the last ledger line from the loop above.
    # Measured 2026-10-17: using `$sym` mapped every source to the last symbol, so the data
    # patch used the wrong asm block and 14 words of the payload changed.
    # 必须用 `${SYMS[$i]}`，不能用 `$sym`——`$sym` 还是上面 while 循环最后一次的值。
    # 2026-10-17 实测：用 `$sym` 会把所有源都映射到最后一个符号，数据改指拿错 asm 块，
    # 载荷因此有 14 个字不同。
    printf '%s\t%s\n' "$src" "${SYMS[$i]}" >> "$SYMTSV"
    if [ -f "$SRCDIR/$src.s" ]; then
        printf '%s\tas\t%s\n' "$src" "$SRCDIR/$src.s" >> "$SRCTSV"
    elif [ -f "$SRCDIR/$src.c" ]; then
        printf '%s\tcc\t%s\n' "$src" "$SRCDIR/$src.c" >> "$SRCTSV"
    else
        echo "missing replacement source: $SRCDIR/$src.{c,s}" >&2; exit 1
    fi
done
# shellcheck disable=SC2086
# Data patch (O-01 (1)): redirect a C object's own data references to the splat symbols.
# It subsumes the jtbl patch, so the jtbl table is not applied when it is on. Set
# HYBRID_DATA_PATCH=0 for the negative control (the old jtbl-only path).
# 数据改指（O-01 ①）：把 C 对象自产的数据引用改指到 splat 符号。它覆盖 jtbl 补丁，因此开启时
# 不再应用跳转表；负面对照用 HYBRID_DATA_PATCH=0 回到旧的 jtbl 路径。
DATA_PATCH="${HYBRID_DATA_PATCH:-1}"
BASE_ELF="$HERE/build/SLPS_258.19.elf"
if [ "$DATA_PATCH" = 1 ]; then
    [ -f "$BASE_ELF" ] || { echo "FAIL: the data patch needs the baseline link $BASE_ELF (run build.sh)"; exit 1; }
    DP_ARGS=(--data-patch --symbols-tsv "$SYMTSV" --image "$BASE_ELF")
    JTBL_ARGS=()
else
    DP_ARGS=()
    JTBL_ARGS=(${JTBLTABLES:+--jtbl-tables "$JTBLTABLES"})
fi
[ "$(wc -l < "$SYMTSV")" = "${#compiled[@]}" ] || {
    echo "FAIL: $SYMTSV has $(wc -l < "$SYMTSV") rows for ${#compiled[@]} sources (the src->symbol map is wrong)"; exit 1; }
python3 "$HERE/tools/project/compile_sources.py" \
    --sources "$SRCTSV" --objdir "$OUT/obj" \
    --gcc "$GCC" --gcc-cri "$GCC_CRI" --cc-map "$CCMAP" --as "$AS" --include include \
    --cflags "$MATCHED_CFLAGS" --flags-file "$FLAGSFILE" \
    "${JTBL_ARGS[@]}" "${DP_ARGS[@]}" \
    --jobs "${JOBS:-4}" ${HYBRID_NO_CACHE:+--no-cache} --label "source" || exit 1
# The compiler map has a header row on line 1. Skip it before the count.
# 编译器表第 1 行是表头；先跳过再计数。
n_cri=$(tail -n +2 "$CCMAP" 2>/dev/null | grep -cv '^[[:space:]]*\(#\|$\)' || echo 0)
echo "  source files = ${#compiled[@]} (per-source compiler table entries: ${n_cri})"

echo "== 2b/6 Residual split (sibling glabel or tail filler; HYBRID_RESIDUAL=$RESIDUAL) =="
mkdir -p "$OUT/residual"
MODES="$OUT/residual.tsv"
python3 - "$HERE" "$OUT" "$RESIDUAL" "${SYMS[@]}" -- "${SRCS[@]}" <<'PY' || exit 1
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tools/project")
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
    print("  [FAIL] HYBRID_RESIDUAL=0, but the .s of these symbols needs the residual split (it would lose sibling symbols or tail bytes):")
    for s in need[:15]:
        print("         " + s)
    sys.exit(1)
if blocked:
    print("  [FAIL] these symbols cannot split safely (cross-block reference, sibling label in the block, and similar). Remove them from the ledger:")
    for b in blocked[:20]:
        print("         " + b)
    sys.exit(1)
(out_dir / "residual.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("  residual objects %d / direct replacements %d" % (len(need), len(rows) - len(need)))
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
    --jobs "${JOBS:-4}" ${HYBRID_NO_CACHE:+--no-cache} --label "residual" || exit 1

echo "== 3/6 Safety gate: a C object must not add a non-empty allocatable section outside .text =="
# 1) A C object must have no allocatable section with size > 0 outside .text*. Otherwise
#    /DISCARD/ drops that content, and the result is a silent wrong code, not a link error.
# 2) A replaced asm object must hold .text only. Otherwise its removal loses data or bss.
# 3) Each symbol must really be defined in its C object.
# 1) 每个 C 对象里，除 .text* 外不得有 size>0 的可分配段（否则那些内容会被 /DISCARD/ 丢掉，
#    得到的是「静默错码」而不是链接错误）。
# 2) 被替换掉的 asm 对象必须只有 .text（否则摘掉它会丢数据/丢 bss）。
# 3) 每个符号必须真的在它的 C 对象里定义。
python3 "$HERE/tools/project/obj_gate.py" \
    --readelf "$READELF" --objdir "$OUT/obj" --srcdir "$SRCDIR" \
    --modes "$MODES" --residual-dir "$OUT/residual" --asm-cod-dir "build/asm/cod" \
    "${SYMS[@]}" -- "${SRCS[@]}" || exit 1

echo "== 4/6 Write the mixed build linker script (in-place replacement, same link order) =="
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
            # The target symbol is the first glabel in the file, so the residual (sibling
            # blocks and tail filler) follows it, in the same order as the original .o.
            keep.append('%s%s/residual/%s.o(.text*);' % (m.group(1), outrel, sym))
        continue
    # The .data/.rodata/.sdata/.sbss/.bss rows of the same symbol:
    #   direct   -- remove them all (the asm .o is no longer a link input)
    #   residual -- point them at the residual object, which keeps everything from the
    #               original .s except the target block
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
    print("  [FAIL] the linker script has no .text* row for: %s" % ', '.join(missing), file=sys.stderr)
    sys.exit(1)
open(out, 'w', encoding='utf-8').write('\n'.join(keep))
n_res = sum(1 for s in syms if modes.get(s) == 'residual')
print("  replaced the .text* row of %d symbols (%d with a residual object) -> %s" % (len(repl), n_res, out))
PY

echo "== 5/6 Link =="
# Define the undefined symbols (D_/func_0/.L) with an absolute address through --defsym. The
# rule is the same as in build.sh.
# Pass 1 links on purpose and fails. The script uses it to collect the undefined set only. The
# measured time on the development machine is about 2m20s (11k objects, more than 10k undefined
# references). That is the largest single cost of the whole mixed build pipeline. The script
# therefore reuses the previous defsyms.rsp for pass 2. It returns to pass 1 only when pass 2
# really fails, which means that a new undefined symbol appeared.
# 未定义符号（D_/func_0/.L）用绝对地址 --defsym 定义，与 build.sh 同一套规则。
# 第一遍「故意链接失败」只为收集未定义集合：在本机实测约 2m20s（11k 个对象、上万条未定义引用），
# 是整条 mixed build 流水线的最大单项开销。故先复用上一次的 defsyms.rsp 直接做第二遍；
# 只有第二遍真的失败（出现新的未定义符号）才回退到第一遍重新收集。
rm -f "$OUT/SLPS_258.19.elf"
link_pass2() {
    "$LD" -EL -m elf32ltsmip -T "$LDS" @"$OUT/defsyms.rsp" -Map "$OUT/SLPS_258.19.map" \
        -o "$OUT/SLPS_258.19.elf" 2>"$OUT/ld2.err"
}
collect_defsyms() {
    echo "  pass 1: collect the undefined symbols (about 2 minutes)"
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
    echo "  absolute address definitions: $(wc -l < "$OUT/defsyms.rsp")"
}

if [ -f "$OUT/defsyms.rsp" ]; then
    link_pass2 || true
    if [ ! -f "$OUT/SLPS_258.19.elf" ]; then
        echo "  the cached defsyms are not sufficient (the ledger changed or new undefined symbols appeared). Collect them again."
        collect_defsyms
        link_pass2 || true
    else
        echo "  reuse the cached defsyms ($(wc -l < "$OUT/defsyms.rsp") entries) and skip pass 1"
    fi
else
    collect_defsyms
    link_pass2 || true
fi
if [ ! -f "$OUT/SLPS_258.19.elf" ]; then
    echo "  link failed:"; grep -v "RWX" "$OUT/ld2.err" | head -20 >&2; exit 1
fi
echo "  ELF: $(stat -c%s "$OUT/SLPS_258.19.elf") B"

echo "== 6/6 Extract the payload and compare the sha1 =="
# The Japanese version has 2 PT_LOAD segments with a 0x80 hole between them. objcopy -O binary
# fills the hole with zeros and gives 9,305,064 B instead of 9,304,936 B. Use the same rule as
# build.sh: concatenate the PT_LOAD segments by the program headers.
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
print("  rebuilt sha1 = %s (%d B)" % (hb, len(b)))
print("  retail sha1 = %s (%d B)" % (hr, len(r)))
print("  expected sha1 = %s" % expect)
print("  word-identical = %d / %d (%.2f%%)" % (same, n//4, 100*same/max(n//4, 1)))

# Read the final address of each symbol and its provider object from the map (the proof for C).
# One pass only. The map has 370,000 lines and 850 symbols. A full scan per symbol took 43 seconds.
print("  -- provider of each ledger symbol (link map evidence) --")
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
print("  >>> %s <<<" % ("byte-identical: the mixed build passed" if ok else "mismatch: the mixed build failed"))
sys.exit(0 if ok else 1)
PY
