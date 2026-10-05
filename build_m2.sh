#!/bin/bash
# M2：C 化流水线（写 C -> ee-gcc 编译 -> objdiff 与原版逐符号比对）
# 前置：已跑过 build.sh（产出 asm/ 与 target）
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
BINUTILS="${BINUTILS:-$HOME/eecc/ps2binutils}"
GCC="${GCC:-$HOME/eecc/ee-gcc3.2-040921/bin/ee-gcc}"   # 已判决：游戏代码用 3.2-ee-040921
OBJDIFF="${OBJDIFF:-$HOME/eecc/objdiff-cli}"
SYMS="baseelf_15 baseelf_19 baseelf_9 baseelf_98 baseelf_36 baseelf_85 baseelf_60 baseelf_77 baseelf_88 LibgccCommon_19 LibgccCommon_20"

mkdir -p build/m2
echo "== 1/3 抽取 target（来自 splat 的 asm，按符号切出）=="
python3 tools/build/m2_extract.py asm build/m2/target.s $SYMS
"$BINUTILS/mips-ps2-decompals-as" -EL -march=r5900 -I include -o build/m2/target.o build/m2/target.s

echo "== 2/3 编译 base（C）=="
"$GCC" -O2 -c -o build/m2/base.o src/m2_probe.c

echo "== 3/3 objdiff =="
"$OBJDIFF" diff -1 build/m2/target.o -2 build/m2/base.o -o build/m2/diff.json --format json
echo "== 4/4 decomp.dev 进度报告 =="
"$OBJDIFF" report generate -o build/report.json 2>&1 | tail -1

python3 - <<'PY'
import json
d=json.load(open('build/m2/diff.json'))
tot=full=0
for s in d['left']['symbols']:
    if s.get('kind')!='SYMBOL_FUNCTION': continue
    tot+=1; mp=s.get('match_percent') or 0
    if mp==100.0: full+=1
    print("  %-22s %6.1f%%"%(s['name'],mp))
print("  ---- 100%% 匹配 = %d / %d"%(full,tot))
try:
    r=json.load(open("build/report.json"))["measures"]
    print("  decomp.dev: matched_functions=%s/%s  matched_code=%.2f%%  fuzzy=%.2f%%"%(r["matched_functions"],r["total_functions"],r["matched_code_percent"],r["fuzzy_match_percent"]))
except Exception as e:
    pass
PY
