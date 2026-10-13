#!/usr/bin/env python3
"""Tests for tools/ci/splat_snapshot.py. No toolchain, no splat, and no build are necessary.

The snapshot is an accelerator: every path that distrusts a group must fall back for that
group, and a matching group must restore exactly what was packaged. The tests build a
synthetic tree, pack both groups into one archive, and drive the `use` code path through each
decision, including the v1 manifest that the live repository still carries.

Usage: python3 tools/check/test_splat_snapshot.py

splat_snapshot.py 的测试（不需要工具链、splat 或构建）。归档只是加速器：任何不信任某一组的分支
都必须对该组回落，命中时必须逐字还原打包的树。测试用合成树把两组打成一个归档，把 `use` 的每条判定
跑一遍，并覆盖线上仍在使用的 v1 清单。
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
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
SCRATCH = WORK / "scratch"          # the raw splat output
STAGE_ASM = WORK / "scratch-asm"    # the assembled objects
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
# The object group lives under build/asm/ (the group split is a path prefix). The .err file is
# a diagnostic and must not be packed.
for rel in ("build/asm/cod/func_00100000.o", "build/asm/cod/func_00100001.o", "build/asm/cod/func_00100000.err"):
    p = STAGE_ASM / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("obj\n" if rel.endswith(".o") else "", encoding="utf-8")

rels = ss.list_outputs(SCRATCH)
asm_rels = ss.list_asm_objects(STAGE_ASM)
digest = ss.tree_digest(SCRATCH, rels)
asm_digest = ss.tree_digest(STAGE_ASM, asm_rels)

print("[1] the file lists and the packing")
check("the splat inputs stay out of the file list",
      all(not r.startswith(("splat.yaml", "config/", "SLPS_258.19.rom")) for r in rels), str(rels))
check("the splat list holds every output", len(rels) == 6, str(rels))
check("the object list holds only *.o", len(asm_rels) == 2 and all(r.endswith(".o") for r in asm_rels),
      str(asm_rels))
check("group_of splits by prefix",
      ss.group_of("build/asm/cod/a.o") == ss.GROUP_ASM and ss.group_of("build/SLPS_258.19.ld") == ss.GROUP_SPLAT)

archive = WORK / "toolchain" / "splat-SLPS_258.19.tar.zst"
roots = [(SCRATCH, sorted({r.split("/", 1)[0] for r in rels})), (STAGE_ASM, ["build/asm"])]
ss.pack_multi(roots, archive)
first = ss.sha256_file(archive)
ss.pack_multi(roots, archive)
check("packing twice gives the same archive", ss.sha256_file(archive) == first)

members = [m.name for m in ss.archive_members(archive)]
check("the archive holds both groups", len(members) == len(rels) + len(asm_rels), str(members))
check("the members keep the project-relative layout",
      "asm/cod/func_00100000.s" in members and "build/asm/cod/func_00100000.o" in members, str(members))
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
(PROJECT / "build.sh").write_text("# the assembly recipe\n", encoding="utf-8")
(PROJECT / "toolchain.lock.json").write_text(json.dumps({"game": {"id": "SLPS_258.19"}}), encoding="utf-8")

GAME = ORIG / "orig" / "SLPS_258.19"
GAME.parent.mkdir(parents=True, exist_ok=True)
GAME.write_bytes(b"retail executable\n")
(ORIG / "toolchain").mkdir(parents=True, exist_ok=True)
shutil.copy2(archive, ORIG / "toolchain" / archive.name)

MANIFEST = PROJECT / ss.MANIFEST_DEFAULT
MANIFEST.parent.mkdir(parents=True, exist_ok=True)
GITHUB_OUTPUT = WORK / "github_output.txt"
RECIPE = "# the assembly recipe\n"


def write_manifest(*, v1: bool = False, with_asm: bool = True, **over):
    """Write a manifest. `splat`/`asm` patch a group, the remaining keywords patch the top level.

    写清单；`splat`/`asm` 改某一组，其余关键字改顶层。
    """
    splat = {"inputs": {rel: ss.sha256_file(PROJECT / rel) for rel in ss.INPUT_FILES},
             "entry_count": len(rels), "tree_sha256": digest}
    asm = {"inputs": {rel: ss.sha256_file(PROJECT / rel) for rel in ss.ASM_INPUT_FILES},
           "as_version": "GNU assembler (test)", "entry_count": len(asm_rels), "tree_sha256": asm_digest}
    splat.update(over.pop("splat", {}))
    asm.update(over.pop("asm", {}))
    if v1:
        manifest = {"schema": ss.SCHEMA_V1, "target": "SLPS_258.19",
                    "path": f"toolchain/{archive.name}", "sha256": ss.sha256_file(archive),
                    "game_sha1": ss.sha1_file(GAME), "splat_version": "0.50.0",
                    "inputs": splat["inputs"], "entry_count": splat["entry_count"],
                    "tree_sha256": splat["tree_sha256"],
                    "created_at": "2026-10-13T00:00:00Z", "generator": "tools/ci/splat_snapshot.py"}
    else:
        groups = {"splat": splat}
        if with_asm:
            groups["asm"] = asm
        manifest = {"schema": ss.SCHEMA, "target": "SLPS_258.19",
                    "path": f"toolchain/{archive.name}", "sha256": ss.sha256_file(archive),
                    "game_sha1": ss.sha1_file(GAME), "splat_version": "0.50.0",
                    "groups": groups, "created_at": "2026-10-13T00:00:00Z",
                    "generator": "tools/ci/splat_snapshot.py"}
    manifest.update(over)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def use(**over) -> tuple[str, str, str]:
    """Run cmd_use on a clean project tree. Returns (verdict, groups, output text).

    在干净项目树上跑 cmd_use，返回（verdict, groups, 输出文本）。
    """
    for rel in set(rels) | set(asm_rels):
        (PROJECT / rel).unlink(missing_ok=True)
    GITHUB_OUTPUT.unlink(missing_ok=True)
    options = dict(project=str(PROJECT), orig=str(ORIG), manifest=str(MANIFEST),
                   game=None, extract=True, github_output=str(GITHUB_OUTPUT))
    options.update(over)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = ss.cmd_use(argparse.Namespace(**options))
    text = buf.getvalue()
    lines = [line for line in text.splitlines() if line in ("snapshot", "splat")]
    verdict = lines[-1] if lines else "?"
    groups = ""
    if GITHUB_OUTPUT.is_file():
        for line in GITHUB_OUTPUT.read_text(encoding="utf-8").splitlines():
            if line.startswith("groups="):
                groups = line.split("=", 1)[1]
    if rc != 0:
        raise AssertionError(f"cmd_use returned {rc}")
    return verdict, groups, text


print("[2] the v2 archive is used when both groups match")
write_manifest()
verdict, groups, text = use()
check("a matching archive extracts", verdict == "snapshot", text.strip()[-160:])
check("both groups are reported", groups == "splat,asm", groups)
check("the splat group is restored", ss.tree_digest(PROJECT, rels) == digest)
check("the object group is restored", (PROJECT / "build/asm/cod/func_00100000.o").is_file())
check("no .err file is packed", not (PROJECT / "build/asm/cod/func_00100000.err").exists())

print("[3] a v1 manifest still works (the live repository carries one)")
write_manifest(v1=True)
verdict, groups, text = use()
check("a v1 manifest is used", verdict == "snapshot", text.strip()[-160:])
check("a v1 manifest reports the splat group only", groups == "splat", groups)
check("a v1 manifest restores the splat files", ss.tree_digest(PROJECT, rels) == digest)
check("a v1 manifest restores no objects", not (PROJECT / "build/asm/cod/func_00100000.o").exists())

print("[4] check-only mode does not touch the tree")
write_manifest()
verdict, groups, _ = use(extract=False)
check("check only reports snapshot", verdict == "snapshot")
check("check only reports both groups", groups == "splat,asm", groups)
check("check only writes nothing", not any((PROJECT / r).exists() for r in set(rels) | set(asm_rels)))

print("[5] a changed build.sh drops the object group only")
write_manifest()
(PROJECT / "build.sh").write_text("# a different recipe\n", encoding="utf-8")
verdict, groups, text = use()
check("the splat group is still used", verdict == "snapshot" and groups == "splat", f"{verdict} {groups}")
check("the splat files are restored", ss.tree_digest(PROJECT, rels) == digest)
check("no object is restored", not (PROJECT / "build/asm/cod/func_00100000.o").exists())
(PROJECT / "build.sh").write_text(RECIPE, encoding="utf-8")

print("[6] a mismatched object group is dropped and its files are removed")
write_manifest(asm={"tree_sha256": "0" * 64})
verdict, groups, _ = use()
check("a bad object digest keeps the splat group", verdict == "snapshot" and groups == "splat", f"{verdict} {groups}")
check("no object is left behind", not (PROJECT / "build/asm/cod/func_00100000.o").exists())
check("the splat group is intact", ss.tree_digest(PROJECT, rels) == digest)

write_manifest(asm={"entry_count": len(asm_rels) + 1})
verdict, groups, _ = use()
check("a wrong object count keeps the splat group", verdict == "snapshot" and groups == "splat", f"{verdict} {groups}")
check("no object is left behind after a count mismatch", not (PROJECT / "build/asm/cod/func_00100000.o").exists())

print("[7] every reason to distrust the whole archive falls back to splat")
write_manifest()
verdict, groups, _ = use()
check("the happy path still works before the negative cases", verdict == "snapshot" and groups == "splat,asm",
      f"{verdict} {groups}")

corrupt = ORIG / "toolchain" / archive.name
good = corrupt.read_bytes()
corrupt.write_bytes(good + b"x")
verdict, groups, _ = use()
check("a corrupt archive falls back", verdict == "splat" and groups == "", f"{verdict} {groups}")
check("the fallback leaves no half tree", not any((PROJECT / r).exists() for r in set(rels) | set(asm_rels)))
corrupt.write_bytes(good)

write_manifest(sha256="0" * 64)
verdict, _, _ = use()
check("a sha256 mismatch falls back", verdict == "splat")

write_manifest(splat={"inputs": {**{rel: ss.sha256_file(PROJECT / rel) for rel in ss.INPUT_FILES},
                                 "splat.yaml": "1" * 64}})
verdict, _, _ = use()
check("a changed splat input falls back", verdict == "splat")

write_manifest(game_sha1="2" * 40)
verdict, _, _ = use()
check("a different retail executable falls back", verdict == "splat")

write_manifest(splat={"entry_count": len(rels) + 1})
verdict, _, _ = use()
check("a wrong splat entry count falls back", verdict == "splat")
check("a wrong count leaves no half tree", not any((PROJECT / r).exists() for r in rels))

write_manifest(splat={"tree_sha256": "3" * 64})
verdict, _, _ = use()
check("a wrong splat tree digest falls back", verdict == "splat")

write_manifest(path="../evil.tar.zst")
verdict, _, _ = use()
check("a path that escapes the companion repository falls back", verdict == "splat")

MANIFEST.unlink()
verdict, _, _ = use()
check("a missing manifest falls back", verdict == "splat")

write_manifest(schema="at2-splat-snapshot/999")
verdict, _, _ = use()
check("an unknown schema falls back", verdict == "splat")

write_manifest(with_asm=False)
verdict, groups, _ = use(extract=False)
check("a v2 manifest without an object group reports splat only",
      verdict == "snapshot" and groups == "splat", f"{verdict} {groups}")

print("[8] assemble_objects runs the repository's build.sh in a copy of the scratch")
# A fake build.sh stands in for the real one: it only has to create build/asm/**/*.o. This
# exercises the staging copy, the environment, the count check, and the failure path without a
# toolchain. It is also the regression test for a missing `import os` in the tool.
FAKE_RECIPE = (
    "#!/usr/bin/env bash\n"
    "set -euo pipefail\n"
    "find asm -name '*.s' | while read -r s; do\n"
    "  o=\"build/asm/${s#asm/}\"; o=\"${o%.s}.o\"\n"
    "  mkdir -p \"$(dirname \"$o\")\"\n"
    "  printf 'obj\\n' > \"$o\"\n"
    "done\n"
)
FAKE_BAD = "#!/usr/bin/env bash\nexit 3\n"
(PROJECT / "build.sh").write_text(FAKE_RECIPE, encoding="utf-8")
staging, objs = ss.assemble_objects(PROJECT, SCRATCH, Path("/bin/true"), expected=2)
check("the staging copy holds the objects", len(objs) == 2 and "build/asm/cod/func_00100000.o" in objs, str(objs))
check("the staging copy is separate from the splat scratch",
      staging != SCRATCH and (SCRATCH / "build/asm").exists() is False)
expected_objs = {f"build/asm/{rel[len('asm/'):-2]}.o" for rel in rels if rel.endswith(".s")}
check("the objects mirror the sources", set(objs) == expected_objs, str(sorted(objs)))

try:
    ss.assemble_objects(PROJECT, SCRATCH, Path("/bin/true"), expected=99)
    check("a wrong object count raises", False, "no error")
except SystemExit:
    check("a wrong object count raises", True)

(PROJECT / "build.sh").write_text(FAKE_BAD, encoding="utf-8")
try:
    ss.assemble_objects(PROJECT, SCRATCH, Path("/bin/true"), expected=2)
    check("a failing build.sh raises", False, "no error")
except SystemExit:
    check("a failing build.sh raises", True)
(PROJECT / "build.sh").write_text(RECIPE, encoding="utf-8")

print("[9] resolve_archive refuses escapes")
check("a relative path inside the checkout is accepted",
      ss.resolve_archive(ORIG, "toolchain/x.tar.zst") is not None)
check("an absolute path is refused", ss.resolve_archive(ORIG, "/etc/passwd") is None)
check("a parent path is refused", ss.resolve_archive(ORIG, "../x.tar.zst") is None)

print("[10] an archive with an unsafe member is refused")
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

print("[11] a same-size, different-content member is refused (the content digest)")
# The manifest's sha256 is kept in sync with the repacked archive and the tree digest still
# matches (the sizes do not change), so ONLY the content digest can catch this (R30 finding B8).
# 清单的 sha256 跟着重打包后的归档更新，树摘要也仍然匹配（大小没变）⇒ 只有内容摘要能抓住它（R30 B8）。
# `assemble_objects` (test 8) replaces scratch-asm with a copy of the splat scratch, and its
# failing-build.sh case leaves no build/asm there. Rebuild the synthetic object tree before
# repacking, so this test compares content and nothing else.
# 测试 8 的 `assemble_objects` 会用 splat scratch 的副本替换 scratch-asm，且最后一次「build.sh
# 失败」的调用不产出 build/asm。重打包前重建合成对象树，让本测试只比内容。
for rel in ("build/asm/cod/func_00100000.o", "build/asm/cod/func_00100001.o"):
    p = STAGE_ASM / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("obj\n", encoding="utf-8")
write_manifest()
splat_member = SCRATCH / "asm" / "cod" / "func_00100000.s"
original_bytes = splat_member.read_bytes()
old_content = ss.content_digest(SCRATCH, rels)
splat_member.write_bytes(b"X" * len(original_bytes))
ss.pack_multi(roots, archive)
shutil.copy2(archive, ORIG / "toolchain" / archive.name)
write_manifest(splat={"content_sha256": old_content})
verdict, groups, text = use()
check("the tampered group falls back", verdict == "splat" and groups == "", f"{verdict} {groups}")
check("the tampered group wrote nothing into the project",
      not any((PROJECT / r).exists() for r in rels), text.strip()[-160:])
stages = list((PROJECT / ".tmp").glob("splat-snapshot-stage-*")) if (PROJECT / ".tmp").is_dir() else []
check("the staging directory is cleaned up", not stages, str(stages))
# Restore the member and repack, so nothing after this depends on the tampering.
splat_member.write_bytes(original_bytes)
ss.pack_multi(roots, archive)
shutil.copy2(archive, ORIG / "toolchain" / archive.name)

print("[12] --scratch is confined to the project")
for bad in (".", "..", "/"):
    try:
        ss.guarded_scratch(PROJECT, bad)
        check(f"guarded_scratch refuses {bad!r}", False, "no error")
    except SystemExit:
        check(f"guarded_scratch refuses {bad!r}", True)
inside = ss.guarded_scratch(PROJECT, ".tmp/scratch")
check("a child directory is accepted", inside == (PROJECT / ".tmp" / "scratch").resolve(), str(inside))

shutil.rmtree(WORK, ignore_errors=True)

print(f"\n{len(fails)} failed" if fails else "\nall splat_snapshot tests passed")
sys.exit(1 if fails else 0)
