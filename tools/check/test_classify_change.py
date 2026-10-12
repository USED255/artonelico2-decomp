#!/usr/bin/env python3
"""Tests for tools/ci/classify_change.py. No toolchain and no build are necessary.

The classifier decides how much of `matching-gate` runs, so a regression here would
silently change what CI verifies. The tests cover the decision table and the git call
(the three-dot diff, which must not count the base branch's own commits).

Usage: python3 tools/check/test_classify_change.py

classify_change.py 的测试（不需要工具链与构建）。分类器决定门禁跑多少，一旦回归会静默改变
CI 的验证范围，所以既测判定表也测 git 调用（三点 diff 不能把 base 分支自己的提交算进来）。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "ci"))
import classify_change as cc  # noqa: E402

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


def mode_of(event: str, base: str, files) -> str:
    return cc.classify(event, base, files)[0]


SHA = "a" * 40
ZERO = "0" * 40

print("[1] the decision table")
cases = [
    # (name, event, base, files, expected)
    ("documentation only", "pull_request", SHA, ["docs/BUILD.md", "README.md", "LICENSE"], "skip"),
    ("a pure test file", "pull_request", SHA, ["tools/check/test_tool_paths.py"], "skip"),
    ("documentation plus a pure test", "pull_request", SHA,
     ["docs/BUILD.md", "tools/check/test_splat_snapshot.py"], "skip"),
    ("matched source", "pull_request", SHA, ["src/matched/func_00123456.c"], "fast"),
    ("matched source + header", "pull_request", SHA, ["src/matched/a.c", "src/matched/a.h"], "fast"),
    ("progress report", "pull_request", SHA, ["progress/SLPS_258.19_report.json"], "fast"),
    ("source plus documentation stays fast", "pull_request", SHA,
     ["src/matched/a.c", "docs/BUILD.md"], "fast"),
    ("the ledger is fast", "pull_request", SHA, ["config/matched_symbols.txt"], "fast"),
    ("the compile flags are fast", "pull_request", SHA, ["config/source_flags.tsv"], "fast"),
    ("the compiler map is fast", "pull_request", SHA, ["config/compiler_map.tsv"], "fast"),
    ("a match usually lands as fast", "pull_request", SHA,
     ["src/matched/a.c", "src/matched/externs.h", "config/matched_symbols.txt",
      "config/source_flags.tsv", "progress/SLPS_258.19_report.json"], "fast"),
    ("the splat symbol list forces full", "pull_request", SHA, ["config/symbol_addrs.txt"], "full"),
    ("the splat reloc list forces full", "pull_request", SHA, ["config/reloc_addrs.txt"], "full"),
    ("a splat input plus the ledger forces full", "pull_request", SHA,
     ["config/symbol_addrs.txt", "config/matched_symbols.txt"], "full"),
    ("a config README stays skip", "pull_request", SHA, ["config/README.md"], "skip"),
    ("a pure test plus matched source is fast", "pull_request", SHA,
     ["tools/check/test_x.py", "src/matched/a.c"], "fast"),
    ("the verifier itself forces full", "pull_request", SHA,
     ["tools/check/check_public_repo.py"], "full"),
    ("a maintainer tool forces full", "pull_request", SHA, ["tools/maintainer/publish_report.py"], "full"),
    ("splat.yaml forces full", "pull_request", SHA, ["splat.yaml"], "full"),
    ("a workflow forces full", "pull_request", SHA, [".github/workflows/matching-gate.yml"], "full"),
    ("the tool itself forces full", "pull_request", SHA, ["tools/ci/classify_change.py"], "full"),
    ("build.sh forces full", "pull_request", SHA, ["build.sh"], "full"),
    ("docs plus a build input forces full", "pull_request", SHA,
     ["docs/BUILD.md", "config/symbol_addrs.txt"], "full"),
    ("a push is always full", "push", SHA, ["docs/BUILD.md"], "full"),
    ("a manual run is always full", "workflow_dispatch", "", ["docs/BUILD.md"], "full"),
    ("an empty base is full", "pull_request", "", ["docs/BUILD.md"], "full"),
    ("an all-zero base is full", "pull_request", ZERO, ["docs/BUILD.md"], "full"),
    ("a failed diff is full", "pull_request", SHA, None, "full"),
    ("an empty diff is full", "pull_request", SHA, [], "full"),
    ("a root file outside the allowlists is full", "pull_request", SHA, ["PUBLISHED.json"], "full"),
]
for name, event, base, files, want in cases:
    got = mode_of(event, base, files)
    check(f"{name} -> {want}", got == want, f"got {got}")


print("[2] changed_files: the three-dot diff against a real repository")
tmp = ROOT / ".tmp" / "classify_test"
shutil.rmtree(tmp, ignore_errors=True)
tmp.mkdir(parents=True, exist_ok=True)
git = ["git", "-C", str(tmp), "-c", "user.email=ci@example.invalid", "-c", "user.name=ci-test"]


def run(*args: str) -> str:
    cp = subprocess.run([*git, *args], capture_output=True, text=True)
    if cp.returncode != 0:
        print(f"    git {' '.join(args)} failed: {cp.stderr.strip()[:120]}")
        return ""
    return cp.stdout


run("init", "-q", "-b", "main")
(tmp / "docs").mkdir(exist_ok=True)
(tmp / "src" / "matched").mkdir(parents=True, exist_ok=True)
(tmp / "docs" / "a.md").write_text("docs\n", encoding="utf-8")
(tmp / "src" / "matched" / "a.c").write_text("int a(void) { return 1; }\n", encoding="utf-8")
run("add", "-A")
run("commit", "-q", "-m", "base")
base = run("rev-parse", "HEAD").strip()

# The base branch moves on after the branch point: its own commits must not show up.
(tmp / "docs" / "base-only.md").write_text("base side\n", encoding="utf-8")
run("add", "-A")
run("commit", "-q", "-m", "base side moves on")
base_moved = run("rev-parse", "HEAD").strip()
run("checkout", "-q", "-b", "topic", base)
(tmp / "src" / "matched" / "b.c").write_text("int b(void) { return 2; }\n", encoding="utf-8")
run("add", "-A")
run("commit", "-q", "-m", "topic change")

files = cc.changed_files(tmp, base)
check("the diff lists only the topic change", files == ["src/matched/b.c"], f"got {files}")
check("the topic change is fast", cc.classify("pull_request", base, files)[0] == "fast")

# A documentation-only branch on top of the moved base: it must classify as skip, and the
# base branch's own commits must not appear in the diff.
run("checkout", "-q", "-b", "docs-only", base_moved)
(tmp / "docs" / "only.md").write_text("docs only\n", encoding="utf-8")
run("add", "-A")
run("commit", "-q", "-m", "documentation only")

docs_files = cc.changed_files(tmp, base_moved)
check("the documentation-only diff lists just that file", docs_files == ["docs/only.md"], f"got {docs_files}")
check("the documentation-only change is skip",
      cc.classify("pull_request", base_moved, docs_files)[0] == "skip")

shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{len(fails)} failed" if fails else "\nall classify_change tests passed")
sys.exit(1 if fails else 0)
