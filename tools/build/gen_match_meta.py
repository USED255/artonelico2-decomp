#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 config/match_meta.tsv —— 「已 C 化符号」的机器可读来源台账。

为什么需要它：
  * `matched_symbols.txt` 是**唯一开关**（构建读它），但它只有「符号 [源] # 注释」；
  * 长期计划（docs/R11）要求每个已匹配符号能追溯：源文件、编译标志、难度类别、批次、
    证据。多个匹配器（trivial/stub/wrapper/...）各自写自己的段，靠这个台账统一汇总。

数据来源（全部已存在，本脚本只做汇总，不猜测）：
  * routebjp/config/matched_symbols.txt   —— 符号 / 源 basename / 段（M2 样板 / M3 / 桩）
  * routebjp/config/source_flags.tsv      —— per-source 额外编译标志
  * out/evidence/jp_m3_workqueue.tsv      —— 难度 category（class 列）

产出：`config/match_meta.tsv`
  sym  src  flags  class  batch  evidence

用法：python3 tools/build/gen_match_meta.py [--check]
      --check 只比对现有台账是否与事实源一致（CI / 收尾用），不回写。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "project"))
from at2_paths import (  # noqa: E402  布局无关的路径解析（MATCHED_LIST/FLAGS_TSV/WORKQUEUE）
    MATCHED_LIST as MATCHED,
    FLAGS_TSV as FLAGS,
    WORKQUEUE,
    PROJECT_ROOT,
)

OUT = PROJECT_ROOT / "config" / "match_meta.tsv"

STUB_BEGIN = "# ---- M3 桩（syscall/break/手写指令；auto_match_stub.py 生成，勿手改本段）----"
M3_BEGIN = "# ---- M3 trivial 自动匹配（auto_match_trivial.py 生成，勿手改本段）----"


def parse_matched():
    """返回 [(sym, src, tag, batch)]。"""
    rows, batch = [], "?"
    for line in MATCHED.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if "---- M2 样板" in s:
            batch = "M2"
            continue
        if s.startswith(M3_BEGIN):
            batch = "M3"
            continue
        if s.startswith(STUB_BEGIN):
            batch = "stub"
            continue
        if s.startswith("#") or not s:
            continue
        body = line.split("#", 1)
        parts = body[0].split()
        if not parts:
            continue
        sym = parts[0]
        src = parts[1] if len(parts) > 1 else sym
        tag = body[1].strip().split()[0] if len(body) > 1 and body[1].strip() else ""
        rows.append((sym, src, tag, batch))
    return rows


def parse_flags():
    out = {}
    if not FLAGS.is_file():
        return out
    for line in FLAGS.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        a = line.split()
        out[a[0]] = " ".join(a[1:])
    return out


def parse_class():
    out = {}
    if not WORKQUEUE.is_file():
        return out
    lines = WORKQUEUE.read_text(encoding="utf-8").splitlines()
    idx = {k: i for i, k in enumerate(lines[0].split("\t"))}
    if "class" not in idx:
        return out
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) >= len(idx):
            out[p[idx["name"]]] = p[idx["class"]]
    return out


def build() -> str:
    flags, cls = parse_flags(), parse_class()
    lines = ["# 已 C 化符号台账（由 tools/build/gen_match_meta.py 汇总；事实源是 matched_symbols.txt / source_flags.tsv）",
             "# sym\tsrc\tflags\tclass\tbatch\tevidence"]
    for sym, src, tag, batch in parse_matched():
        evidence = "objdiff100+ratchet" + (f":{tag}" if tag else "")
        lines.append("\t".join([sym, src, flags.get(src, ""), cls.get(sym, ""), batch, evidence]))
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验不回写")
    args = ap.parse_args()
    text = build()
    if args.check:
        if not OUT.is_file():
            print(f"FAIL: 缺少 {OUT}")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"FAIL: {OUT} 与事实源不一致（跑 python3 tools/build/gen_match_meta.py 重新生成）")
            return 1
        print(f"ok: {OUT.relative_to(ROOT)} 与事实源一致（{len(text.splitlines()) - 2} 条）")
        return 0
    OUT.write_text(text, encoding="utf-8")
    n = len(text.splitlines()) - 2
    print(f"写出 {OUT.relative_to(ROOT)}：{n} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
