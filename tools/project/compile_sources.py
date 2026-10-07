#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""增量编译/汇编驱动：给 build_hybrid.sh 用，只重建「源或标志变了」的对象。

为什么需要：
  hybrid 构建要对每个已 C 化符号编译一次 C（或汇编一次桩），并按符号汇编 residual 对象。
  850 个符号时单次全量约 4–6 分钟；到几千个符号后，每批验证都会变成瓶颈。
  本脚本按「源文件内容 sha1 + 编译标志 + 工具链版本」做 stamp，命中即跳过，并 4 路并行。

输入（全部临时文件，派生）：
  --sources TSV   每行 `key<TAB>kind<TAB>srcfile`；kind ∈ cc|as；key 是输出对象名（不含 .o）
  --objdir DIR    输出对象目录（stamp 写 DIR/<key>.stamp）
  --cflags  ...   基础标志（C）
  --flags-file    每源额外标志 TSV（<src-basename><TAB><flags>），键 = key
  --cc-map        每源编译器 TSV（<key><TAB><tag>），tag ∈ game|cri|<绝对路径>；
                  缺省时全部走 --gcc（向后兼容）。游戏代码 = ee-gcc 3.2-ee-040921，
                  CRI 中间件 = ee-gcc 2.96-ee-001003-1（两个归档都在 toolchain.lock.json 里，
                  CI 早已安装并导出 GCC_CRI）——见 docs/kb/reports/R17 §4.2。
  --gcc-cri       cri 编译器的路径（tag=cri 时使用）
  --jobs N        并行度（默认 4）

行为：
  * stamp 内容 = kind|工具链版本|extra-flags|srcfile-sha1；不匹配或对象缺失才重建；
  * --no-cache 强制全量；
  * 任何一条编译失败 → 非 0 退出并打印最后几行错误。

用法（由 build_hybrid.sh 调用，也可单独跑做一致性对照）：
  python3 routebjp/tools/compile_sources.py --sources ... --objdir ... \
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
try:                                   # jtbl 跳转表修补（同目录；缺失时退化为不支持）
    import jtbl_patch as JTBL          # noqa: E402
except Exception:                      # pragma: no cover
    JTBL = None


OBJCOPY: str | None = None
READELF: str | None = None


