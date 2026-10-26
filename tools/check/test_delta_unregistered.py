#!/usr/bin/env python3
"""Regression test: `make delta` must stop on a changed source that the ledger does not register.

Background: `cmd_delta` used to print `skip N unregistered files` and return 0 when no
registered function was affected. A contributor who added a new `src/matched/*.c` file
therefore saw a successful exit code although the build never compiled the file and the
gate never compared it. The fix returns 1 and names the files. This test runs the real
driver against a throwaway git repository under `.tmp/`, so it needs no toolchain and no
retail executable.

Usage: python3 tools/check/test_delta_unregistered.py

回归测试：改动的源文件未登记台账时，`make delta` 必须失败。

背景：`cmd_delta` 过去对未登记文件只打印 `skip N unregistered files` 并返回 0；贡献者
新增 `src/matched/*.c` 时会看到「成功」，但构建没有编译该文件，门禁也没有比对它。本测试
在 `.tmp/` 的临时 git 仓库里跑真正的驱动，不需要工具链与原版可执行文件。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "tools" / "build" / "decomp_build.py"
WORK = ROOT / ".tmp" / "delta_unregistered"

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True, text=True)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    cp = run(["git", "-C", repo, *args], ROOT)
    if cp.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
    return cp


def delta(repo: Path, base: str) -> subprocess.CompletedProcess:
    return run([sys.executable, DRIVER, "--root", repo, "--layout", "flat",
                "--name", "test-target", "delta", "--base", base], ROOT)


def main() -> int:
    shutil.rmtree(WORK, ignore_errors=True)
    (WORK / "src" / "matched").mkdir(parents=True)
    (WORK / "config").mkdir(parents=True)
    (WORK / "config" / "matched_symbols.txt").write_text(
        "# <symbol> [<source-basename>]   # <tag>\nfunc_aaaa\n", encoding="utf-8")
    (WORK / "src" / "matched" / "func_aaaa.c").write_text(
        "void func_aaaa(void) {}\n", encoding="utf-8")

    git(WORK, "init", "-q")
    git(WORK, "config", "user.email", "audit@example.com")
    git(WORK, "config", "user.name", "audit")
    git(WORK, "add", "-A")
    git(WORK, "commit", "-qm", "base")
    base = git(WORK, "rev-parse", "HEAD").stdout.strip()

    # 1) No change keeps the old success path.
    cp = delta(WORK, base)
    check("no change exits 0", cp.returncode == 0, f"rc={cp.returncode} err={cp.stderr[-300:]}")
    check("no change says nothing to compare", "nothing to compare" in cp.stdout, cp.stdout[-200:])

    # 2) A new source that is still untracked (the normal state before the first commit).
    new = WORK / "src" / "matched" / "func_bbbb.c"
    new.write_text("void func_bbbb(void) {}\n", encoding="utf-8")
    cp = delta(WORK, base)
    check("an untracked new source exits 1", cp.returncode == 1,
          f"rc={cp.returncode} out={cp.stdout[-300:]} err={cp.stderr[-300:]}")
    check("the untracked source is named on stderr", "func_bbbb.c" in cp.stderr, cp.stderr[-300:])
    check("the message points at the ledger", "config/matched_symbols.txt" in cp.stderr,
          cp.stderr[-300:])
    check("the old skip message is gone", "skip 1 unregistered" not in cp.stdout, cp.stdout[-300:])

    # 3) The same source after it is committed. The base diff sees it; the answer must not change.
    git(WORK, "add", "-A")
    git(WORK, "commit", "-qm", "add func_bbbb")
    cp = delta(WORK, base)
    check("a committed new source still exits 1", cp.returncode == 1,
          f"rc={cp.returncode} out={cp.stdout[-300:]}")
    check("the committed source is named on stderr", "func_bbbb.c" in cp.stderr, cp.stderr[-300:])

    print()
    if fails:
        print(f"FAIL: {len(fails)} checks failed: {fails}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
