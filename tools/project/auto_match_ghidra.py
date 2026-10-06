#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 批量匹配：Ghidra 伪 C 草稿 → 编译 → objdiff 裁决 → 落地（P1a/P1d 的生产版）。

流程（每个候选符号）：
  1. 从 `routebjp/build/ghidra/SLPS_258.19.decomp.c` 抽该函数的伪 C，补 shim、
     把 `FUN_x` 改回我们的符号名、`DAT_x/_DAT_x/PTR_..._x` 改回 `D_<HEX>`（否则重定位名不匹配）；
  2. 用指定编译档（默认 `-O2`，可选追加 `-O1` 回退）编译；
  3. 与 `asm/cod/<sym>.s` 的目标块做 objdiff，**只收 100%**；
  4. `--apply`：写入 `src/matched/<sym>.c`、合并清单 M3 段、维护 `config/source_flags.tsv`。

判据（与既有流水线一致）：objdiff == 100.0 才落地；落地后由 hybrid 载荷棘轮兜底。
G1 实测（docs/R11 §4，2026-10-03）：随机 60 例（B/D/E/F 各 15）编译 87%、objdiff 100% 13.3%；
B/D 两类 27%/20%，高于 15% 判定线 ⇒ 采信伪 C 草稿路线。

用法：
  python3 routebjp/tools/auto_match_ghidra.py run [--classes B_straight,D_single_call,...] \
      [--limit N] [--flags "-O2,-O1"] [--jobs 4] [--apply]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_draft as GD  # noqa: E402
from auto_match_trivial import (  # noqa: E402
    ROOT, WORK_ROOT, EVIDENCE_ROOT, WORKQUEUE, MATCHED_LIST, SRCDIR, GCC, AS, OBJDIFF,
    CFLAGS, split_mode, matched_in_list, M3_BEGIN, M3_END,
)

BUILD = WORK_ROOT / "m2" / "ghidra_batch"
FLAGS_FILE = ROOT / "config" / "source_flags.tsv"   # 配置在项目根（公开仓库）
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
# G_mmi 不跳过：Ghidra 的 r5900 语言把 lq/sq 展开成 4 次 32 位访存，实测不少
# MMI 函数能出**普通 C**（见 out/evidence/jp_m3_p1_result.txt），值得一起试。
SKIP_CLASSES = {"jtbl", "gp_rel", "no_asm", "unknown"}


def rows():
    lines = WORKQUEUE.read_text(encoding="utf-8").splitlines()
    idx = {k: i for i, k in enumerate(lines[0].split("\t"))}
    return [{k: p[i] for k, i in idx.items()} for p in (l.split("\t") for l in lines[1:])
            if len(p) >= len(idx)]


def target_block(sym: str) -> str | None:
    f = ROOT / "asm" / "cod" / f"{sym}.s"
    if not f.is_file():
        return None
    L = f.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next((i for i, x in enumerate(L) if re.match(r"\s*glabel\s+", x)), None)
    en = next((i for i in range(gi or 0, len(L)) if re.match(r"\s*endlabel\s+", L[i])), None)
    if gi is None or en is None:
        return None
    return PREAMBLE + "\n".join(L[gi:en + 1]) + "\n"


def candidates(classes: set[str], limit: int):
    have = matched_in_list()
    out = []
    for r in rows():
        if r["name"] in have:
            continue
        # 显式点名类别时不套用默认跳过表（用于 gp_rel/jtbl 这类"机制外"的实验）
        if classes:
            if r["class"] not in classes:
                continue
        elif r["class"] in SKIP_CLASSES:
            continue
        if split_mode(r["name"]).startswith("blocked"):
            continue
        if GD.body_of(r["name"]) is None:
            continue
        out.append(r)
    if limit:
        out = out[:limit]
    return out


