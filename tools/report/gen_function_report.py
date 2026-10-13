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
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "project"))
import at2_io

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


def sha1_file(path: Path) -> str:
    """Streaming sha1 of a file (the payload is 9.3 MB; do not read it into memory twice).

    流式 sha1（载荷 9.3 MB，不要整份读进内存两次）。
    """
    h = hashlib.sha1()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


_INCLUDE_DIGEST: dict[str, str] = {}


def include_digest(include_dir: Path) -> str:
    """A digest of `include/**` (path + content). Computed once per process and cached.

    The per-object assembly cache must notice a regenerated `include/macro.inc`, so the header
    content is part of the cache key (R30 finding B6). The tree is hashed once: the assembler is
    called for every symbol, and re-hashing the tree each time would dominate the run.

    `include/**`（路径 + 内容）摘要，每进程只算一次并缓存。逐对象汇编缓存必须能察觉
    `include/macro.inc` 被重新生成，因此头文件内容进缓存键（R30 B6）。整棵树只哈希一次：
    每个符号都会调汇编器，逐次重算会变成主要开销。
    """
    key = str(include_dir)
    cached = _INCLUDE_DIGEST.get(key)
    if cached is not None:
        return cached
    lines = []
    if include_dir.is_dir():
        for p in sorted(include_dir.rglob("*")):
            if p.is_file():
                try:
                    lines.append(f"{p.relative_to(include_dir).as_posix()}\t{sha1_file(p)}")
                except OSError:
                    lines.append(f"{p.relative_to(include_dir).as_posix()}\t?")
    digest = hashlib.sha1(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
    _INCLUDE_DIGEST[key] = digest
    return digest


def payload_check(project: Path, lock: dict) -> dict:
    """Measure the payload the build produced and compare it with `toolchain.lock.json`.

    The provenance record must not *claim* a payload check: this function is the only writer of
    the `payload_check*` fields, and it reads the real files. `build.sh` writes the baseline
    payload, `build_mixed.sh` the mixed one; both must equal the expected sha1.

    provenance 不得只是「声称」做过载荷校验：`payload_check*` 字段只有这里会写，且读的是真文件。
    `build.sh` 写基线载荷、`build_mixed.sh` 写混合载荷，两者都必须等于期望 sha1。
    """
    expected = (lock.get("game") or {}).get("payload_sha1")
    out = {"expected_sha1": expected, "baseline_sha1": None, "mixed_sha1": None,
           "baseline_path": "build/SLPS_258.19.bin", "mixed_path": "build/mixed/SLPS_258.19.bin",
           "ok": False}
    for key, rel in (("baseline_sha1", out["baseline_path"]), ("mixed_sha1", out["mixed_path"])):
        p = project / rel
        if p.is_file():
            out[key] = sha1_file(p)
    out["ok"] = bool(expected) and out["baseline_sha1"] == expected and out["mixed_sha1"] == expected
    return out


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
    """Assemble one single-function .s. Skip the file only when the whole cache key matches.

    The key covers the source bytes, the assembler version, AS_FLAGS and the `include/**` digest.
    A bare mtime comparison missed a regenerated `macro.inc` and a new AS_FLAGS value, so the
    report could be measured from stale objects while it recorded the current tools (R30 B6).

    汇编一个单函数 .s；只有缓存键整体匹配才跳过。键覆盖源字节、汇编器版本、AS_FLAGS 与
    `include/**` 摘要。只比 mtime 会漏掉重生成的 `macro.inc` 与新 AS_FLAGS 值，报告就可能
    用陈旧对象量出数字，却记录了当前工具（R30 B6）。
    """
    stamp = out_o.with_suffix(".stamp")
    want = "|".join((sha1_file(src_s), tool_version(as_bin), " ".join(AS_FLAGS),
                     include_digest(include_dir)))
    if out_o.exists() and stamp.is_file():
        try:
            if stamp.read_text(encoding="utf-8") == want:
                return None
        except OSError:
            pass
    proc = subprocess.run(
        [as_bin, *AS_FLAGS, "-I", str(include_dir), "-o", str(out_o), str(src_s)],
        cwd=str(cwd), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return f"{src_s.name}: {proc.stderr.strip()[:400]}"
    try:
        stamp.write_text(want, encoding="utf-8")
    except OSError:
        pass
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
    ap.add_argument("--require-c100", action="store_true",
                    help="Fail (exit 1) when any C unit is below 100 percent; CI uses this so a partial run cannot be mistaken for a publishable report")
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
    # The provenance record must measure, not claim: the lock file gives the expected payload
    # sha1 and `payload_check()` reads the payloads the build really wrote.
    # provenance 必须「实测」而不是「声称」：锁文件给期望载荷 sha1，payload_check() 读构建真正写出的载荷。
    lock = at2_io.guarded_json_load(project / "toolchain.lock.json") or {}

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
    unconfined_incbin: list[str] = []
    for e in extra:
        for line in sym_body[e]:
            if RE_INSTR.match(line):
                extra_code_bytes += 4
            m = RE_INCBIN.match(line)
            if m:
                # The path comes from the asm tree, so it is repo-derived input, not a constant:
                # resolve it and require it to stay inside the project (R30 finding B5).
                # 路径来自 asm 树，属仓库派生输入而非常量：解析后必须仍在项目内（R30 B5）。
                cand = (project / m.group(1)).resolve()
                if cand != project and project not in cand.parents:
                    unconfined_incbin.append(m.group(1))
                    continue
                if cand.is_file():
                    extra_data_bytes += cand.stat().st_size
    if unconfined_incbin:
        print(f"WARNING: {len(unconfined_incbin)} .incbin path(s) escape the project root and count "
              f"as 0 B: " + ", ".join(sorted(set(unconfined_incbin))[:3]))
    extra_bytes = extra_code_bytes + extra_data_bytes

    syms = sa_syms if args.universe == "symbol_addrs" else sorted(sym_body)
    if args.limit:
        syms = syms[: args.limit]
    # Every unit name becomes a path (`units_dir/<sym>.s`) and a key in the report. A name that
    # is not a plain path component would escape the units directory, and skipping it silently
    # would shrink the published denominator. Refuse instead (R30 finding B5).
    # 每个 unit 名都会变成路径（`units_dir/<sym>.s`）与报告里的键。不是普通路径分量的名字会逃出
    # units 目录；静默跳过又会缩小已发布的分母。因此直接拒绝（R30 B5）。
    bad_names = [s for s in syms if not at2_io.symbol_ok(s)]
    if bad_names:
        print(f"FAIL: the unit set holds {len(bad_names)} name(s) that are not safe path "
              f"components (for example {bad_names[:5]})", file=sys.stderr)
        return 2
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
    # The source basename from the ledger becomes `build/mixed/obj/<src>.o` and a metadata path.
    # A name that is not a plain path component is refused, not skipped: skipping would shrink
    # the denominator silently (R30 finding B5).
    # 台账里的源基名会变成 `build/mixed/obj/<src>.o` 与 metadata 路径。不是普通路径分量的名字一律
    # 拒绝而不是跳过：跳过会静默缩小分母（R30 B5）。
    bad_srcs = sorted({src for src, _tag in matched.values() if not at2_io.symbol_ok(src)})
    if bad_srcs:
        print(f"FAIL: the ledger holds {len(bad_srcs)} source basename(s) that are not safe path "
              f"components (for example {bad_srcs[:5]})", file=sys.stderr)
        return 2
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
        if bad and args.require_c100:
            print(f"FAIL: {len(bad)} C unit(s) are below 100 percent and --require-c100 is set; "
                  f"a partial report is not publishable.", file=sys.stderr)
            return 1

        # Measured, not claimed: read the payloads the build wrote and compare them with the lock.
        # 实测而非声称：读构建写出的载荷并与锁文件比对。
        payload = payload_check(project, lock)
        if not payload["ok"]:
            print(f"       WARNING: the payload check did not pass "
                  f"(baseline={payload['baseline_sha1']} mixed={payload['mixed_sha1']} "
                  f"expected={payload['expected_sha1']}); the provenance records ok=false")
        head, dirty = git_head(REPO)
        baseline = {
            "schema": "at2-progress-baseline/1",
            "target_binary": "SLPS_258.19",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_commit": head,
            "source_dirty": bool(dirty.strip()),
            "payload_check_sha1": payload["mixed_sha1"],
            "payload_check": payload,
            "require_c100": bool(args.require_c100),
            "limit": int(args.limit),
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
            # The runner identity, when the report is produced in CI. It makes the provenance
            # record traceable to the run that measured it.
            # CI 里产出报告时带上 runner 身份，使 provenance 可追溯到那一次运行。
            "runner": {k.lower(): os.environ[k] for k in
                       ("GITHUB_RUN_ID", "GITHUB_RUN_URL", "GITHUB_SHA") if os.environ.get(k)},
            "generator": "tools/report/gen_function_report.py",
        }
        if args.baseline_out:
            bp = Path(args.baseline_out)
            at2_io.atomic_write_text(bp, json.dumps(baseline, indent=1, ensure_ascii=False) + "\n")
            print(f"       baseline written {bp}")
        if args.public_dir:
            # `--public-dir` writes into the published tree, so it refuses anything that is not a
            # full verified run (R30 finding D2). `publish_report.py` applies the same gate plus
            # its own provenance check.
            # `--public-dir` 会写进已发布目录，因此拒绝任何「非完整已验证」的运行（R30 D2）。
            # publish_report.py 施加同样的门，另有它自己的 provenance 校验。
            problems = []
            if bad:
                problems.append(f"{len(bad)} C unit(s) are below 100 percent")
            if args.limit:
                problems.append(f"--limit {args.limit} was used (a smoke test is not publishable)")
            if baseline.get("source_dirty"):
                problems.append("the source tree is dirty")
            if not payload.get("ok"):
                problems.append("the payload check did not pass")
            if not args.require_c100:
                problems.append("--require-c100 was not set")
            if problems:
                print("FAIL: --public-dir refused: " + "; ".join(problems), file=sys.stderr)
                return 1
            pd = Path(args.public_dir)
            dst = pd / "SLPS_258.19_report.json"
            at2_io.atomic_copy(report_out, dst)
            print(f"       public report written {dst}")

    print(f"done: total {time.time()-t0:.1f}s")
    if baseline and report_measures:
        print("BASELINE_JSON " + json.dumps({k: baseline[k] for k in
              ("source_commit", "measures", "accounting", "timing_seconds")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
