#!/usr/bin/env python3
"""函数粒度（per-function）objdiff 报告生成器 —— decomp.dev 上报口径。

为什么需要（P8，2026-10-05）：
  旧的 `tools/build/gen_objdiff_full.py` 用 splat 拆出的 **.s 文件**当 target。splat 的
  `cod/*.s` 并不总是「一个文件一个函数」：实测 `routebjp/asm/cod` 里 1,677 个文件含
  ≥2 个 `glabel`（整棵 asm 树共 13,250 个 glabel，symbol_addrs 只列了 10,923 个）。
  于是一条 unit 里塞了多个函数，只要 base 只提供了其中一个，objdiff 就把它判成 partial
  （`matched_code_percent < 100`），**即使链接后的载荷字节完全一致**。
  实测：把 target 抽成「单函数对象」后同一函数报 100%。

本脚本的口径（与 task-4 任务书一致）：
  * unit 集合 = `config/symbol_addrs.txt` 里 `type:func` 的**全部函数**（10,923 个），
    一个函数一条 unit；
  * target = 从 `asm/` 抽出该函数（沿用 `tools/build/m2_extract.py` 的 glabel/endlabel
    语义）写成 `build/units/<sym>.s`，用 `mips-ps2-decompals-as` 独立汇编成
    `build/units/<sym>.target.o`（增量：内容没变就复用旧 .o）；
  * base = `build/hybrid/obj/<src>.o`，仅当该符号在 `config/matched_symbols.txt`
    且**注释 tag 不以 `stub_` 开头**；其余（未匹配 + `stub_*` 照抄桩）base_path = null，
    在报告里就是**未匹配**；
  * 分类：非 stub 已 C 化 → `c`；stub 桩 → `asm`（base 仍为 null，matched_functions = 0）。

产物：
  * `<project>/build/report_function.json`（objdiff 原生报告）；
  * 可选 `--baseline-out`：把本报告的 measures 写成「不得回退」的基线 JSON；
  * 可选 `--public-dir`：把报告拷成 `<public-dir>/SLPS_258.19_report.json`。

用法：
  python3 tools/report/gen_function_report.py                 # 全量：抽函数 + 汇编 + 出报告
  python3 tools/report/gen_function_report.py --limit 50      # 冒烟测试
  python3 tools/report/gen_function_report.py --no-run        # 只写 objdiff.json
  python3 tools/report/gen_function_report.py --baseline-out <path> --public-dir <dir>
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

REPO = Path(__file__).resolve().parents[2]          # at2/
DEFAULT_AS = os.environ.get("MIPS_AS", str(Path.home() / "eecc" / "ps2binutils" / "mips-ps2-decompals-as"))
DEFAULT_OBJDIFF = os.environ.get("OBJDIFF", str(Path.home() / "eecc" / "objdiff-cli"))
SCHEMA = "https://raw.githubusercontent.com/encounter/objdiff/main/config.schema.json"

RE_GLABEL = re.compile(r"\s*glabel\s+(\S+)")
RE_ENDLABEL = re.compile(r"\s*endlabel\s+(\S+)")
RE_NONMATCHING = re.compile(r"\s*nonmatching\b")
RE_INSTR = re.compile(r"^\s*/\* [0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+ \*/")
RE_INCBIN = re.compile(r'^\s*\.incbin\s+"([^"]+)"')

AS_FLAGS = ["-EL", "-march=r5900"]


def parse_symbol_addrs(path: Path) -> list[str]:
    """symbol_addrs.txt → 全部 `type:func` 符号名（保持文件顺序 = 地址序）。"""
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
    """matched_symbols.txt → {sym: (source_basename, tag)}；tag 为行内注释去掉 `#` 后的原文。"""
    out: dict[str, tuple[str, str]] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        body, _, comment = raw.partition("#")
        body = body.strip()
        if not body:
            continue
        parts = body.split()
        sym = parts[0]
        src = parts[1] if len(parts) > 1 else sym
        out[sym] = (src, comment.strip())
    return out


def matched_entry_stats(path: Path) -> tuple[int, int, int]:
    """matched_symbols.txt 的**条目级**统计：(总条目, stub 条目, 去重后的非 stub 符号数)。"""
    total = stub = 0
    nonstub: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        body, _, comment = raw.partition("#")
        body = body.strip()
        if not body:
            continue
        total += 1
        if comment.strip().startswith("stub_"):
            stub += 1
        else:
            nonstub.add(body.split()[0])
    return total, stub, len(nonstub)


def index_asm(asm_root: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """单遍扫描整棵 asm 树。

    返回 (sym -> body_lines, file -> [glabel...])。语义与 `tools/build/m2_extract.py`
    的 glabel/endlabel 抽取一致：只取 `glabel X` 与 `endlabel X` 之间的行。
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
    """内容相同则不落盘（保住 .o 的增量缓存）。返回是否发生写入。"""
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == text:
                return False
        except OSError:
            pass
    path.write_text(text, encoding="utf-8")
    return True


