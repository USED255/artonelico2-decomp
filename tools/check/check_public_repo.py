#!/usr/bin/env python3
"""Public repository checks for CI. The tool uses the standard library only.

Four tasks:
  1. Publication record integrity: the report, the baseline, and the toolchain lock
     sha256 values in `PUBLISHED.json` must agree with the files on disk.
  2. Denied material: `*.s` files (transcription stubs), `routeb/`, `docs/private/`,
     ROM and ISO images, and toolchain archives must all FAIL.
  3. Report rules: the schema and the arithmetic of
     `progress/SLPS_258.19_report.json` must hold (matched <= total).
  4. No regression: the report must not fall behind `progress/baseline.json`
     (`--baseline` and `--report` select other files).

Usage:
    python3 tools/check/check_public_repo.py --check
    python3 tools/check/check_public_repo.py --baseline progress/baseline.json --report progress/SLPS_258.19_report.json
Exit code: 0 on success, 1 when the tool finds a problem that you must repair.

公开仓库自检（CI 的快速门禁；只依赖标准库）。

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

# The help text stays English only, because the module docstring is bilingual.
# argparse 的 help 只输出英文，因此这里单独给一段英文说明。
EN_USAGE = "Check the public repository: publication record, denied material, and report rules."

ROOT = Path(__file__).resolve().parents[2]      # public repository root (tools/check/ -> two levels up)
# 公开仓库根（tools/check/ → 上溯两级）

DENY = ["*.s", "*.o", "*.rom", "*.iso", "*.tar.xz", "*.tar.gz", "*.tar.zst", "*.zst",
        "routeb/*", "docs/private/*", "out/*", ".tmp/*"]

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
    """Publication record integrity: the report, baseline, and lock hashes must agree with the disk."""
    pub_path = ROOT / "PUBLISHED.json"
    if not pub_path.is_file():
        bad("PUBLISHED.json is missing (the publication record; tools/publish_report.py maintains it)")
        return
    try:
        pub = json.loads(pub_path.read_text(encoding="utf-8"))
    except Exception as e:
        bad(f"PUBLISHED.json is not valid JSON: {e}")
        return
    if pub.get("schema") != "at2-published/2":
        bad(f"unexpected PUBLISHED.json schema: {pub.get('schema')!r}")
    for key in ("report", "baseline"):
        item = pub.get(key) or {}
        rel, want = item.get("path"), item.get("sha256")
        if not rel or not want:
            bad(f"PUBLISHED.json has no {key}.path or {key}.sha256")
            continue
        f = ROOT / rel
        if not f.is_file():
            bad(f"the publication record points to a file that does not exist: {rel}")
        elif sha256(f) != want:
            bad(f"the sha256 of {rel} does not match PUBLISHED.json (was the file changed after publication?)")
        else:
            ok(f"the publication record agrees: {rel}")
    lock = ROOT / "toolchain.lock.json"
    if pub.get("toolchain_lock_sha256") and lock.is_file():
        if sha256(lock) != pub["toolchain_lock_sha256"]:
            bad("the sha256 of toolchain.lock.json does not match PUBLISHED.json")
        else:
            ok("the publication record agrees: toolchain.lock.json")
    ok(f"the publication record is consistent (source_revision={str(pub.get('source_revision'))[:12]})")



def check_deny(allowed: set[str]) -> None:
    present = tracked_files() or [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()]
    hits = []
    for rel in present:
        for pat in DENY:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, "*/" + pat):
                hits.append(f"{rel} (matches {pat})")
    if hits:
        bad(f"the public tree contains material that the project cannot publish: {hits[:8]}")
    else:
        ok("the denied-material scan passed")


def load_report(path: Path) -> dict:
    if not path.is_file():
        bad(f"the report does not exist: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        bad(f"the report is not valid JSON: {e}")
        return {}
    return data


def check_report(path: Path) -> dict:
    data = load_report(path)
    if not data:
        return {}
    m = data.get("measures") or {}
    missing = [k for k in REQUIRED_MEASURES if k not in m]
    if missing:
        bad(f"the report measures are missing fields: {missing}")
    else:
        ok(f"the report schema passed (units={m.get('total_units')})")

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
            bad(f"the report arithmetic fails: {a}({va}) > {b}({vb})")
    if not bad:
        ok("the report arithmetic is consistent (matched <= total)")
    if not data.get("units"):
        bad("the report has no unit (the generation probably failed)")
    return data


def check_no_regression(base_path: Path, report_path: Path) -> None:
    base = load_report(base_path)
    cur = load_report(report_path)
    if not base or not cur:
        bad("the baseline or the report is missing, so the comparison is not possible")
        return
    bm, cm = base.get("measures", {}), cur.get("measures", {})
    for key in ("matched_code", "matched_functions"):
        b, c = int(bm.get(key, 0) or 0), int(cm.get(key, 0) or 0)
        if c < b:
            bad(f"regression: {key} {c} < baseline {b}")
        else:
            ok(f"no regression: {key} {c} >= {b}")
    for key in ("matched_code_percent", "matched_functions_percent"):
        b, c = float(bm.get(key, 0) or 0), float(cm.get(key, 0) or 0)
        if c + 1e-9 < b:
            bad(f"percentage regression: {key} {c:.4f} < baseline {b:.4f}")


def check_contrib(base: str, allow_restructure: bool = False) -> None:
    """Contribution mode (for a pull request): any path is open except the read-only paths.

    A delete, a binary file, and denied material always FAIL unless `allow_restructure`
    permits a delete. A rename or a copy needs `allow_restructure` too.

    Read-only paths = `progress/**` and `PUBLISHED.json` (published content that CI and
    the maintainers write). They stay read-only in every mode.

    贡献模式（PR 用）：除只读路径外都可以改；删除、二进制、忌语一律 FAIL。
    `allow_restructure` 只放开重命名/复制/删除，不放开只读路径。

    只读路径 = `progress/**` 与 `PUBLISHED.json`（CI/维护者产出的发布内容）。
    """
    # The public repository is the main repository now. Every path is open except the
    # read-only paths that CI and the maintainers produce.
    # 公开仓库现在是项目主仓库：除「CI/维护者产出的只读路径」外都可以贡献。
    readonly = {
        "progress/": "the progress report comes from a verified build (tools/publish_report.py writes it), so a manual change is not acceptable",
        "PUBLISHED.json": "tools/publish_report.py maintains the publication record",
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
        bad(f"cannot get the diff against the base {base}: {cp.stderr.strip()[:120]}")
        return
    changes: list[tuple[str, str]] = []
    allowed_restructure: list[str] = []
    for line in cp.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, rel = parts[0], parts[-1]
        if status.startswith(("R", "C")):
            if not allow_restructure:
                bad(f"a rename or a copy is not accepted: {parts[1]} -> {rel} (add a new file and keep the original file)")
                continue
            allowed_restructure.append(f"a rename or a copy is allowed (--allow-restructure): {parts[1]} -> {rel}")
            src_reason = why(parts[1])
            if src_reason:
                bad(f"a read-only path cannot be changed: {parts[1]} - {src_reason}")
                continue
            changes.append((status, rel))
            continue
        changes.append((status, rel))

    if not changes:
        ok("this pull request has no file change")
    for status, rel in changes:
        if status.startswith("D"):
            if not allow_restructure:
                bad(f"a delete is not accepted: {rel} (this pull request may add or change files only)")
                continue
            allowed_restructure.append(f"a delete is allowed (--allow-restructure): {rel}")
        reason = why(rel)
        if reason:
            bad(f"a read-only path cannot be changed: {rel} - {reason}")
            continue
        p = ROOT / rel
        if p.is_file():
            if p.stat().st_size > max_bytes:
                bad(f"the file is too large (limit {max_bytes // 1024} KiB): {rel}")
                continue
            try:
                p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                bad(f"not a text file: {rel} (this repository accepts text contributions only)")
                continue
        ok(f"allowed contribution: {rel}")
    for m in allowed_restructure:
        ok(m)

    check_deny(set())
    check_report(ROOT / "progress" / "SLPS_258.19_report.json")


def main() -> int:
    ap = argparse.ArgumentParser(description=EN_USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="integrity, denied material, and report rules (the default action)")
    ap.add_argument("--compare-only", action="store_true",
                    help="compare numbers only: the report schema and the baseline (use the report that CI just wrote, and do not check the hashes of the committed copy)")
    ap.add_argument("--pr", metavar="BASE", default="",
                    help="contribution mode: compare with BASE (for example pull_request.base.sha); allow added or changed files only")
    ap.add_argument("--allow-restructure", action="store_true",
                    help="with --pr, also allow a rename, a copy, and a delete (a same-repository pull request only)")
    ap.add_argument("--report", default="progress/SLPS_258.19_report.json")
    ap.add_argument("--baseline", default="progress/baseline.json")
    args = ap.parse_args()

    if args.compare_only:
        check_report(ROOT / args.report)
        check_no_regression(ROOT / args.baseline, ROOT / args.report)
    elif args.pr:
        check_contrib(args.pr, args.allow_restructure)
    else:
        check_published()
        check_deny(set())
        check_report(ROOT / args.report)
        if (ROOT / args.baseline).is_file():
            check_no_regression(ROOT / args.baseline, ROOT / args.report)
        else:
            bad("progress/baseline.json is missing (the exporter writes the baseline of the first report)")

    for m in OK:
        print(f"[  ok ] {m}")
    for m in BAD:
        print(f"[FAIL ] {m}")
    print(f"\n{len(OK) + len(BAD)} checks: FAIL {len(BAD)} / OK {len(OK)}")
    if BAD:
        print("result: the public repository check FAILED")
        return 1
    print("result: the public repository check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
