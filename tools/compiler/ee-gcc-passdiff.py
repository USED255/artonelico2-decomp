#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ee_gcc_passdiff —— 把「最终指令不同」上溯到「第一个不同的编译器 pass」。

背景（外部调研 2026-10-06，报告 R22）：
  dds-decomp（Digital Devil Saga，同 ee-gcc 2.96 工具链）文档化了一套 EE GCC
  优化流水线诊断法：用 `-da` 导出每个 pass 的 RTL，找到两份**都讲得通**的源码
  第一次分叉的 pass，再按 `compiler-decision-atlas.md` 的「决策族」去查该 pass
  的输入（类型/CFG/别名/活跃区间/调度），而不是盯着最终 objdump 猜。
  那份 atlas 与工具（`ee_gcc_why.py`）**无 LICENSE**，本脚本是**独立重实现**，
  只借用「逐 pass RTL 比较」这一方法学；未复制其任何代码或文本。

本机实测（2026-10-06，见 out/evidence/ee_gcc_rtl_dump_probe.txt）：
  * ee-gcc 3.2-ee-040921 -da → 00.rtl 01.sibling 03.jump ... 20.sched ... 33.dbr
  * ee-gcc 2.96-ee-001003-1 -da → 00.rtl 01.sibling 02.jump ... 17.sched ... 29.dbr
  ⇒ 两个编译器都支持；**pass 编号不同**，比较表按同一编译器内才有意义。

用法：
  python3 tools/compiler/ee-gcc-passdiff.py a.c b.c
  python3 tools/compiler/ee-gcc-passdiff.py a.c b.c --cc ~/eecc/ee-gcc2.96/bin/ee-gcc
  python3 tools/compiler/ee-gcc-passdiff.py a.c b.c --keep     # 保留 dump 目录
  python3 tools/compiler/ee-gcc-passdiff.py a.c b.c --dump-dir .tmp/passdiff

判读：
  * 第一次分叉在 00.rtl/01.sibling/03.jump  → 语义/CFG 层（类型、分支结构、表达式）
  * 分叉在 09.cse/11.gcse/15.cse2           → CSE/翻译单元上下文
  * 分叉在 16.life/19.regmove/22.lreg/23.greg → 活跃区间与寄存器分配
  * 分叉在 17.combine/18.ce/20.sched/29.sched2 → 组合/调度与延迟槽
  （编号为 3.2 的名称；2.96 的对应名见 out/evidence/ee_gcc_rtl_dump_probe.txt）

退出码：0=两者逐 pass 相同；1=某 pass 起分叉；2=编译/参数错误。
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_CC = os.environ.get("EE_GCC", str(Path.home() / "eecc" / "ee-gcc3.2-040921" / "bin" / "ee-gcc"))
DEFAULT_FLAGS = ["-O2", "-G0"]

# RTL dump 里的 insn uid（`(insn 7 6 8 ...)`）在两次编译间无意义，必须归一化；
# 但常量/立即数必须保留（它们才是语义）。
_UID_KW = ("insn", "jump_insn", "call_insn", "code_label", "note", "barrier",
           "jump_table_data", "addr_vec", "addr_diff_vec")
_UID_RE = re.compile(r"\((" + "|".join(_UID_KW) + r")\s+(?:\d+\s+)*")
# 伪寄存器（`(reg:SI 151)`，无 `$` 名）编号在两次编译间无意义；硬寄存器写成 `(reg:SI 8 $8)`，不匹配。
_PSEUDO_REG_RE = re.compile(r"\(reg((?:/[a-z]+)?:\w+) (\d+)\)")
_LINE_RE = re.compile(r"\s+")
_SKIP_PREFIX = ("(note", "(barrier")
_PASS_RE = re.compile(r"^\d\d\.")


def normalize(text: str) -> str:
    """把一份 RTL dump 归一化成可跨两次编译比较的「代码形状」。

    * 丢弃 `;;` 注释行、`(note ...)` 与 `(barrier ...)` 行 —— note 里既有编译器内部
      指针，也有作用域块标记（BLOCK_BEG/DELETED），都是源码拼写的噪声，会把**假分叉**
      钉在 00.rtl（2026-10-06 标定时实测到）。
    * insn uid 与**伪寄存器编号**归一化（`(reg:SI 151)` → `(reg:SI PSEUDO)`）；
      硬寄存器（`(reg:SI 8 $8)`）与立即数/常量原样保留，它们才是语义。
    """
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(";;") or s.startswith(_SKIP_PREFIX):
            continue
        s = _UID_RE.sub(r"(\1 ", s)
        s = _PSEUDO_REG_RE.sub(r"(reg\1 PSEUDO)", s)
        out.append(_LINE_RE.sub(" ", s))
    return "\n".join(out)


