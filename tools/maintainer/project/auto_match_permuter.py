#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Near-miss convergence: connect decomp-permuter to the route B pipeline ("objdiff keeps 100% only", P1c).

Background (measured 2026-10-03):
  The Ghidra draft batch leaves many **near-miss** functions (objdiff 80-99%). Of 8,111
  unhit candidates, **1,197 are at 80% or more**, and 319 of those are at 95-99%. The
  meaning and the structure of these functions already agree. The difference is the
  **register allocation and the schedule**, which is the domain of decomp-permuter. One
  example, `func_00277d50` (99.75%), converged to score 0 in about 580 permuter iterations.

Method (for each candidate):
  1. Make the directory build/m2/perm/<sym>/ with base.c (the Ghidra draft), target.o (the
     assembled target block), compile.sh (fixed ee-gcc flags), and settings.toml
     (func_name/compiler_type/objdump_command).
  2. Run the permuter (`--stop-on-zero`, external timeout). It writes the converged source
     to output-0-*/source.c.
  3. **Verify the 100% result with objdiff**. The permuter score is only its own diff
     penalty, so the tool does not use it as acceptance.
  4. `--apply`: write src/matched/<sym>.c and merge the list (the same as the other matchers).

Usage:
  python3 tools/maintainer/project/auto_match_permuter.py run --from routebjp/build/m2/ghidra_batch/result.json \
      --min-match 95 --limit 30 --timeout 120 --jobs 3 [--apply]

近失收敛：把 decomp-permuter 接进路线 B 的「objdiff 只收 100%」流水线（P1c）。

背景（2026-10-03 实测）：
  Ghidra 草稿批留下大量**近失**函数（objdiff 80–99%）：8,111 个未命中候选里
  **1,197 个 ≥80%**（其中 95–99% 有 319 个）。这些函数语义/结构已对，
  差的是**寄存器分配与调度**——正是 decomp-permuter 的领域。
  单个样例 `func_00277d50`（99.75%）用 permuter 在 ~580 次迭代内收敛到 score 0。

做法（每个候选）：
  1. 建目录 build/m2/perm/<sym>/：base.c（Ghidra 草稿）、target.o（asm 目标块汇编）、
     compile.sh（ee-gcc 固定标志）、settings.toml（func_name/compiler_type/objdump_command）；
  2. 跑 permuter（`--stop-on-zero`，外部超时），它把收敛到的源码写到 output-0-*/source.c；
  3. **用 objdiff 复核 100%**（permuter 自己的 score 只是它的 diff 罚分，不作为验收）；
  4. `--apply`：写入 src/matched/<sym>.c + 合并清单（与其它匹配器一致）。

用法：
  python3 tools/maintainer/project/auto_match_permuter.py run --from routebjp/build/m2/ghidra_batch/result.json \
      --min-match 95 --limit 30 --timeout 120 --jobs 3 [--apply]
