#!/usr/bin/env python3
"""发布进度报告：把一次**已验证**构建的报告写入 progress/，并更新 PUBLISHED.json。

用法：
    python3 tools/publish_report.py --report <构建产物.json> [--accept-baseline]
    python3 tools/publish_report.py --check
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # tools/ → 仓库根
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
    print(f"✅ 已更新 {PUB.name}（报告 {pub['report']['sha256'][:12]}…）")


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
        print("FAIL: 缺少 PUBLISHED.json"); return 1
    pub = json.loads(PUB.read_text(encoding="utf-8"))
    for key in ("report", "baseline"):
        item = pub.get(key, {})
        f = ROOT / item.get("path", "")
        if not f.is_file() or sha256(f) != item.get("sha256"):
            problems.append(f"{key} 与 PUBLISHED.json 不一致")
    if pub.get("toolchain_lock_sha256") != sha256(LOCK):
        problems.append("toolchain.lock.json 与 PUBLISHED.json 不一致")
    cur, base = measures(REPORT), measures(BASELINE)
    for k in ("matched_code", "matched_functions"):
        if int(cur.get(k, 0)) < int(base.get(k, 0)):
            problems.append(f"进度回退：{k} {cur.get(k)} < 基线 {base.get(k)}")
    if problems:
        print("FAIL: " + "；".join(problems)); return 1
    print("✅ 发布记录自洽，且未回退"); return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", help="新报告 JSON（来自一次已验证构建）")
    ap.add_argument("--accept-baseline", action="store_true", help="同时把新报告接受为新基线")
    ap.add_argument("--force", action="store_true", help="允许发布比基线更差的报告（默认拒绝）")
    ap.add_argument("--refresh", action="store_true",
                    help="只按当前文件重算 PUBLISHED.json 的哈希（例如改过 toolchain.lock.json 之后）")
    ap.add_argument("--check", action="store_true", help="只校验发布记录自洽")
    a = ap.parse_args()
    if a.refresh:
        write_published()
        return check()
    if a.check or not a.report:
        return check()
    src = Path(a.report)
    if not src.is_file():
        print(f"FAIL: 找不到 {src}"); return 1
    if not a.force:
        cur, base = measures(src), measures(BASELINE)
        for k in ("matched_code", "matched_functions"):
            if int(cur.get(k, 0)) < int(base.get(k, 0)):
                print(f"FAIL: 新报告比基线差（{k} {cur.get(k)} < {base.get(k)}）；确认无误后用 --force")
                return 1
    shutil.copy2(src, REPORT)
    if a.accept_baseline:
        shutil.copy2(src, BASELINE)
        print("✅ 基线已更新")
    write_published()
    return 0


if __name__ == "__main__":
    sys.exit(main())
