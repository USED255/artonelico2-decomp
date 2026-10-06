#!/usr/bin/env python3
"""为路线 B（日版主目标）生成**全量 unit** 的 objdiff.json —— decomp.dev 上报的前置件。

背景（见 docs/R15-路线B-decomp.dev发表方案.md）：
  * decomp.dev 只接受 objdiff 报告（`objdiff-cli report generate`）。
  * objdiff 报告的分母来自 objdiff.json 里的 `units`：**每一个被链接进二进制的对象**都应当是一条
    unit，未反编译的 unit 允许 `base_path: null`。
  * 本项目 routebjp/objdiff.json 目前只有 1 条 unit（m2_probe 探针），因此 `build/report.json`
    的 measure 只有 11 个函数 —— 不能代表路线 B 的真实进度，也不能上报。

本脚本做三件事（只读构建产物，不编译、不改动任何已有文件）：
  1. 扫描 `<project>/build/asm/**/*.o`（M1 全量汇编产物，10,938 个）作为 target；
  2. 用 `<project>/config/matched_symbols.txt`（sym → source）把已 C 化的 unit 连到
     `<project>/build/hybrid/obj/<source>.o`（M2.5 hybrid 的 C/asm 替换源产物）；
  3. 写出 `<project>/build/objdiff-full/objdiff.json`，并按 `--out-report` 可选地直接调用
     objdiff-cli 生成报告。

分类口径（progress_categories）：
  * `c`   —— 由 C 源码反推（src/matched/<src>.c）
  * `asm` —— src/matched/<src>.s（逐条照抄原反汇编的桩/库函数，**不是反推 C**）
  * 未匹配的 unit 不带分类，进 "All" 合计。
  decomp.dev 会为每个分类单独显示一条进度曲线，便于把「真 C 反推」与「照抄汇编」分开报。

用法：
  python3 tools/build/gen_objdiff_full.py                       # 只写 objdiff.json
  python3 tools/build/gen_objdiff_full.py --run                 # 写完后调用 objdiff-cli 出报告
  python3 tools/build/gen_objdiff_full.py --project routeb --run
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
    """matched_symbols.txt → {sym: source_basename}（source 缺省时等于 sym）。"""
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
    """objdiff.json 的路径一律相对 `-p` 目录（= out_dir）书写，便于本地/CI 复用同一份配置。

    code_only=True 时排除 `build/asm/data/**`：① 路线 B 的范围本就不含数据段/ERX；
    ② 本项目的 splat 布局把整个 `.data` 放在**单个 13.7 MB 对象**里（`276000.data.o`），
    objdiff 处理它会耗时 >2 分钟（2026-10-04 实测），全量报告会因此不可用。
    """
    matched = read_matched(project)
    asm_root = project / "build" / "asm"
    hybrid_obj = project / "build" / "hybrid" / "obj"
    if not asm_root.is_dir():
        sys.exit(f"FAIL: 缺少 {asm_root}（先跑 routebjp/build.sh 产出 M1 全量汇编对象）")

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
            base = hybrid_obj / f"{src}.o"
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
    ap.add_argument("--project", default="routebjp", help="路线 B 项目目录（默认 routebjp）")
    ap.add_argument("--code-only", action="store_true", help="排除 build/asm/data/**（路线 B 只发表代码段；也避开 13.7 MB 的巨型数据对象）")
    ap.add_argument("--out", default=None, help="objdiff.json 输出路径（默认 <project>/build/objdiff-full/objdiff.json）")
    ap.add_argument("--run", action="store_true", help="生成后调用 objdiff-cli report generate")
    ap.add_argument("--objdiff", default=DEFAULT_OBJDIFF, help=f"objdiff-cli 路径（默认 {DEFAULT_OBJDIFF}）")
    ap.add_argument("--report-out", default=None, help="报告输出路径（默认 build/report_full.json）")
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
    print(f"写出 {out}")
    print(
        "  units={target}  base={has_base}（c={c} / asm={asm}）"
        "  缺 base 产物={missing_obj}  清单里无对应 unit={orphan_src}  跳过={skipped}".format(**stats)
    )

    if args.run:
        cli = args.objdiff
        if not Path(cli).exists() and shutil.which(cli) is None:
            sys.exit(f"FAIL: 找不到 objdiff-cli（{cli}）")
        report_out = (
            Path(args.report_out) if args.report_out
            else project / "build" / ("report_code.json" if args.code_only else "report_full.json")
        )
        cmd = [cli, "report", "generate", "-p", str(out_dir), "-o", str(report_out)]
        print("运行:", " ".join(cmd))
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
