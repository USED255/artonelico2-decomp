#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify a change set into the mode the `matching-gate` workflow should run.

The gate is expensive (about 6 minutes), and most of that cost verifies things a
documentation-only or pure-source change cannot break. This tool answers one question:
"how much of the gate does this change need?"

Modes
-----
  skip   every changed file is documentation or a pure test (`tools/check/test_*.py`).
         The gate runs no build at all. It never applies to a push: the report artifact
         that decomp.dev publishes comes from a push to the default branch.
  fast   every changed file is documentation, a pure test, matched source
         (`src/matched/**`), the progress report, or `config/**` except the two files
         `splat split` reads (`config/symbol_addrs.txt`, `config/reloc_addrs.txt`). The
         gate assembles the baseline, skips the baseline link, and still runs the mixed
         build, the delta check, and the report. The mixed payload is compared against
         the retail payload, so the image is verified byte for byte.
  full   everything else: any push, any manual run, and any change that touches a build
         input (`splat.yaml`, the two splat inputs above, `build*.sh`, `Makefile`,
         `configure.py`, the build tools, `toolchain.lock.json`, the workflows). This is
         the default: the tool denies by default, and an error also lands in `full`.

Why `config/**` may be fast: `build.sh` (the baseline link) does not read `config/` at all,
and every config file the mixed build reads is covered by the mixed payload check, which
compares the final image against the retail payload byte for byte. The two exceptions are
the files `splat split` reads: they change the assembly tree, and only the baseline link
verifies that tree.

The decision is a property of the whole change set, never of a single file: a pull
request that changes one `.c` file and one `.md` file is `fast`, not `skip`.

Usage
-----
  python3 tools/ci/classify_change.py --event pull_request --base <sha> [--head HEAD] [--verbose]
  -> prints one of: skip | fast | full   (exit code 0)

Exit code 2 is a usage error only. A git failure or an unusable base prints `full`.

把一次改动的集合分类成 `matching-gate` 该跑的模式。

门禁很贵（约 6 分钟），而其中大部分验证与纯文档 / 纯源码改动无关。本工具只回答一个问题：
「这次改动需要门禁的哪一部分？」

模式
----
  skip   改动全是文档、或纯测试（`tools/check/test_*.py`）⇒ 完全不构建。**不适用于 push**：
         decomp.dev 用的报告 artifact 来自默认分支的 push。
  fast   改动只落在文档、纯测试、`src/matched/**`、进度报告，或 `config/**`（但**不含**
         `splat split` 会读的 `config/symbol_addrs.txt` 与 `config/reloc_addrs.txt`）⇒ 装配基线、
         跳过基线链接，但混合构建、delta、报告照跑；混合载荷比的是零售载荷，镜像仍被逐字节验证。
  full   其余全部：任何 push、任何手动运行、以及任何触碰构建输入的改动（`splat.yaml`、上面两个
         splat 输入、`build*.sh`、`Makefile`、`configure.py`、构建工具、`toolchain.lock.json`、
         workflows）。这是默认值：本工具默认拒绝，出错也落到 full。

为什么 `config/**` 可以是 fast：`build.sh`（基线链接）根本不读 `config/`；而混合构建读的那些
配置文件，其效果都已被「混合载荷 == 零售载荷」的逐字节比对覆盖。两个例外是 `splat split` 读的
文件——它们改变汇编树，而只有基线链接能验那棵树。

判定针对**整个改动集合**，不是单个文件：一个 PR 同时改了 `.c` 与 `.md` 属于 `fast`，不是 `skip`。

用法
----
  python3 tools/ci/classify_change.py --event pull_request --base <sha> [--head HEAD] [--verbose]
  → 输出 skip | fast | full 之一（退出码 0）

退出码 2 只表示用法错误；git 失败或 base 不可用一律输出 full。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Default deny. A path that matches neither pattern of the two wide sets lands in `full`.
# 默认拒绝：两个宽集都不匹配的路径落到 `full`。
SKIP_ONLY = re.compile(r"^(docs/|.*\.md$|LICENSE$|tools/check/test_[^/]*\.py$)")
FAST_EXTRA = re.compile(r"^(src/matched/|progress/|config/)")
# `splat split` reads these two, so they change the assembly tree that only the baseline link
# verifies. They must stay `full` even though the rest of `config/` may be `fast`.
# 这两个文件是 `splat split` 的输入，会改变只有基线链接能验证的汇编树，因此即使 `config/` 其余
# 文件可以是 `fast`，这两个必须留在 `full`。
FAST_DENY = re.compile(r"^config/(symbol_addrs|reloc_addrs)\.txt$")

ZERO_SHA = re.compile(r"^0+$")


def changed_files(root: str | Path, base: str, head: str = "HEAD") -> list[str] | None:
    """Files this change adds, changes, or deletes relative to `base`. None when git fails.

    相对 `base` 新增/修改/删除的文件；git 失败时返回 None。
    """
    cp = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", f"{base}...{head}"],
        capture_output=True, text=True)
    if cp.returncode != 0:
        return None
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def classify(event: str, base: str, files: list[str] | None) -> tuple[str, str]:
    """Return (mode, reason). `files` is None when the diff could not be computed.

    返回 (mode, reason)；`files` 为 None 表示算不出 diff。
    """
    if event != "pull_request":
        return "full", f"the event is {event!r}, not a pull request"
    if not base or ZERO_SHA.match(base):
        return "full", "the base commit is missing"
    if files is None:
        return "full", "git could not compute the diff against the base"
    if not files:
        return "full", "the diff is empty"
    if all(SKIP_ONLY.match(f) for f in files):
        return "skip", "every changed file is documentation or a pure test"
    denied = [f for f in files if FAST_DENY.match(f)]
    if denied:
        return "full", ("the change touches a build input that only the baseline link can verify: "
                        + ", ".join(sorted(denied)[:5]))
    if all(SKIP_ONLY.match(f) or FAST_EXTRA.match(f) for f in files):
        return "fast", ("every changed file is documentation, a pure test, matched source, "
                        "the progress report, or a configuration file the mixed build consumes")
    offending = [f for f in files if not (SKIP_ONLY.match(f) or FAST_EXTRA.match(f))]
    return "full", "the change touches a build input: " + ", ".join(sorted(offending)[:5])


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="classify_change.py",
        description="Classify a change set into the CI mode: skip (documentation or pure tests), "
                    "fast (matched source / progress / configuration the mixed build consumes), "
                    "or full (everything else).")
    ap.add_argument("--root", default=".", help="Repository root (default: the current directory)")
    ap.add_argument("--event", required=True, help="The GitHub event name (for example pull_request or push)")
    ap.add_argument("--base", default="", help="The base commit: pull_request.base.sha, or github.event.before")
    ap.add_argument("--head", default="HEAD", help="The commit to compare with (default: HEAD)")
    ap.add_argument("--verbose", action="store_true", help="List the changed files on stderr")
    args = ap.parse_args()

    files = None
    if args.event == "pull_request" and args.base and not ZERO_SHA.match(args.base):
        files = changed_files(args.root, args.base, args.head)
        if args.verbose and files is not None:
            for f in files:
                print(f"  changed: {f}", file=sys.stderr)

    mode, reason = classify(args.event, args.base, files)
    print(f"classify: mode={mode} — {reason}", file=sys.stderr)
    print(mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
