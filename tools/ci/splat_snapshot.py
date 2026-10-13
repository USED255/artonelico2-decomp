#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package and reuse the `splat split` output, so CI does not have to run splat again.

`splat split` is the most expensive step of the build (about 150 s of the 400 s `make build`),
it is single-threaded, and its output is a pure function of the retail executable and a few
inputs that rarely change. This tool packs that output into one `.tar.zst` and lets CI restore
it byte for byte.

The archive lives in the **private companion repository** (the same checkout that already
carries the retail executable and the Sony toolchain) and never in the public repository: the
`asm/` tree is material this project cannot publish. Only the small manifest -- hashes,
counts, no content -- is committed to the public repository.

Contract
--------
  create  Run `splat split` in a clean scratch directory, pack its output, and write the
          manifest. With `--with-asm` it also assembles the baseline (in a copy of the
          scratch, using the repository's own `build.sh`) and packs the objects as a second
          group. The maintainer runs this, pushes the archive to the companion repository,
          and commits the manifest.
  use     Check the manifest and the archive against the current checkout: the input
          hashes, the archive sha256, the retail executable, and only then extract. Any
          doubt means the tree is left alone and splat runs as before.

The archive holds two groups, split by path prefix: `build/asm/**` are the assembled
objects, and everything else is the raw `splat split` output. The object group is only used
when the splat group is usable too, and any change to `build.sh` (the assembly recipe)
drops the object group while keeping the splat group, so CI re-runs the new recipe.

`use` never fails the job: every reason to distrust a group prints a `::warning::` and
falls back for that group. The archive is an accelerator, not an input to correctness --
CI still compares the mixed payload against the retail payload, so a wrong archive can only
fail the build, never pass it.

用法与契约
----------
  create  在干净 scratch 里跑 `splat split`、打包、写清单；加 `--with-asm` 时还会在 scratch 的
          副本里用仓库自带的 `build.sh` 汇编一遍，把对象作为第二组打进同一个归档。维护者执行，
          然后把归档推到私有伴生仓库、把清单提交到公开仓库。
  use     拿清单与归档对照当前检出（输入哈希、归档 sha256、原版可执行文件），全部通过才解包；
          任何存疑都原样不动，回落真 splat。

归档按路径前缀分两组：`build/asm/**` 是汇编产物，其余是 `splat split` 的原始输出。只有 splat 组
可用时对象组才会被使用；`build.sh`（汇编配方）一变，对象组作废、splat 组保留 ⇒ CI 会用新配方重跑。

`use` 永不失败：任何不可信的理由都打 `::warning::` 并对该组回落。归档只是加速器，不是正确性的
输入 —— CI 仍把混合载荷与零售载荷比对，坏归档只能让构建失败，不可能让它通过。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

SCHEMA = "at2-splat-snapshot/2"
SCHEMA_V1 = "at2-splat-snapshot/1"
MANIFEST_DEFAULT = "toolchain/splat-snapshot.json"
ARCHIVE_DEFAULT = "toolchain/splat-SLPS_258.19.tar.zst"

# The archive holds two groups, split by path prefix: `build/asm/**` (the assembled objects,
# which the build may reuse) and everything else (the raw `splat split` output). Members under
# this prefix belong to the object group.
# 归档分两组，按路径前缀切分：`build/asm/**`（汇编产物，构建可复用）与其余（`splat split` 的原始
# 输出）。这个前缀下的成员属于对象组。
GROUP_SPLAT = "splat"
GROUP_ASM = "asm"
ASM_PREFIX = "build/asm/"
ASM_INPUT = "build.sh"

# `splat split` on this target peaks at about 1.3 GB of resident memory and takes about 150 s
# on a 4 vCPU runner. On a small workstation it swaps instead and can take the machine down
# (2026-10-12: 20 minutes and then a hard freeze on a 4 core / 3.8 GiB box). `create` therefore
# refuses to run without headroom: pack on a GitHub runner with
# .github/workflows/splat-snapshot.yml.
# 本目标的 `splat split` 峰值常驻内存约 1.3 GB，4 vCPU runner 上约 150 s；小机器上会改成换页，
# 甚至把机器拖死（2026-10-12 在 4 核 / 3.8 GiB 上发生：20 分钟未结束，随后死机）。因此 `create`
# 在没有余量时拒绝运行：请用 .github/workflows/splat-snapshot.yml 在 runner 上打包。
MIN_AVAILABLE_KB = 4 * 1024 * 1024


def available_memory_kb() -> int | None:
    """MemAvailable from /proc/meminfo, or None when it is not readable.

    /proc/meminfo 的 MemAvailable；读不到时返回 None。
    """
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None

# The files `splat split` reads. A change to any of them makes the archive stale, and the
# tool falls back to running splat. `create` writes this set into the manifest and `use`
# re-reads the set from the manifest, so the two commands cannot drift apart.
# splat split 读的输入文件。任何一个变了归档就过期 → 回落真 splat。`create` 把这组写进清单，
# `use` 从清单读同一组，避免两个子命令各写一份而漂移。
INPUT_FILES = (
    "splat.yaml",
    "config/symbol_addrs.txt",
    "config/reloc_addrs.txt",
    "tools/ci/splat-requirements.txt",
)

# The inputs of the object group: the assembly recipe (flags and the alignment repair). The
# assembler itself is pinned by toolchain.lock.json, which CI verifies on every run. A change
# to build.sh drops the object group but keeps the splat group, so CI re-runs the new recipe.
# 对象组的输入：汇编配方（标志与对齐修复）。汇编器本身由 toolchain.lock.json 钉住，CI 每次核验。
# build.sh 一变就作废对象组、保留 splat 组 ⇒ CI 会用新配方重跑一遍。
ASM_INPUT_FILES = (ASM_INPUT,)

# What the scratch directory holds on purpose. Everything else under it is splat output.
# scratch 目录里「有意放进去」的东西；其余文件都是 splat 的产物。
SCRATCH_INPUTS = ("splat.yaml", "SLPS_258.19.rom", "config")
ROM_NAME = "SLPS_258.19.rom"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path, rels) -> str:
    """A digest of the shape of a file set: every path and its size, order independent.

    Shape only. `content_digest` covers the bytes: a same-size, different-content member used to
    pass the group check (R30 finding B8).

    文件集合**形状**摘要：每个路径 + 大小，与顺序无关。只管形状；字节由 `content_digest` 覆盖 ——
    同大小不同内容的成员此前能通过组校验（R30 B8）。
    """
    lines = []
    for rel in sorted(rels):
        p = root / rel
        size = p.stat().st_size if p.is_file() else -1
        lines.append(f"{rel}\t{size}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def content_digest(root: Path, rels) -> str:
    """A digest of the content of a file set: every path and its sha256, order independent.

    文件集合**内容**摘要：每个路径 + 其 sha256，与顺序无关。
    """
    lines = []
    for rel in sorted(rels):
        p = root / rel
        lines.append(f"{rel}\t{sha256_file(p) if p.is_file() else '-'}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def list_outputs(root: Path) -> list[str]:
    """Every file under `root` that `splat split` produced, as relative POSIX paths.

    scratch 里 splat 产出的全部文件（相对路径）。
    """
    rels = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(rel == skip or rel.startswith(skip + "/") for skip in SCRATCH_INPUTS):
            continue
        if "__pycache__" in rel.split("/"):
            continue
        rels.append(rel)
    return rels


def group_of(rel: str) -> str:
    """The group a project-relative path belongs to. 项目相对路径属于哪一组。"""
    return GROUP_ASM if rel.startswith(ASM_PREFIX) else GROUP_SPLAT


def list_asm_objects(root: Path) -> list[str]:
    """The assembled objects under `root/build/asm`, as project-relative paths.

    `root/build/asm` 下的汇编产物（项目相对路径）。只取 `*.o`：旁边的 `.err` 是空诊断文件。
    """
    base = root / "build" / "asm"
    return [p.relative_to(root).as_posix() for p in sorted(base.rglob("*.o")) if p.is_file()]


def assemble_objects(project: Path, scratch: Path, as_path: Path, expected: int) -> tuple[Path, list[str]]:
    """Assemble in a copy of the splat scratch, using the repository's own `build.sh`.

    Returns the staging directory and the objects. Raises SystemExit when the assembly fails or
    when the object count does not match `expected` (the number of `.s` files).

    在 splat scratch 的副本里用**仓库自带的** `build.sh` 汇编，返回（staging 目录, 对象列表）。
    汇编失败、或对象数与 `expected`（`.s` 个数）不符时抛 SystemExit。
    """
    staging = scratch.with_name(scratch.name + "-asm")
    shutil.rmtree(staging, ignore_errors=True)
    # `build.sh` repairs `include/macro.inc` and `asm/**` in place, and the archive must keep the
    # raw splat output in its splat group, so the assembly runs in a copy. `build.sh` cds into its
    # own directory, hence the copy of the script into the staging directory.
    # `build.sh` 会就地把 include/macro.inc 与 asm/** 修好，而归档的 splat 组必须保留原始输出，
    # 所以在副本里汇编。`build.sh` 会 cd 到脚本自身所在目录，因此要把脚本复制进 staging。
    shutil.copytree(scratch, staging, ignore=shutil.ignore_patterns(ROM_NAME))
    shutil.copy2(project / ASM_INPUT, staging / ASM_INPUT)
    print(f"assembling in {staging} with {as_path} ...")
    env = dict(os.environ, BASELINE_ASSEMBLE_ONLY="1", BINUTILS=str(as_path.parent))
    if subprocess.run(["bash", ASM_INPUT], cwd=str(staging), env=env).returncode != 0:
        raise SystemExit("the assembly failed (see the build.sh log above)")
    rels = list_asm_objects(staging)
    if len(rels) != expected:
        raise SystemExit(f"assembled {len(rels)} objects but the scratch holds {expected} sources")
    return staging, rels


def pack_multi(roots: list[tuple[Path, list[str]]], out: Path) -> None:
    """Write one deterministic tar.zst from several (directory, top-level entries) roots.

    The assembler writes a `.err` next to every object; they are diagnostics (empty on
    success) and never belong in the archive, so the selector excludes them.
    从多个（目录, 顶层条目）根打出一个确定性 tar.zst；成员名保持项目相对布局。汇编器会在每个对象
    旁边写一个 `.err`（成功时为空）——那只是诊断，从不进归档，因此打包时排除。
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    tar_cmd = ["tar", "--sort=name", "--mtime=@0", "--owner=0", "--group=0", "--numeric-owner",
               "--exclude=*.err", "--create", "--file", "-"]
    for root, tops in roots:
        tar_cmd += ["--directory", str(root), *tops]
    zstd_cmd = ["zstd", "-3", "--check", "-T0", "-q", "-f", "-o", str(out)]
    with subprocess.Popen(tar_cmd, stdout=subprocess.PIPE) as tar_proc:
        with subprocess.Popen(zstd_cmd, stdin=tar_proc.stdout) as zstd_proc:
            tar_proc.stdout.close()
            rc_zstd = zstd_proc.wait()
            rc_tar = tar_proc.wait()
    if rc_tar != 0 or rc_zstd != 0:
        raise SystemExit("FAIL: packaging failed (tar/zstd)")


def pack(root: Path, rels: list[str], out: Path) -> None:
    """One root: the top-level entries of `rels`. 单根打包（`rels` 的顶层条目）。"""
    pack_multi([(root, sorted({rel.split("/", 1)[0] for rel in rels}))], out)


def archive_members(archive: Path):
    """Yield the file members of an archive. Raises on an unsafe member.

    逐个产出归档里的文件成员；遇到不安全成员直接抛错。
    """
    with subprocess.Popen(["zstd", "-dc", str(archive)], stdout=subprocess.PIPE) as proc:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
            for member in tf:
                name = member.name
                if name.startswith(("/", "\\")) or ".." in Path(name).parts:
                    raise SystemExit(f"the archive holds an unsafe path: {name}")
                if not (member.isfile() or member.isdir()):
                    raise SystemExit(f"the archive holds a non-regular member: {name}")
                if member.isfile():
                    yield member


def pinned_splat_version(project: Path) -> str | None:
    """The `splat64==` pin from tools/ci/splat-requirements.txt, if it is there.

    从 tools/ci/splat-requirements.txt 读 `splat64==` 钉版。
    """
    req = project / "tools" / "ci" / "splat-requirements.txt"
    if not req.is_file():
        return None
    for line in req.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^splat64==(\S+)", line.strip())
        if m:
            return m.group(1)
    return None


def splat_version(splat: str) -> str:
    cp = subprocess.run([splat, "--version"], capture_output=True, text=True)
    text = (cp.stdout or cp.stderr).strip().splitlines()
    if not text:
        return ""
    m = re.search(r"(\d+\.\d+\.\d+\S*)", text[0])
    return m.group(1) if m else text[0]


def as_version(assembler: Path) -> str:
    """The assembler's version banner, for the record. 汇编器版本横幅，只作追溯记录。"""
    try:
        cp = subprocess.run([str(assembler), "--version"], capture_output=True, text=True)
    except OSError:
        return ""
    lines = (cp.stdout or cp.stderr).strip().splitlines()
    return lines[0] if lines else ""


def lock_game(project: Path) -> dict:
    lock = json.loads((project / "toolchain.lock.json").read_text(encoding="utf-8"))
    return lock.get("game") or {}


# --------------------------------------------------------------------------- #
# create
# --------------------------------------------------------------------------- #
def project_path(project: Path, value: str) -> Path:
    """Resolve a command-line path against the project root when it is relative.

    命令行里给的相对路径按项目根解析（默认值与用户输入都适用）。
    """
    p = Path(value)
    return (project / p if not p.is_absolute() else p).resolve()


def guarded_scratch(project: Path, value: str) -> Path:
    """Resolve `--scratch` and refuse anything that is not a child directory of the project.

    `create` starts with `shutil.rmtree(scratch)`, and `--scratch .` would therefore delete the
    repository; `--scratch ..` would delete the parent directory (R30 finding B7).

    `create` 第一件事就是 `shutil.rmtree(scratch)`：`--scratch .` 会删掉整个仓库，`--scratch ..`
    会删掉父目录（R30 B7）。
    """
    p = project_path(project, value)
    if p == project or project not in p.parents:
        raise SystemExit(f"--scratch must be a directory inside {project} (got {p})")
    if p == Path("/") or p == Path.home().resolve():
        raise SystemExit(f"--scratch must not be {p}")
    return p


def cmd_create(args) -> int:
    project = Path(args.project).resolve()
    game = project_path(project, args.game)
    splat = args.splat
    out = project_path(project, args.out)
    manifest_path = project_path(project, args.manifest)
    try:
        scratch = guarded_scratch(project, args.scratch)
    except SystemExit as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    target = lock_game(project).get("id") or "SLPS_258.19"

    for rel in INPUT_FILES:
        if not (project / rel).is_file():
            print(f"FAIL: the project has no {rel}", file=sys.stderr)
            return 2
    if not game.is_file():
        print(f"FAIL: no retail executable at {game}", file=sys.stderr)
        return 2

    # Validate the object-group arguments before any heavy work: a missing assembler must fail
    # immediately, not after 150 s of splat.
    # 在干重活之前先校验对象组参数：汇编器缺失要立刻失败，而不是等 splat 跑完 150 s。
    as_path = Path(args.as_path).resolve() if args.as_path else None
    if args.with_asm and (as_path is None or not as_path.is_file() or not os.access(as_path, os.X_OK)):
        print("FAIL: --with-asm needs --as pointing at an executable assembler "
              "(the toolchain's mips-ps2-decompals-as)", file=sys.stderr)
        return 2

    # Refuse to start splat without headroom: on a small machine it swaps for many minutes and
    # can take the whole box down. See MIN_AVAILABLE_KB.
    # 没有余量就不启动 splat：小机器上它会换页几十分钟，甚至把整台机器拖死（见 MIN_AVAILABLE_KB）。
    avail = available_memory_kb()
    if not args.allow_low_memory and avail is not None and avail < MIN_AVAILABLE_KB:
        print(f"FAIL: only {avail / 1024 / 1024:.1f} GiB of memory is available and splat needs about "
              f"1.3 GiB of resident memory plus room to work. Run the pack on a GitHub runner with "
              f".github/workflows/splat-snapshot.yml, or pass --allow-low-memory if you accept that "
              f"this machine may swap or freeze.", file=sys.stderr)
        return 2

    pin = pinned_splat_version(project)
    have = splat_version(splat)
    if pin and have and pin != have:
        print(f"FAIL: splat is {have} but tools/ci/splat-requirements.txt pins {pin}; "
              f"use the pinned version or the archive will not match CI.", file=sys.stderr)
        return 2
    print(f"splat {have or '?'} (pinned {pin or '?'})")

    shutil.rmtree(scratch, ignore_errors=True)
    (scratch / "config").mkdir(parents=True)
    (scratch / "build").mkdir()
    for rel in ("splat.yaml", "config/symbol_addrs.txt", "config/reloc_addrs.txt"):
        shutil.copy2(project / rel, scratch / rel)

    # The ROM is the split input, and its sha1 pins which payload we split.
    # ROM 是拆分输入，它的 sha1 钉住「拆的是哪一份载荷」。
    cp = subprocess.run([sys.executable, str(project / "tools" / "project" / "extract_payload.py"),
                         str(game), ROM_NAME], cwd=str(scratch), capture_output=True, text=True)
    if cp.returncode != 0:
        print(cp.stdout, cp.stderr, file=sys.stderr)
        print("FAIL: extract_payload.py failed", file=sys.stderr)
        return 2
    rom_sha1 = sha1_file(scratch / ROM_NAME)
    want_payload = lock_game(project).get("payload_sha1")
    if want_payload and rom_sha1 != want_payload:
        print(f"FAIL: the derived payload is {rom_sha1} but toolchain.lock.json expects {want_payload}",
              file=sys.stderr)
        return 2
    print(f"retail payload sha1 {rom_sha1}")

    print("running splat split ...")
    if subprocess.run([splat, "split", "splat.yaml"], cwd=str(scratch)).returncode != 0:
        print("FAIL: splat split failed", file=sys.stderr)
        return 2

    rels = list_outputs(scratch)
    if not rels:
        print("FAIL: splat produced no output", file=sys.stderr)
        return 2
    # The group split is by path prefix, so `splat split` must not write into build/asm/.
    # 分组按路径前缀切分，因此 splat 不得往 build/asm/ 里写东西。
    stray = [rel for rel in rels if group_of(rel) == GROUP_ASM]
    if stray:
        print(f"FAIL: splat wrote into {ASM_PREFIX}: {stray[:3]} (the group split would be wrong)",
              file=sys.stderr)
        return 2

    single_inputs = {rel: sha256_file(project / rel) for rel in INPUT_FILES}
    groups = {
        GROUP_SPLAT: {
            "inputs": single_inputs,
            "entry_count": len(rels),
            "tree_sha256": tree_digest(scratch, rels),
            "content_sha256": content_digest(scratch, rels),
        }
    }
    roots: list[tuple[Path, list[str]]] = [(scratch, sorted({rel.split("/", 1)[0] for rel in rels}))]
    asm_count = 0

    if args.with_asm:
        # `as_path` was validated above.
        expected = sum(1 for rel in rels if rel.endswith(".s"))
        try:
            staging, asm_rels = assemble_objects(project, scratch, as_path, expected)
        except SystemExit as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 2
        groups[GROUP_ASM] = {
            "inputs": {rel: sha256_file(project / rel) for rel in ASM_INPUT_FILES},
            "as_version": as_version(as_path),
            "entry_count": len(asm_rels),
            "tree_sha256": tree_digest(staging, asm_rels),
            "content_sha256": content_digest(staging, asm_rels),
        }
        roots.append((staging, ["build/asm"]))
        asm_count = len(asm_rels)

    pack_multi(roots, out)

    packed = sum(1 for _ in archive_members(out))
    if packed != len(rels) + asm_count:
        print(f"FAIL: the archive holds {packed} files but the groups have {len(rels) + asm_count}",
              file=sys.stderr)
        return 2
    print(f"packed {len(rels)} splat files + {asm_count} objects -> {out} ({out.stat().st_size} B)")

    elf_sha1 = sha1_file(game)
    want_elf = lock_game(project).get("elf_sha1")
    if want_elf and elf_sha1 != want_elf:
        print(f"WARNING: the retail executable is {elf_sha1} but toolchain.lock.json expects {want_elf}",
              file=sys.stderr)

    manifest = {
        "schema": SCHEMA,
        "target": target,
        "path": str(args.remote_path),
        "sha256": sha256_file(out),
        "game_sha1": elf_sha1,
        "splat_version": have,
        "groups": groups,
        "created_at": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                     capture_output=True, text=True).stdout.strip(),
        "generator": "tools/ci/splat_snapshot.py",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {manifest_path}")
    print(f"archive sha256 {manifest['sha256']}")
    staging = scratch.with_name(scratch.name + "-asm")
    if args.keep_scratch:
        print(f"kept the scratch directories {scratch} and {staging}")
    else:
        shutil.rmtree(scratch, ignore_errors=True)
        shutil.rmtree(staging, ignore_errors=True)
    return 0


# --------------------------------------------------------------------------- #
# use
# --------------------------------------------------------------------------- #
def load_manifest(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if data.get("schema") in (SCHEMA, SCHEMA_V1) else None


def groups_of(manifest: dict) -> dict:
    """The groups of a manifest, adapting a v1 manifest to the single-group shape.

    清单的分组；v1 清单会被适配成「只有 splat 组」的形态（向后兼容）。
    """
    if manifest.get("schema") == SCHEMA_V1:
        return {
            GROUP_SPLAT: {
                "inputs": manifest.get("inputs") or {},
                "entry_count": manifest.get("entry_count"),
                "tree_sha256": manifest.get("tree_sha256"),
            }
        }
    return manifest.get("groups") or {}


def group_input_reason(project: Path, group: dict) -> str | None:
    """The first input of a group that does not match this checkout, or None.

    该组第一条对不上当前检出的输入；全部命中时返回 None。
    """
    for rel, want in (group.get("inputs") or {}).items():
        p = project / rel
        if not p.is_file():
            return f"the checkout has no {rel}"
        if sha256_file(p) != want:
            return f"{rel} changed since the archive was made"
    return None


def resolve_archive(orig: Path, remote_path: str) -> Path | None:
    """Resolve the manifest's path inside the companion checkout. Refuses anything that escapes.

    把清单里的路径解析到伴生仓库检出内；任何越界一律拒绝。
    """
    if not remote_path or remote_path.startswith(("/", "\\")):
        return None
    if any(part == ".." for part in Path(remote_path).parts):
        return None
    base = orig.resolve()
    candidate = (base / remote_path).resolve()
    if candidate != base and base not in candidate.parents:
        return None
    return candidate


def archive_reason(manifest: dict, archive: Path | None, game: Path) -> str | None:
    """The first reason not to use the archive at all, or None.

    第一条「整档不能用」的理由（与分组无关：路径、存在性、整档 sha256、原版可执行文件）。
    """
    if archive is None:
        return "the manifest path escapes the companion repository"
    if not archive.is_file():
        return f"the companion repository has no {manifest.get('path')}"
    if sha256_file(archive) != manifest.get("sha256"):
        return "the archive sha256 does not match the manifest"
    if not game.is_file():
        return f"no retail executable at {game}"
    if sha1_file(game) != manifest.get("game_sha1"):
        return "the retail executable is not the one the archive was made from"
    return None


def extract(project: Path, archive: Path, allow: set[str]) -> tuple[list[str], int, Path]:
    """Extract the allowed members into a staging directory. Nothing touches the project yet.

    Returns `(member paths, count of members that already exist in the project, staging dir)`.
    The caller verifies each group against the manifest and only then moves the kept files into
    place. The previous version wrote into the project first and deleted on a mismatch, so a bad
    archive had already overwritten (and could then delete) tracked files (R30 finding B3).

    把 `allow` 里的成员解到**暂存目录**，此时不碰项目树。返回（成员路径, 项目中已存在的个数, 暂存目录）。
    调用方逐组对照清单校验，通过后才把保留的文件搬到位。旧实现先写进项目、校验失败再删，于是坏归档
    已经覆盖过（随后还可能删掉）tracked 文件（R30 B3）。
    """
    stage_parent = project / ".tmp"
    stage_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(dir=str(stage_parent), prefix="splat-snapshot-stage-"))
    members: list[str] = []
    existed = 0
    try:
        with subprocess.Popen(["zstd", "-dc", str(archive)], stdout=subprocess.PIPE) as proc:
            with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
                for member in tf:
                    name = member.name
                    if name.startswith(("/", "\\")) or ".." in Path(name).parts:
                        raise SystemExit(f"the archive holds an unsafe path: {name}")
                    if not (member.isfile() or member.isdir()):
                        raise SystemExit(f"the archive holds a non-regular member: {name}")
                    if member.isfile():
                        rel = Path(name).as_posix()
                        if group_of(rel) not in allow:
                            continue          # leave this group alone  这一组不动
                        members.append(rel)
                        if (project / rel).exists():
                            existed += 1
                    tf.extract(member, path=str(staging), filter="data")
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return members, existed, staging


def cmd_use(args) -> int:
    project = Path(args.project).resolve()
    orig = Path(args.orig).resolve()
    # The manifest default is project-relative: `--project <dir>` must find
    # `<dir>/toolchain/splat-snapshot.json`, not a file next to the current directory.
    # 清单默认相对**项目根**：`--project <dir>` 要找到 `<dir>/toolchain/splat-snapshot.json`。
    manifest_path = project_path(project, args.manifest)
    game = project_path(project, args.game) if args.game else orig / "orig" / "SLPS_258.19"
    active: list[str] = []

    def verdict(value: str, reason: str, groups: list[str] | None = None) -> int:
        level = "notice" if value == "snapshot" else "warning"
        used = groups if groups is not None else active
        print(f"::{level}::splat snapshot: {value} — {reason}")
        if args.github_output:
            with Path(args.github_output).open("a", encoding="utf-8") as fh:
                fh.write(f"verdict={value}\n")
                fh.write("groups=" + ",".join(used) + "\n")
        print(value)
        return 0

    manifest = load_manifest(manifest_path)
    if manifest is None:
        return verdict("splat", f"no usable manifest at {manifest_path}", [])
    groups = groups_of(manifest)
    archive = resolve_archive(orig, str(manifest.get("path") or ""))
    reason = archive_reason(manifest, archive, game)
    if reason:
        return verdict("splat", reason, [])

    # Per group, in dependency order: the objects are only useful when the splat group (the
    # assembly tree they were built from) is usable too.
    # 按依赖顺序逐组判定：只有 splat 组（对象所基于的汇编树）可用时，对象组才有意义。
    wanted: list[str] = []
    first_reason = ""
    for name in (GROUP_SPLAT, GROUP_ASM):
        group = groups.get(name)
        if not group:
            continue
        if name == GROUP_ASM and GROUP_SPLAT not in wanted:
            first_reason = first_reason or "the splat group is not usable"
            continue
        bad = group_input_reason(project, group)
        if bad:
            first_reason = first_reason or f"{name}: {bad}"
            print(f"::notice::splat snapshot: the {name} group does not match this checkout ({bad})")
            continue
        wanted.append(name)

    if not wanted:
        return verdict("splat", first_reason or "no usable group in the manifest", [])
    if not args.extract:
        return verdict("snapshot", "the archive matches this checkout (check only)", wanted)

    try:
        members, existed, staging = extract(project, archive, set(wanted))
    except SystemExit as exc:
        return verdict("splat", str(exc), [])
    except FileNotFoundError as exc:
        return verdict("splat", f"cannot run the extractor: {exc}", [])

    if existed:
        print(f"::warning::the extraction will overwrite {existed} existing files")

    # Verify each group against its count and digests IN THE STAGING DIRECTORY. A group that
    # fails is dropped there; the project tree is only touched afterwards, and only for the kept
    # groups. A bad archive therefore cannot overwrite or delete anything (R30 finding B3), and a
    # same-size different-content member is caught by the content digest (R30 finding B8).
    # 在**暂存目录**里逐组核对计数与摘要：失败的组就此丢弃，项目树只在校验之后、且只为保留的组
    # 发生改动 ⇒ 坏归档无法覆盖或删除任何东西（R30 B3）；同大小不同内容的成员由内容摘要抓住（R30 B8）。
    dropped: list[str] = []
    try:
        for name in wanted:
            rels = [rel for rel in members if group_of(rel) == name]
            group = groups[name]
            want_count = int(group.get("entry_count") or -1)
            if len(rels) != want_count:
                dropped.append(name)
                print(f"::warning::splat snapshot: the {name} group holds {len(rels)} files, "
                      f"the manifest says {want_count}")
                continue
            want_content = group.get("content_sha256")
            if want_content and content_digest(staging, rels) != want_content:
                dropped.append(name)
                print(f"::warning::splat snapshot: the {name} group content does not match the manifest")
                continue
            if tree_digest(staging, rels) != group.get("tree_sha256"):
                dropped.append(name)
                print(f"::warning::splat snapshot: the extracted {name} group does not match the manifest")

        kept = [name for name in wanted if name not in dropped]
        if GROUP_SPLAT in dropped or not kept:
            return verdict("splat", "the extraction did not match the manifest", [])

        moved = 0
        for name in kept:
            for rel in [m for m in members if group_of(m) == name]:
                src = staging / rel
                dst = project / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                os.replace(src, dst)
                moved += 1
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    detail = f"{moved} files extracted ({','.join(kept)})"
    return verdict("snapshot", detail, kept)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="splat_snapshot.py",
        description="Package the splat split output into a private archive, and restore it in CI.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Run splat in a clean scratch directory and pack its output")
    c.add_argument("--project", default=".", help="Project root (default: .)")
    c.add_argument("--game", required=True, help="Retail executable (SLPS_258.19)")
    c.add_argument("--splat", required=True, help="The pinned splat binary (for example .tmp/splatvenv/bin/splat)")
    c.add_argument("--out", default=ARCHIVE_DEFAULT, help=f"Archive to write, relative to --project (default: {ARCHIVE_DEFAULT})")
    c.add_argument("--manifest", default=MANIFEST_DEFAULT, help=f"Manifest to write, relative to --project (default: {MANIFEST_DEFAULT})")
    c.add_argument("--remote-path", default=ARCHIVE_DEFAULT,
                   help="Path of the archive inside the private companion repository")
    c.add_argument("--scratch", default=".tmp/splat-snapshot", help="Scratch directory, relative to --project (default: .tmp/splat-snapshot)")
    c.add_argument("--keep-scratch", action="store_true", help="Keep the scratch directory")
    c.add_argument("--with-asm", action="store_true",
                   help="Also assemble the baseline in a copy of the scratch and pack the objects "
                        "as the `asm` group (needs --as)")
    c.add_argument("--as", dest="as_path", default=None,
                   help="The toolchain assembler (mips-ps2-decompals-as); required with --with-asm")
    c.add_argument("--allow-low-memory", action="store_true",
                   help="Run even when this machine has little free memory (it may swap or freeze)")
    c.set_defaults(func=cmd_create)

    u = sub.add_parser("use", help="Check the manifest and, when it matches, extract the archive")
    u.add_argument("--project", default=".", help="Project root (default: .)")
    u.add_argument("--orig", required=True, help="The private companion checkout (CI uses .orig)")
    u.add_argument("--manifest", default=MANIFEST_DEFAULT, help=f"Manifest to read, relative to --project (default: {MANIFEST_DEFAULT})")
    u.add_argument("--game", default=None, help="Retail executable (default: <orig>/orig/SLPS_258.19)")
    u.add_argument("--extract", action="store_true", help="Extract the archive when it matches")
    u.add_argument("--github-output", default=None, help="Append verdict=<snapshot|splat> to this file")
    u.set_defaults(func=cmd_use)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
