#!/usr/bin/env python3
"""Generate the per-function objdiff report. This report is the decomp.dev upload rule.

Why the script exists (P8, 2026-10-05):
  The older `tools/build/gen_objdiff_full.py` used the .s files from splat as the
  target. A splat `cod/*.s` file does not always hold one function. In
  `routebjp/asm/cod`, 1,677 files hold two or more `glabel` lines. The whole asm
  tree holds 13,250 glabel lines, and symbol_addrs lists 10,923. Therefore one
  unit held several functions. When the base held only one of them, objdiff
  marked the unit partial (`matched_code_percent < 100`) even though the linked
  payload was byte-identical. Measured: a target extracted as a single-function
  object reports 100 percent for the same function.

The rule of this script (the same as the task-4 work order):
  * The unit set is every `type:func` entry in `config/symbol_addrs.txt`
    (10,923 functions). One function is one unit.
  * target = the function extracted from `asm/` and written to
    `build/units/<sym>.s`. The glabel/endlabel extraction is the same as before.
    `mips-ps2-decompals-as` assembles the file into
    `build/units/<sym>.target.o`. If the content does not change, the script
    reuses the old .o file.
  * base = `build/mixed/obj/<src>.o`. The script uses this base only when the
    symbol is in `config/matched_symbols.txt` and its comment tag does not start
    with `stub_`. For every other symbol, base_path = null, and the report counts
    the function as unmatched.
  * category: a non-stub symbol with C code goes to `c`. A stub goes to `asm`
    with base_path = null, so matched_functions stays 0.

Output:
  * `<project>/build/report_function.json` (the objdiff report);
  * with `--baseline-out`: write the measures of this report to a JSON baseline;
  * with `--public-dir`: copy the report to
    `<public-dir>/SLPS_258.19_report.json`.

Usage:
  python3 tools/report/gen_function_report.py                 # full run: extract, assemble, report
  python3 tools/report/gen_function_report.py --limit 50      # smoke test
  python3 tools/report/gen_function_report.py --no-run        # write objdiff.json only
  python3 tools/report/gen_function_report.py --baseline-out <path> --public-dir <dir>

函数粒度（per-function）objdiff 报告生成器，这是 decomp.dev 上报口径。

为什么需要（P8，2026-10-05）：旧的 gen_objdiff_full.py 用 splat 拆出的 .s 文件当
target，但 cod/*.s 不总是「一个文件一个函数」（1,677 个文件含两个以上 glabel），
于是一条 unit 塞了多个函数；base 只提供其中一个时 objdiff 就判 partial，
即使链接后的载荷字节完全一致。把 target 抽成单函数对象后同一函数报 100%。

本脚本口径：unit 集合 = config/symbol_addrs.txt 里 type:func 的全部函数，一个函数一条
unit；target = 从 asm/ 抽出该函数写成 build/units/<sym>.s 并独立汇编成
build/units/<sym>.target.o（抽出算法与此前一致，内容未变则复用旧 .o）；
base = build/mixed/obj/<src>.o，仅当符号已登记且注释 tag 不以 stub_ 开头；
其余 base_path = null，报告里就是未匹配。

用法见上。
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build"))
import matched_ledger

REPO = Path(__file__).resolve().parents[2]          # at2/
DEFAULT_AS = os.environ.get("MIPS_AS", str(Path.home() / "eecc" / "ps2binutils" / "mips-ps2-decompals-as"))
DEFAULT_OBJDIFF = os.environ.get("OBJDIFF", str(Path.home() / "eecc" / "objdiff-cli"))
SCHEMA = "https://raw.githubusercontent.com/encounter/objdiff/main/config.schema.json"

# ---- objdiff `scratch` defaults (one-click push to decomp.me) ----
# Evidence (2026-10-06, private repository R22 sections 3.3 and 3.7): the
# decomp.me `ps2` platform holds the two compilers of this project. The
# GovanifY/kh2 project (MIT, same ee-gcc 3.2-ee-040921) already uses them in
# objdiff. c_flags must equal MATCHED_CFLAGS in build_mixed.sh. The schema
# excludes include paths, so the value holds no -I.
#
# objdiff scratch（一键推 decomp.me）默认值。
# 依据（2026-10-06，私有仓库 R22 §3.3 / §3.7）：decomp.me 的 ps2 平台收录了与本案
# 逐字相同的两个编译器；GovanifY/kh2（MIT，同版 ee-gcc 3.2-ee-040921）已在 objdiff
# 里这样用。c_flags 与 build_mixed.sh 的 MATCHED_CFLAGS 保持一致（schema 要求排除
# include 路径，所以不含 -I）。
SCRATCH_PLATFORM = "ps2"
SCRATCH_COMPILER_GAME = "ee-gcc3.2-040921"
SCRATCH_COMPILER_CRI = "ee-gcc2.96"
DEFAULT_SCRATCH_CFLAGS = "-O2 -falign-functions=4 -ffunction-sections"
DEFAULT_CC_MAP = "config/compiler_map.tsv"
DEFAULT_FLAGS_FILE = "config/source_flags.tsv"


def parse_kv_tsv(path: Path) -> dict[str, str]:
    """Read a `<key><TAB><value...>` table. Line 1 is a header row and is skipped. `#` starts a comment (inline comments count). Empty lines are skipped. A later entry wins.

    读 `<key><TAB><value...>` 表；第 1 行是表头，跳过；`#` 起注释（含行内），空行跳过，
    后出现者覆盖先出现者。
    """
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            out[parts[0]] = " ".join(parts[1:])
    return out

RE_GLABEL = re.compile(r"\s*glabel\s+(\S+)")
RE_ENDLABEL = re.compile(r"\s*endlabel\s+(\S+)")
RE_NONMATCHING = re.compile(r"\s*nonmatching\b")
RE_INSTR = re.compile(r"^\s*/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
RE_INCBIN = re.compile(r'^\s*\.incbin\s+"([^"]+)"')

AS_FLAGS = ["-EL", "-march=r5900"]


def parse_symbol_addrs(path: Path) -> list[str]:
    """Read symbol_addrs.txt and return every `type:func` symbol. File order equals address order.

    symbol_addrs.txt → 全部 `type:func` 符号名（保持文件顺序 = 地址序）。
    """
    syms: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        body = raw.split("//", 1)[0].strip()
        if not body or "=" not in body:
            continue
        if "type:func" not in raw:
            continue
        syms.append(body.split("=", 1)[0].strip())
    return syms


def parse_matched(path: Path) -> dict[str, tuple[str, str]]:
    """Ledger -> {sym: (source_basename, tag)}. The implementation is in tools/build/matched_ledger.py. The incremental check shares it.

    台账 → {sym: (source_basename, tag)}；实现见 tools/build/matched_ledger.py，增量检查共用。
    """
    return matched_ledger.parse_ledger(path)

def matched_entry_stats(path: Path) -> tuple[int, int, int]:
    """Entry statistics: total entries / stub entries / distinct non-stub symbols. The shared implementation provides them.

    条目级统计：总条目 / stub 条目 / 去重后的非 stub 符号数（共用实现）。
    """
    return matched_ledger.entry_stats(path)

def index_asm(asm_root: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Scan the whole asm tree in one pass.

    Return (sym -> body_lines, file -> [glabel...]). The rule takes the lines
    between `glabel X` and `endlabel X`. It is the same as before.

    单遍扫描整棵 asm 树，返回 (sym -> body_lines, file -> [glabel...])。
    抽取规则：只取 `glabel X` 与 `endlabel X` 之间的行，与此前实现一致。
    """
    sym_body: dict[str, list[str]] = {}
    file_glabels: dict[str, list[str]] = {}
    for path in sorted(asm_root.rglob("*.s")):
        cur: str | None = None
        body: list[str] = []
        glabels: list[str] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = RE_GLABEL.match(line)
            if m:
                cur, body = m.group(1), []
                glabels.append(cur)
                continue
            m = RE_ENDLABEL.match(line)
            if m:
                if cur is not None and m.group(1) == cur:
                    sym_body[cur] = body
                cur, body = None, []
                continue
            if cur is not None:
                if RE_NONMATCHING.match(line):
                    continue
                body.append(line.rstrip())
        # Measured: 54 glabel entries sit at the end of a file, and splat writes
        # no endlabel for them (nonmatching tail functions). The function runs to
        # the end of the file. Add it here to keep those functions.
        #
        # 实测有 54 个 glabel 位于文件末尾、splat 没写 endlabel（nonmatching 尾巴函数）：
        # 语义上它一直延伸到文件结束，这里补上，避免漏掉这些函数。
        if cur is not None:
            sym_body[cur] = body
        file_glabels[str(path)] = glabels
    return sym_body, file_glabels


