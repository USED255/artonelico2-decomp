#!/usr/bin/env python3
"""公开仓库的配置入口（社区惯例：`python3 configure.py`）。

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

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "toolchain.lock.json"


def sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default="orig/SLPS_258.19", help="原版 SLPS_258.19 的路径")
    ap.add_argument("--allow-mismatch", action="store_true", help="校验失败也让配置通过（仅供调试）")
    args = ap.parse_args()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    want = lock["game"]
    game = Path(args.game)
    if not game.is_absolute():
        game = ROOT / game

    problems: list[str] = []
    if not game.is_file():
        problems.append(f"找不到原版 ELF：{game}（需要自备正版光盘中的 SLPS_258.19）")
    else:
        size = game.stat().st_size
        digest = sha1(game)
        if size != want["elf_size"]:
            problems.append(f"ELF 大小不符：{size} != {want['elf_size']}")
        if digest != want["elf_sha1"]:
            problems.append(f"ELF sha1 不符：{digest} != {want['elf_sha1']}")

    if problems and not args.allow_mismatch:
        print("❌ configure 失败：", file=sys.stderr)
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
    print(f"✅ configure 完成：{ROOT/'build'/'config.json'}")
    print(f"   原版 ELF：{game}")
    print("   下一步：make build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
