#!/usr/bin/env python3
"""Tests for tools/check/check_public_repo.py. No network, no toolchain, no build.

These tests pin the R30 findings A2 (the denied-material list missed the retail ELF and other
restricted classes), A5 (a non-ASCII path was C-quoted by `git ls-files`, so it bypassed both the
deny scan and the contribution checks) and the size backstop that backs them up.

The git cases run against throwaway repositories under `.tmp/`; the real repository is never
modified.

Usage: python3 tools/check/test_public_repo.py

check_public_repo.py 的测试（无网络/工具链/构建）。固定 R30 的 A2（禁材列表漏掉原版 ELF 等类别）、
A5（非 ASCII 路径被 `git ls-files` 做 C-quoting，同时绕过禁材扫描与贡献检查）与兜底尺寸线。
git 用例都在 `.tmp/` 下的一次性仓库里跑，**不碰真实仓库**。
用法：python3 tools/check/test_public_repo.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "check"))
import check_public_repo as C  # noqa: E402

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


WORK = ROOT / ".tmp" / "public_repo_test"
shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True, exist_ok=True)

GIT_ENV = dict(
    os.environ,
    GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
    GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid",
    GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args],
                          capture_output=True, text=True, env=GIT_ENV, check=True)


# A minimal valid progress report: `check_contrib` also runs the report rules, and the
# throwaway repositories need something for those rules to read.
# 一份最小合法报告：`check_contrib` 末尾也会跑报告规则，一次性仓库需要它能读。
MIN_REPORT = {
    "measures": {"matched_code": "1", "total_code": "2", "matched_functions": "1",
                 "total_functions": "2", "matched_code_percent": 50.0,
                 "matched_functions_percent": 50.0, "total_units": 1},
    "units": [{"name": "func_00000000"}],
}


def new_repo(name: str, base_files: dict[str, str] | None = None) -> tuple[Path, str]:
    """A throwaway repository with one commit. Returns (path, base-sha).

    `base_files` are committed in that first commit, so a later delete or rename shows up as a
    D / R record in `base...HEAD` (a file that is added and then changed inside the range does not).

    `base_files` 会进第一个提交：这样后续的删除/重命名才会在 `base...HEAD` 里显示为 D / R 记录
    （区间内「新增又改动」的文件不会显示）。
    """
    repo = WORK / name
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    (repo / "progress").mkdir(parents=True, exist_ok=True)
    (repo / "progress" / "SLPS_258.19_report.json").write_text(
        json.dumps(MIN_REPORT), encoding="utf-8")
    paths = ["README.md", "progress/SLPS_258.19_report.json"]
    for rel, text in (base_files or {}).items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        paths.append(rel)
    git(repo, "add", *paths)
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").stdout.strip()
    return repo, base


def bad_text() -> str:
    return " | ".join(C.BAD)


def run_contrib(repo: Path, base: str, **kw) -> None:
    C.OK.clear()
    C.BAD.clear()
    C.check_contrib(base, root=repo, **kw)


print("[1] the denied-material patterns cover the classes that matter")
for rel in ("orig/SLPS_258.19", "orig/SLPS_258.19.elf", "build/SLPS_258.19.bin",
            "routebjp/stubs/func_x.s", "asm/cod/func_00100000.s", "asm/日本.s",
            "assets/cod/x.bin", "assets/x.irx", "include/macro.inc",
            "toolchain/e32.tar.xz", "toolchain/x.zip", "docs/private/notes.md",
            "out/evidence/x.txt", "SLPS_258.19.rom"):
    check(f"denied: {rel}", bool(C.deny_hits([rel])), str(C.deny_hits([rel])))
for rel in ("src/matched/func_00100000.c", "config/matched_symbols.txt", "splat.yaml",
            "progress/SLPS_258.19_report.json", "工具.md", "Makefile", "build.sh"):
    check(f"allowed: {rel}", not C.deny_hits([rel]), str(C.deny_hits([rel])))

print("[2] the size backstop catches a big file and exempts the published reports")
sizes = {
    "orig/SLPS_258.19": 9_352_548,
    "progress/SLPS_258.19_report.json": 9_352_548,   # exempt even when large
    "progress/baseline.json": 5_002_527,             # exempt
    "splat.yaml": 696_377,
    "exactly-eight-mib.bin": C.SIZE_BACKSTOP,        # boundary: not above
    "routebjp/note.txt": 12 << 20,
}
hits = C.oversize_hits(list(sizes), size_of=sizes.get)
check("a 9.35 MB extension-less file hits", any("orig/SLPS_258.19" in h for h in hits), str(hits))
check("routebjp/note.txt hits by size", any("routebjp/note.txt" in h for h in hits), str(hits))
check("progress/*.json is exempt", not any("progress/" in h for h in hits), str(hits))
check("the boundary itself does not hit", not any("exactly-eight-mib" in h for h in hits), str(hits))
check("splat.yaml does not hit", not any("splat.yaml" in h for h in hits), str(hits))

print("[3] git -z keeps a non-ASCII path usable (the A5 regression)")
repo, base = new_repo("quoting")
(repo / "日本.s").write_text("nop\n", encoding="utf-8")
git(repo, "add", "-f", "日本.s")
git(repo, "commit", "-q", "-m", "add a non-ASCII assembly file")
tracked = C.tracked_files(repo)
check("tracked_files returns the real, unquoted path",
      bool(tracked) and "日本.s" in tracked and not any('"' in t for t in tracked), str(tracked))
check("the -z path matches the deny list", bool(C.deny_hits(tracked or [])),
      str(C.deny_hits(tracked or [])))

# The old code called `git ls-files` without -z. Show what that produced: a C-quoted string that
# matches nothing and is not a file on disk.
quoted = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True,
                        env=GIT_ENV, check=True).stdout.splitlines()
check("the old (quoted) output is what the old code saw",
      any(q.startswith('"') for q in quoted), str(quoted))
check("the quoted path matched no deny pattern (the old hole)", not C.deny_hits(quoted),
      str(C.deny_hits(quoted)))

C.OK.clear(); C.BAD.clear()
C.check_deny(repo)
check("check_deny refuses the whole tree over a non-ASCII stub",
      any("cannot publish" in m for m in C.BAD), bad_text())

print("[4] contribution mode: the old fail-open path is now fail-closed")

repo, base = new_repo("plain")
(repo / "new.txt").write_text("hello\n", encoding="utf-8")
git(repo, "add", "new.txt")
git(repo, "commit", "-q", "-m", "add a text file")
run_contrib(repo, base)
check("a plain text addition is allowed",
      any("allowed contribution: new.txt" in m for m in C.OK) and not C.BAD, bad_text())

repo, base = new_repo("quoted-deny")
(repo / "asm").mkdir()
(repo / "asm" / "日本.s").write_text("nop\n", encoding="utf-8")
git(repo, "add", "-f", "asm/日本.s")
git(repo, "commit", "-q", "-m", "add a non-ASCII assembly file")
run_contrib(repo, base)
check("a non-ASCII denied path is refused by the deny scan",
      any("cannot publish" in m for m in C.BAD), bad_text())

repo, base = new_repo("ghost")
(repo / "ghost.txt").write_text("here\n", encoding="utf-8")
git(repo, "add", "ghost.txt")
git(repo, "commit", "-q", "-m", "add a file, then remove it from the working tree")
os.unlink(repo / "ghost.txt")
run_contrib(repo, base)
check("a path that is not a regular file is refused (the C-quoting symptom)",
      any("not a regular file" in m for m in C.BAD), bad_text())

repo, base = new_repo("symlink")
os.symlink("README.md", repo / "link.md")
git(repo, "add", "link.md")
git(repo, "commit", "-q", "-m", "add a symbolic link")
run_contrib(repo, base)
check("a symbolic link is refused", any("symbolic link" in m for m in C.BAD), bad_text())

repo, base = new_repo("readonly")
(repo / "progress" / "x.json").write_text("{}\n", encoding="utf-8")
git(repo, "add", "progress/x.json")
git(repo, "commit", "-q", "-m", "add a file under the read-only tree")
run_contrib(repo, base)
check("a read-only path is refused", any("read-only path" in m for m in C.BAD), bad_text())

repo, base = new_repo("delete", base_files={"gone.txt": "bye\n"})
git(repo, "rm", "-q", "gone.txt")
git(repo, "commit", "-q", "-m", "delete it")
run_contrib(repo, base)
check("a delete is refused without --allow-restructure",
      any("a delete is not accepted" in m for m in C.BAD), bad_text())
run_contrib(repo, base, allow_restructure=True)
check("a delete is allowed with --allow-restructure",
      any("allowed delete: gone.txt" in m for m in C.OK) and not C.BAD, bad_text())

repo, base = new_repo("rename", base_files={"old.txt": "x\n"})
git(repo, "mv", "old.txt", "new.txt")
git(repo, "commit", "-q", "-m", "rename it")
run_contrib(repo, base)
check("a rename is refused without --allow-restructure",
      any("rename or a copy is not accepted" in m for m in C.BAD), bad_text())
run_contrib(repo, base, allow_restructure=True)
check("a rename is parsed from -z and allowed with --allow-restructure",
      any("rename or a copy is allowed" in m for m in C.OK) and not C.BAD, bad_text())

repo, base = new_repo("big")
with (repo / "big.txt").open("wb") as fh:
    fh.write(b"a" * ((1 << 20) + 1))
git(repo, "add", "big.txt")
git(repo, "commit", "-q", "-m", "add a large text file")
run_contrib(repo, base)
check("a file above the 1 MiB contribution limit is refused",
      any("too large" in m for m in C.BAD), bad_text())

print("[5] publication mode (a maintainer pull request that updates the published record)")
PAYLOAD = "7cc42d275750600d1f232b2632447f77205f3fc0"


def sha_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def measures_for(matched: int, total: int = 20) -> dict:
    return {"matched_code": str(matched), "total_code": str(total),
            "matched_functions": str(matched), "total_functions": str(total),
            "matched_code_percent": matched / total * 100,
            "matched_functions_percent": matched / total * 100, "total_units": total}


def report_bytes(matched: int) -> bytes:
    doc = {"measures": measures_for(matched), "units": [{"name": "u0"}]}
    return (json.dumps(doc, indent=1) + "\n").encode()


def provenance_for(rep: bytes, measures: dict, **over) -> dict:
    prov = {"schema": "at2-progress-baseline/1", "source_commit": "b" * 40, "source_dirty": False,
            "payload_check": {"ok": True, "baseline_sha1": PAYLOAD, "mixed_sha1": PAYLOAD,
                              "expected_sha1": PAYLOAD},
            "c_units_below_100": 0, "limit": 0, "report_sha256": sha_of(rep), "measures": measures}
    prov.update(over)
    return prov


def published_json(report_sha: str, baseline_sha: str, lock_sha: str, *, verified: bool = True) -> dict:
    return {"schema": "at2-published/2",
            "report": {"path": "progress/SLPS_258.19_report.json", "sha256": report_sha},
            "baseline": {"path": "progress/baseline.json", "sha256": baseline_sha},
            "toolchain_lock_sha256": lock_sha, "payload_sha1": PAYLOAD,
            "payload_verified": verified, "source_revision": "a" * 40}


def publication_repo(name: str, *, new_matched: int = 11, old_matched: int = 10,
                     prov_over: dict | None = None, extra_file: str | None = None,
                     break_hash: bool = False):
    """A repo whose base commit holds a legacy publication and whose HEAD holds a publication."""
    repo = WORK / name
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q")
    (repo / "progress").mkdir(parents=True, exist_ok=True)
    (repo / "toolchain.lock.json").write_text(json.dumps({"game": {"payload_sha1": PAYLOAD}}), encoding="utf-8")
    lock_sha = sha_of((repo / "toolchain.lock.json").read_bytes())
    old = report_bytes(old_matched)
    (repo / "progress" / "SLPS_258.19_report.json").write_bytes(old)
    (repo / "progress" / "baseline.json").write_bytes(old)
    (repo / "PUBLISHED.json").write_text(json.dumps(published_json(sha_of(old), sha_of(old), lock_sha)),
                                         encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").stdout.strip()

    new = report_bytes(new_matched)
    prov = provenance_for(new, measures_for(new_matched), **(prov_over or {}))
    prov_b = (json.dumps(prov, indent=1) + "\n").encode()
    (repo / "progress" / "SLPS_258.19_report.json").write_bytes(new)
    (repo / "progress" / "baseline.json").write_bytes(prov_b)
    (repo / "PUBLISHED.json").write_text(
        json.dumps(published_json(sha_of(new + (b"\n" if break_hash else b"")), sha_of(prov_b), lock_sha)),
        encoding="utf-8")
    if extra_file:
        (repo / extra_file).write_text("sneaky\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "publish")
    return repo, base


def run_pub(repo: Path, base: str) -> list[str]:
    C.OK.clear()
    C.BAD.clear()
    C.check_contrib(base, root=repo, allow_publication=True)
    return list(C.BAD)


repo, base = publication_repo("pub-ok")
check("a complete publication PR passes", not run_pub(repo, base), bad_text())
run_contrib(repo, base)   # without allow_publication
check("without publication mode the read-only rule still applies",
      any("read-only path" in m for m in C.BAD), bad_text())

repo, base = publication_repo("pub-dirty", prov_over={"source_dirty": True})
check("a dirty provenance is refused",
      any("source tree was dirty" in m for m in run_pub(repo, base)), bad_text())

repo, base = publication_repo("pub-unverified", prov_over={"payload_check": {"ok": False}})
check("an unverified payload is refused",
      any("payload check did not pass" in m for m in run_pub(repo, base)), bad_text())

repo, base = publication_repo("pub-badhash", break_hash=True)
check("a record that does not match its file is refused",
      any("sha256 does not match" in m for m in run_pub(repo, base)), bad_text())

repo, base = publication_repo("pub-regress", new_matched=5)
check("a regression is refused", any("regression" in m for m in run_pub(repo, base)), bad_text())

repo, base = publication_repo("pub-mixed", extra_file="sneaky.txt")
check("a mixed change is refused",
      any("may change only" in m for m in run_pub(repo, base)), bad_text())

shutil.rmtree(WORK, ignore_errors=True)

print(f"\n{len(fails)} failed" if fails else "\nall check_public_repo tests passed")
sys.exit(1 if fails else 0)