def probe(rec: dict, flags_sets: list[list[str]]) -> dict:
    sym = rec["name"]
    d = BUILD / sym
    d.mkdir(parents=True, exist_ok=True)
    res = {"sym": sym, "class": rec["class"], "size": int(rec["size"]), "flags": "", "match": None,
           "compile_ok": False}
    # gp_rel 类：从汇编里取 %gp_rel(D_x) 的符号，让草稿把它们写成 **weak 定义**（放在 .sdata/.sbss），
    # 这样 GCC 才发 gp 相对寻址；这些段不在 hybrid 链接脚本里 → 被 /DISCARD/ 丢弃，存储仍来自原数据对象。
    gprel = None
    if rec.get("class") == "gp_rel":
        asm = (ROOT / "asm" / "cod" / f"{sym}.s").read_text(encoding="utf-8", errors="replace")
        gprel = set(re.findall(r"%gp_rel\((\w+)\)", asm))
    src = GD.emit(sym, d, gprel_syms=gprel)
    if src is None:
        res["error"] = "no_draft"
        return res
    tb = target_block(sym)
    if tb is None:
        res["error"] = "no_block"
        return res
    ts = d / "target.s"
    ts.write_text(tb, encoding="utf-8")
    t_o = d / "t.o"
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(t_o), str(ts)],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        res["error"] = "target_as"
        return res
    for fs in flags_sets:
        c_o = d / ("c" + ("_" + "_".join(fs) if fs else "") + ".o")
        r = subprocess.run([GCC, *CFLAGS, *fs, "-I", "include", "-c", "-o", str(c_o), str(src)],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode:
            res["compile_ok"] = False
            lines = [l for l in r.stderr.splitlines() if "error" in l.lower()]
            res["compile_error"] = (lines[0] if lines else "")[:140]
            continue
        res["compile_ok"] = True
        dj = d / ("diff_" + ("_".join(fs) if fs else "base") + ".json")
        r = subprocess.run([OBJDIFF, "diff", "-1", str(t_o), "-2", str(c_o), "-o", str(dj), "--format", "json"],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode:
            continue
        data = json.loads(dj.read_text(encoding="utf-8"))
        per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
               if s.get("kind") == "SYMBOL_FUNCTION"}
        m = per.get(sym)
        if m is not None:
            if res["match"] is None or m > res["match"]:
                res["match"] = float(m)
                res["flags"] = " ".join(fs)
            if m == 100.0:
                res["cfile"] = str(c_o)
                return res
    return res


def do_apply(winners: dict):
    SRCDIR.mkdir(parents=True, exist_ok=True)
    for sym, info in winners.items():
        shutil.copyfile(BUILD / sym / f"{sym}.draft.c", SRCDIR / f"{sym}.c")
    text = MATCHED_LIST.read_text(encoding="utf-8")
    pre = text.split(M3_BEGIN)[0].rstrip("\n") if M3_BEGIN in text else text.rstrip("\n")
    post = text.split(M3_END, 1)[1].lstrip("\n") if M3_END in text else ""
    existing: "OrderedDict[str, str]" = OrderedDict()
    if M3_BEGIN in text:
        seg = text.split(M3_BEGIN, 1)[1]
        seg = seg.split(M3_END, 1)[0] if M3_END in seg else seg
        for line in seg.split("\n"):
            a = line.split("#", 1)
            if a[0].strip():
                existing[a[0].strip()] = a[1].strip() if len(a) > 1 else ""
    n0 = len(existing)
    for sym, info in winners.items():
        existing[sym] = "ghidra_draft" + (":" + info["flags"].replace(" ", "") if info["flags"] else "")
    body = "\n".join([pre, "", M3_BEGIN] + [f"{s}    # {existing[s]}" for s in sorted(existing)] + [M3_END])
    if post:
        body = body.rstrip("\n") + "\n" + post
    MATCHED_LIST.write_text(body.rstrip("\n") + "\n", encoding="utf-8")

    flags = {}
    if FLAGS_FILE.is_file():
        for line in FLAGS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                a = line.split()
                flags[a[0]] = " ".join(a[1:])
    for sym, info in winners.items():
        fl = info["flags"]
        if fl and fl != "-O2":          # -O2 是默认档，不写进标志表（避免噪声）
            flags[sym] = fl
        else:
            flags.pop(sym, None)
    out = ["# 每源额外编译标志（build_hybrid.sh 读取；-O2 为默认，不写）",
           "# 格式：<source-basename>\t<extra-cflags>"]
    out += [f"{s}\t{flags[s]}" for s in sorted(flags)]
    FLAGS_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"apply: 写 {len(winners)} 个 C 源；清单 M3 段 {n0} -> {len(existing)}；标志表 {len(flags)} 条")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "apply-only"])
    ap.add_argument("--classes", default="", help="逗号分隔；空=所有非跳过类")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--flags", default="Os,O2,O1,O3,O2 -G8,O1 -G8,O3 -G8,O2 -fno-common,O2 -fomit-frame-pointer,O1 -fomit-frame-pointer,O2 -fno-builtin",
                    help="逗号分隔的编译档候选（**不要带前导 -**，如 O2,O1）。P-32：编译档轴必须探索")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if args.mode == "apply-only":
        res = json.loads((BUILD / "result.json").read_text(encoding="utf-8"))
        winners = {r["sym"]: r for r in res if r.get("match") == 100.0}
        print(f"apply-only：从 result.json 取 {len(winners)} 个 objdiff 100% 的符号")
        do_apply(winners)
        return 0

    classes = {c for c in args.classes.split(",") if c}
    # 每个逗号分隔项 = 一组标志，组内可含空格（如 "O2 -G8"）
    flags_sets = []
    for item in args.flags.split(","):
        item = item.strip()
        if not item:
            flags_sets.append([])
            continue
        toks = []
        for tok in item.split():
            toks.append(tok if tok.startswith("-") else "-" + tok)
        flags_sets.append(toks)
    cands = candidates(classes, args.limit)
    print(f"== Ghidra 草稿批：候选 {len(cands)} 个（编译档 {args.flags}）==")
    BUILD.mkdir(parents=True, exist_ok=True)

    results = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i, res in enumerate(pool.map(lambda r: probe(r, flags_sets), cands), 1):
            results.append(res)
            if i % 200 == 0:
                print(f"   ... {i}/{len(cands)}（已命中 {sum(1 for x in results if x.get('match') == 100.0)}）")

    winners = {r["sym"]: r for r in results if r.get("match") == 100.0}
    (BUILD / "result.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    by = {}
    for r in results:
        v = by.setdefault(r["class"], {"n": 0, "compile": 0, "hit": 0})
        v["n"] += 1
        v["compile"] += 1 if r.get("compile_ok") else 0
        v["hit"] += 1 if r.get("match") == 100.0 else 0
    print("  " + f"{'class':16s}{'n':>7}{'编译':>8}{'命中':>7}{'命中率':>8}")
    for k in sorted(by):
        v = by[k]
        print(f"  {k:16s}{v['n']:>7}{v['compile']:>8}{v['hit']:>7}{(100.0*v['hit']/v['n']):>7.1f}%")
    n = len(results)
    print(f"  合计：候选 {n}，编译通过 {sum(1 for r in results if r.get('compile_ok'))}，"
          f"objdiff 100% = {len(winners)}（{100.0*len(winners)/max(n,1):.1f}%）")
    fl = Counter(w["flags"] for w in winners.values())
    for k, v in fl.most_common():
        print(f"    命中档位 {k or '-O2(默认)'}: {v}")
    print(f"结果 JSON -> {BUILD / 'result.json'}")
    if args.apply:
        do_apply(winners)
    return 0


if __name__ == "__main__":
    sys.exit(main())
