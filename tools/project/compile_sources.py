#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental compile/assemble driver for build_mixed.sh. It rebuilds only an object whose source or flags changed.

Why this tool is necessary:
  The mixed build compiles C once per C-ified symbol (or assembles a stub once), and
  assembles a residual object per symbol. A full build of 850 symbols takes about 4 to 6
  minutes. At several thousand symbols, each verification batch becomes a bottleneck.
  This script makes a stamp from "source content sha1 + compile flags + toolchain
  version". A stamp hit skips the work. The script also runs 4 jobs in parallel.

Input (all files are temporary and derived):
  --sources TSV   each line `key<TAB>kind<TAB>srcfile`. kind is cc or as. key is the
                  output object name without .o.
  --objdir DIR    output object directory (the stamp goes to DIR/<key>.stamp)
  --cflags  ...   base flags for C
  --flags-file    per-source extra flags file: a header row and data rows
                  (<src-basename><TAB><flags>). The key is key.
  --cc-map        per-source compiler file: a header row and data rows
                  (<key><TAB><tag>[<TAB>note]). tag is game, cri, or an
                  absolute path. With no entry, the code uses --gcc for all sources
                  (backward compatible). Game code uses ee-gcc 3.2-ee-040921. The CRI
                  middleware uses ee-gcc 2.96-ee-001003-1. Both archives are in
                  toolchain.lock.json. CI installs them and exports GCC_CRI. See
                  docs/kb/reports/R17 section 4.2.
  --gcc-cri       path of the cri compiler (used when tag=cri)
  --jobs N        parallel job count (default 4)

Behavior:
  * stamp content = kind|toolchain version|extra-flags|srcfile-sha1. The code rebuilds
    only on a mismatch or a missing object.
  * --no-cache forces a full build.
  * Any compile failure exits with a non-zero code and prints the last error lines.

Usage (build_mixed.sh calls this script. A manual run is a consistency check):
  python3 tools/project/compile_sources.py --sources ... --objdir ... \
      --gcc ~/eecc/... --as ~/eecc/... --include include --cflags "-O2 -ffunction-sections"

增量编译/汇编驱动：给 build_mixed.sh 用，只重建「源或标志变了」的对象。

为什么需要：
  mixed 构建要对每个已 C 化符号编译一次 C（或汇编一次桩），并按符号汇编 residual 对象。
  850 个符号时单次全量约 4–6 分钟；到几千个符号后，每批验证都会变成瓶颈。
  本脚本按「源文件内容 sha1 + 编译标志 + 工具链版本」做 stamp，命中即跳过，并 4 路并行。

输入（全部临时文件，派生）：
  --sources TSV   每行 `key<TAB>kind<TAB>srcfile`；kind ∈ cc|as；key 是输出对象名（不含 .o）
  --objdir DIR    输出对象目录（stamp 写 DIR/<key>.stamp）
  --cflags  ...   基础标志（C）
  --flags-file    每源额外标志文件：表头行 + 数据行（<src-basename><TAB><flags>），键 = key
  --cc-map        每源编译器文件：表头行 + 数据行（<key><TAB><tag>[<TAB>备注]），tag ∈ game|cri|<绝对路径>；
                  缺省时全部走 --gcc（向后兼容）。游戏代码 = ee-gcc 3.2-ee-040921，
                  CRI 中间件 = ee-gcc 2.96-ee-001003-1（两个归档都在 toolchain.lock.json 里，
                  CI 早已安装并导出 GCC_CRI）——见 docs/kb/reports/R17 §4.2。
  --gcc-cri       cri 编译器的路径（tag=cri 时使用）
  --jobs N        并行度（默认 4）

行为：
  * stamp 内容 = kind|工具链版本|extra-flags|srcfile-sha1；不匹配或对象缺失才重建；
  * --no-cache 强制全量；
  * 任何一条编译失败 → 非 0 退出并打印最后几行错误。

用法（由 build_mixed.sh 调用，也可单独跑做一致性对照）：
  python3 tools/project/compile_sources.py --sources ... --objdir ... \
      --gcc ~/eecc/... --as ~/eecc/... --include include --cflags "-O2 -ffunction-sections"
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import at2_io                          # shared name/path/atomic-write helpers  # noqa: E402
try:                                   # jtbl jump table patch in the same directory. The module is optional.
    import jtbl_patch as JTBL          # noqa: E402
