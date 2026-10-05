#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""大池筛查：把 N 个候选草稿合并成**一个 TU**，每档只编译一次，再用 objdiff 逐符号取分。

动机（2026-10-05，队友 task-4 的 `combined` 思路）：
  逐候选编译 8,000 个×5 档 = 4 万次 ee-gcc（约 1.5 小时）。合并 TU 后 **每档只编译 1 次**（共 5 次），
  objdiff 仍按符号逐个比对（每次 ~50 ms），总耗时降到 **分钟级**。
  队友已验证：同一写法在合并 TU 与单独编译下 **逐字节相同**（12 样本），所以筛查结论可信；
  但正式入库前仍要**逐候选复核**（沿用 auto_match_m2c/permuter 的 verify）。

用法：
  python3 routebjp/tools/screen_flags.py run [--limit N] [--flags "O2,O1,O3,O2 -G8,O1 -G8,Os"] [--frontend m2c|ghidra]
  python3 routebjp/tools/screen_flags.py report        # 打印历史最佳（build/screen/screen.json）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_draft as GD  # noqa: E402
import m2c_draft as M2C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
GCC = str(Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / "ee-gcc")
AS = str(Path.home() / "eecc" / "ps2binutils" / "mips-ps2-decompals-as")
OBJDIFF = str(Path.home() / "eecc" / "objdiff-cli")
OUT = ROOT / "build" / "screen"
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
DEFAULT_FLAGS = ("Os,O2,O1,O3,O2 -G8,O1 -G8,O3 -G8,Os -G8,O2 -fno-common,O3 -fno-common,"
                 "G0,G4,O2 -fomit-frame-pointer,O1 -fomit-frame-pointer,O2 -fno-builtin,"
                 "O2 -fno-schedule-insns2,Os -fno-schedule-insns2")
WORKQUEUE = REPO / "out" / "evidence" / "jp_m3_workqueue.tsv"
MATCHED = ROOT / "config" / "matched_symbols.txt"


def unmatched() -> list[dict]:
    have = set()
    for line in MATCHED.read_text(encoding="utf-8").splitlines():
        a = line.split("#", 1)[0].strip()
        if a:
            have.add(a.split()[0])
    rows = []
    for line in WORKQUEUE.read_text(encoding="utf-8").splitlines()[1:]:
        p = line.split("\t")
        if len(p) > 12 and p[0] not in have and p[11].strip() != "blocked_cross_ref" \
                and p[11].strip() != "blocked_inner_label" and p[11].strip() != "blocked_no_endlabel":
            rows.append({"sym": p[0], "size": int(p[2]), "class": p[12]})
    return rows


PLACEHOLDERS = [
    (re.compile(r"\b(?:first|second)\s+half\s+of\s+(?:f64|u64|s64|f32|s32|u32)\b"), "0"),
    (re.compile(r"\bsubroutine_arg\d+\b"), "0"),
    (re.compile(r"\bunreachable\b"), "0"),
    (re.compile(r"\bunknown_[a-z_]+\b"), "0"),
]


def sanitize(txt: str) -> str:
    """把 m2c 的「不可表达」占位短语替换成 0，让合并 TU 至少能编译。

    这类草稿本来就对不上目标（m2c 自己也没恢复出来），筛查只需它们不阻塞编译。
    """
    # m2c 会把「// Error: ...」插在表达式中间 ⇒ 该行被截断成语法错误。筛查阶段直接剥掉行内注释。
    txt = re.sub(r"//[^\n]*", "", txt)
    for rx, rep in PLACEHOLDERS:
        txt = rx.sub(rep, txt)
    return txt