def assemble_one(as_bin: str, include_dir: Path, cwd: Path, src_s: Path, out_o: Path) -> str | None:
    """汇编一个单函数 .s；已存在且不比 .s 旧则跳过。返回错误信息或 None。"""
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
    ap.add_argument("--jobs", "-P", type=int, default=4, help="汇编并行度（默认 4）")
    ap.add_argument("--as", dest="as_bin", default=DEFAULT_AS)
    ap.add_argument("--objdiff", default=DEFAULT_OBJDIFF)
    ap.add_argument("--out-dir", default=None, help="objdiff.json 所在目录（默认 <project>/build/objdiff-function）")
    ap.add_argument("--units-dir", default=None, help="单函数 target 输出目录（默认 <project>/build/units）")
    ap.add_argument("--report-out", default=None, help="报告输出（默认 <project>/build/report_function.json）")
    ap.add_argument("--baseline-out", default=None, help="把 measures 写成基线 JSON")
    ap.add_argument("--public-dir", default=None, help="额外把报告拷成 <dir>/SLPS_258.19_report.json")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个符号（冒烟测试）")
    ap.add_argument("--universe", choices=["symbol_addrs", "all"], default="symbol_addrs",
                    help="unit 全集：symbol_addrs（默认，任务书口径）或 all（含 splat 自动识别的额外 glabel）")
    ap.add_argument("--no-run", action="store_true", help="只写 objdiff.json，不调用 objdiff-cli")
    args = ap.parse_args()

    t0 = time.time()
    project = (REPO / args.project).resolve()
    if not project.is_dir():
        sys.exit(f"FAIL: 项目目录不存在 {project}")
    out_dir = Path(args.out_dir).resolve() if args.out_dir else project / "build" / "objdiff-function"
    units_dir = Path(args.units_dir).resolve() if args.units_dir else project / "build" / "units"
    report_out = Path(args.report_out).resolve() if args.report_out else project / "build" / "report_function.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    units_dir.mkdir(parents=True, exist_ok=True)

    sa_syms = parse_symbol_addrs(project / "config" / "symbol_addrs.txt")
    print(f"[1/5] symbol_addrs 函数：{len(sa_syms)}")

    asm_root = project / "asm"
    if not asm_root.is_dir():
        sys.exit(f"FAIL: 缺少 {asm_root}（先跑 M1 产出 splat 反汇编树）")
    t = time.time()
    sym_body, file_glabels = index_asm(asm_root)
    print(f"[2/5] 索引 asm 树：{len(file_glabels)} 文件 / {len(sym_body)} glabel（{time.time()-t:.1f}s）")
    missing = [s for s in sa_syms if s not in sym_body]
    if missing:
        sys.exit(f"FAIL: {len(missing)} 个 symbol_addrs 函数在 asm 树里找不到，例：{missing[:5]}")

    # 口径提示：asm 树里有、symbol_addrs 里没有的 glabel（splat disassemble_all 自动识别出的边界）。
    # 字节数**精确**计算：每条指令注释行 = 4 B（`/* off va word */`，splat 的 raw 反汇编 1 行 1 条指令），
    # 外加 `.incbin` 内嵌资产的真实文件大小（实测 2,327 个里只有 1 个是数据 blob：
    # `__cod_26C630_textbin` = assets/cod/26C630.textbin.bin 39,360 B，位于 asm/data/cod/26C630.s）。
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
        print(f"      universe={args.universe}：units={len(syms)}（含 {len(extra)} 个额外 glabel）")

    # ---- 写单函数 .s + 汇编 ----
    t = time.time()
    written = 0
    for sym in syms:
        if write_unit_source(units_dir / f"{sym}.s", unit_source(sym, sym_body[sym])):
            written += 1
    print(f"[3/5] 写出 {len(syms)} 个单函数 .s（内容变更 {written} 个，{time.time()-t:.1f}s）")

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
                print(f"      汇编进度 {done}/{len(syms)}（{time.time()-t:.1f}s）")
    asm_seconds = time.time() - t
    if errors:
        print(f"FAIL: {len(errors)} 个函数汇编失败：")
        for e in errors[:10]:
            print("   ", e)
        sys.exit(1)
    print(f"       汇编完成 {len(syms)} 个 target.o（{asm_seconds:.1f}s，-P{args.jobs}，增量跳过已最新者）")

    # ---- 组装 objdiff.json ----
    matched = parse_matched(project / "config" / "matched_symbols.txt")
    entry_total, entry_stub, distinct_nonstub = matched_entry_stats(project / "config" / "matched_symbols.txt")
    hybrid_obj = project / "build" / "hybrid" / "obj"
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
                # 口径：stub_*（逐条照抄原反汇编的 .s）不计入「已反编译」→ base_path 保持 null，
                # 报告里就是未匹配。这里只保留分类，便于在报告里单列一条曲线。
                stats["stub_excluded"] += 1
                stats["asm"] += 1
                unit["metadata"] = {
                    "progress_categories": ["asm"],
                    "source_path": str(Path("src") / "matched" / f"{src}.s"),
                }
            else:
                base = hybrid_obj / f"{src}.o"
                if base.exists():
                    unit["base_path"] = rel(base, out_dir)
                    unit["metadata"] = {
                        "progress_categories": ["c"],
                        "source_path": str(Path("src") / "matched" / f"{src}.c"),
                    }
                    stats["c"] += 1
                else:
                    stats["missing_obj"] += 1
        units.append(unit)

    config = {
        "$schema": SCHEMA,
        "units": units,
        "progress_categories": [
            {"id": "c", "name": "C (反推)"},
            {"id": "asm", "name": "ASM (照抄/桩，不计入已反编译)"},
        ],
    }
    (out_dir / "objdiff.json").write_text(json.dumps(config, indent=1, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    print("[4/5] 写出 {}：units={}（c={c} / asm={asm} / 未匹配={no_base} / 桩排除={stub_excluded} / 缺 base={missing_obj}）"
          .format(out_dir / "objdiff.json", len(units), **stats))

    baseline: dict = {}
    report_measures: dict = {}
    if not args.no_run:
        cli = args.objdiff
        if not Path(cli).exists() and shutil.which(cli) is None:
            sys.exit(f"FAIL: 找不到 objdiff-cli（{cli}）")
        t = time.time()
        cmd = [cli, "report", "generate", "-p", str(out_dir), "-o", str(report_out)]
        print("       运行:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        report_seconds = time.time() - t
        data = json.loads(report_out.read_text(encoding="utf-8"))
        m = data["measures"]
        report_measures = m
        print("[5/5] decomp.dev measures：")
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

        # 验收：已 C 化 unit 必须 100%（逐条核对）
        bad: list[tuple[str, float, dict]] = []
        c_units = [u for u in data["units"]
                   if (u.get("metadata") or {}).get("progress_categories") == ["c"]]
        for u in c_units:
            mcp = u["measures"].get("matched_code_percent", 0.0)
            if round(mcp, 4) < 100.0:
                bad.append((u["name"], mcp, u["measures"]))
        print(f"       已 C 化 unit = {len(c_units)}；matched_code_percent == 100 的比例 = "
              f"{len(c_units) - len(bad)}/{len(c_units)}")
        if bad:
            print(f"       ⚠ 非 100% 的已 C 化 unit：{len(bad)} 个")
            for name, mcp, ms in bad[:20]:
                print(f"         {name}: {mcp:.4f}%  {ms}")

        head, dirty = git_head(REPO)
        baseline = {
            "schema": "at2-progress-baseline/1",
            "target_binary": "SLPS_258.19",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_commit": head,
            "source_dirty": bool(dirty.strip()),
            "ratchet_payload_sha1": "7cc42d275750600d1f232b2632447f77205f3fc0",
            "report_sha256": hashlib.sha256(report_out.read_bytes()).hexdigest(),
            "measures": m,
            "categories": {c["id"]: c["measures"] for c in data.get("categories", [])},
            "units_total": len(units),
            "units_with_base": sum(1 for u in units if u["base_path"]),
            "c_only_units": len(c_units),
            "c_units_below_100": len(bad),
            "accounting": {
                "unit_universe": f"config/symbol_addrs.txt 的 type:func（{len(sa_syms)} 个，一个函数一条 unit）",
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
                    "note": ("把上面 %d 个缺失 glabel 也当 unit（`--universe all`）后的投影；"
                             "已用一次实测 --universe all 运行核对，total_code/百分比完全一致" % len(extra)),
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
                "note": ("stub_* （注释 tag）照抄汇编桩不计入已反编译，base_path=null；"
                         "asm 树里由 splat disassemble_all 自动识别、但不在 symbol_addrs 的 "
                         f"{len(extra)} 个 glabel（{extra_code_bytes} B 代码 + "
                         f"{extra_data_bytes} B .incbin 数据 = {extra_bytes} B）**不在本报告分母内**；"
                         "若纳入则见 universe_all_projection"),
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
            print(f"       基线写出 {bp}")
        if args.public_dir:
            pd = Path(args.public_dir)
            pd.mkdir(parents=True, exist_ok=True)
            dst = pd / "SLPS_258.19_report.json"
            shutil.copyfile(report_out, dst)
            print(f"       公开报告写出 {dst}")

    print(f"完成：总耗时 {time.time()-t0:.1f}s")
    if baseline and report_measures:
        print("BASELINE_JSON " + json.dumps({k: baseline[k] for k in
              ("source_commit", "measures", "accounting", "timing_seconds")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
