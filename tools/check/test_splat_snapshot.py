#!/usr/bin/env python3
"""Tests for tools/ci/splat_snapshot.py. No toolchain, no splat, and no build are necessary.

The snapshot is an accelerator: every path that distrusts the archive must fall back to
running splat, and a matching archive must restore exactly the packaged tree. The tests
build a synthetic tree, pack it, and drive the `use` code path through each decision.

Usage: python3 tools/check/test_splat_snapshot.py

splat_snapshot.py 的测试（不需要工具链、splat 或构建）。归档只是加速器：任何不信任它的分支都必须
回落真 splat，匹配时必须逐字还原打包的树。测试用合成树打包，再把 `use` 的每条判定跑一遍。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "ci"))
import splat_snapshot as ss  # noqa: E402

fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  — ' + detail}")
    if not cond:
        fails.append(name)


WORK = ROOT / ".tmp" / "splat_snapshot_test"
shutil.rmtree(WORK, ignore_errors=True)
SCRATCH = WORK / "scratch"
PROJECT = WORK / "project"
ORIG = WORK / "orig"

# --- a synthetic splat output tree (the inputs must stay out of the archive) -------------
for rel, text in (
    ("splat.yaml", "options:\n  basename: SLPS_258.19\n"),
    ("config/symbol_addrs.txt", "func_00100000 0x100000\n"),
    ("SLPS_258.19.rom", "retail payload bytes\n"),
    ("asm/cod/func_00100000.s", ".text\nglabel_func_00100000:\n  nop\n"),
    ("asm/data/dat.s", ".data\n.incbin \"assets/cod/x.bin\"\n"),
    ("include/macro.inc", ".macro glabel label\n\\label:\n.endm\n"),
    ("assets/cod/x.bin", "binary\n"),
    ("build/SLPS_258.19.ld", "SECTIONS { }\n"),
    ("undefined_funcs_auto.txt", "func_00100000\n"),
):
    p = SCRATCH / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

rels = ss.list_outputs(SCRATCH)
check("the inputs stay out of the file list",
      all(not r.startswith(("splat.yaml", "config/", "SLPS_258.19.rom")) for r in rels), str(rels))
check("the file list holds every splat output", len(rels) == 6, str(rels))

digest = ss.tree_digest(SCRATCH, rels)

# --- packing is deterministic and excludes the inputs ------------------------------------
archive = WORK / "toolchain" / "splat-SLPS_258.19.tar.zst"
ss.pack(SCRATCH, rels, archive)
first = ss.sha256_file(archive)
ss.pack(SCRATCH, rels, archive)
check("packing twice gives the same archive", ss.sha256_file(archive) == first)

members = [m.name for m in ss.archive_members(archive)]
check("the archive holds every output", len(members) == len(rels), str(members))
check("the archive has no input file",
      not any(m.startswith(("splat.yaml", "config/", "SLPS_258.19.rom")) for m in members), str(members))
check("the archive has no absolute or parent path",
      all(not m.startswith("/") and ".." not in Path(m).parts for m in members), str(members))

# --- the fake checkout and companion repository ------------------------------------------
for rel in ss.INPUT_FILES:
    dst = PROJECT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if (SCRATCH / rel).is_file():
        shutil.copy2(SCRATCH / rel, dst)
    else:
        dst.write_text(f"# {rel}\n", encoding="utf-8")
(PROJECT / "toolchain.lock.json").write_text(json.dumps({"game": {"id": "SLPS_258.19"}}), encoding="utf-8")

GAME = ORIG / "orig" / "SLPS_258.19"
GAME.parent.mkdir(parents=True, exist_ok=True)
GAME.write_bytes(b"retail executable\n")
(ORIG / "toolchain").mkdir(parents=True, exist_ok=True)
shutil.copy2(archive, ORIG / "toolchain" / archive.name)

MANIFEST = PROJECT / ss.MANIFEST_DEFAULT
MANIFEST.parent.mkdir(parents=True, exist_ok=True)


def write_manifest(**over):
    manifest = {
        "schema": ss.SCHEMA,
        "target": "SLPS_258.19",
        "path": f"toolchain/{archive.name}",
        "sha256": ss.sha256_file(archive),
        "game_sha1": ss.sha1_file(GAME),
        "splat_version": "0.50.0",
        "inputs": {rel: ss.sha256_file(PROJECT / rel) for rel in ss.INPUT_FILES},
        "entry_count": len(rels),
        "tree_sha256": digest,
        "created_at": "2026-10-13T00:00:00Z",
        "generator": "tools/ci/splat_snapshot.py",
    }
    manifest.update(over)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def use(**over) -> str:
    """Run cmd_use and return the verdict it printed. 跑 cmd_use，返回它打印的 verdict。

    Every scenario starts from a clean project tree.
    每个场景都从干净的项目树开始。
    """
    for rel in rels:
        (PROJECT / rel).unlink(missing_ok=True)
    options = dict(project=str(PROJECT), orig=str(ORIG), manifest=str(MANIFEST),
                   game=None, extract=True, github_output=None)
    options.update(over)
    args = argparse.Namespace(**options)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = ss.cmd_use(args)
    text = buf.getvalue()
    verify = [line for line in text.splitlines() if line in ("snapshot", "splat")]
    return (verify[-1] if verify else "?"), rc, text


print("[1] the archive is used when everything matches")
write_manifest()
verdict, rc, text = use()
check("a matching archive extracts", verdict == "snapshot", text.strip().splitlines()[-1] if text else "")
check("cmd_use returns 0", rc == 0)
check("the extracted tree matches the packaged one",
      ss.tree_digest(PROJECT, rels) == digest,
      str(sorted(ss.list_outputs(PROJECT))))
check("the archive says it is used", "verdict=snapshot" in text or verdict == "snapshot")

print("[2] check-only mode does not touch the tree")
verdict, rc, text = use(extract=False)
check("check only still reports snapshot", verdict == "snapshot")
check("check only writes nothing", not any((PROJECT / rel).exists() for rel in rels))

print("[3] every reason to distrust the archive falls back to splat")
write_manifest()
verdict, _, _ = use()
check("the happy path still works before the negative cases", verdict == "snapshot")

corrupt = ORIG / "toolchain" / archive.name
good = corrupt.read_bytes()
corrupt.write_bytes(good + b"x")
verdict, rc, _ = use()
check("a corrupt archive falls back", verdict == "splat" and rc == 0)
check("the fallback leaves no half tree", not any((PROJECT / rel).exists() for rel in rels))
corrupt.write_bytes(good)

write_manifest(sha256="0" * 64)
verdict, _, _ = use()
check("a sha256 mismatch falls back", verdict == "splat")

write_manifest(inputs={**{rel: ss.sha256_file(PROJECT / rel) for rel in ss.INPUT_FILES},
                       "splat.yaml": "1" * 64})
verdict, _, _ = use()
check("a changed input falls back", verdict == "splat")

write_manifest(game_sha1="2" * 40)
verdict, _, _ = use()
check("a different retail executable falls back", verdict == "splat")

write_manifest(entry_count=len(rels) + 1)
verdict, _, _ = use()
check("a wrong entry count falls back", verdict == "splat")
check("the wrong count leaves no half tree", not any((PROJECT / rel).exists() for rel in rels))

write_manifest(tree_sha256="3" * 64)
verdict, _, _ = use()
check("a wrong tree digest falls back", verdict == "splat")

write_manifest(path="../evil.tar.zst")
verdict, _, _ = use()
check("a path that escapes the companion repository falls back", verdict == "splat")

MANIFEST.unlink()
verdict, _, _ = use()
check("a missing manifest falls back", verdict == "splat")

write_manifest(schema="at2-splat-snapshot/999")
verdict, _, _ = use()
check("an unknown schema falls back", verdict == "splat")

print("[4] resolve_archive refuses escapes")
check("a relative path inside the checkout is accepted",
      ss.resolve_archive(ORIG, "toolchain/x.tar.zst") is not None)
check("an absolute path is refused", ss.resolve_archive(ORIG, "/etc/passwd") is None)
check("a parent path is refused", ss.resolve_archive(ORIG, "../x.tar.zst") is None)

print("[5] an archive with an unsafe member is refused")
evil_dir = WORK / "evil"
evil_dir.mkdir(parents=True, exist_ok=True)
(evil_dir / "payload").write_text("x", encoding="utf-8")
evil = WORK / "evil.tar.zst"
with subprocess.Popen(["tar", "--create", "--file", "-", "--directory", str(evil_dir),
                       "--transform", "s|payload|../escaped|", "payload"], stdout=subprocess.PIPE) as tp:
    with subprocess.Popen(["zstd", "-3", "-q", "-f", "-o", str(evil)], stdin=tp.stdout) as zp:
        tp.stdout.close()
        zp.wait()
        tp.wait()
try:
    list(ss.archive_members(evil))
    check("an unsafe member raises", False, "no error")
except SystemExit:
    check("an unsafe member raises", True)

shutil.rmtree(WORK, ignore_errors=True)

print(f"\n{len(fails)} failed" if fails else "\nall splat_snapshot tests passed")
sys.exit(1 if fails else 0)
