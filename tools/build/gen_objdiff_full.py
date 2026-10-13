#!/usr/bin/env python3
"""Generate objdiff.json with all units for Route B (the Japanese main target). The file feeds the decomp.dev upload.

Background (private repository design note R15):
  * decomp.dev accepts an objdiff report only (`objdiff-cli report generate`).
  * The report denominator comes from the `units` in objdiff.json. Each object
    that links into the binary must be one unit. A unit without C code can have
    `base_path: null`.
  * matching-jp/objdiff.json holds one unit. Therefore the measures in
    `build/report.json` cover 11 functions only. Those measures do not show the
    real progress of Route B, and the upload needs the full set.

The script does three steps. It reads build output only. It does not compile
and it does not change an existing file.
  1. Scan `<project>/build/asm/**/*.o`. These objects come from the baseline
     build. Use each object as a target.
  2. Use `<project>/config/matched_symbols.txt` (sym -> source) to link a unit
     with C code to `<project>/build/mixed/obj/<source>.o`. The mixed build
     writes these replacement objects.
  3. Write `<project>/build/objdiff-full/objdiff.json`. With `--out-report`,
     call objdiff-cli and write a report.

Category rules (progress_categories):
  * `c`   -- reconstructed from C source (src/matched/<src>.c)
  * `asm` -- src/matched/<src>.s (a copy of the original disassembly, not C)
  * A unit without a match has no category and joins the "All" total.
  decomp.dev shows one progress curve for each category.

Usage:
  python3 tools/build/gen_objdiff_full.py                       # write objdiff.json only
  python3 tools/build/gen_objdiff_full.py --run                 # write the file, then generate a report
  python3 tools/build/gen_objdiff_full.py --project matching-jp --run

为路线 B（日版主目标）生成全量 unit 的 objdiff.json，这是 decomp.dev 上报的前置件。

背景（私有仓库设计记录 R15）：decomp.dev 只接受 objdiff 报告；报告分母来自
objdiff.json 的 units，每个被链接进二进制的对象都应是一条 unit，
未反编译的 unit 允许 base_path 为 null。matching-jp/objdiff.json 只有一条 unit，
所以 build/report.json 的 measure 只覆盖 11 个函数，不能代表路线 B 的真实进度。

本脚本只读构建产物，不编译、不改动任何已有文件：
  1. 扫描 build/asm/**/*.o（baseline 构建的全量汇编对象）作为 target；
  2. 按 config/matched_symbols.txt 把已 C 化的 unit 连到
     build/mixed/obj/<source>.o（mixed 构建的替换源产物）；
  3. 写出 build/objdiff-full/objdiff.json，可用 --out-report 预先出报告。

分类口径：c = 由 C 源码反推；asm = src/matched/<src>.s（照抄汇编，不是反推 C）；
未匹配 unit 不带分类，进 All 合计。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_OBJDIFF = os.environ.get("OBJDIFF", str(Path.home() / "eecc" / "objdiff-cli"))
SCHEMA = "https://raw.githubusercontent.com/encounter/objdiff/main/config.schema.json"


def read_matched(project: Path) -> dict[str, str]:
    """Return {sym: source_basename} from matched_symbols.txt. The source defaults to sym.

    把 matched_symbols.txt 读成 {sym: source_basename}，source 缺省时等于 sym。
    """
    path = project / "config" / "matched_symbols.txt"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        sym = parts[0]
        src = parts[1] if len(parts) > 1 else sym
        out[sym] = src
    return out


def classify(project: Path, src: str) -> str:
    if (project / "src" / "matched" / f"{src}.s").exists():
        return "asm"
    return "c"


def build_units(project: Path, out_dir: Path, code_only: bool = False) -> tuple[list[dict], dict[str, int]]:
    """Write each objdiff.json path relative to the `-p` directory (out_dir). Local runs and CI share one config.

    With code_only=True, exclude `build/asm/data/**`. Route B covers code only.
    The splat layout of this project puts the whole `.data` section in one
    13.7 MB object (`276000.data.o`). objdiff needs more than 2 minutes for that
    object (measured 2026-10-04), so the full report would be unusable.

    objdiff.json 的路径一律相对 -p 目录（= out_dir）书写，便于本地与 CI 复用同一份配置。
    code_only=True 时排除 build/asm/data/**：路线 B 不含数据段，且 13.7 MB 的巨型数据对象
    会让 objdiff 耗时超过 2 分钟（2026-10-04 实测）。
    """
    matched = read_matched(project)
    asm_root = project / "build" / "asm"
    mixed_obj = project / "build" / "mixed" / "obj"
    if not asm_root.is_dir():
        sys.exit(f"FAIL: missing {asm_root} (run matching-jp/build.sh first to write the baseline assembly objects)")

    def rel(p: Path) -> str:
        return os.path.relpath(p, out_dir)

    units: list[dict] = []
    stats = {"target": 0, "has_base": 0, "c": 0, "asm": 0, "missing_obj": 0, "orphan_src": 0, "skipped": 0}
    matched_used: set[str] = set()
    for target in sorted(asm_root.rglob("*.o")):
        if code_only and target.relative_to(asm_root).parts[0] == "data":
            stats["skipped"] += 1
            continue
        stats["target"] += 1
        sym = target.stem
        unit = {
            "name": str(target.relative_to(asm_root).with_suffix("")),
            "target_path": rel(target),
            "base_path": None,
        }
        src = matched.get(sym)
        if src is not None:
            matched_used.add(sym)
            base = mixed_obj / f"{src}.o"
            if base.exists():
                cat = classify(project, src)
                ext = "s" if cat == "asm" else "c"
                unit["base_path"] = rel(base)
                unit["metadata"] = {
                    "progress_categories": [cat],
                    "source_path": str(Path("src") / "matched" / f"{src}.{ext}"),
                }
                stats["has_base"] += 1
                stats[cat] += 1
            else:
                stats["missing_obj"] += 1
        units.append(unit)
    stats["orphan_src"] = len(set(matched) - matched_used)
    return units, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default="matching-jp", help="Route B project directory (default matching-jp)")
    ap.add_argument("--code-only", action="store_true", help="Exclude build/asm/data/** (Route B publishes code only; this also skips the 13.7 MB data object)")
    ap.add_argument("--out", default=None, help="objdiff.json output path (default <project>/build/objdiff-full/objdiff.json)")
    ap.add_argument("--run", action="store_true", help="Call objdiff-cli report generate after the write")
    ap.add_argument("--objdiff", default=DEFAULT_OBJDIFF, help=f"objdiff-cli path (default {DEFAULT_OBJDIFF})")
    ap.add_argument("--report-out", default=None, help="Report output path (default build/report_full.json)")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    out_dir = project / "build" / ("objdiff-code" if args.code_only else "objdiff-full")
    out_dir.mkdir(parents=True, exist_ok=True)
    units, stats = build_units(project, out_dir, code_only=args.code_only)
    out = Path(args.out) if args.out else out_dir / "objdiff.json"
    config = {
        "$schema": SCHEMA,
        "units": units,
        "progress_categories": [
            {"id": "c", "name": "C (反推)"},
            {"id": "asm", "name": "ASM (照抄/桩)"},
        ],
    }
    out.write_text(json.dumps(config, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(
        "  units={target}  base={has_base} (c={c} / asm={asm})"
        "  missing base objects={missing_obj}  matched symbols without a unit={orphan_src}  skipped={skipped}".format(**stats)
    )

    if args.run:
        cli = args.objdiff
        if not Path(cli).exists() and shutil.which(cli) is None:
            sys.exit(f"FAIL: objdiff-cli not found ({cli})")
        report_out = (
            Path(args.report_out) if args.report_out
            else project / "build" / ("report_code.json" if args.code_only else "report_full.json")
        )
        cmd = [cli, "report", "generate", "-p", str(out_dir), "-o", str(report_out)]
        print("run:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        data = json.loads(report_out.read_text(encoding="utf-8"))
        m = data["measures"]
        print(
            "  decomp.dev measures: matched_code={mc}/{tc} ({mcp:.2f}%)  "
            "matched_functions={mf}/{tf} ({mfp:.2f}%)  units={tu}".format(
                mc=m.get("matched_code"), tc=m.get("total_code"), mcp=m.get("matched_code_percent", 0.0),
                mf=m.get("matched_functions"), tf=m.get("total_functions"),
                mfp=m.get("matched_functions_percent", 0.0), tu=m.get("total_units"),
            )
        )
        for cat in data.get("categories", []):
            cm = cat["measures"]
            print(
                "    [{}] matched_code={mc}/{tc} ({mcp:.2f}%)  functions={mf}/{tf}".format(
                    cat["name"], mc=cm.get("matched_code"), tc=cm.get("total_code"),
                    mcp=cm.get("matched_code_percent", 0.0),
                    mf=cm.get("matched_functions"), tf=cm.get("total_functions"),
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
