#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test for every tool the compiler handbook documents.

Why: a handbook that tells a reader to run a command is only useful if that command still works. The
data check (`test_compiler_laws.py`) verifies the handbook's *facts*; this script verifies its
*interfaces* — that each documented invocation parses, runs, and produces the shape the handbook says.

Two tiers, so this stays useful in CI (where the game and the Sony toolchain are absent):

  1. Always: `tools/compiler/laws-query.py` against `docs/compiler/laws.json`. Every law id must be
     reachable through `law`, `list` must mention all of them, and the symptom/lever/pass/guide lookups
     must return something.
  2. Only when the toolchain is present (detected through the tool itself): `ee-gcc-anchor.py selftest`,
     `ee-gcc-passdiff.py` on two synthetic sources that differ, and `ee-gcc-spill-map.py` on a synthetic
     function that spills. Each skipped tier is reported as SKIP, never as a pass.

Usage: `python3 tools/check/test_compiler_tools.py` (`make check` calls it).

手册里写「请运行这条命令」，只有当这条命令**仍然能跑**时才有用。数据校验（`test_compiler_laws.py`）保证手册的
**事实**；本脚本保证手册的**接口**——每条文档化的调用都能解析、能跑、形状与手册一致。

分两级，使其在 CI（没有游戏、没有 Sony 工具链）里依然有效：
1. **总是跑**：`laws-query.py` 对 `laws.json` 的各个子命令。
2. **有工具链才跑**：`ee-gcc-anchor.py selftest`、`ee-gcc-passdiff.py`（两份会分叉的合成源码）、
   `ee-gcc-spill-map.py`（会溢出的合成函数）。缺条件一律记 SKIP，绝不记成 pass。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAWS_JSON = ROOT / "docs" / "compiler" / "laws.json"
LAWS_QUERY = ROOT / "tools" / "compiler" / "laws-query.py"
ANCHOR = ROOT / "tools" / "compiler" / "ee-gcc-anchor.py"
PASSDIFF = ROOT / "tools" / "compiler" / "ee-gcc-passdiff.py"
SPILLMAP = ROOT / "tools" / "compiler" / "ee-gcc-spill-map.py"
OBSERVE = ROOT / "tools" / "compiler" / "ee-gcc-observe.py"

DEFAULT_CC1 = Path.home() / "eecc" / "ee-gcc3.2-040921" / "lib" / "gcc-lib" / "ee" / "3.2-ee-040921" / "cc1"
DEFAULT_EE_GCC = Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / "ee-gcc"

passed = failed = skipped = 0
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"[ok  ] {label}")
    else:
        failed += 1
        failures.append(label + (f" — {detail}" if detail else ""))
        print(f"[FAIL] {label}" + (f" — {detail}" if detail else ""))


def skip(label: str, why: str) -> None:
    global skipped
    skipped += 1
    print(f"[skip] {label} ({why})")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *cmd], capture_output=True, text=True, cwd=ROOT, **kw)


def tier_laws_query() -> None:
    data = json.loads(LAWS_JSON.read_text(encoding="utf-8"))
    laws = data["laws"]
    ids = [law["id"] for law in laws]

    out = run([str(LAWS_QUERY), "list"])
    check("laws-query list runs", out.returncode == 0, out.stderr.strip()[:120])
    missing = [i for i in ids if i not in out.stdout]
    check(f"laws-query list mentions all {len(ids)} laws", not missing, f"missing {missing}")

    for law_id in ids:
        out = run([str(LAWS_QUERY), "law", law_id])
        check(f"laws-query law {law_id}", out.returncode == 0 and law_id in out.stdout,
              out.stderr.strip()[:80])

    out = run([str(LAWS_QUERY), "find", "allocation"])
    check("laws-query find returns hits", out.returncode == 0 and "L-EE-" in out.stdout)

    out = run([str(LAWS_QUERY), "guide", "frame"])
    check("laws-query guide frame returns a lever", out.returncode == 0 and len(out.stdout.strip()) > 40)

    passes = sorted({p for law in laws for p in law.get("pass", [])})
    if passes:
        out = run([str(LAWS_QUERY), "pass", passes[0]])
        check(f"laws-query pass {passes[0]}", out.returncode == 0 and "L-EE-" in out.stdout)

    out = run([str(LAWS_QUERY), "--json", "list"])
    try:
        json.loads(out.stdout)
        ok = True
    except Exception as exc:  # noqa: BLE001
        ok = False
        detail = str(exc)[:80]
    check("laws-query --json emits parseable JSON", ok, "" if ok else detail)

    # 每个 law 的 evidence 路径在同一仓库里必须存在（`private:` 前缀的除外）
    missing_ev = []
    for law in laws:
        for item in law.get("evidence", []):
            if item.startswith(("private:", "party:")):
                continue  # 指向私有研究仓库（证据文件 / 本项目自己的报告）
            if not (ROOT / item).exists():
                missing_ev.append(f"{law['id']}:{item}")
    check("every public evidence path exists", not missing_ev, f"{missing_ev[:3]}")


