#!/usr/bin/env python3
"""公开仓库自检（CI 的快速门禁；只依赖标准库）。

四件事：
  1. **发布记录自洽**：`PUBLISHED.json` 记录的报告/基线/工具链锁 sha256 必须与磁盘一致。
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


def check_published() -> None:
    """发布记录自洽：PUBLISHED.json 里的报告/基线/工具链哈希必须与磁盘一致。"""
    pub_path = ROOT / "PUBLISHED.json"
    if not pub_path.is_file():
        bad("缺少 PUBLISHED.json（发布记录；由 maintainers/tools/publish_report.py 维护）")
        return
    try:
        pub = json.loads(pub_path.read_text(encoding="utf-8"))
    except Exception as e:
        bad(f"PUBLISHED.json 不是合法 JSON：{e}")
        return
    if pub.get("schema") != "at2-published/2":
        bad(f"PUBLISHED.json 的 schema 异常：{pub.get('schema')!r}")
    for key in ("report", "baseline"):
        item = pub.get(key) or {}
        rel, want = item.get("path"), item.get("sha256")
        if not rel or not want:
            bad(f"PUBLISHED.json 缺 {key}.path/sha256")
            continue
        f = ROOT / rel
        if not f.is_file():
            bad(f"发布记录指向的文件不存在：{rel}")
        elif sha256(f) != want:
            bad(f"{rel} 与 PUBLISHED.json 记录的 sha256 不一致（发布后被改动过？）")
        else:
            ok(f"发布记录一致：{rel}")
    lock = ROOT / "toolchain.lock.json"
    if pub.get("toolchain_lock_sha256") and lock.is_file():
        if sha256(lock) != pub["toolchain_lock_sha256"]:
            bad("toolchain.lock.json 与 PUBLISHED.json 记录的 sha256 不一致")
        else:
            ok("发布记录一致：toolchain.lock.json")
    ok(f"发布记录自洽（source_revision={str(pub.get('source_revision'))[:12]}）")



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


def check_contrib(base: str) -> None:
    """贡献模式（PR 用）：除只读路径外都可以改；删除、二进制、忌语一律 FAIL。

    只读路径 = `progress/**` 与 `PUBLISHED.json`（CI/维护者产出的发布内容）。
    """
    # 公开仓库现在是项目主仓库：除「CI/维护者产出的只读路径」外都可以贡献
    readonly = {
        "progress/": "进度报告由经过验证的构建产出（tools/publish_report.py 写入），不接受手工改动",
        "PUBLISHED.json": "发布记录由 tools/publish_report.py 维护",
    }
    max_bytes = 1 << 20

    def why(rel: str) -> str | None:
        for prefix, reason in readonly.items():
            if rel == prefix or rel.startswith(prefix):
                return reason
        return None

    cp = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-status", f"{base}...HEAD"],
                        capture_output=True, text=True)
    if cp.returncode != 0:
        bad(f"无法取得与基线 {base} 的差异：{cp.stderr.strip()[:120]}")
        return
    changes, renames = [], 0
    for line in cp.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, rel = parts[0], parts[-1]
        if status.startswith(("R", "C")):
            renames += 1
            bad(f"不接受重命名/复制：{parts[1]} → {rel}（请改成「新增文件」+「不改原文件」）")
            continue
        changes.append((status, rel))

    if not changes:
        ok("本次 PR 没有文件改动")
    for status, rel in changes:
        if status.startswith("D"):
            bad(f"不接受删除：{rel}（生成物由导出器管理，删掉会在下一次导出中回来）")
            continue
        reason = why(rel)
        if reason:
            bad(f"只读路径不可改：{rel} —— {reason}")
            continue
        p = ROOT / rel
        if p.is_file():
            if p.stat().st_size > max_bytes:
                bad(f"文件过大（限 {max_bytes // 1024} KiB）：{rel}")
                continue
            try:
                p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                bad(f"不是文本文件：{rel}（本仓库只收文本贡献）")
                continue
        ok(f"允许贡献：{rel}")
    if renames:
        ok(f"（重命名 {renames} 项已按上面的 FAIL 处理）")

    check_deny(set())
    check_report(ROOT / "progress" / "SLPS_258.19_report.json")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="完整性 + 类别 + 报告不变量（默认动作）")
    ap.add_argument("--compare-only", action="store_true",
                    help="只比数字：报告 schema + 相对基线不回退（用 CI 刚生成的报告，不校验已提交副本的哈希）")
    ap.add_argument("--pr", metavar="BASE", default="",
                    help="贡献模式：与 BASE（如 pull_request.base.sha）比较，只允许白名单内的新增/修改")
    ap.add_argument("--report", default="progress/SLPS_258.19_report.json")
    ap.add_argument("--baseline", default="progress/baseline.json")
    args = ap.parse_args()

    if args.compare_only:
        check_report(ROOT / args.report)
        check_no_regression(ROOT / args.baseline, ROOT / args.report)
    elif args.pr:
        check_contrib(args.pr)
    else:
        check_published()
        check_deny(set())
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
