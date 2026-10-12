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
                  (<key><TAB><tag>). tag is game, cri, or an
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
  --cc-map        每源编译器文件：表头行 + 数据行（<key><TAB><tag>），tag ∈ game|cri|<绝对路径>；
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
try:                                   # jtbl jump table patch in the same directory. The module is optional.
    import jtbl_patch as JTBL          # noqa: E402
except Exception:                      # pragma: no cover
    JTBL = None


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
                cc_map[a[0]] = tag          # An absolute path is also permitted.
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
        src = Path(srcfile)
        if not src.is_file():
            print(f"FAIL: replacement source is missing: {src}", file=sys.stderr)
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
        # stamp 必须覆盖**基础标志**与**每源编译器**：MATCHED_CFLAGS/编译器被换掉时要失效重建
        # al4：2026-10-04 起 cc 对象统一把 .text* 段对齐降到 4（见 build 里的 objcopy），
        #      版本串加后缀让旧缓存失效重建。
        want = f"{kind}|{ver}|al4|{base}|{ex}|{gcc}|{sha1_file(src)}"
        if jtbl.get(key):
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
