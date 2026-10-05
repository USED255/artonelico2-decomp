#!/usr/bin/env python3
"""公开仓库自检（CI 的快速门禁；只依赖标准库）。

四件事：
  1. **完整性**：`PROVENANCE.json` 里每个文件的 sha256 必须与磁盘一致；树里不允许出现清单外的文件。
  2. **不可公开类别**：`*.s`（逐条转录桩）、`routeb/`、`docs/private/`、ROM/ISO、工具链压缩包等一律 FAIL。
  3. **报告不变量**：`progress/SLPS_258.19_report.json` 的 schema 与算术自洽（matched ≤ total 等）。
  4. **不回归**：报告相对 `progress/baseline.json` 不得回退（`--baseline`/`--report` 也可单独指定）。

用法：
    python3 tools/check/check_public_repo.py --check
    python3 tools/check/check_public_repo.py --baseline progress/baseline.json --report progress/SLPS_258.19_report.json
退出码：0 通过；1 有必须修复的问题。
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # 公开仓库根（tools/check/ → 上溯两级）

DENY = ["*.s", "*.rom", "*.iso", "*.tar.xz", "*.tar.gz", "routeb/*", "docs/private/*", "out/*", ".tmp/*"]

REQUIRED_MEASURES = [
    "matched_code", "total_code", "matched_functions", "total_functions",
    "matched_code_percent", "matched_functions_percent", "total_units",
]

OK, BAD = [], []


def ok(msg: str) -> None:
    OK.append(msg)


def bad(msg: str) -> None:
    BAD.append(msg)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files() -> list[str] | None:
    try:
        cp = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
        if cp.returncode == 0:
            return [l for l in cp.stdout.splitlines() if l]
    except Exception:
        pass
    return None


def check_integrity() -> set[str]:
    prov_path = ROOT / "PROVENANCE.json"
    if not prov_path.is_file():
        bad("缺少 PROVENANCE.json（公开仓库必须由导出器生成）")
        return set()
    meta = json.loads(prov_path.read_text(encoding="utf-8"))
    files = meta.get("files", {})
    for rel, digest in files.items():
        p = ROOT / rel
        if not p.is_file():
            bad(f"清单文件缺失：{rel}")
        elif sha256(p) != digest:
            bad(f"清单文件内容与 PROVENANCE 不一致：{rel}")
    ok(f"PROVENANCE 校验：{len(files)} 个清单文件")

    allowed = set(files)
    allowed |= {".github/workflows/validate.yml", ".github/workflows/matching-gate.yml",
                "README.md", "LICENSE", "CONTRIBUTING.md", ".gitignore", "Makefile", "configure.py",
                "toolchain.lock.json", "docs/BUILD.md", "PROVENANCE.json"}
    # 报告由报告生成器产出（不是导出器产出）：显式允许这两个路径，而不是放开整个 progress/ 前缀
    allowed |= {"progress/SLPS_258.19_report.json", "progress/baseline.json"}
    allowed |= set(meta.get("overlay_files", []) or [])
    present = tracked_files()
    if present is None:
        present = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()
                   and ".git/" not in p.as_posix() and "__pycache__" not in p.parts]
        ok(f"非 git 树：按文件系统清点 {len(present)} 个文件")
    extra = [p for p in present if p not in allowed]
    if extra:
        bad(f"出现清单外文件 {len(extra)} 个（默认拒绝）：{extra[:8]}")
    else:
        ok(f"清单外文件检查通过（{len(present)} 个受控文件）")
    return allowed


def check_deny(allowed: set[str]) -> None:
    present = tracked_files() or [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()]
    hits = []
    for rel in present:
        for pat in DENY:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, "*/" + pat):
                hits.append(f"{rel}（命中 {pat}）")
    if hits:
        bad(f"公开树含不可公开类别：{hits[:8]}")
    else:
        ok("不可公开类别扫描通过")


def load_report(path: Path) -> dict:
    if not path.is_file():
        bad(f"报告不存在：{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        bad(f"报告不是合法 JSON：{e}")
        return {}
    return data


def check_report(path: Path) -> dict:
    data = load_report(path)
    if not data:
        return {}
    m = data.get("measures") or {}
    missing = [k for k in REQUIRED_MEASURES if k not in m]
    if missing:
        bad(f"报告 measures 缺字段：{missing}")
    else:
        ok(f"报告 schema 通过（units={m.get('total_units')}）")

    def as_int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    pairs = [("matched_code", "total_code"), ("matched_functions", "total_functions")]
    for a, b in pairs:
        va, vb = as_int(m.get(a)), as_int(m.get(b))
        if va is None or vb is None:
            continue
        if va > vb:
            bad(f"报告算术不成立：{a}({va}) > {b}({vb})")
    if not bad:
        ok("报告算术自洽（matched ≤ total）")
    if not data.get("units"):
        bad("报告没有任何 unit（可能生成失败）")
    return data


def check_no_regression(base_path: Path, report_path: Path) -> None:
    base = load_report(base_path)
    cur = load_report(report_path)
    if not base or not cur:
        bad("基线或报告缺失，无法比较")
        return
    bm, cm = base.get("measures", {}), cur.get("measures", {})
    for key in ("matched_code", "matched_functions"):
        b, c = int(bm.get(key, 0) or 0), int(cm.get(key, 0) or 0)
        if c < b:
            bad(f"进度回退：{key} {c} < 基线 {b}")
        else:
            ok(f"不回退：{key} {c} ≥ {b}")
    for key in ("matched_code_percent", "matched_functions_percent"):
        b, c = float(bm.get(key, 0) or 0), float(cm.get(key, 0) or 0)
        if c + 1e-9 < b:
            bad(f"百分比回退：{key} {c:.4f} < 基线 {b:.4f}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="完整性 + 类别 + 报告不变量（默认动作）")
    ap.add_argument("--report", default="progress/SLPS_258.19_report.json")
    ap.add_argument("--baseline", default="progress/baseline.json")
    args = ap.parse_args()

    if args.check or not (args.report and args.baseline):
        allowed = check_integrity()
        check_deny(allowed)
        check_report(ROOT / args.report)
        if (ROOT / args.baseline).is_file():
            check_no_regression(ROOT / args.baseline, ROOT / args.report)
        else:
            bad("缺少 progress/baseline.json（第一条报告的基线由导出器写入）")

    for m in OK:
        print(f"[  ok ] {m}")
    for m in BAD:
        print(f"[FAIL ] {m}")
    print(f"\n合计 {len(OK) + len(BAD)} 项：FAIL {len(BAD)} / OK {len(OK)}")
    if BAD:
        print("结论：❌ 公开仓库自检未通过")
        return 1
    print("结论：✅ 公开仓库自检通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