def compile_dumps(cc: str, flags: list[str], src: Path, workdir: Path) -> tuple[dict[str, str], str]:
    """在独占目录里编译 src 并收集 <name>.<NN>.<name> RTL dump。返回 (pass->文本, .o 字节)。

    两份源码都**复制成同一个文件名**（`input.c`）再编译：`ee-gcc` 会把源文件名写进
    对象的符号/字符串表，文件名不同会让 `.o` 差 1 个字节（2026-10-06 实测），
    从而把「两条写法其实完全等价」误报成「对象不同」。
    """
    workdir.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix if src.suffix else ".c"
    local = workdir / ("input" + suffix)
    shutil.copyfile(src, local)
    cmd = [cc, *flags, "-da", "-c", "-o", "input.o", local.name]
    r = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"编译失败（{src.name}）:\n{' '.join(cmd)}\n{r.stderr[:2000]}")
    dumps: dict[str, str] = {}
    for f in sorted(workdir.glob(local.name + ".[0-9][0-9].*")):
        dumps[f.name[len(local.name) + 1:]] = normalize(f.read_text(errors="replace"))
    obj = workdir / "input.o"
    asm = obj.read_bytes().hex() if obj.exists() else ""
    return dumps, asm


def main() -> int:
    ap = argparse.ArgumentParser(description="找到两份 ee-gcc 源码第一个不同的编译 pass")
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--cc", default=DEFAULT_CC)
    ap.add_argument("--flags", default=" ".join(DEFAULT_FLAGS),
                    help=f"传给 ee-gcc 的标志（默认 {DEFAULT_FLAGS!r}，不含 -da/-c）")
    ap.add_argument("--dump-dir", type=Path, default=Path(".tmp/passdiff"))
    ap.add_argument("--keep", action="store_true", help="保留 dump 目录（默认删除）")
    args = ap.parse_args()

    flags = args.flags.split()
    root = args.dump_dir
    if root.exists():
        shutil.rmtree(root)

    try:
        da, asm_a = compile_dumps(args.cc, flags, args.a, root / "a")
        db, asm_b = compile_dumps(args.cc, flags, args.b, root / "b")
    finally:
        pass

    print(f"编译器: {args.cc}")
    print(f"标志  : {' '.join(flags)}")
    print(f"pass 数: a={len(da)} b={len(db)}")
    print(f"最终目标文件(.o): {'相同' if asm_a == asm_b else '不同'}")

    first = None
    for name in sorted(set(da) | set(db)):
        if da.get(name) != db.get(name):
            first = name
            break
    if first is None:
        print("== 逐 pass 完全相同 ==")
        if asm_a != asm_b:
            print("提醒：RTL 相同但汇编不同 —— 差异在 emit/汇编器层，不要改 C。")
    else:
        print(f"== 第一个不同的 pass: {first} ==")
        # 给出该 pass 的第一处差异行，便于直接看
        la, lb = da.get(first, "").splitlines(), db.get(first, "").splitlines()
        for i in range(max(len(la), len(lb))):
            x = la[i] if i < len(la) else "<缺>"
            y = lb[i] if i < len(lb) else "<缺>"
            if x != y:
                print(f"  第 {i + 1} 行:")
                print(f"    a: {x[:300]}")
                print(f"    b: {y[:300]}")
                break
        later = [n for n in sorted(set(da) | set(db)) if n > first]
        recon = next((n for n in later if da.get(n) == db.get(n)), None)
        if recon:
            print(f"  ↺ 分叉后在 {recon} 又收敛回相同 ⇒ 该差异被后续 pass 消除"
                  f"（{'两条写法最终等价' if asm_a == asm_b else '但最终对象仍不同，另有分歧点'}）")
        elif asm_a == asm_b:
            print("  ✓ 最终对象相同：两条写法等价 —— 不必追这个分叉。")
        else:
            print("  最终对象不同：该分叉是**最早**的成因候选（按 R22 §4.1 决策族查对应输入）。")
    if not args.keep:
        shutil.rmtree(root, ignore_errors=True)
    else:
        print(f"dump 保留在: {root}")
    return 0 if first is None else 1


if __name__ == "__main__":
    sys.exit(main())
