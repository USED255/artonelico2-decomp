#!/usr/bin/env python3
"""Public repository checks for CI. The tool uses the standard library only.

Five tasks:
  1. Publication record integrity: the report, the baseline, and the toolchain lock
     sha256 values in `PUBLISHED.json` must agree with the files on disk.
  2. Denied material: assembly, ROM/ISO images, toolchain archives, the retail executable and
     every generated splat tree must FAIL. A tracked file above `SIZE_BACKSTOP` also FAILS:
     that is the backstop for a restricted file whose name carries no telling extension
     (the retail ELF is `orig/SLPS_258.19`, 9.35 MB, and matches no pattern).
  3. Report rules: the schema and the arithmetic of
     `progress/SLPS_258.19_report.json` must hold (matched <= total).
  4. No regression: the report must not fall behind `progress/baseline.json`
     (`--baseline` and `--report` select other files). The denominators count too: a smaller
     `total_code` with an unchanged `matched_code` inflates the percentage.
  5. Contribution mode (`--pr`): an added or changed path must be a regular, UTF-8 text file
     inside the size limit. A path that is not a regular file in the working tree is refused
     (fail closed), and a symbolic link is always refused.

Every git call below uses `-z`. With the default `core.quotePath=true`, git C-quotes a path
that holds non-ASCII bytes (`日本.s` becomes `"\\346\\227\\245.s"`). A quoted path matches no
pattern, and `ROOT / quoted` is not a file, so a quoted path used to pass both the denied
material scan and the contribution checks. `-z` returns the real bytes.

Usage:
    python3 tools/check/check_public_repo.py --check
    python3 tools/check/check_public_repo.py --baseline progress/baseline.json --report progress/SLPS_258.19_report.json
Exit code: 0 on success, 1 when the tool finds a problem that you must repair.

公开仓库自检（CI 的快速门禁；只依赖标准库）。

五件事：
  1. **发布记录自洽**：`PUBLISHED.json` 记录的报告/基线/工具链锁 sha256 必须与磁盘一致。
  2. **不可公开类别**：汇编、ROM/ISO、工具链压缩包、原版可执行文件、splat 生成树一律 FAIL；
     tracked 文件超过 `SIZE_BACKSTOP` 也 FAIL —— 这是「名字看不出类别」的兜底
     （原版 ELF 是 `orig/SLPS_258.19`，9.35 MB，任何模式都匹配不到）。
  3. **报告不变量**：`progress/SLPS_258.19_report.json` 的 schema 与算术自洽（matched ≤ total）。
  4. **不回归**：报告相对 `progress/baseline.json` 不得回退；**分母也参与比较** ——
     `total_code` 变小而 `matched_code` 不变，等于把百分比灌水。
  5. **贡献模式（`--pr`）**：新增/修改的路径必须是尺寸受限的普通 UTF-8 文本文件；
     磁盘上不是普通文件的一律**拒绝（fail closed）**，符号链接一律拒绝。

下面所有 git 调用都用 `-z`：默认 `core.quotePath=true` 会把含非 ASCII 字节的路径做 C-quoting
（`日本.s` → `"\\346\\227\\245.s"`）。被引号包裹的路径匹配不到任何模式，`ROOT / 引号串` 也不是文件，
于是**同时**骗过禁材扫描与贡献检查。`-z` 返回真实字节。

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

# `*.s` stays a global deny: PUBLICATION-POLICY section 2 says a copied assembly listing is
# never published. `build_mixed.sh` can consume `src/matched/<src>.s`, but that path is a
# private-side reproduction device, not a publishable artifact.
# `*.s` 保持全局禁入：PUBLICATION-POLICY §2 明确「照抄的汇编列表不可发布」。build_mixed.sh 能消费
# `src/matched/<src>.s`，但那只属私有侧复现手段，不是可发布物。
DENY = [
    "*.s", "*.o", "*.elf", "*.bin", "*.rom", "*.iso", "*.BIN", "*.irx", "*.ERX",
    "*.lzr", "*.evd", "*.AFS", "*.ADX", "*.SFD",
    "*.zip", "*.7z", "*.tar", "*.tar.xz", "*.tar.gz", "*.tar.zst", "*.zst",
    "orig/*", "assets/*", "include/*", "out/*", ".tmp/*",
    "routeb/*", "routebjp/*", "docs/private/*",
]

# Backstop for a restricted file whose name carries no telling extension. Measured 2026-10-13:
# the retail ELF is 9,352,548 B, the derived payload 9,304,936 B, and the largest legitimate
# tracked file is 5,002,527 B (`progress/*.json`, exempt below because it is published and
# hash-pinned in PUBLISHED.json).
# 「名字看不出类别」的兜底。2026-10-13 实测：原版 ELF 9,352,548 B、派生载荷 9,304,936 B，
# 最大的合法 tracked 文件 5,002,527 B（`progress/*.json`，已在 PUBLISHED.json 里锁哈希，故豁免）。
SIZE_BACKSTOP = 8 << 20
SIZE_EXEMPT = ["progress/*.json"]

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


def tracked_files(root: Path = ROOT) -> list[str] | None:
    """The tracked paths, exactly as git stores them (`-z`, no C-quoting). None when git fails.

    tracked 路径（`-z`，不做 C-quoting）；git 不可用时返回 None。
    """
    try:
        cp = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                            capture_output=True, text=True)
        if cp.returncode == 0:
            return [p for p in cp.stdout.split("\0") if p]
    except Exception:
        pass
    return None


def present_files(root: Path = ROOT) -> list[str]:
    """Tracked files when git is available, otherwise every file on disk."""
    tf = tracked_files(root)
    if tf is not None:
        return tf
    return [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]


def deny_hits(paths: list[str]) -> list[str]:
    """Pure: which of `paths` match the denied-material list. 纯函数：命中的禁材路径。"""
    hits = []
    for rel in paths:
        for pat in DENY:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, "*/" + pat):
                hits.append(f"{rel} (matches {pat})")
                break
    return hits


def oversize_hits(paths: list[str], size_of=None, root: Path = ROOT) -> list[str]:
    """Pure: which of `paths` exceed SIZE_BACKSTOP and are not exempt.

    `size_of(rel)` defaults to the real file size under `root`; a test can pass its own callable.
    纯函数：超过 SIZE_BACKSTOP 且不豁免的路径；`size_of` 可注入以便单测。
    """
    if size_of is None:
        def size_of(rel: str) -> int:
            try:
                return (root / rel).stat().st_size
            except OSError:
                return 0
    hits = []
    for rel in paths:
        if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, "*/" + pat)
               for pat in SIZE_EXEMPT):
            continue
        size = size_of(rel)
        if size > SIZE_BACKSTOP:
            hits.append(f"{rel} ({size} B > {SIZE_BACKSTOP} B)")
    return hits


def diff_name_status(base: str, root: Path = ROOT) -> list[tuple[str, ...]] | None:
    """Parse `git diff --name-status -z <base>...HEAD` into (status, path[, new_path]) tuples.

    A rename or a copy yields `(status, old, new)`; every other status yields `(status, path)`.
    None means git failed or the stream was malformed (the caller must fail closed).

    解析 `-z` 的 name-status 流：重命名/复制给 (status, 旧, 新)，其余给 (status, 路径)；
    git 失败或流畸形一律返回 None（调用方按 fail closed 处理）。
    """
    cp = subprocess.run(["git", "-C", str(root), "diff", "--name-status", "-z", f"{base}...HEAD"],
                        capture_output=True, text=True)
    if cp.returncode != 0:
        return None
    tokens = cp.stdout.split("\0")
    out: list[tuple[str, ...]] = []
    i = 0
    while i < len(tokens):
        status = tokens[i]
        if not status:
            i += 1
            continue
        if status[0] in ("R", "C"):
            if i + 2 >= len(tokens) or not tokens[i + 1] or not tokens[i + 2]:
                return None
            out.append((status, tokens[i + 1], tokens[i + 2]))
            i += 3
        else:
            if i + 1 >= len(tokens) or not tokens[i + 1]:
                return None
            out.append((status, tokens[i + 1]))
            i += 2
    return out


def check_published() -> None:
    """Publication record integrity: the report, baseline, and lock hashes must agree with the disk."""
    pub_path = ROOT / "PUBLISHED.json"
    if not pub_path.is_file():
        bad("PUBLISHED.json is missing (the publication record; tools/maintainer/publish_report.py maintains it)")
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


def check_deny(root: Path = ROOT) -> None:
    """Denied material and the size backstop over every tracked file."""
    present = present_files(root)
    hits = deny_hits(present)
    if hits:
        bad(f"the public tree contains material that the project cannot publish: {hits[:8]}")
    else:
        ok("the denied-material scan passed")
    big = oversize_hits(present, root=root)
    if big:
        bad(f"the public tree holds a file above the {SIZE_BACKSTOP} B backstop: {big[:8]}")
    else:
        ok(f"the size backstop passed (no tracked file above {SIZE_BACKSTOP} B outside {SIZE_EXEMPT})")


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

    arithmetic_ok = True
    pairs = [("matched_code", "total_code"), ("matched_functions", "total_functions")]
    for a, b in pairs:
        va, vb = as_int(m.get(a)), as_int(m.get(b))
        if va is None or vb is None:
            continue
        if va > vb:
            bad(f"the report arithmetic fails: {a}({va}) > {b}({vb})")
            arithmetic_ok = False
    if arithmetic_ok:
        ok("the report arithmetic is consistent (matched <= total)")
    if not data.get("units"):
        bad("the report has no unit (the generation probably failed)")
    return data


def check_no_regression(base_path: Path, report_path: Path) -> None:
    """The report must not fall behind the baseline. Denominators count: a smaller universe
    with an unchanged numerator inflates every percentage.

    报告不得落后于基线；**分母也参与比较**：分子不变而分母变小等于给百分比灌水。
    """
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
    for key in ("total_code", "total_functions"):
        b, c = int(bm.get(key, 0) or 0), int(cm.get(key, 0) or 0)
        if b and c and c < b:
            bad(f"denominator regression: {key} {c} < baseline {b} (the percentage would inflate)")
        elif b and c:
            ok(f"no denominator regression: {key} {c} >= {b}")
    for key in ("matched_code_percent", "matched_functions_percent"):
        b, c = float(bm.get(key, 0) or 0), float(cm.get(key, 0) or 0)
        if c + 1e-9 < b:
            bad(f"percentage regression: {key} {c:.4f} < baseline {b:.4f}")


def check_contrib(base: str, allow_restructure: bool = False, root: Path = ROOT) -> None:
    """Contribution mode (for a pull request): any path is open except the read-only paths.

    A delete, a binary file, a symbolic link, a path that is not a regular file in the working
    tree, and denied material always FAIL unless `allow_restructure` permits a delete. A rename
    or a copy needs `allow_restructure` too.

    Read-only paths = `progress/**` and `PUBLISHED.json` (published content that CI and
    the maintainers write). They stay read-only in every mode.

    贡献模式（PR 用）：除只读路径外都可以改；删除、二进制、符号链接、非普通文件路径、禁材一律 FAIL。
    `allow_restructure` 只放开重命名/复制/删除，不放开只读路径。

    只读路径 = `progress/**` 与 `PUBLISHED.json`（CI/维护者产出的发布内容）。
    """
    # The public repository is the main repository now. Every path is open except the
    # read-only paths that CI and the maintainers produce.
    # 公开仓库现在是项目主仓库：除「CI/维护者产出的只读路径」外都可以贡献。
    readonly = {
        "progress/": "the progress report comes from a verified build (tools/maintainer/publish_report.py writes it), so a manual change is not acceptable",
        "PUBLISHED.json": "tools/maintainer/publish_report.py maintains the publication record",
    }
    max_bytes = 1 << 20

    def why(rel: str) -> str | None:
        for prefix, reason in readonly.items():
            if rel == prefix or rel.startswith(prefix):
                return reason
        return None

    def problem(rel: str) -> str | None:
        """Why this path is not an acceptable contribution, or None when it is.

        该路径为什么不能作为贡献，或 None 表示可以。
        """
        reason = why(rel)
        if reason:
            return f"a read-only path cannot be changed: {rel} - {reason}"
        p = root / rel
        if p.is_symlink():
            return f"a symbolic link is not accepted: {rel}"
        if not p.is_file():
            # A C-quoted path, a submodule, a directory, or a path that git reports but the
            # working tree does not hold. Never accept it.
            # 被 C-quoting 的路径、submodule、目录、或 git 报了但工作树里没有的路径：一律不接受。
            return (f"the changed path is not a regular file in the working tree: {rel} "
                    f"(fail closed)")
        size = p.stat().st_size
        if size > max_bytes:
            return f"the file is too large (limit {max_bytes // 1024} KiB): {rel}"
        try:
            p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"not a text file: {rel} (this repository accepts text contributions only)"
        except OSError as e:
            return f"cannot read {rel}: {e}"
        return None

    changes = diff_name_status(base, root)
    if changes is None:
        bad(f"cannot get the diff against the base {base} (fail closed)")
        return

    allowed_restructure: list[str] = []
    if not changes:
        ok("this pull request has no file change")
    for rec in changes:
        status = rec[0]
        if status.startswith(("R", "C")):
            old, rel = rec[1], rec[2]
            if not allow_restructure:
                bad(f"a rename or a copy is not accepted: {old} -> {rel} (add a new file and keep the original file)")
                continue
            allowed_restructure.append(f"a rename or a copy is allowed (--allow-restructure): {old} -> {rel}")
            old_reason = why(old)
            if old_reason:
                bad(f"a read-only path cannot be changed: {old} - {old_reason}")
                continue
            reason = problem(rel)
        elif status.startswith("D"):
            rel = rec[1]
            if not allow_restructure:
                bad(f"a delete is not accepted: {rel} (this pull request may add or change files only)")
                continue
            allowed_restructure.append(f"a delete is allowed (--allow-restructure): {rel}")
            reason = why(rel)
            if reason:
                bad(f"a read-only path cannot be changed: {rel} - {reason}")
                continue
            ok(f"allowed delete: {rel}")
            continue
        elif status.startswith(("A", "M")):
            rel = rec[1]
            reason = problem(rel)
        else:
            bad(f"unknown change status {status!r} (fail closed): {rec[1] if len(rec) > 1 else '?'}")
            continue
        if reason:
            bad(reason)
        else:
            ok(f"allowed contribution: {rel}")
    for m in allowed_restructure:
        ok(m)

    check_deny(root)
    check_report(root / "progress" / "SLPS_258.19_report.json")


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
        check_deny()
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