"""

# Private layout names (routebjp/build/m2/perm, routebjp/.tmp/permvenv, routebjp/build/llm_eval), do not rename.  私有布局名（routebjp/build/m2/perm、routebjp/.tmp/permvenv、routebjp/build/llm_eval），勿改名。

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_draft as GD  # noqa: E402
import m2c_draft as M2C  # noqa: E402
# Make the shared tools in tools/project importable.  让 tools/project 的共享工具可被导入。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project"))
from auto_match_trivial import (  # noqa: E402
    ROOT, PRIVATE_ROOT, WORK_ROOT, EVIDENCE_ROOT, MATCHED_LIST, SRCDIR, FLAGS_TSV,
    WORKQUEUE, GCC, AS, OBJDIFF, CFLAGS, M3_BEGIN, M3_END,
)
from at2_paths import OBJDUMP  # noqa: E402  section-size guard (P-97)
import split_asm as SPLIT  # noqa: E402  block boundary rule shared with the mixed build

REPO = PRIVATE_ROOT or ROOT            # Private work area (the .tmp/permvenv directory lives here)
PERMUTER = Path(os.environ.get("PERMUTER", Path.home() / "eecc" / "decomp-permuter" / "permuter.py"))
PYTHON = os.environ.get("PERMUTER_PYTHON", str(REPO / ".tmp" / "permvenv" / "bin" / "python"))
WORK = WORK_ROOT / "m2" / "perm"
# Output directory of the LLM candidate generator (written by `llm_match_eval.py`). It is a
# private work state, at the same level as the m2c drafts.
# Structure: <WORK_ROOT>/llm_eval/{llm,llm-fix}/<model>/<sym>/cand.c
# LLM 候选生成器的产物目录（`llm_match_eval.py` 写；私有侧工作状态，与 m2c 草稿同级）。
# 结构：<WORK_ROOT>/llm_eval/{llm,llm-fix}/<model>/<sym>/cand.c
LLM_EVAL = WORK_ROOT / "llm_eval"


def llm_drafts(sym: str) -> list[Path]:
    """Collect all LLM drafts of this symbol (several models and several arms).

    Added in round 66: use an LLM near-miss as a permuter seed.

    收集该符号的所有 LLM 草稿（多模型 / 多臂）。轮次 66 新增：把 LLM 近失当 permuter 种子。
    """
    if not LLM_EVAL.is_dir():
        return []
    return sorted(LLM_EVAL.glob(f"*/*/{sym}/cand.c"))
FLAGS_TSV = FLAGS_TSV
PREAMBLE = '.include "macro.inc"\n\n.set noat\n.set noreorder\n\n.section .text, "ax"\n'
OBJDUMP = str(Path.home() / "eecc" / "ps2binutils" / "mips-ps2-decompals-objdump")


def _score(sym: str, src: Path, d: Path) -> float | None:
    """Compile and run objdiff. Return the match percentage. Use it to select the best front end draft.

    编译 + objdiff，返回 match%；用于 best 前端挑草稿。
    """
    o = d / "score.o"
    r = subprocess.run([GCC, *CFLAGS, "-I", str(Path.home() / "eecc" / "m2c"), "-I", "include",
                        "-c", "-o", str(o), str(src)], cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    tj = d / "score.json"
    r = subprocess.run([OBJDIFF, "diff", "-1", str(d / "target.o"), "-2", str(o), "-o", str(tj), "--format", "json"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    try:
        data = json.loads(tj.read_text(encoding="utf-8"))
    except Exception:
        return None
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    m = per.get(sym)
    return float(m) if m is not None else None


# Flag matrix (P-32/P-40): try every -O level, every -G value, and every -f* option.
# `-Os` became known as an effective level only on 2026-10-05.
# 档位矩阵（P-32/P-40）：-O 级别 × -G × -f* 都要试；`-Os` 是 2026-10-05 才发现的有效档位。
FLAG_SETS = [["-Os"], ["-O2"], ["-O1"], ["-O3"], ["-O2", "-G8"], ["-O1", "-G8"], ["-O3", "-G8"],
             ["-Os", "-G8"], ["-O2", "-fno-common"], ["-O2", "-fomit-frame-pointer"],
             ["-O1", "-fomit-frame-pointer"], ["-O2", "-fno-builtin"],
             # R22 section 7-P4 (measured in round 70): the tail-call form lever j <-> jal+jr
             # (see O-05), and address splitting
             # R22 §7-P4（轮次 70 实测有效）：尾调用形态杠杆 j ↔ jal+jr（见 O-05），以及地址拆分
             ["-O2", "-fno-optimize-sibling-calls"], ["-Os", "-fno-optimize-sibling-calls"],
             ["-O1", "-fno-optimize-sibling-calls"], ["-O2", "-mno-split-addresses"]]


def best_flags(sym: str, src: Path, d: Path) -> list:
    """Select the flag level that is closest to the target.

    Measurement on 2026-10-04 (a teammate found it and the Lead verified it): `-O1` brings
    `func_001f72d0` from objdiff 75.2% directly to **100%**. All earlier batches used only
    `-O2`, so nobody had explored the compile flag axis.

    在若干编译档里挑与目标最接近的一档。

    2026-10-04 实测（由队友分析发现、Lead 复核）：`-O1` 能让 `func_001f72d0` 从 objdiff 75.2% 直接到 **100%**；
    此前所有批次都只用 `-O2`，编译档轴从未被探索。
    """
    best, best_m = FLAG_SETS[0], -1.0
    for fs in FLAG_SETS:
        o = d / ("flag" + "".join(fs).replace("-", "") + ".o")
        r = subprocess.run([GCC, *fs, "-falign-functions=4", "-ffunction-sections",
                            "-I", "include", "-c", "-o", str(o), str(src)],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode:
            continue
        m = None
        tj = d / "flag.json"
        rr = subprocess.run([OBJDIFF, "diff", "-1", str(d / "target.o"), "-2", str(o),
                             "-o", str(tj), "--format", "json"], cwd=str(ROOT),
                            capture_output=True, text=True)
        if rr.returncode == 0:
            try:
                data = json.loads(tj.read_text(encoding="utf-8"))
                per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
                       if s.get("kind") == "SYMBOL_FUNCTION"}
                m = per.get(sym)
            except Exception:
                m = None
        if m is not None and float(m) > best_m:
            best, best_m = list(fs), float(m)
            if best_m == 100.0:
                break
    (d / "_flags.txt").write_text(" ".join(best) + "\t%.2f" % best_m, encoding="utf-8")
    return best


def setup_dir(sym: str, frontend: str = "ghidra") -> Path | None:
    d = WORK / sym
    d.mkdir(parents=True, exist_ok=True)
    cands = []
    if frontend in ("m2c", "best", "best3"):
        s = M2C.emit(sym, d)
        if s is not None:
            cands.append(("m2c", s))
    if frontend in ("ghidra", "best", "best3"):
        s = GD.emit(sym, d)
        if s is not None:
            cands.append(("ghidra", s))
    if frontend in ("llm", "best3"):
        for i, q in enumerate(llm_drafts(sym)):
            cands.append((f"llm{i}", q))
    if not cands:
        return None
    shutil.copyfile(cands[0][1], d / "base.c")
    d.joinpath("_cands.txt").write_text("\n".join(f"{n}\t{q}" for n, q in cands), encoding="utf-8")
    f = ROOT / "asm" / "cod" / f"{sym}.s"
    if not f.is_file():
        return None
    L = f.read_text(encoding="utf-8", errors="replace").split("\n")
    gi = next((i for i, l in enumerate(L) if re.match(r"\s*glabel\s+", l)), None)
    en = next((i for i in range(gi or 0, len(L)) if re.match(r"\s*endlabel\s+", L[i])), None)
    if gi is None:
        return None
    if en is None:
        # 54 of the 10,926 .s files carry no endlabel: their body runs to the last instruction
        # (2026-10-12). split_asm decides the boundary and accepts only a whole-file
        # replacement that cannot lose a byte, so a wrong block stays impossible here.
        # 10,926 个 .s 里有 54 个没有 endlabel：块尾 = 最后一条指令（2026-10-12）。判定交给
        # split_asm；它只在「整份替换不丢字节」时接受，因此这里不会取出错误的块。
        info = SPLIT.analyze(sym, asm_dir=ROOT / "asm" / "cod")
        if info.get("mode") != "direct" or "end" not in info:
            return None
        en = info["end"]
    block = L[gi:en + 1]
    if not any(re.match(r"\s*endlabel\s+", x) for x in block):
        # Without an `endlabel` the target symbol carries no `.size`, so objdiff can guess the
        # size and stop before the end of the block (false 100.0; see auto_match_m2c.py).
        # 没有 endlabel 时目标符号没有 .size，objdiff 可能提前停止（假 100.0；见 auto_match_m2c.py）。
        block = block + [f"endlabel {sym}"]
    (d / "target.s").write_text(PREAMBLE + "\n".join(block) + "\n", encoding="utf-8")
    r = subprocess.run([AS, "-EL", "-march=r5900", "-I", "include", "-o", str(d / "target.o"), str(d / "target.s")],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    fl = best_flags(sym, d / "base.c", d)          # Select the flag level first (see best_flags).
    (d / "compile.sh").write_text(
        "#!/bin/bash\nexec %s %s -falign-functions=4 -ffunction-sections -c -I %s/include -I %s \"$@\"\n"
        % (GCC, " ".join(fl), ROOT, Path.home() / "eecc" / "m2c"), encoding="utf-8")
    os.chmod(d / "compile.sh", 0o755)
    (d / "settings.toml").write_text(
        'func_name = "%s"\ncompiler_type = "gcc"\nobjdump_command = "%s -d"\n' % (sym, OBJDUMP),
        encoding="utf-8")
    cf = d / "_cands.txt"          # best-of-both: select the draft by its match rate against the target
    if cf.is_file():
        scored = []
        for line in cf.read_text(encoding="utf-8").splitlines():
            if "\t" not in line:
                continue
            name, ps = line.split("\t", 1)
            m = _score(sym, Path(ps), d)
            scored.append((m if m is not None else -1.0, name, ps))
        if len(scored) > 1 and scored:
            scored.sort(reverse=True)
            if scored[0][0] >= 0:
                shutil.copyfile(scored[0][2], d / "base.c")
            (d / "_frontend.txt").write_text(
                "\n".join(f"{n}\t{m:.2f}" for m, n, _ in scored), encoding="utf-8")
    return d


def best_output(sym: str) -> Path | None:
    """Return the best source that the permuter wrote (score 0).

    取 permuter 写出的最优（score 0）源码。
    """
    d = WORK / sym
    cands = sorted(d.glob("output-0-*"))
    if not cands:
        # Also accept an output with a lower score. A non-zero score does not go to the
        # repository, but the code records it for a later analysis.
        # 也接受 score 更小的输出（非 0 不落地，但记录下来供后续分析）
        cands = sorted(d.glob("output-*"), key=lambda p: int(p.name.split("-")[1]) if p.name.split("-")[1].isdigit() else 999)
    for c in cands:
        s = c / "source.c"
        if s.is_file():
            return s
    return None


def _match_of(sym: str, c_o: Path, d: Path) -> float | None:
    dj = d / "verify.json"
    r = subprocess.run([OBJDIFF, "diff", "-1", str(d / "target.o"), "-2", str(c_o), "-o", str(dj), "--format", "json"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        return None
    try:
        data = json.loads(dj.read_text(encoding="utf-8"))
    except Exception:
        return None
    per = {s["name"]: s.get("match_percent") for s in data["left"]["symbols"]
           if s.get("kind") == "SYMBOL_FUNCTION"}
    m = per.get(sym)
    return float(m) if m is not None else None


def _text_size(obj: Path) -> int:
    """Sum every `.text*` section of one object. The C objects use -ffunction-sections.

    求和一个对象的全部 `.text*` 节（C 对象带 `-ffunction-sections`，节名是 `.text.<sym>`）。
    """
    r = subprocess.run([OBJDUMP, "-h", str(obj)], cwd=str(ROOT), capture_output=True, text=True)
    tot = 0
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) >= 3 and p[0].isdigit() and p[1].startswith(".text"):
            tot += int(p[2], 16)
    return tot


def verify(sym: str, source: Path) -> float | None:
    """Verify one candidate source and return the **best match rate over all compile flag levels**.

    Warning, 2026-10-05: earlier code verified with the default CFLAGS (-O2) only, but the
    permuter had converged at the level from best_flags() (-O1/-O3). The verification then
    rejected a converged result by mistake. That is why only 18 of 66 score-0 results in
    that batch passed.

    复核一个候选源码，返回**所有编译档里的最好命中率**。

    ⚠️ 2026-10-05：此前只用默认 CFLAGS（-O2）复核，而 permuter 是在 best_flags() 选出的档位下收敛的
    （-O1/-O3）⇒ 收敛结果在复核时被误判。该批 66 个 score-0 里只有 18 个过检，就是这个原因。
    """
    d = WORK / sym
    best: float | None = None
    flags_list = list(FLAG_SETS)
    # Try the flag level recorded for this candidate first (if one exists). Then try the other levels.
    # 先用本候选记录的档位（若有），再依次试其余档位
    try:
        rec = (d / "_flags.txt").read_text(encoding="utf-8").split("\t")[0].split()
        if rec:
            flags_list = [rec] + [f for f in FLAG_SETS if f != rec]
    except Exception:
        pass
    for i, fs in enumerate(flags_list):
        c_o = d / f"verify{i}.o"
        r = subprocess.run([GCC, *fs, "-falign-functions=4", "-ffunction-sections",
                            "-I", "include", "-c", "-o", str(c_o), str(source)],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode:
            continue
        # P-97 (measured 2026-10-12): objdiff 100.0 does **not** prove that the C object has the
        # same length as the asm object. The mixed build removes the whole asm .o, so a shorter
        # C object shifts every later byte and changes the payload. Require equal length here.
        # P-97（2026-10-12 实测）：objdiff 100.0 **不保证** C 对象与 asm 对象等长；混合构建是整份
        # 替换 .o，短一个字节就会让后续全体前移、载荷变化。这里要求等长。
        a_o = ROOT / "build" / "asm" / "cod" / f"{sym}.o"
        if a_o.is_file() and _text_size(c_o) != _text_size(a_o):
            continue
        m = _match_of(sym, c_o, d)
        if m is not None and (best is None or m > best):
            best = m
        if best == 100.0:
            break
    return best


def attempt(rec: dict, timeout: int, frontend: str = "ghidra") -> dict:
    sym = rec["sym"]
    out = {"sym": sym, "class": rec.get("class"), "base_match": rec.get("match"),
           "frontend": frontend, "permuter": "none", "objdiff": None}
    d = setup_dir(sym, frontend)
    if d is None:
        out["permuter"] = "setup_failed"
        return out
    for old in d.glob("output-*"):
        shutil.rmtree(old, ignore_errors=True)
    cmd = [PYTHON, str(PERMUTER), str(d), "-j1", "--stop-on-zero", "--quiet"]
    # ⚠️ Use a **separate process group** and kill the whole group on a timeout. permuter.py
    #    forks more child processes. A kill of the direct child only leaves orphans that
    #    continue to use CPU. (Measured 2026-10-05: 9 orphans, the oldest ran for 29 hours.)
    # ⚠️ 必须用**独立进程组**并在超时时杀整组：permuter.py 会再 fork 子进程，
    #    只杀直接子进程会留下孤儿继续吃 CPU（2026-10-05 实测清出 9 个，最久的跑了 29 小时）。
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, start_new_session=True)
    try:
        proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            proc.kill()
        try:
            proc.communicate(timeout=30)
        except Exception:
            pass
    # The output-0-* file from the permuter decides convergence. The code does not parse
    # stdout in --quiet mode.
    # 「是否收敛」以 permuter 自己写出的 output-0-* 为准（--quiet 下不解析 stdout）
    zero = any(p.name.startswith("output-0-") for p in d.glob("output-*"))
    out["permuter"] = "zero" if zero else "no_zero"
    src = best_output(sym)
    if src:
        out["objdiff"] = verify(sym, src)
        out["source"] = str(src)
    return out


def do_apply(winners: dict):
    SRCDIR.mkdir(parents=True, exist_ok=True)
    # Write the compile flag level of each converged candidate into source_flags.tsv. The key
    # is the second list column, that is the symbol name without extension (see P-34). Without
    # this, the build recompiles with the default -O2. The level then differs from the
    # verified level, and the payload check fails.
    # 把每个候选收敛时的编译档写进 source_flags.tsv（键 = 清单第二列，即符号名，无扩展名；见 P-34），
    # 否则构建会用默认 -O2 重编 ⇒ 与复核时的档位不一致 ⇒ 载荷校验红。
    fmap: dict[str, str] = {}
    if FLAGS_TSV.is_file():
        # Line 1 is the header row (source-basename<TAB>extra-cflags). Skip it.
        # 第 1 行是表头（source-basename<TAB>extra-cflags），跳过。
        for line in FLAGS_TSV.read_text(encoding="utf-8").splitlines()[1:]:
            a = line.split("\t")
            if len(a) >= 2 and not line.lstrip().startswith("#"):
                fmap[a[0]] = a[1]
    for sym, info in winners.items():
        shutil.copyfile(info["source"], SRCDIR / f"{sym}.c")
        try:
            rec = (WORK / sym / "_flags.txt").read_text(encoding="utf-8").split("\t")[0].strip()
        except Exception:
            rec = ""
        if rec and rec != "-O2":
            fmap[sym] = rec
        elif rec == "-O2" and sym in fmap:
            del fmap[sym]
    FLAGS_TSV.write_text("\n".join(["source-basename\textra-cflags"]
                                     + [f"{k}\t{fmap[k]}" for k in sorted(fmap)]) + "\n", encoding="utf-8")
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
    for sym in winners:
        existing[sym] = "permuter"
    body = "\n".join([pre, "", M3_BEGIN] + [f"{s}    # {existing[s]}" for s in sorted(existing)] + [M3_END])
    if post:
        body = body.rstrip("\n") + "\n" + post
    MATCHED_LIST.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
    print(f"apply: wrote {len(winners)} C sources; matching batch section {n0} -> {len(existing)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "apply-workdir"])
    ap.add_argument("--from", dest="src_json", default="routebjp/build/m2/ghidra_batch/result.json")
    ap.add_argument("--min-match", type=float, default=95.0)
    ap.add_argument("--max-match", type=float, default=99.999)
    ap.add_argument("--classes", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--symbols-file", default="")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--frontend", default="ghidra", choices=["ghidra", "m2c", "best", "llm", "best3"])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if args.mode == "apply-workdir":
        # Harvest from build/m2/perm/*/output-0-*/source.c. This form commits the converged
        # results while a batch is still running.
        # 从 build/m2/perm/*/output-0-*/source.c 收割（可在批量跑一半时落地已收敛的结果）
        winners = {}
        for d in sorted(WORK.glob("*")):
            outs = sorted(d.glob("output-0-*"))
            if not outs or not (outs[-1] / "source.c").is_file():
                continue
            sym = d.name
            m = verify(sym, outs[-1] / "source.c")
            if m == 100.0:
                winners[sym] = {"source": str(outs[-1] / "source.c"), "objdiff": m}
            print(f"  {sym}: objdiff={m}")
        print(f"workdir harvest: {len(winners)} at objdiff 100%")
        if args.apply and winners:
            do_apply(winners)
        (WORK / "accepted.json").write_text(json.dumps(winners, indent=1, ensure_ascii=False), encoding="utf-8")
        return 0

    data = json.loads(Path(args.src_json).read_text(encoding="utf-8"))
    # Skip a symbol that is already in the list. A second run only wastes CPU.
    # 已在清单里的符号跳过（重复跑只是浪费 CPU）
    have = set()
    if MATCHED_LIST.is_file():
        for line in MATCHED_LIST.read_text(encoding="utf-8").splitlines():
            a = line.split("#", 1)[0].strip()
            if a:
                have.add(a.split()[0])
    data = [r for r in data if r["sym"] not in have]
    if args.symbols_file:
        want = [l.strip() for l in Path(args.symbols_file).read_text(encoding="utf-8").splitlines() if l.strip()]
        by = {r["sym"]: r for r in data}
        data = [by[s] for s in want if s in by]
    sel = [r for r in data if r.get("match") is not None and args.min_match <= r["match"] < args.max_match]
    if args.classes:
        want = set(args.classes.split(","))
        sel = [r for r in sel if r.get("class") in want]
    sel.sort(key=lambda r: -r["match"])
    if args.limit:
        sel = sel[:args.limit]
    print(f"== near-miss convergence: {len(sel)} candidates (frontend {args.frontend}, match in [{args.min_match},{args.max_match}), timeout {args.timeout}s, parallel {args.jobs}) ==")
    WORK.mkdir(parents=True, exist_ok=True)

    results = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i, res in enumerate(pool.map(lambda r: attempt(r, args.timeout, args.frontend), sel), 1):
            results.append(res)
            if i % 5 == 0 or i == len(sel):
                ok = sum(1 for x in results if x.get("objdiff") == 100.0)
                print(f"   ... {i}/{len(sel)} (objdiff 100% = {ok})")
    winners = {r["sym"]: r for r in results if r.get("objdiff") == 100.0}
    (WORK / "result.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    c = Counter(r["permuter"] for r in results)
    print("  permuter status:", dict(c))
    if sel:
        print(f"  hits: {len(winners)}/{len(sel)} = {100.0*len(winners)/len(sel):.1f}%")
    if args.apply and winners:
        do_apply(winners)
    return 0


if __name__ == "__main__":
    sys.exit(main())
