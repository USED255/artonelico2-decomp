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
          manifest. The maintainer runs this, pushes the archive to the companion
          repository, and commits the manifest.
  use     Check the manifest and the archive against the current checkout: the input hashes,
          the archive sha256, the retail executable, and only then extract. Any doubt means
          the tree is left alone and splat runs as before.

`use` never fails the job: every reason to distrust the archive prints a `::warning::` and
falls back to running splat. The archive is an accelerator, not an input to correctness --
CI still compares the mixed payload against the retail payload, so a wrong archive can only
fail the build, never pass it.

用法与契约
----------
  create  在干净 scratch 里跑 `splat split`、打包、写清单（维护者执行，然后把归档推到私有
          伴生仓库、把清单提交到公开仓库）。
  use     拿清单与归档对照当前检出（输入哈希、归档 sha256、原版可执行文件），全部通过才解包；
          任何存疑都原样不动，回落真 splat。

`use` 永不失败：任何不可信的理由都打 `::warning::` 并回落真 splat。归档只是加速器，不是正确性的
输入 —— CI 仍把混合载荷与零售载荷比对，坏归档只能让构建失败，不可能让它通过。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

SCHEMA = "at2-splat-snapshot/1"
MANIFEST_DEFAULT = "toolchain/splat-snapshot.json"
ARCHIVE_DEFAULT = "toolchain/splat-SLPS_258.19.tar.zst"

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

    文件集合形状摘要：每个路径 + 大小，与顺序无关。
    """
    lines = []
    for rel in sorted(rels):
        p = root / rel
        size = p.stat().st_size if p.is_file() else -1
        lines.append(f"{rel}\t{size}")
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


def pack(root: Path, rels: list[str], out: Path) -> None:
    """Write a deterministic tar.zst of the top-level entries of `rels`.

    把 `rels` 的顶层条目打成确定性 tar.zst（名字排序、mtime/owner 归零）。
    """
    tops = sorted({rel.split("/", 1)[0] for rel in rels})
    out.parent.mkdir(parents=True, exist_ok=True)
    tar_cmd = ["tar", "--directory", str(root), "--sort=name", "--mtime=@0", "--owner=0",
               "--group=0", "--numeric-owner", "--create", "--file", "-", *tops]
    zstd_cmd = ["zstd", "-3", "--check", "-T0", "-q", "-f", "-o", str(out)]
    with subprocess.Popen(tar_cmd, stdout=subprocess.PIPE) as tar_proc:
        with subprocess.Popen(zstd_cmd, stdin=tar_proc.stdout) as zstd_proc:
            tar_proc.stdout.close()
            rc_zstd = zstd_proc.wait()
            rc_tar = tar_proc.wait()
    if rc_tar != 0 or rc_zstd != 0:
        raise SystemExit("FAIL: packaging failed (tar/zstd)")


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


def lock_game(project: Path) -> dict:
    lock = json.loads((project / "toolchain.lock.json").read_text(encoding="utf-8"))
    return lock.get("game") or {}


# --------------------------------------------------------------------------- #
# create
# --------------------------------------------------------------------------- #
def cmd_create(args) -> int:
    project = Path(args.project).resolve()
    game = Path(args.game).resolve()
    splat = args.splat
    out = Path(args.out).resolve()
    manifest_path = Path(args.manifest).resolve()
    scratch = Path(args.scratch).resolve()
    target = lock_game(project).get("id") or "SLPS_258.19"

    for rel in INPUT_FILES:
        if not (project / rel).is_file():
            print(f"FAIL: the project has no {rel}", file=sys.stderr)
            return 2
    if not game.is_file():
        print(f"FAIL: no retail executable at {game}", file=sys.stderr)
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
    pack(scratch, rels, out)

    packed = sum(1 for _ in archive_members(out))
    if packed != len(rels):
        print(f"FAIL: the archive holds {packed} files but the scratch has {len(rels)}", file=sys.stderr)
        return 2
    print(f"packed {len(rels)} files -> {out} ({out.stat().st_size} B)")

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
        "inputs": {rel: sha256_file(project / rel) for rel in INPUT_FILES},
        "entry_count": len(rels),
        "tree_sha256": tree_digest(scratch, rels),
        "created_at": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                     capture_output=True, text=True).stdout.strip(),
        "generator": "tools/ci/splat_snapshot.py",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {manifest_path}")
    print(f"archive sha256 {manifest['sha256']}")
    if args.keep_scratch:
        print(f"kept the scratch directory {scratch}")
    else:
        shutil.rmtree(scratch, ignore_errors=True)
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
    return data if data.get("schema") == SCHEMA else None


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


def reason_to_skip(project: Path, manifest: dict, archive: Path | None, game: Path) -> str | None:
    """The first reason not to use the archive, or None when it matches this checkout.

    第一条「不能用这个归档」的理由；完全匹配时返回 None。
    """
    if archive is None:
        return "the manifest path escapes the companion repository"
    if not archive.is_file():
        return f"the companion repository has no {manifest.get('path')}"
    if sha256_file(archive) != manifest.get("sha256"):
        return "the archive sha256 does not match the manifest"
    for rel, want in (manifest.get("inputs") or {}).items():
        p = project / rel
        if not p.is_file():
            return f"the checkout has no {rel}"
        if sha256_file(p) != want:
            return f"{rel} changed since the archive was made"
    if not game.is_file():
        return f"no retail executable at {game}"
    if sha1_file(game) != manifest.get("game_sha1"):
        return "the retail executable is not the one the archive was made from"
    return None


def extract(project: Path, archive: Path) -> tuple[list[str], int]:
    """Extract into the project root. Returns (member paths, how many already existed).

    解包到项目根，返回（成员路径，其中原本已存在的个数）。
    """
    members: list[str] = []
    existed = 0
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
                    members.append(rel)
                    if (project / rel).exists():
                        existed += 1
                tf.extract(member, path=str(project), filter="data")
    return members, existed


def cmd_use(args) -> int:
    project = Path(args.project).resolve()
    orig = Path(args.orig).resolve()
    manifest_path = Path(args.manifest).resolve()
    game = Path(args.game).resolve() if args.game else orig / "orig" / "SLPS_258.19"

    def verdict(value: str, reason: str) -> int:
        level = "notice" if value == "snapshot" else "warning"
        print(f"::{level}::splat snapshot: {value} — {reason}")
        if args.github_output:
            with Path(args.github_output).open("a", encoding="utf-8") as fh:
                fh.write(f"verdict={value}\n")
        print(value)
        return 0

    manifest = load_manifest(manifest_path)
    if manifest is None:
        return verdict("splat", f"no usable manifest at {manifest_path}")
    archive = resolve_archive(orig, str(manifest.get("path") or ""))
    skip = reason_to_skip(project, manifest, archive, game)
    if skip:
        return verdict("splat", skip)
    if not args.extract:
        return verdict("snapshot", "the archive matches this checkout (check only)")

    try:
        members, existed = extract(project, archive)
    except SystemExit as exc:
        return verdict("splat", str(exc))
    except FileNotFoundError as exc:
        return verdict("splat", f"cannot run the extractor: {exc}")

    if existed:
        print(f"::warning::the extraction overwrote {existed} existing files")

    def undo() -> None:
        for rel in members:
            try:
                (project / rel).unlink()
            except OSError:
                pass

    want_count = int(manifest.get("entry_count") or -1)
    if len(members) != want_count:
        undo()
        return verdict("splat", f"the archive holds {len(members)} files, the manifest says {want_count}")
    if tree_digest(project, members) != manifest.get("tree_sha256"):
        undo()
        return verdict("splat", "the extracted tree does not match the manifest")
    return verdict("snapshot", f"{len(members)} files extracted")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="splat_snapshot.py",
        description="Package the splat split output into a private archive, and restore it in CI.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Run splat in a clean scratch directory and pack its output")
    c.add_argument("--project", default=".", help="Project root (default: .)")
    c.add_argument("--game", required=True, help="Retail executable (SLPS_258.19)")
    c.add_argument("--splat", required=True, help="The pinned splat binary (for example .tmp/splatvenv/bin/splat)")
    c.add_argument("--out", default=ARCHIVE_DEFAULT, help=f"Archive to write (default: {ARCHIVE_DEFAULT})")
    c.add_argument("--manifest", default=MANIFEST_DEFAULT, help=f"Manifest to write (default: {MANIFEST_DEFAULT})")
    c.add_argument("--remote-path", default=ARCHIVE_DEFAULT,
                   help="Path of the archive inside the private companion repository")
    c.add_argument("--scratch", default=".tmp/splat-snapshot", help="Scratch directory (default: .tmp/splat-snapshot)")
    c.add_argument("--keep-scratch", action="store_true", help="Keep the scratch directory")
    c.add_argument("--allow-low-memory", action="store_true",
                   help="Run even when this machine has little free memory (it may swap or freeze)")
    c.set_defaults(func=cmd_create)

    u = sub.add_parser("use", help="Check the manifest and, when it matches, extract the archive")
    u.add_argument("--project", default=".", help="Project root (default: .)")
    u.add_argument("--orig", required=True, help="The private companion checkout (CI uses .orig)")
    u.add_argument("--manifest", default=MANIFEST_DEFAULT, help=f"Manifest to read (default: {MANIFEST_DEFAULT})")
    u.add_argument("--game", default=None, help="Retail executable (default: <orig>/orig/SLPS_258.19)")
    u.add_argument("--extract", action="store_true", help="Extract the archive when it matches")
    u.add_argument("--github-output", default=None, help="Append verdict=<snapshot|splat> to this file")
    u.set_defaults(func=cmd_use)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