def unit_source(sym: str, body: list[str]) -> str:
    return (
        '.include "macro.inc"\n'
        "\n"
        ".set noat\n"
        ".set noreorder\n"
        "\n"
        '.section .text, "ax"\n'
        "\n"
        f"glabel {sym}\n" + "\n".join(body) + f"\nendlabel {sym}\n"
    )


def write_unit_source(path: Path, text: str) -> bool:
    """Write nothing when the content is the same, to keep the .o incremental cache. Return whether a write occurred.

    内容相同则不落盘（保住 .o 的增量缓存）。返回是否发生写入。
    """
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == text:
                return False
        except OSError:
            pass
    path.write_text(text, encoding="utf-8")
    return True


def assemble_one(as_bin: str, include_dir: Path, cwd: Path, src_s: Path, out_o: Path) -> str | None:
    """Assemble one single-function .s. Skip the file when the .o is not older than the .s. Return an error message or None.

    汇编一个单函数 .s；已存在且不比 .s 旧则跳过。返回错误信息或 None。
    """
    if out_o.exists() and out_o.stat().st_mtime >= src_s.stat().st_mtime:
        return None
    proc = subprocess.run(
        [as_bin, *AS_FLAGS, "-I", str(include_dir), "-o", str(out_o), str(src_s)],
        cwd=str(cwd), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return f"{src_s.name}: {proc.stderr.strip()[:400]}"
    return None


def rel(path: Path, base: Path) -> str:
    return os.path.relpath(path, base).replace(os.sep, "/")


def git_head(repo: Path) -> tuple[str, str]:
    try:
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        head = "unknown"
    try:
        st = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout
    except Exception:
        st = ""
    return head, st


def tool_version(cmd: str) -> str:
    for args in (["--version"], ["version"]):
        try:
            p = subprocess.run([cmd, *args], capture_output=True, text=True)
            out = (p.stdout + p.stderr).strip().splitlines()
            if out:
                return out[0]
        except Exception:
            pass
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default="routebjp")
    ap.add_argument("--jobs", "-P", type=int, default=4, help="Assembly parallelism (default 4)")
    ap.add_argument("--as", dest="as_bin", default=DEFAULT_AS)
    ap.add_argument("--objdiff", default=DEFAULT_OBJDIFF)
    ap.add_argument("--out-dir", default=None, help="Directory of objdiff.json (default <project>/build/objdiff-function)")
    ap.add_argument("--units-dir", default=None, help="Output directory of the single-function targets (default <project>/build/units)")
    ap.add_argument("--report-out", default=None, help="Report output (default <project>/build/report_function.json)")
    ap.add_argument("--baseline-out", default=None, help="Write the measures to a baseline JSON file")
    ap.add_argument("--public-dir", default=None, help="Also copy the report to <dir>/SLPS_258.19_report.json")
    ap.add_argument("--limit", type=int, default=0, help="Process the first N symbols only (smoke test)")
    ap.add_argument("--universe", choices=["symbol_addrs", "all"], default="symbol_addrs",
                    help="Unit set: symbol_addrs (default, the work-order rule) or all (this set adds the extra glabels that splat finds)")
    ap.add_argument("--no-run", action="store_true", help="Write objdiff.json only; do not call objdiff-cli")
    ap.add_argument("--no-scratch", action="store_true",
                    help="Do not write the decomp.me scratch block into objdiff.json (the default writes it)")
    ap.add_argument("--cc-map", default=DEFAULT_CC_MAP, help="Per-source compiler table (relative to the project)")
    ap.add_argument("--flags-file", default=DEFAULT_FLAGS_FILE, help="Per-source extra flags table (relative to the project)")
    ap.add_argument("--scratch-cflags", default=DEFAULT_SCRATCH_CFLAGS,
                    help="Base c_flags for scratch (no -I; the script appends the per-source extra flags)")
    args = ap.parse_args()

    t0 = time.time()
    project = (REPO / args.project).resolve()
    if not project.is_dir():
        sys.exit(f"FAIL: the project directory does not exist: {project}")
    out_dir = Path(args.out_dir).resolve() if args.out_dir else project / "build" / "objdiff-function"
    units_dir = Path(args.units_dir).resolve() if args.units_dir else project / "build" / "units"
    report_out = Path(args.report_out).resolve() if args.report_out else project / "build" / "report_function.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    units_dir.mkdir(parents=True, exist_ok=True)

    sa_syms = parse_symbol_addrs(project / "config" / "symbol_addrs.txt")
    print(f"[1/5] symbol_addrs functions: {len(sa_syms)}")

    asm_root = project / "asm"
    if not asm_root.is_dir():
        sys.exit(f"FAIL: missing {asm_root} (run the baseline build first to write the splat disassembly tree)")
    t = time.time()
    sym_body, file_glabels = index_asm(asm_root)
    print(f"[2/5] asm tree index: {len(file_glabels)} files / {len(sym_body)} glabels ({time.time()-t:.1f}s)")
    missing = [s for s in sa_syms if s not in sym_body]
    if missing:
        sys.exit(f"FAIL: {len(missing)} symbol_addrs functions are missing from the asm tree. For example: {missing[:5]}")

    # Rule note: the asm tree holds glabel entries that symbol_addrs does not
    # list. splat disassemble_all finds those bounds. The byte count is exact:
    # each instruction comment line is 4 B (`/* off va word */`; the splat raw
    # disassembly writes one instruction per line), plus the real file size of
    # each `.incbin` asset. Of 2,327 assets, one is a data blob:
    # `__cod_26C630_textbin` = assets/cod/26C630.textbin.bin 39,360 B, in
    # asm/data/cod/26C630.s.
    #
    # 口径提示：asm 树里有、symbol_addrs 里没有的 glabel 由 splat disassemble_all
    # 识别。字节数精确计算：每条指令注释行 = 4 B，外加 .incbin 内嵌资产的真实文件
    # 大小（实测 2,327 个里只有 1 个是数据 blob，见上）。
    extra = sorted(set(sym_body) - set(sa_syms))
    extra_code_bytes = 0
    extra_data_bytes = 0
    for e in extra:
        for line in sym_body[e]:
            if RE_INSTR.match(line):
                extra_code_bytes += 4
            m = RE_INCBIN.match(line)
            if m:
                asset = project / m.group(1)
                if asset.is_file():
                    extra_data_bytes += asset.stat().st_size
    extra_bytes = extra_code_bytes + extra_data_bytes

    syms = sa_syms if args.universe == "symbol_addrs" else sorted(sym_body)
    if args.limit:
        syms = syms[: args.limit]
    if args.universe != "symbol_addrs":
        print(f"      universe={args.universe}: units={len(syms)} (includes {len(extra)} extra glabels)")

    # ---- write the single-function .s files and assemble them ----
    t = time.time()
    written = 0
    for sym in syms:
        if write_unit_source(units_dir / f"{sym}.s", unit_source(sym, sym_body[sym])):
            written += 1
    print(f"[3/5] wrote {len(syms)} single-function .s files (content changed: {written}, {time.time()-t:.1f}s)")

    t = time.time()
    errors: list[str] = []
    include_dir = project / "include"
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futs = {
            pool.submit(assemble_one, args.as_bin, include_dir, project,
                        units_dir / f"{sym}.s", units_dir / f"{sym}.target.o"): sym
            for sym in syms
        }
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            err = fut.result()
            if err:
                errors.append(err)
            done += 1
            if done % 2000 == 0:
                print(f"      assembling {done}/{len(syms)} ({time.time()-t:.1f}s)")
    asm_seconds = time.time() - t
    if errors:
        print(f"FAIL: {len(errors)} functions failed to assemble:")
        for e in errors[:10]:
            print("   ", e)
        sys.exit(1)
    print(f"       assembled {len(syms)} target.o files ({asm_seconds:.1f}s, -P{args.jobs}, up-to-date files skipped)")

    # ---- assemble objdiff.json ----
    matched = parse_matched(project / "config" / "matched_symbols.txt")
    cc_map = parse_kv_tsv(project / args.cc_map)
    extra_flags = parse_kv_tsv(project / args.flags_file)
    scratch_stats = {"game": 0, "cri": 0}
    entry_total, entry_stub, distinct_nonstub = matched_entry_stats(project / "config" / "matched_symbols.txt")
    mixed_obj = project / "build" / "mixed" / "obj"
    units: list[dict] = []
    stats = {"c": 0, "asm": 0, "no_base": 0, "missing_obj": 0, "stub_excluded": 0}
    for sym in syms:
        target = units_dir / f"{sym}.target.o"
        unit = {"name": sym, "target_path": rel(target, out_dir), "base_path": None}
        entry = matched.get(sym)
        if entry is None:
            stats["no_base"] += 1
        else:
            src, tag = entry
            is_stub = tag.startswith("stub_")
            if is_stub:
                # Rule: a stub_* file (a line-by-line copy of the original
                # disassembly) does not count as decompiled. base_path stays
                # null, so the report counts the function as unmatched. Keep the
                # category to show a separate curve in the report.
                #
                # 口径：stub_*（逐条照抄原反汇编的 .s）不计入已反编译，
                # base_path 保持 null，报告里就是未匹配。这里只保留分类，
                # 便于在报告里单列一条曲线。
                stats["stub_excluded"] += 1
                stats["asm"] += 1
                unit["metadata"] = {
                    "progress_categories": ["asm"],
                    "source_path": str(Path("src") / "matched" / f"{src}.s"),
                }
            else:
                base = mixed_obj / f"{src}.o"
                if base.exists():
                    unit["base_path"] = rel(base, out_dir)
                    unit["metadata"] = {
                        "progress_categories": ["c"],
                        "source_path": str(Path("src") / "matched" / f"{src}.c"),
                    }
                    if not args.no_scratch:
                        tag_cc = cc_map.get(src, "game")
                        flags = args.scratch_cflags.split() + extra_flags.get(src, "").split()
                        unit["scratch"] = {
                            "platform": SCRATCH_PLATFORM,
                            "compiler": (SCRATCH_COMPILER_CRI if tag_cc == "cri"
                                         else SCRATCH_COMPILER_GAME),
                            "c_flags": " ".join(flags),
                        }
                        scratch_stats["cri" if tag_cc == "cri" else "game"] += 1
                    stats["c"] += 1
                else:
                    stats["missing_obj"] += 1
        units.append(unit)

    config = {
        "$schema": SCHEMA,
        "units": units,
        "progress_categories": [
            {"id": "c", "name": "C (reconstructed)"},
            {"id": "asm", "name": "ASM (copied or stub; not counted as decompiled)"},
        ],
    }
    (out_dir / "objdiff.json").write_text(json.dumps(config, indent=1, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    print("[4/5] wrote {}: units={} (c={c} / asm={asm} / unmatched={no_base} / stub excluded={stub_excluded} / missing base={missing_obj} / scratch: game={gs} cri={cs})"
          .format(out_dir / "objdiff.json", len(units), **stats,
                  gs=scratch_stats["game"], cs=scratch_stats["cri"]))

    baseline: dict = {}
    report_measures: dict = {}
    if not args.no_run:
        cli = args.objdiff
        if not Path(cli).exists() and shutil.which(cli) is None:
            sys.exit(f"FAIL: objdiff-cli not found ({cli})")
        t = time.time()
        cmd = [cli, "report", "generate", "-p", str(out_dir), "-o", str(report_out)]
        print("       run:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        report_seconds = time.time() - t
        data = json.loads(report_out.read_text(encoding="utf-8"))
        m = data["measures"]
        report_measures = m
        print("[5/5] decomp.dev measures:")
        print("       matched_code      = {}/{}  ({:.4f}%)".format(
            m.get("matched_code"), m.get("total_code"), m.get("matched_code_percent", 0.0)))
        print("       matched_functions = {}/{}  ({:.4f}%)".format(
            m.get("matched_functions"), m.get("total_functions"), m.get("matched_functions_percent", 0.0)))
        print("       total_units       = {}".format(m.get("total_units")))
        for cat in data.get("categories", []):
            cm = cat["measures"]
            print("       [{}] matched_functions={}/{}  matched_code={}/{} ({:.4f}%)  units={}".format(
                cat["name"], cm.get("matched_functions"), cm.get("total_functions"),
                cm.get("matched_code"), cm.get("total_code"), cm.get("matched_code_percent", 0.0),
                cm.get("total_units")))

        # Acceptance: each unit with C code must reach 100 percent. Check them
        # one by one.
        bad: list[tuple[str, float, dict]] = []
        c_units = [u for u in data["units"]
                   if (u.get("metadata") or {}).get("progress_categories") == ["c"]]
        for u in c_units:
            mcp = u["measures"].get("matched_code_percent", 0.0)
            if round(mcp, 4) < 100.0:
                bad.append((u["name"], mcp, u["measures"]))
        print(f"       C units = {len(c_units)}; matched_code_percent == 100 ratio = "
              f"{len(c_units) - len(bad)}/{len(c_units)}")
        if bad:
            print(f"       WARNING: {len(bad)} C units are below 100 percent:")
            for name, mcp, ms in bad[:20]:
                print(f"         {name}: {mcp:.4f}%  {ms}")

        head, dirty = git_head(REPO)
        baseline = {
            "schema": "at2-progress-baseline/1",
            "target_binary": "SLPS_258.19",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_commit": head,
            "source_dirty": bool(dirty.strip()),
            "payload_check_sha1": "7cc42d275750600d1f232b2632447f77205f3fc0",
            "report_sha256": hashlib.sha256(report_out.read_bytes()).hexdigest(),
            "measures": m,
            "categories": {c["id"]: c["measures"] for c in data.get("categories", [])},
            "units_total": len(units),
            "units_with_base": sum(1 for u in units if u["base_path"]),
            "c_only_units": len(c_units),
            "c_units_below_100": len(bad),
            "accounting": {
                "unit_universe": f"the type:func entries of config/symbol_addrs.txt ({len(sa_syms)} functions; one function is one unit)",
                "matched_symbols_entries_total": entry_total,
                "matched_symbols_entries_non_stub": entry_total - entry_stub,
                "matched_symbols_distinct_non_stub_symbols": distinct_nonstub,
                "c_only_entries_in_matched_symbols": entry_total - entry_stub,
                "stub_entries_excluded_from_decompiled": entry_stub,
                "splat_glabels_total": len(sym_body),
                "splat_glabels_absent_from_symbol_addrs": len(extra),
                "splat_glabels_absent_bytes": extra_bytes,
                "splat_glabels_absent_bytes_code": extra_code_bytes,
                "splat_glabels_absent_bytes_data_incbin": extra_data_bytes,
                "universe_all_projection": {
                    "note": ("The projection when the %d missing glabels are also units (`--universe all`). "
                             "One measured --universe all run confirmed that total_code and the percentages "
                             "agree." % len(extra)),
                    "total_units": len(units) + len(extra),
                    "total_functions": len(units) + len(extra),
                    "total_code": int(m["total_code"]) + extra_bytes,
                    "matched_code": int(m["matched_code"]),
                    "matched_code_percent": round(
                        int(m["matched_code"]) / (int(m["total_code"]) + extra_bytes) * 100, 4),
                    "matched_functions": int(m["matched_functions"]),
                    "matched_functions_percent": round(
                        int(m["matched_functions"]) / (len(units) + len(extra)) * 100, 4),
                },
                "note": ("An entry with a stub_* tag is a copied assembly stub. The report does not count "
                         "it as decompiled code, and its base_path stays null. "
                         "The asm tree holds glabels that splat disassemble_all finds, but that "
                         f"symbol_addrs.txt does not list: {len(extra)} glabels, {extra_code_bytes} B code, "
                         f"and {extra_data_bytes} B .incbin data, {extra_bytes} B in total. "
                         "The report does not count these glabels in its denominator. "
                         "See universe_all_projection."),
            },
            "timing_seconds": {
                "total": round(time.time() - t0, 1),
                "assemble": round(asm_seconds, 1),
                "objdiff_report": round(report_seconds, 1),
            },
            "tool_versions": {
                "objdiff-cli": tool_version(cli),
                "mips-ps2-decompals-as": tool_version(args.as_bin),
            },
            "generator": "tools/report/gen_function_report.py",
        }
        if args.baseline_out:
            bp = Path(args.baseline_out)
            bp.parent.mkdir(parents=True, exist_ok=True)
            bp.write_text(json.dumps(baseline, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"       baseline written {bp}")
        if args.public_dir:
            pd = Path(args.public_dir)
            pd.mkdir(parents=True, exist_ok=True)
            dst = pd / "SLPS_258.19_report.json"
            shutil.copyfile(report_out, dst)
            print(f"       public report written {dst}")

    print(f"done: total {time.time()-t0:.1f}s")
    if baseline and report_measures:
        print("BASELINE_JSON " + json.dumps({k: baseline[k] for k in
              ("source_commit", "measures", "accounting", "timing_seconds")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
