#!/usr/bin/env python3
"""Contract test for the `matching-gate` workflow: a required check must not be green when
the gate verified nothing.

The workflow is not valid YAML-only logic: GitHub runs it on a runner. This test reads the
workflow as text and asserts the properties that make the fork path honest:

  1. the job that owns the required check is still named `matching`;
  2. the repository checkout and the mode classifier run without the private material;
  3. a `skip` change can pass without a build;
  4. a `fast`/`full` change without the private material fails with `exit 1`, before the
     private companion repository is checked out;
  5. the mode for a no-secret pull request comes from the base commit's classifier, not
     from the pull request's own copy.

This is a guard against the exact regression the 2026-10-26 audit found: the job printed a
notice and passed, so the required check was green although nothing was verified. The test
is intentionally text-based because `make check` must stay standard-library only.

Usage: python3 tools/check/test_workflow_contract.py

`matching-gate` 工作流契约测试：门禁什么都没验证时，required check 不能是绿的。
测试只读文本（不引入 YAML 依赖），守 5 条：job 名仍为 `matching`；checkout 与分类器在没有私有
材料时也运行；`skip` 可不构建通过；`fast`/`full` 在无私有材料时于私有取件之前 `exit 1`；无 secret
的 PR 用 base commit 的分类器而不是 PR 自己的副本。这是对 2026-10-26 审计发现的回归护栏。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "matching-gate.yml"

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


def step_if(chunk: str) -> str:
    """The `if:` expression of one step chunk, or "" when the step has none."""
    m = re.search(r"^\s+if:\s*(.+)$", chunk, re.M)
    return m.group(1).strip() if m else ""


def main() -> int:
    if not WORKFLOW.is_file():
        print(f"FAIL: workflow is missing: {WORKFLOW}")
        return 1
    text = WORKFLOW.read_text(encoding="utf-8")

    check("the workflow is still named matching-gate", "name: matching-gate" in text)
    check("the job that owns the required check is still named matching",
          re.search(r"^  matching:$", text, re.M) is not None)
    check("no continued-on-error step hides a failure", "continue-on-error" not in text)

    job = text.split("\n  matching:\n", 1)[-1]
    parts = re.split(r"\n      - ", job.split("\n    steps:\n", 1)[-1])
    chunks = ["- " + p for p in parts[1:]]

    def find(name: str) -> tuple[int, str]:
        for i, chunk in enumerate(chunks):
            if f"name: {name}" in chunk:
                return i, chunk
        return -1, ""

    i_checkout, c_checkout = find("Checkout this repository")
    i_classify, c_classify = find("Classify the change (skip / fast / full)")
    i_skip, c_skip = find("Notice (documentation or pure tests only, the build gate is skipped)")
    i_fail, c_fail = find("Fail when the gate is necessary but the private material is absent")
    i_private, c_private = find("Checkout the private companion (retail executable and Sony toolchain)")

    check("the checkout step exists", i_checkout >= 0)
    check("the classifier step exists", i_classify >= 0)
    check("the skip notice exists", i_skip >= 0)
    check("the fail step exists", i_fail >= 0)
    check("the private checkout exists", i_private >= 0)

    check("the checkout runs without the private material",
          "HAS_ORIG" not in step_if(c_checkout), step_if(c_checkout))
    check("the classifier runs without the private material",
          "HAS_ORIG" not in step_if(c_classify), step_if(c_classify))
    check("the classifier is selected from the base commit for no-secret pull requests",
          "$RUNNER_TEMP/classify_base.py" in c_classify and "git show" in c_classify)
    check("a classification error still falls back to full", "mode=full" in c_classify)

    check("a skip change passes without a build",
          step_if(c_skip) == "steps.mode.outputs.mode == 'skip'", step_if(c_skip))
    check("a build without the private material fails",
          "steps.mode.outputs.mode != 'skip'" in step_if(c_fail)
          and "env.HAS_ORIG != 'true'" in step_if(c_fail), step_if(c_fail))
    check("the fail step exits non-zero", re.search(r"^\s+exit 1\s*$", c_fail, re.M) is not None)
    check("the fail step runs before the private checkout",
          0 <= i_fail < i_private, f"fail={i_fail} private={i_private}")
    check("the private checkout still needs the private material",
          "env.HAS_ORIG == 'true'" in step_if(c_private), step_if(c_private))
    check("the checkout, the classifier, and the fail step are in that order",
          0 <= i_checkout < i_classify < i_fail, f"{i_checkout},{i_classify},{i_fail}")

    print()
    if fails:
        print(f"FAIL: {len(fails)} checks failed: {fails}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