def tier_toolchain(tmp: Path) -> None:
    if not DEFAULT_CC1.exists():
        skip("ee-gcc-anchor selftest", f"no cc1 at {DEFAULT_CC1}")
    else:
        out = run([str(ANCHOR), "--cc1", str(DEFAULT_CC1), "selftest"])
        check("ee-gcc-anchor selftest", out.returncode == 0 and "pass" in out.stdout,
              (out.stdout + out.stderr).strip()[-120:])
        out = run([str(ANCHOR), "--cc1", str(DEFAULT_CC1), "symbol", "allocno_compare"])
        check("ee-gcc-anchor symbol resolves", out.returncode == 0 and "0x" in out.stdout)

    if not DEFAULT_EE_GCC.exists():
        skip("ee-gcc-passdiff", f"no compiler at {DEFAULT_EE_GCC}")
        skip("ee-gcc-spill-map", f"no compiler at {DEFAULT_EE_GCC}")
        skip("ee-gcc-observe selftest", f"no compiler at {DEFAULT_EE_GCC}")
        return

    # 手册的 10 组合成夹具：把手册里的规则变成可执行断言（`--selftest`）
    out = run([str(OBSERVE), "--cc", str(DEFAULT_EE_GCC), "--selftest", "--work", str(tmp / "observe")])
    check("ee-gcc-observe selftest (10 fixtures)", out.returncode == 0 and "10 passed" in out.stdout,
          (out.stdout + out.stderr).strip()[-160:])

    a = tmp / "a.c"
    b = tmp / "b.c"
    a.write_text("int f(int x) { return x + 1; }\n", encoding="utf-8")
    b.write_text("int f(int x) { return x + 2; }\n", encoding="utf-8")
    out = run([str(PASSDIFF), "--cc", str(DEFAULT_EE_GCC), str(a), str(b)])
    check("ee-gcc-passdiff finds a divergence (exit 1)", out.returncode == 1,
          f"exit {out.returncode}: {(out.stdout + out.stderr).strip()[-100:]}")

    spill = tmp / "spill.c"
    body = "\n".join(f"    s += sink(v{i});" for i in range(12))
    decl = "\n".join(f"    int v{i} = p[{i}];" for i in range(12))
    use = " + ".join(f"v{i}" for i in range(12))
    spill.write_text(f"extern int sink(int);\nint demo(int *p) {{\n{decl}\n    int s = 0;\n{body}\n"
                     f"    return s + {use};\n}}\n", encoding="utf-8")
    out = run([str(SPILLMAP), "--cc", str(DEFAULT_EE_GCC), "--src", str(spill),
               "--flags=-Os", "--work", str(tmp / "sm")])
    check("ee-gcc-spill-map reports a frame", out.returncode == 0 and "frame=" in out.stdout,
          (out.stdout + out.stderr).strip()[-120:])


def main() -> int:
    if not LAWS_JSON.exists():
        print(f"FAIL: {LAWS_JSON} missing")
        return 2
    tier_laws_query()
    with tempfile.TemporaryDirectory(prefix="compiler-tools-") as td:
        tier_toolchain(Path(td))
    print(f"\ncompiler tools: {passed} passed / {failed} failed / {skipped} skipped")
    if failed:
        for line in failures:
            print(f"  - {line}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