def force_text_align4(obj: Path) -> None:
    """把对象里所有 `.text*` 输入段的对齐强制为 4。

    背景（2026-10-04，见 P-30）：某些 C 源会让 GCC 把 `.text.<fn>` 段对齐到 8，
    而原汇编块（splat 的 `.align 2`）只要求 4；链接器会插入填充 → 载荷位移、棘轮变红。
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
    """修正 ELF32 对象 `.symtab` 的 `sh_info`（= 第一个非 LOCAL 符号下标）。

    背景（2026-10-06，CI PR #3）：`ee-gcc 2.96` 汇编出的对象把 `gcc2_compiled.` /
    `__gnu_compiled_c` 两个 LOCAL 符号放在全局符号**之前**，但 `sh_info` 只数到 8，
    而实际有 10 个 LOCAL ⇒ GNU ld 报
    `.symtab local symbol at index 8 (>= sh_info of 8)` / `error adding symbols: bad value`，
    整个混合构建在链接期挂掉（M1 基线仍然绿，所以只有全量构建能发现）。
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
    ap.add_argument("--sources", required=True, help="TSV：key<TAB>kind<TAB>srcfile")
    ap.add_argument("--objdir", required=True)
    ap.add_argument("--gcc", required=True)
    ap.add_argument("--gcc-cri", default="", help="CRI 段编译器（tag=cri）；未提供且用到 cri 时报错")
    ap.add_argument("--cc-map", default="", help="每源编译器 TSV：<key><TAB><tag>（tag=game|cri|路径）")
    ap.add_argument("--as", dest="as_", required=True)
    ap.add_argument("--include", default="include")
    ap.add_argument("--cflags", default="")
    ap.add_argument("--asflags", default="-EL -march=r5900")
    ap.add_argument("--flags-file", default="")
    ap.add_argument("--jtbl-tables", default="",
                    help="每源跳转表 TSV：<key><TAB><jtbl_符号>；编译后用 jtbl_patch 把 C 自产表的引用"
                         "改指到既有数据符号（见 tools/project/jtbl_patch.py）")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--label", default="源")
    args = ap.parse_args()

    objdir = Path(args.objdir)
    objdir.mkdir(parents=True, exist_ok=True)

    extra = {}
    if args.flags_file and Path(args.flags_file).is_file():
        for line in Path(args.flags_file).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                a = line.split()
                extra[a[0]] = " ".join(a[1:])

    # 跳转表 TSV（<key>\t<jtbl_符号>）：编译后把 C 自产 `.rodata` 表的引用改指到既有数据符号。
    jtbl = {}
    if args.jtbl_tables and Path(args.jtbl_tables).is_file():
        for line in Path(args.jtbl_tables).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                a = line.split()
                if len(a) >= 2:
                    jtbl[a[0]] = a[1]

    # 每源编译器（CRI 段用 ee-gcc 2.96，游戏代码用 3.2；见 R17 §4.2）
    cc_map = {}
    if args.cc_map and Path(args.cc_map).is_file():
        for line in Path(args.cc_map).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            a = line.split()
            if len(a) < 2:
                print(f"FAIL: cc-map 行格式不对: {line!r}", file=sys.stderr)
                return 2
            tag = a[1]
            if tag == "cri":
                if not args.gcc_cri:
                    print("FAIL: cc-map 用到 cri，但没有 --gcc-cri", file=sys.stderr)
                    return 2
                cc_map[a[0]] = args.gcc_cri
            elif tag == "game":
                cc_map[a[0]] = args.gcc
            else:
                cc_map[a[0]] = tag          # 允许直接写绝对路径
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
            print(f"FAIL: sources 行格式不对: {line!r}", file=sys.stderr)
            return 2
        key, kind, srcfile = parts
        if key in seen:                      # 同一源被多个符号引用：只编一次
            continue
        seen.add(key)
        src = Path(srcfile)
        if not src.is_file():
            print(f"FAIL: 缺少替换源 {src}", file=sys.stderr)
            return 2
        ex = extra.get(key, "")
        gcc = (cc_map.get(key, args.gcc) if kind == "cc" else args.gcc)
        ver = cc_version(gcc) if kind == "cc" else as_ver
        base = " ".join(base_cflags if kind == "cc" else base_asflags)
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
            # ⚠️ 关键修复（2026-10-04）：某些 C 源（如 m2c 草稿里出现 8 字节类型/跳转表）会让 GCC 把
            #    `.text.<fn>` 段对齐到 8，而原汇编块只要求 4 对齐 → 链接器插入填充 → 载荷整体位移、棘轮变红。
            #    这里统一把该对象所有 `.text*` 段的对齐强制为 4（与 splat 的 `.align 2` 一致）。
            force_text_align4(obj)
            # ee-gcc 2.96（CRI 段）还会写出 `.symtab sh_info` 与 LOCAL 符号数不一致的对象，
            # GNU ld 直接拒绝；按 ELF 规范重算（见 fix_symtab_info 的 docstring）。
            fix_symtab_info(obj)
            # jtbl（2026-10-07）：真 `switch` 会自产 `.rodata` 跳转表；把它的引用改指到 splat 既有的
            # `jtbl_*` 符号，`.rodata` 随即变成无人引用的段（被 /DISCARD/ 丢掉）⇒ 代码字节与原版一致。
            table = jtbl.get(key)
            if table:
                if JTBL is None:
                    return (key, ["需要 jtbl_patch 模块，但导入失败"])
                ok, msg = JTBL.patch(obj, table, obj)
                if not ok:
                    return (key, ["jtbl 修补失败：%s" % msg])
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
        print(f"FAIL: {args.label}编译失败 {key}:", file=sys.stderr)
        for l in err:
            print("   " + l, file=sys.stderr)
    if fails:
        return 1
    print(f"  {args.label}：重建 {len(todo)}，命中缓存 {cached}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
