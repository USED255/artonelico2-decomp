#!/usr/bin/env python3
"""Publish a progress report, or check the publication record.

Publishing is gated. `--report` must come with `--provenance`: the record the CI run wrote
(`build/report_provenance.json`). The tool refuses to publish unless that record says the
payload sha1 was measured and matches, every C unit reached 100 percent, the tree was clean,
and the run was not a `--limit` smoke test (R30 finding A3). `--force --reason "..."` is the
documented escape hatch, and the reason is recorded in `PUBLISHED.json`.

`progress/baseline.json` is the frozen reference. `--freeze-baseline` writes the *provenance
record* there (not a copy of the report), so the baseline carries what was verified instead of
being byte-identical to the report, which made "no regression" self-referential.

Usage:
    python3 tools/maintainer/publish_report.py --report <report.json> --provenance <provenance.json> [--freeze-baseline]
    python3 tools/maintainer/publish_report.py --check
    python3 tools/maintainer/publish_report.py --refresh          # re-hash after a lock change

发布进度报告 / 检查发布记录。

发布有门禁：`--report` 必须与 `--provenance`（CI 运行写出的 `build/report_provenance.json`）
一起给。只有该记录表明「载荷 sha1 实测通过、全部 C 单元 100%、工作树干净、不是 `--limit`
冒烟」时才会发布（R30 A3）。唯一的口子是 `--force --reason "..."`，理由会记进 `PUBLISHED.json`。

`progress/baseline.json` 是冻结参照。`--freeze-baseline` 把**provenance 记录**写进去（不是报告副本），
于是基线带着「验证了什么」，不再与报告逐字节相同 —— 那会让「不回归」变成自引用。

用法：
    python3 tools/maintainer/publish_report.py --report <report.json> --provenance <provenance.json> [--freeze-baseline]
    python3 tools/maintainer/publish_report.py --check
    python3 tools/maintainer/publish_report.py --refresh          # 换锁文件后重算哈希
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "project"))
import at2_io  # noqa: E402

# The help text stays English only, because the module docstring is bilingual.
# argparse 的 help 只输出英文，因此这里单独给一段英文说明。
EN_USAGE = "Publish a verified progress report, or check the publication record."

ROOT = Path(__file__).resolve().parents[2]   # tools/maintainer/ -> repository root
REPORT = ROOT / "progress" / "SLPS_258.19_report.json"
BASELINE = ROOT / "progress" / "baseline.json"
PUB = ROOT / "PUBLISHED.json"
LOCK = ROOT / "toolchain.lock.json"

# The provenance schema written by tools/report/gen_function_report.py --baseline-out.
# tools/report/gen_function_report.py --baseline-out 写出的 provenance schema。
PROVENANCE_SCHEMA = "at2-progress-baseline/1"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

# The counters and denominators that must not regress. `total_*` are the denominators: a smaller
# universe with an unchanged numerator inflates every percentage.
# 不得回退的计数与分母。`total_*` 是分母：分子不变而分母变小等于给百分比灌水。
COUNT_KEYS = ("matched_code", "matched_functions", "total_code", "total_functions")
PERCENT_KEYS = ("matched_code_percent", "matched_functions_percent")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _git_head() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def _lock_payload_sha1() -> str:
    lock = at2_io.guarded_json_load(LOCK) or {}
    return str((lock.get("game") or {}).get("payload_sha1") or "")


def measures(p: Path) -> dict:
    """The `measures` object of a report or a provenance record (both carry it at top level)."""
    data = at2_io.guarded_json_load(p) or {}
    return data.get("measures") or {}


def _num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _flt(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def regression_problems(cur: dict, base: dict) -> list[str]:
    """Every way the new numbers fall behind the baseline."""
    out: list[str] = []
    for k in COUNT_KEYS:
        c, b = _num(cur.get(k)), _num(base.get(k))
        if c is None or b is None:
            continue
        if k.startswith("total_"):
            if b and c < b:
                out.append(f"denominator regression: {k} {c} < baseline {b} (the percentage would inflate)")
        elif c < b:
            out.append(f"regression: {k} {c} < baseline {b}")
    for k in PERCENT_KEYS:
        c, b = _flt(cur.get(k)), _flt(base.get(k))
        if c is None or b is None:
            continue
        if c + 1e-9 < b:
            out.append(f"percentage regression: {k} {c:.6f} < baseline {b:.6f}")
    return out


def provenance_problems(prov: object, src_sha: str) -> list[str]:
    """Every reason the provenance record does not justify publishing this report."""
    if not isinstance(prov, dict):
        return ["the provenance file is missing or not valid JSON"]
    out: list[str] = []
    if prov.get("schema") != PROVENANCE_SCHEMA:
        out.append(f"unexpected provenance schema: {prov.get('schema')!r}")
    if prov.get("report_sha256") != src_sha:
        out.append("the provenance does not describe this report (report_sha256 mismatch)")
    p = prov.get("payload_check") or {}
    if not p.get("ok"):
        out.append("the payload check did not pass (payload_check.ok is not true)")
    elif not (p.get("baseline_sha1") == p.get("expected_sha1") == p.get("mixed_sha1")):
        out.append("the provenance payload sha1 values disagree")
    below = _num(prov.get("c_units_below_100"))
    if below is None:
        out.append("the provenance has no c_units_below_100")
    elif below != 0:
        out.append(f"{below} C unit(s) are below 100 percent")
    if prov.get("source_dirty"):
        out.append("the source tree was dirty when the report was generated")
    limit = _num(prov.get("limit"))
    if limit is None:
        out.append("the provenance has no limit field")
    elif limit != 0:
        out.append(f"the report came from a --limit {limit} smoke test")
    commit = str(prov.get("source_commit") or "")
    if not COMMIT_RE.match(commit):
        out.append(f"the provenance has no usable source_commit: {commit!r}")
    return out


def baseline_warning() -> str | None:
    """A warning about a baseline that carries no provenance, or None when it is fine."""
    data = at2_io.guarded_json_load(BASELINE) or {}
    if data.get("schema") != PROVENANCE_SCHEMA:
        return ("the baseline has no provenance (legacy objdiff report); after the next verified CI run, "
                "run publish_report.py --report ... --provenance ... --freeze-baseline to convert it")
    p = data.get("payload_check") or {}
    if not p.get("ok"):
        return "the baseline provenance says the payload check did not pass"
    if (_num(data.get("c_units_below_100")) or 0) != 0:
        return "the baseline provenance says some C units are below 100 percent"
    if data.get("source_dirty"):
        return "the baseline provenance says the source tree was dirty"
    return None


def write_published(*, source_revision: str, payload_sha1: str, payload_verified: bool,
                    force_reason: str = "") -> int:
    """Rewrite PUBLISHED.json atomically. Returns non-zero when a hashed file is missing.

    `source_revision` is the commit the **verified run** built, not the commit that publishes:
    publishing from a branch would otherwise record a revision CI never saw (P-112). Callers pass
    the provenance's `source_commit`; `--refresh` keeps the value already in the record.
    `source_revision` 是**被验证的那次运行**所用的提交，而不是执行发布动作的提交：否则从分支发布
    就会记下一个 CI 从未验证过的版本（P-112）。发布路径传 provenance 的 `source_commit`；
    `--refresh` 沿用记录里已有的值。
    """
    for f in (REPORT, BASELINE, LOCK):
        if not f.is_file():
            print(f"FAIL: cannot update PUBLISHED.json: {f.relative_to(ROOT)} is missing", file=sys.stderr)
            return 1
    pub = {
        "schema": "at2-published/2",
        "project": "Ar tonelico II: Melody of Metafalica — matching decompilation",
        "target": "SLPS_258.19",
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_revision": source_revision or _git_head(),
        # The value the publication refers to, plus whether this tool verified it. `--refresh`
        # writes the toolchain lock's expectation and records `payload_verified: false`.
        # 本次发布指向的载荷 sha1，以及本工具是否**实测**过它。`--refresh` 只写锁文件里的期望值，
        # 并记 `payload_verified: false`。
        "payload_sha1": payload_sha1,
        "payload_verified": payload_verified,
        "report": {"path": str(REPORT.relative_to(ROOT)), "sha256": sha256(REPORT)},
        "baseline": {"path": str(BASELINE.relative_to(ROOT)), "sha256": sha256(BASELINE)},
        "toolchain_lock_sha256": sha256(LOCK),
        "policy": "docs/PUBLICATION-POLICY.md",
    }
    if force_reason:
        pub["force_reason"] = force_reason
    at2_io.atomic_write_text(PUB, json.dumps(pub, indent=1, ensure_ascii=False) + "\n")
    print(f"updated {PUB.name} (report {pub['report']['sha256'][:12]}...)")
    return 0


def check() -> int:
    problems: list[str] = []
    if not PUB.is_file():
        print("FAIL: PUBLISHED.json is missing")
        return 1
    pub = at2_io.guarded_json_load(PUB)
    if not isinstance(pub, dict):
        print("FAIL: PUBLISHED.json is not valid JSON")
        return 1
    for key in ("report", "baseline"):
        item = pub.get(key) or {}
        rel = str(item.get("path") or "")
        cand = (ROOT / rel).resolve()
        if not rel or (cand != ROOT and ROOT not in cand.parents):
            problems.append(f"{key}.path escapes the repository: {rel!r}")
            continue
        if not cand.is_file() or sha256(cand) != item.get("sha256"):
            problems.append(f"{key} does not match PUBLISHED.json")
    if pub.get("toolchain_lock_sha256") != sha256(LOCK):
        problems.append("toolchain.lock.json does not match PUBLISHED.json")
    base_doc = at2_io.guarded_json_load(BASELINE) or {}
    if str(pub.get("source_revision") or "") != str(base_doc.get("source_commit") or ""):
        problems.append("source_revision is not the commit the baseline provenance verified "
                        f"({str(pub.get('source_revision'))[:12]!r} vs {str(base_doc.get('source_commit'))[:12]!r})")
    problems += regression_problems(measures(REPORT), measures(BASELINE))
    warn = baseline_warning()
    if warn:
        print(f"WARN: {warn}")
    if problems:
        print("FAIL: " + "; ".join(problems))
        return 1
    print("OK: the publication record is consistent, and no measure regressed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=EN_USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", help="new report JSON (the artifact of a verified run)")
    ap.add_argument("--provenance", help="build/report_provenance.json produced with the report (required unless --force)")
    ap.add_argument("--freeze-baseline", action="store_true",
                    help="also write the provenance record as progress/baseline.json (an explicit, separate decision)")
    ap.add_argument("--accept-baseline", action="store_true",
                    help="DEPRECATED (renamed): it used to copy the report over the baseline")
    ap.add_argument("--force", action="store_true", help="publish without a passing provenance; needs --reason")
    ap.add_argument("--reason", default="", help="the reason recorded in PUBLISHED.json when --force is used")
    ap.add_argument("--refresh", action="store_true",
                    help="recompute the PUBLISHED.json hashes from the files on disk (for example after a toolchain.lock.json change)")
    ap.add_argument("--check", action="store_true", help="check the publication record only")
    a = ap.parse_args()

    if a.accept_baseline:
        print("FAIL: --accept-baseline was renamed to --freeze-baseline: the baseline now holds the "
              "provenance record, not a copy of the report", file=sys.stderr)
        return 2
    if a.refresh:
        # A refresh only re-hashes the files, so it must not rewrite the verified revision that the
        # record already carries (the local HEAD is a different commit). P-112.
        # refresh 只重算哈希，不能改写记录里已经写好的「被验证版本」（本地 HEAD 是另一个提交）。P-112。
        prev = at2_io.guarded_json_load(PUB) or {}
        return write_published(source_revision=str(prev.get("source_revision") or ""),
                               payload_sha1=_lock_payload_sha1(), payload_verified=False) or check()
    if a.check or not a.report:
        return check()

    src = Path(a.report)
    if not src.is_file():
        print(f"FAIL: cannot find {src}", file=sys.stderr)
        return 1
    src_sha = sha256(src)

    if a.force:
        if not a.reason.strip():
            print('FAIL: --force needs --reason "..." (it is recorded in PUBLISHED.json)', file=sys.stderr)
            return 2
        print(f"WARNING: --force skips the provenance and regression gates: {a.reason.strip()}")
        prov: object = at2_io.guarded_json_load(Path(a.provenance)) if a.provenance else None
        problems: list[str] = []
    else:
        if not a.provenance:
            print("FAIL: --provenance is required (it is the artifact of the matching-gate run that "
                  "produced the report); use --force --reason to override", file=sys.stderr)
            return 2
        prov = at2_io.guarded_json_load(Path(a.provenance))
        problems = provenance_problems(prov, src_sha)
        # The measures comparison needs the real report, so it lives here rather than in the helper.
        # 与真实报告比 measures 这一步需要真报告，因此放在这里而不是 helper 里。
        if isinstance(prov, dict) and prov.get("measures") != measures(src):
            problems.append("the provenance measures differ from the report")

    problems += regression_problems(measures(src), measures(BASELINE))
    if problems:
        print("FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1

    at2_io.atomic_copy(src, REPORT)
    if a.freeze_baseline:
        if not isinstance(prov, dict):
            print("FAIL: --freeze-baseline needs a provenance file", file=sys.stderr)
            return 2
        at2_io.atomic_write_text(BASELINE, json.dumps(prov, indent=1, ensure_ascii=False) + "\n")
        print("the baseline now holds the provenance record")
    payload = (prov or {}).get("payload_check") if isinstance(prov, dict) else None
    payload_sha1 = str((payload or {}).get("mixed_sha1") or "") or _lock_payload_sha1()
    # Prefer the provenance's own commit; `--force` without a provenance falls back to the local HEAD.
    # 优先用 provenance 自带的提交；`--force` 且没给 provenance 时才回落到本地 HEAD。
    source_revision = str((prov or {}).get("source_commit") or "") if isinstance(prov, dict) else ""
    return write_published(source_revision=source_revision,
                           payload_sha1=payload_sha1,
                           payload_verified=bool((payload or {}).get("ok")),
                           force_reason=a.reason.strip() if a.force else "")


if __name__ == "__main__":
    sys.exit(main())