except Exception:                      # pragma: no cover
    JTBL = None
try:                                   # data-reference redirect (O-01 (1)). Optional, like jtbl_patch.
    import data_patch as DATP          # noqa: E402
except Exception:                      # pragma: no cover
    DATP = None


# Flags that make the compiler read an arbitrary file or run an arbitrary program. The per-source
# flag table is repository content (a pull request can change it), so it may not carry them
# (R30 finding B5).
# 会让编译器读任意文件或运行任意程序的标志。每源标志表是仓库内容（PR 可改），因此不允许携带（R30 B5）。
FORBIDDEN_FLAG = re.compile(r"^(@|-wrapper(=|$)|-fplugin(=|$)|-B(=|$)|-specs=)")


def forbidden_flag(flags: str) -> str | None:
    """The first forbidden flag in `flags`, or None."""
    for tok in flags.split():
        if FORBIDDEN_FLAG.match(tok):
            return (f"the flag {tok!r}, which can make the compiler read an arbitrary file "
                    f"or run an arbitrary program")
    return None


def include_digest(include_dir: str) -> str:
    """sha1 over the include tree (path + content), or "none" when the directory is absent.

    The stamp must notice a regenerated `include/macro.inc`: without it, a new splat split kept
    the old objects and the report recorded the current tools over stale bytes (R30 finding B6).

    include 树（路径 + 内容）的 sha1；目录不存在时返回 "none"。stamp 必须能察觉
    `include/macro.inc` 被重新生成：否则重新 split 后会继续用旧对象，而记录里写的是当前工具（R30 B6）。
    """
    root = Path(include_dir)
    if not root.is_dir():
        return "none"
    h = hashlib.sha1()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(root).as_posix().encode("utf-8"))
            h.update(b"\0")
            h.update(sha1_file(p).encode("ascii"))
            h.update(b"\n")
    return h.hexdigest()


OBJCOPY: str | None = None
READELF: str | None = None


