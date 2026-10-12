#!/usr/bin/env python3
"""Publish a progress report. This tool copies a verified build report into progress/ and updates PUBLISHED.json.

Usage:
    python3 tools/publish_report.py --report <build output.json> [--accept-baseline]
    python3 tools/publish_report.py --check

发布进度报告：把一次**已验证**构建的报告写入 progress/，并更新 PUBLISHED.json。

用法：
    python3 tools/publish_report.py --report <构建产物.json> [--accept-baseline]
    python3 tools/publish_report.py --check
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, time
from pathlib import Path

# The help text stays English only, because the module docstring is bilingual.
# argparse 的 help 只输出英文，因此这里单独给一段英文说明。
EN_USAGE = "Publish a verified progress report, or check the publication record."

ROOT = Path(__file__).resolve().parents[1]   # tools/ -> repository root
REPORT = ROOT / "progress" / "SLPS_258.19_report.json"
BASELINE = ROOT / "progress" / "baseline.json"
PUB = ROOT / "PUBLISHED.json"
LOCK = ROOT / "toolchain.lock.json"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def write_published() -> None:
    pub = {
        "schema": "at2-published/2",
        "project": "Ar tonelico II: Melody of Metafalica — matching decompilation",
        "target": "SLPS_258.19",
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_revision": _git_head(),
        "payload_sha1": "7cc42d275750600d1f232b2632447f77205f3fc0",
        "report": {"path": str(REPORT.relative_to(ROOT)), "sha256": sha256(REPORT)},
        "baseline": {"path": str(BASELINE.relative_to(ROOT)), "sha256": sha256(BASELINE)},
        "toolchain_lock_sha256": sha256(LOCK),
        "policy": "docs/PUBLICATION-POLICY.md",
    }
    PUB.write_text(json.dumps(pub, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {PUB.name} (report {pub['report']['sha256'][:12]}...)")


def _git_head() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def measures(p: Path) -> dict:
    return (json.loads(p.read_text(encoding="utf-8")) or {}).get("measures", {})


def check() -> int:
    problems = []
    if not PUB.is_file():
        print("FAIL: PUBLISHED.json is missing"); return 1
    pub = json.loads(PUB.read_text(encoding="utf-8"))
    for key in ("report", "baseline"):
        item = pub.get(key, {})
        f = ROOT / item.get("path", "")
        if not f.is_file() or sha256(f) != item.get("sha256"):
            problems.append(f"{key} does not match PUBLISHED.json")
    if pub.get("toolchain_lock_sha256") != sha256(LOCK):
        problems.append("toolchain.lock.json does not match PUBLISHED.json")
    cur, base = measures(REPORT), measures(BASELINE)
    for k in ("matched_code", "matched_functions"):
        if int(cur.get(k, 0)) < int(base.get(k, 0)):
            problems.append(f"regression: {k} {cur.get(k)} < baseline {base.get(k)}")
    if problems:
        print("FAIL: " + "; ".join(problems)); return 1
    print("OK: the publication record is consistent, and no measure regressed"); return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=EN_USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", help="new report JSON (from a verified build)")
    ap.add_argument("--accept-baseline", action="store_true", help="also accept the new report as the new baseline")
    ap.add_argument("--force", action="store_true", help="publish a report that is worse than the baseline (refused by default)")
    ap.add_argument("--refresh", action="store_true",
                    help="recompute the PUBLISHED.json hashes from the current files (for example after a toolchain.lock.json change)")
    ap.add_argument("--check", action="store_true", help="check the publication record only")
    a = ap.parse_args()
    if a.refresh:
        write_published()
        return check()
    if a.check or not a.report:
        return check()
    src = Path(a.report)
    if not src.is_file():
        print(f"FAIL: cannot find {src}"); return 1
    if not a.force:
        cur, base = measures(src), measures(BASELINE)
        for k in ("matched_code", "matched_functions"):
            if int(cur.get(k, 0)) < int(base.get(k, 0)):
                print(f"FAIL: the new report is worse than the baseline ({k} {cur.get(k)} < {base.get(k)}). Use --force to accept it.")
                return 1
    shutil.copy2(src, REPORT)
    if a.accept_baseline:
        shutil.copy2(src, BASELINE)
        print("the baseline is updated")
    write_published()
    return 0


if __name__ == "__main__":
    sys.exit(main())
