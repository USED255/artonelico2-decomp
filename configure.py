#!/usr/bin/env python3
"""Write the build configuration for the public repository (community convention: `python3 configure.py`).

This script does three things only:
  1. Find the retail ELF (`--game` or `orig/SLPS_258.19`).
  2. Check the sha1 against `toolchain.lock.json`.
  3. Write the configuration to `build/config.json` for `tools/build/decomp_build.py`.

The real build logic lives in `tools/build/decomp_build.py`. This file stays thin on purpose.

Usage:
    python3 configure.py --game /path/to/SLPS_258.19

公开仓库的配置入口（社区惯例：`python3 configure.py`）。

只做三件事：① 找原版 ELF（`--game` 或 `orig/SLPS_258.19`）；② 校验 sha1 与 `toolchain.lock.json` 一致；
③ 把配置写进 `build/config.json`，供 `tools/build/decomp_build.py` 使用。

真正的构建逻辑在 `tools/build/decomp_build.py`；本文件刻意保持很薄。

用法：
    python3 configure.py --game /path/to/SLPS_258.19
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# The help text stays English only, because the module docstring is bilingual.
# argparse 的 help 只输出英文，因此这里单独给一段英文说明。
EN_USAGE = "Check the retail ELF against toolchain.lock.json, then write build/config.json."

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "toolchain.lock.json"


def sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=EN_USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default="orig/SLPS_258.19", help="path to the retail SLPS_258.19")
    ap.add_argument("--allow-mismatch", action="store_true",
                    help="write the configuration even when a check fails (debug only)")
    args = ap.parse_args()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    want = lock["game"]
    game = Path(args.game)
    if not game.is_absolute():
        game = ROOT / game

    problems: list[str] = []
    if not game.is_file():
        problems.append(f"retail ELF not found: {game} (supply SLPS_258.19 from your own legal disc)")
    else:
        size = game.stat().st_size
        digest = sha1(game)
        if size != want["elf_size"]:
            problems.append(f"ELF size mismatch: {size} != {want['elf_size']}")
        if digest != want["elf_sha1"]:
            problems.append(f"ELF sha1 mismatch: {digest} != {want['elf_sha1']}")

    if problems and not args.allow_mismatch:
        print("configure failed:", file=sys.stderr)
        for p in problems:
            print("   -", p, file=sys.stderr)
        return 1

    (ROOT / "build").mkdir(exist_ok=True)
    cfg = {
        "root": str(ROOT),
        "layout": "flat",
        "game": str(game),
        "game_sha1": want["elf_sha1"],
        "payload_sha1": want["payload_sha1"],
        "toolchain_lock": str(LOCK),
        "objdiff": "objdiff-cli",
    }
    (ROOT / "build" / "config.json").write_text(json.dumps(cfg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"configure done: {ROOT / 'build' / 'config.json'}")
    print(f"retail ELF: {game}")
    print("next step: make build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