def target_obj(sym: str, d: Path) -> Path | None:
    f = ROOT / "asm" / "cod" / f"{sym}.s"
    if not f.is_file():
        return None
    L = f.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next((i for i, l in enumerate(L) if re.match(r"\s*glabel\s+", l)), None)
    en = next((i for i in range(gi or 0, len(L)) if re.match(r"\s*endlabel\s+", L[i])), None)
    if gi is None or en is None:
        return None
    ts = d / f"{sym}.t.s"
    ts.write_text(PREAMBLE + "\n".join(L[gi:en + 1]) + "\n", encoding="utf-8")
    to = d / f"{sym}.t.o"
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(to), str(ts)],
                       cwd=str(ROOT), capture_output=True, text=True)
    return to if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "report"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--flags", default=DEFAULT_FLAGS)
    ap.add_argument("--frontend", default="m2c", choices=["m2c", "ghidra"])
    ap.add_argument("--classes", default="")
    a = ap.parse_args()

    if a.mode == "report":
        f = OUT / "screen.json"
        if not f.is_file():
            print("还没有筛查结果")
            return 0
        data = json.loads(f.read_text(encoding="utf-8"))
        best = data.get("best", {})
        perfect = [s for s, v in best.items() if v.get("match") == 100.0]
        print(f"历史最佳：覆盖 {len(best)} 个候选，其中 100% = {len(perfect)}")
        c = Counter(best[s]["flags"] for s in perfect)
        print("  命中档位:", dict(c))
        for s in perfect[:40]:
            print(f"   {s:20s} {best[s]['flags']}")
        return 0

    rows = unmatched()
    if a.classes:
        want = set(a.classes.split(","))
        rows = [r for r in rows if r["class"] in want]
    rows.sort(key=lambda r: r["size"])
    if a.limit:
        rows = rows[:a.limit]
    print(f"== 合并 TU 筛查：候选 {len(rows)} 个，前端 {a.frontend}，档位 {a.flags} ==")
    OUT.mkdir(parents=True, exist_ok=True)
    dr = OUT / "drafts"
    dr.mkdir(parents=True, exist_ok=True)

    # 1) 生成草稿 + 目标对象
    ok: list[dict] = []
    for r in rows:
        sym = r["sym"]
        # 复用历史草稿（build/m2c/batch/<sym>/<sym>.m2c.c）以省掉重新生成的时间；
        # 没有才现生成。注意：m2c_draft.py 若已更新，历史草稿可能略旧 —— 筛查只用来**找候选**，
        # 命中后仍要逐候选重新生成 + 复核，所以不影响正确性。
        cached = ROOT / "build" / "m2c" / "batch" / sym / f"{sym}.m2c.c"
        try:
            if a.frontend == "m2c" and cached.is_file():
                src = dr / f"{sym}.m2c.c"
                src.write_text(cached.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
            else:
                src = M2C.emit(sym, dr) if a.frontend == "m2c" else GD.emit(sym, dr)
        except Exception:
            src = None
        if src is None:
            continue
        to = target_obj(sym, dr)
        if to is None:
            continue
        ok.append({"sym": sym, "draft": src})
    print(f"   可用草稿 {len(ok)} / {len(rows)}")

    CHUNK = 60       # 每块函数数：太大编译冲突多、太小编译次数多；60 是折中（P-39/P-40）
    # 2) 合并（分块）
    header = ("typedef signed char s8; typedef unsigned char u8; typedef short s16; typedef unsigned short u16;\n"
              "typedef int s32; typedef unsigned int u32; typedef long long s64; typedef unsigned long long u64;\n"
              "typedef float f32; typedef double f64;\n"
              "typedef int s128 __attribute__((mode(V4SI))); typedef int u128 __attribute__((mode(V4SI)));\n"
              "typedef s32 M2C_UNK; typedef s8 M2C_UNK8; typedef s16 M2C_UNK16; typedef s32 M2C_UNK32; typedef s64 M2C_UNK64;\n"
              "#define M2C_FIELD(expr, type_ptr, offset) (*(type_ptr)((s8 *)(expr) + (offset)))\n"
              "#define M2C_BITWISE(type, expr) ((type)(expr))\n#define M2C_LIKELY(x) (x)\n#define M2C_UNLIKELY(x) (x)\n"
              "#define NULL 0\n#define M2C_ERROR() 0\nextern unsigned char *sp;\n")
    # 合并 TU 的类型冲突处理（两遍）：
    #   ① 先收集「在某个草稿里被定义」的函数名（m2c 偶尔会在草稿里带上邻接 thunk 的定义）；
    #   ② extern 声明按标识符去重，且**跳过已被定义的**——否则会出现 conflicting types。
    kept = []
    for r in ok:
        txt = sanitize(r["draft"].read_text(encoding="utf-8", errors="replace"))
        if "M2C_ERROR" in txt or "Error:" in txt:
            continue          # m2c 恢复失败的草稿：占位符会把表达式结构破坏，且本来也不可能匹配
        r["text"] = txt
        kept.append(r)
    ok = kept
    print(f"   可并入合并 TU 的草稿 {len(ok)}")
    chunks = [ok[i:i + CHUNK] for i in range(0, len(ok), CHUNK)]
    print(f"   切成 {len(chunks)} 块（每块 ≤{CHUNK} 个函数）", flush=True)
    defined: set[str] = set()
    def_re = re.compile(r"^\s*(?:[A-Za-z_][\w \*]*?)\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{", re.M)
    for r in ok:
        for m in def_re.finditer(r["text"]):
            defined.add(m.group(1))

    def build_chunk(chunk: list, path: Path) -> None:
        decls: dict[str, str] = {}
        bodies = []
        for r in chunk:
            keep = []
            for l in r["text"].split("\n"):
                if re.match(r"^\s*(typedef|#define|#include)", l):
                    continue
                m = re.match(r"^\s*extern\b.*?\b([A-Za-z_]\w*)\s*(\[[^\]]*\])?\s*(__attribute__[^;]*)?;", l)
                if m:
                    name = m.group(1)
                    if name in defined:
                        continue
                    decls.setdefault(name + (m.group(2) or ""), l.strip())
                    continue
                # m2c 的「函数原型 + /* extern */」写法。跨草稿的签名经常互相冲突
                # （too many/few arguments to function）⇒ 统一降级成 C89 无参原型 `extern int NAME();`，
                # 召唤实参不再做类型/个数检查，合并 TU 才能编过（筛查只关心候选本身能否匹配）。
                m2 = re.match(r"^\s*[A-Za-z_][\w \*]*?\b([A-Za-z_]\w*)\s*\([^;{]*\)\s*;\s*(/\*\s*extern\s*\*/)?\s*$", l)
                if m2 and m2.group(2):
                    name = m2.group(1)
                    if name in defined:
                        continue
                    decls.setdefault(name, f"extern int {name}();")
                    continue
                keep.append(l)
            bodies.append("\n".join(keep))
        path.write_text("\n\n".join([header + "\n".join(sorted(decls.values()))] + bodies), encoding="utf-8")

    flags_list = [[t if t.startswith("-") else "-" + t for t in item.split()]
                  for item in a.flags.split(",")]
    best: dict[str, dict] = {}
    import collections as _c
    queue = _c.deque((i, c) for i, c in enumerate(chunks))
    cid = len(chunks)
    while queue:
        ci, chunk = queue.popleft()
        merged = OUT / f"chunk{ci}.c"
        build_chunk(chunk, merged)
        # 先把这一块在所有档位都编译一遍；任一档失败 → 二分重试（跨草稿类型冲突常见）
        objs = []
        bad = False
        for fs in flags_list:
            key = "".join(fs).replace("-", "")
            mo = OUT / f"chunk{ci}_{key}.o"
            r = subprocess.run([GCC, *fs, "-falign-functions=4", "-ffunction-sections",
                                "-I", "include", "-c", "-o", str(mo), str(merged)],
                               cwd=str(ROOT), capture_output=True, text=True)
            if r.returncode:
                bad = True
                break
            objs.append((fs, mo))
        if bad:
            if len(chunk) <= 4:
                print(f"   块 {ci}（{len(chunk)} 个函数）编不过，跳过", flush=True)
                continue
            mid = len(chunk) // 2
            queue.append((cid, chunk[:mid])); cid += 1
            queue.append((cid, chunk[mid:])); cid += 1
            continue
        for fs, mo in objs:
            for rec in chunk:
                sym = rec["sym"]
                to = dr / f"{sym}.t.o"
                dj = OUT / "one.json"
                rr = subprocess.run([OBJDIFF, "diff", "-1", str(to), "-2", str(mo),
                                     "-o", str(dj), "--format", "json"],
                                    cwd=str(ROOT), capture_output=True, text=True)
                if rr.returncode:
                    continue
                try:
                    data = json.loads(dj.read_text(encoding="utf-8"))
                except Exception:
                    continue
                per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
                       if s.get("kind") == "SYMBOL_FUNCTION"}
                m = per.get(sym)
                if m is None:
                    continue
                prev = best.get(sym)
                if prev is None or float(m) > prev["match"]:
                    best[sym] = {"match": float(m), "flags": " ".join(fs)}
        n100 = sum(1 for v in best.values() if v["match"] == 100.0)
        print(f"   块 {ci}（{len(chunk)} 个）完成：累计覆盖 {len(best)}，100% = {n100}", flush=True)
    sj = OUT / "screen.json"
    prev_all = {}
    if sj.is_file():
        try:
            prev_all = json.loads(sj.read_text(encoding="utf-8")).get("best", {})
        except Exception:
            prev_all = {}
    for s, v in best.items():
        if s not in prev_all or v["match"] > prev_all[s]["match"]:
            prev_all[s] = v
    sj.write_text(json.dumps({"best": prev_all}, indent=1, ensure_ascii=False), encoding="utf-8")
    perfect = sum(1 for v in prev_all.values() if v["match"] == 100.0)
    print(f"  合计：覆盖 {len(prev_all)} 个候选，历史 100% = {perfect}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