def force_text_align4(obj: Path) -> None:
    """Force the alignment of every `.text*` input section in the object to 4.

    Background (2026-10-04, see P-30): some C sources make GCC align a `.text.<fn>`
    section to 8. The original assembly block (splat `.align 2`) needs only 4. The
    linker then inserts fill. The payload shifts and the payload check fails.

    把对象里所有 `.text*` 输入段的对齐强制为 4。

    背景（2026-10-04，见 P-30）：某些 C 源会让 GCC 把 `.text.<fn>` 段对齐到 8，
    而原汇编块（splat 的 `.align 2`）只要求 4；链接器会插入填充 → 载荷位移、载荷校验变红。
    """
    if not OBJCOPY or not READELF or not Path(OBJCOPY).is_file() or not Path(READELF).is_file():
        return
    try:
        out = subprocess.run([READELF, "-SW", str(obj)], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return
    secs = []
    for line in out.splitlines():
        m = re.search(r"\]\s+(\.text[\w.$]*)\s", line)
        if m and m.group(1) not in secs:
            secs.append(m.group(1))
    if not secs:
        return
    tmp = obj.with_suffix(".al4.o")
    cmd = [OBJCOPY] + [f"--set-section-alignment={s}=4" for s in secs] + [str(obj), str(tmp)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and tmp.is_file():
        os.replace(tmp, obj)


def fix_symtab_info(obj: Path) -> None:
    """Fix the `sh_info` field of the `.symtab` of an ELF32 object (= index of the first non-LOCAL symbol).

    Background (2026-10-06, CI PR #3): an object assembled by `ee-gcc 2.96` puts the two
    LOCAL symbols `gcc2_compiled.` and `__gnu_compiled_c` **before** the global symbols.
    But `sh_info` counts only 8, while 10 LOCAL symbols exist. GNU ld then reports
    `.symtab local symbol at index 8 (>= sh_info of 8)` or `error adding symbols: bad value`.
    The whole mixed build dies at link time. (The baseline build stays green, so only a
    full build finds the problem.)
    This code recomputes `sh_info` from the ELF specification. It rewrites the value only
    on a mismatch. The function is idempotent.

    修正 ELF32 对象 `.symtab` 的 `sh_info`（= 第一个非 LOCAL 符号下标）。

    背景（2026-10-06，CI PR #3）：`ee-gcc 2.96` 汇编出的对象把 `gcc2_compiled.` /
    `__gnu_compiled_c` 两个 LOCAL 符号放在全局符号**之前**，但 `sh_info` 只数到 8，
    而实际有 10 个 LOCAL ⇒ GNU ld 报
    `.symtab local symbol at index 8 (>= sh_info of 8)` / `error adding symbols: bad value`，
    整个 mixed 构建在链接期挂掉（baseline build 仍然绿，所以只有全量构建能发现）。
    这里按 ELF 规范重算 `sh_info`；只在不一致时改写，幂等。
    """
    try:
        data = bytearray(obj.read_bytes())
    except Exception:
        return
    if len(data) < 0x34 or data[:4] != b"\x7fELF" or data[4] != 1:
        return
    e_shoff, = struct.unpack_from("<I", data, 0x20)
    e_shentsize, e_shnum = struct.unpack_from("<HH", data, 0x2E)
    if not e_shoff or not e_shentsize or not e_shnum:
        return
    changed = False
    for i in range(e_shnum):
        o = e_shoff + i * e_shentsize
        if o + 40 > len(data):
            break
        (sh_type, sh_off, sh_size, sh_info,
         sh_entsize) = (struct.unpack_from("<I", data, o + 4)[0],
                        struct.unpack_from("<I", data, o + 16)[0],
                        struct.unpack_from("<I", data, o + 20)[0],
                        struct.unpack_from("<I", data, o + 28)[0],
                        struct.unpack_from("<I", data, o + 36)[0])
        if sh_type != 2 or not sh_entsize:          # SHT_SYMTAB
            continue
        n = sh_size // sh_entsize
        first_global = n
        for k in range(n):
            if data[sh_off + k * sh_entsize + 12] >> 4:   # st_info >> 4 != STB_LOCAL
                first_global = k
                break
        if sh_info != first_global:
            struct.pack_into("<I", data, o + 28, first_global)
            changed = True
    if changed:
        obj.write_bytes(bytes(data))


def sha1_file(p: Path) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def tool_version(exe: str) -> str:
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=20)
        first = (r.stdout or r.stderr).splitlines()
        return first[0].strip() if first else "?"
    except Exception:
        return "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, help="TSV: key<TAB>kind<TAB>srcfile")
    ap.add_argument("--objdir", required=True)
    ap.add_argument("--gcc", required=True)
    ap.add_argument("--gcc-cri", default="", help="CRI section compiler (tag=cri). The code reports an error if it is necessary and absent.")
    ap.add_argument("--cc-map", default="", help="per-source compiler file (line 1 is a header row): <key><TAB><tag> (tag=game|cri|path)")
    ap.add_argument("--as", dest="as_", required=True)
    ap.add_argument("--include", default="include")
    ap.add_argument("--cflags", default="")
    ap.add_argument("--asflags", default="-EL -march=r5900")
    ap.add_argument("--flags-file", default="",
                    help="per-source extra flags file (line 1 is a header row): <key><TAB><flags>")
    ap.add_argument("--jtbl-tables", default="",
                    help="per-source jump table file (line 1 is a header row): <key><TAB><jtbl_symbol>. After the compile, jtbl_patch redirects "
                         "the reference of the C jump table to the existing data symbol (see tools/project/jtbl_patch.py)")
    ap.add_argument("--data-patch", action="store_true",
                    help="after the compile, redirect the C object's own data references to the splat data symbols "
                         "(text literals, static tables). Requires --symbols-tsv and --image. When set, the jtbl table is "
                         "not applied: the same pass covers a switch table (see tools/project/data_patch.py)")
    ap.add_argument("--symbols-tsv", default="", help="<key><TAB><symbol> for the data patch (default: the symbol is the key)")
    ap.add_argument("--image", default="", help="the baseline link (build.sh output) for data symbols and bytes")
    ap.add_argument("--data-patch-asm-dir", default="asm/cod", help="the splat asm tree for the data patch")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--label", default="sources")
    args = ap.parse_args()

    objdir = Path(args.objdir)
    objdir.mkdir(parents=True, exist_ok=True)

    extra = {}
    if args.flags_file and Path(args.flags_file).is_file():
        # Line 1 is the header row (source-basename<TAB>extra-cflags). Skip it.
        # 第 1 行是表头（source-basename<TAB>extra-cflags），跳过。
        for line in Path(args.flags_file).read_text(encoding="utf-8").splitlines()[1:]:
            line = line.split("#", 1)[0].strip()
            if line:
                a = line.split()
                bad = forbidden_flag(" ".join(a[1:]))
                if bad:
                    print(f"FAIL: {args.flags_file}: {a[0]} carries {bad}", file=sys.stderr)
                    return 2
                extra[a[0]] = " ".join(a[1:])

    # Jump table file (a header row and data rows, <key>\t<jtbl_symbol>): after the compile,
    # redirect the reference of the C `.rodata` table to the existing data symbol.
    # 跳转表文件（表头行 + 数据行，<key>\t<jtbl_符号>）：编译后把 C 自产 `.rodata` 表的引用改指到既有数据符号。
    jtbl = {}
    if args.jtbl_tables and Path(args.jtbl_tables).is_file():
        # Line 1 is the header row (symbol<TAB>jtbl-symbol). Skip it.
        # 第 1 行是表头（symbol<TAB>jtbl-symbol），跳过。
        for line in Path(args.jtbl_tables).read_text(encoding="utf-8").splitlines()[1:]:
            line = line.split("#", 1)[0].strip()
            if line:
                a = line.split()
                if len(a) >= 2:
                    jtbl[a[0]] = a[1]

    # Data patch (O-01 (1)): <key><TAB><symbol>. The key is the source basename; the symbol is
    # what the linker script and the asm block are named after. They are usually equal, but the
    # ledger permits a different source name, so the mapping is explicit.
    # 数据改指（O-01 ①）：<key><TAB><符号>。key 是源码基名，符号是链接脚本与 asm 块的名字；
    # 两者通常相同，但台账允许不同名，所以映射必须显式给出。
    symof: dict[str, str] = {}
    if args.data_patch:
        if not (args.symbols_tsv and args.image):
            print("FAIL: --data-patch needs --symbols-tsv and --image", file=sys.stderr)
            return 2
        if DATP is None:
            print("FAIL: the data_patch module is necessary, but the import failed", file=sys.stderr)
            return 2
        for line in Path(args.symbols_tsv).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            a = line.split()
            symof[a[0]] = a[1] if len(a) > 1 else a[0]
        if not Path(args.image).is_file():
            print(f"FAIL: the data-patch image is missing: {args.image}", file=sys.stderr)
            return 2
    image_sha = sha1_file(Path(args.image)) if args.data_patch else ""

    # Per-source compiler. The CRI section uses ee-gcc 2.96. The game code uses 3.2. See R17 section 4.2.
    # 每源编译器（CRI 段用 ee-gcc 2.96，游戏代码用 3.2；见 R17 §4.2）
    cc_map = {}
    if args.cc_map and Path(args.cc_map).is_file():
        # Line 1 is the header row (source-basename<TAB>compiler). Skip it here, before the
        # format check below: the header is not a data row, and the check would report FAIL.
        # 第 1 行是表头（source-basename<TAB>compiler）。必须在这里跳过——它先于下面的格式校验，
        # 否则校验会把表头当成非法数据行并 FAIL。
        for line in Path(args.cc_map).read_text(encoding="utf-8").splitlines()[1:]:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            a = line.split()
            if len(a) < 2:
                print(f"FAIL: bad cc-map line format: {line!r}", file=sys.stderr)
                return 2
            tag = a[1]
            if tag == "cri":
                if not args.gcc_cri:
                    print("FAIL: cc-map uses cri, but --gcc-cri is absent", file=sys.stderr)
                    return 2
                cc_map[a[0]] = args.gcc_cri
            elif tag == "game":
                cc_map[a[0]] = args.gcc
            else:
                # An absolute path is also permitted, but it must be a real executable: the map
                # is repo content, and a typo or a crafted entry must fail loudly (R30 finding B5).
                # 也允许绝对路径，但必须是真实可执行文件：该表是仓库内容，写错或被构造都必须显式失败（R30 B5）。
                if not Path(tag).is_file() or not os.access(tag, os.X_OK):
                    print(f"FAIL: cc-map entry {a[0]!r} names a compiler that is not an executable file: {tag!r}",
                          file=sys.stderr)
                    return 2
                cc_map[a[0]] = tag
    _ver_cache: dict[str, str] = {}

    def cc_version(cc: str) -> str:
        if cc not in _ver_cache:
            _ver_cache[cc] = tool_version(cc)
        return _ver_cache[cc]

    global OBJCOPY, READELF
    bindir = Path(args.as_).parent
    for name in ("mips-ps2-decompals-objcopy", "objcopy"):
        c = bindir / name
        if c.is_file():
            OBJCOPY = str(c); break
    for name in ("mips-ps2-decompals-readelf", "readelf"):
        c = bindir / name
        if c.is_file():
            READELF = str(c); break
    cc_ver, as_ver = tool_version(args.gcc), tool_version(args.as_)
    base_cflags = args.cflags.split()
    base_asflags = args.asflags.split()

    todo, cached = [], 0
    seen = set()
    # Hash the include tree once per run: every source depends on it, and re-hashing it per source
    # would dominate the run (R30 finding B6).
    # 每次运行只哈希一次 include 树：每个源都依赖它，逐源重算会成为主要开销（R30 B6）。
    inc = include_digest(args.include)
    for line in Path(args.sources).read_text(encoding="utf-8").splitlines():
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            print(f"FAIL: bad sources line format: {line!r}", file=sys.stderr)
            return 2
        key, kind, srcfile = parts
        if key in seen:                      # Several symbols use the same source. Compile it once.
            continue
        seen.add(key)
        try:
            # The key names the output object and its stamp. A key that is not a plain path
            # component would write outside `--objdir` (R30 finding B5).
            # key 决定输出对象与 stamp 的文件名。不是普通路径分量的 key 会写到 `--objdir` 之外（R30 B5）。
            key = at2_io.safe_symbol(key, what="sources key")
        except ValueError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 2
        src = Path(srcfile)
        if not src.is_file():
            print(f"FAIL: replacement source is missing: {src}", file=sys.stderr)
            return 2
        # The source path is repo-derived too: keep it inside the project directory (the mixed
        # build runs from the repository root) so a crafted TSV cannot compile an arbitrary file.
        # 源路径同样是仓库派生：必须留在项目目录内（混合构建从仓库根运行），被构造的 TSV 无法编译任意文件。
        cwd = Path.cwd().resolve()
        cand = src.resolve()
        if cand != cwd and cwd not in cand.parents:
            print(f"FAIL: the replacement source {srcfile} is outside the project directory {cwd}",
                  file=sys.stderr)
            return 2
        bad = forbidden_flag(extra.get(key, ""))
        if bad:
            print(f"FAIL: {key} carries {bad}", file=sys.stderr)
            return 2
        ex = extra.get(key, "")
        gcc = (cc_map.get(key, args.gcc) if kind == "cc" else args.gcc)
        ver = cc_version(gcc) if kind == "cc" else as_ver
        base = " ".join(base_cflags if kind == "cc" else base_asflags)
        # The stamp must cover the **base flags** and the **per-source compiler**. A new
        # MATCHED_CFLAGS value or compiler must invalidate the cache.
        # al4: from 2026-10-04, a cc object has its .text* alignment lowered to 4 (see the
        #      objcopy call in the build). The version string has a suffix, so an old cache
        #      entry is invalid.
        # stamp 必须覆盖**基础标志**、**每源编译器**与 **include 树内容**：MATCHED_CFLAGS/编译器/
        # 头文件任何一个被换掉都要失效重建
        # al4：2026-10-04 起 cc 对象统一把 .text* 段对齐降到 4（见 build 里的 objcopy），
        #      版本串加后缀让旧缓存失效重建。
        want = f"{kind}|{ver}|al4|{base}|{ex}|{gcc}|{inc}|{sha1_file(src)}"
        if args.data_patch:
            # The patch result depends on the target symbol, the asm block (derived from it) and
            # the baseline image. Any of them changing must rebuild the object.
            # 补丁结果取决于目标符号、它派生的 asm 块与基线镜像；任一变化都要重建。
            want += f"|dp={symof.get(key, key)}:{image_sha}"
        elif jtbl.get(key):
            want += f"|jtbl={jtbl[key]}"
        stamp = objdir / f"{key}.stamp"
        obj = objdir / f"{key}.o"
        if not args.no_cache and obj.is_file() and stamp.is_file() and stamp.read_text() == want:
            cached += 1
            continue
        todo.append((key, kind, src, ex, want, obj, stamp, gcc))

    def build(item):
        key, kind, src, ex, want, obj, stamp, gcc = item
        if kind == "cc":            cmd = [gcc, *base_cflags, *ex.split(), "-I", args.include, "-c", "-o", str(obj), str(src)]
        else:
            cmd = [args.as_, *base_asflags, "-I", args.include, "-o", str(obj), str(src)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            return (key, r.stderr.strip().splitlines()[-3:] if r.stderr else ["<no stderr>"])
        if kind == "cc":
            # Critical fix (2026-10-04): some C sources (for example 8-byte types or a jump
            # table in an m2c draft) make GCC align a `.text.<fn>` section to 8. The original
            # assembly block requires only alignment 4. The linker then inserts fill, the
            # whole payload shifts, and the payload check fails.
            # This code forces the alignment of every `.text*` section of the object to 4
            # (the same as splat `.align 2`).
            # ⚠️ 关键修复（2026-10-04）：某些 C 源（如 m2c 草稿里出现 8 字节类型/跳转表）会让 GCC 把
            #    `.text.<fn>` 段对齐到 8，而原汇编块只要求 4 对齐 → 链接器插入填充 → 载荷整体位移、载荷校验变红。
            #    这里统一把该对象所有 `.text*` 段的对齐强制为 4（与 splat 的 `.align 2` 一致）。
            force_text_align4(obj)
            # An object assembled by ee-gcc 2.96 (CRI section) also has a `.symtab sh_info`
            # value that disagrees with the LOCAL symbol count. GNU ld rejects it. This code
            # recomputes the value from the ELF specification (see the fix_symtab_info docstring).
            # ee-gcc 2.96（CRI 段）还会写出 `.symtab sh_info` 与 LOCAL 符号数不一致的对象，
            # GNU ld 直接拒绝；按 ELF 规范重算（见 fix_symtab_info 的 docstring）。
            fix_symtab_info(obj)
            # jtbl (2026-10-07): a real `switch` makes its own `.rodata` jump table. This code
            # redirects its reference to the existing splat `jtbl_*` symbol. The `.rodata`
            # section then has no reference and the link discards it with /DISCARD/. The code
            # bytes then agree with the original.
            # jtbl（2026-10-07）：真 `switch` 会自产 `.rodata` 跳转表；把它的引用改指到 splat 既有的
            # `jtbl_*` 符号，`.rodata` 随即变成无人引用的段（被 /DISCARD/ 丢掉）⇒ 代码字节与原版一致。
            if args.data_patch:
                # The data patch subsumes the jtbl patch (a switch table is just another data
                # reference), and it also handles a function that has a switch table *and* a
                # string: the jtbl patch requires the table at .rodata offset 0, which such a
                # function does not satisfy.
                # 数据改指覆盖 jtbl 改指（跳转表无非另一种数据引用），并能处理「跳转表 + 字符串」同时存在的
                # 函数——jtbl 补丁要求表在 .rodata 偏移 0，这种函数不满足。
                sym = symof.get(key, key)
                asm = Path(args.data_patch_asm_dir) / f"{sym}.s"
                if not asm.is_file():
                    return (key, ["the data patch needs the asm block: %s" % asm])
                ok, msg = DATP.patch(obj, sym, asm, Path(args.image), obj)
                if not ok:
                    return (key, ["data patch failed: %s" % msg])
            else:
                table = jtbl.get(key)
                if table:
                    if JTBL is None:
                        return (key, ["the jtbl_patch module is necessary, but the import failed"])
                    ok, msg = JTBL.patch(obj, table, obj)
                    if not ok:
                        return (key, ["jtbl patch failed: %s" % msg])
        stamp.write_text(want, encoding="utf-8")
        return None

    fails = []
    if todo:
        workers = max(1, min(args.jobs, len(todo)))
        with cf.ThreadPoolExecutor(max_workers=workers) as ex_:
            for res in ex_.map(build, todo):
                if res:
                    fails.append(res)
    for key, err in fails:
        print(f"FAIL: {args.label} compile failed for {key}:", file=sys.stderr)
        for l in err:
            print("   " + l, file=sys.stderr)
    if fails:
        return 1
    print(f"  {args.label}: rebuilt {len(todo)}, cache hits {cached}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
