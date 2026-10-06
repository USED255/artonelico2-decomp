#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""布局无关的构建驱动（私有主仓库 + 未来公开仓库共用一套入口）。

设计目标
--------
把 `routebjp/build.sh`、`build_hybrid.sh`、`build_m2.sh` 里的**路径假设**收敛到本脚本：
那些脚本仍然保留为「薄包装 / 被驱动者」，但「项目根在哪、载荷叫什么、期望 sha1 是多少、
objdiff 配置在哪」全部由本脚本按 `--root` + `--layout` 解析，主仓库与公开仓库共用同一套命令。

子命令
------
  configure --game <ELF>      校验原版 ELF 的 sha1，写 `<root>/build/config.json`。
                              `--layout repo` 且未给 `--game` 时 no-op（主仓库沿用现有配置）。
  build [--stage all|m1|hybrid|m2]
                              M1 基线 → 载荷 sha1 棘轮断言 → hybrid → 再断言（两处都断言，
                              任何一次不符都打印期望/实际并返回非 0）；hybrid 额外与 M1 产物 cmp。
  report [--out JSON] [--full]
                              用 objdiff-cli 生成报告（默认 `<root>/build/report.json`）。
                              `--full` 先跑 `tools/build/gen_objdiff_full.py` 出全量 objdiff.json。
  delta --base <git-ref>      只对 git diff 里改动的**已匹配源**逐个 objdiff，要求 100%；
                              任一非 100% 返回非 0，产物缺失返回 2（先跑 build）。
  check-config                打印解析出的全部路径与存在性，便于自检。

布局约定
--------
  --layout repo   主仓库：`--root routebjp`，项目根 = routebjp/
                  （asm/ build/ src/matched/ config/ SLPS_258.19.yaml），工具在 `<root>/../tools`。
  --layout flat   公开仓库：`--root .`，项目根 = .（asm/ build/ src/matched/ config/ splat.yaml），
                  工具在 `<root>/tools`。
  --layout auto   默认：项目根下存在 `tools/` 判为 flat，否则判为 repo。

退出码：0 成功；1 断言失败（棘轮 / 非 100%）；2 前置缺失（产物或工具不存在）；3 用法错误。
工具链位置（工作区外，见 docs/kb/ENV.md）：
  as/ld 由 `<root>/build.sh` 自己解析；objdiff-cli 默认 `~/eecc/objdiff-cli`（可用 OBJDIFF 覆盖）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# 已知目标（版本 → 期望值）；未知目标必须用 --expect-sha1 显式给出
# 事实源：docs/kb/facts.json（此处只做构建期默认值，不替代 facts.json）
# --------------------------------------------------------------------------- #
KNOWN_TARGETS = {
    "SLPS_258.19": {
        "game_sha1": "766836783c16b8616d3d84cfbd6af70a50b6c052",
        "game_size": 9352548,
        "payload_sha1": "7cc42d275750600d1f232b2632447f77205f3fc0",
        "payload_size": 9304936,
        "compiler": "ee-gcc 3.2-ee-040921",
    },
    "SLUS_217.88": {
        "game_sha1": None,  # 美版零售 ELF 全文件 sha1 未登记；用 --expect-sha1
        "game_size": None,
        "payload_sha1": "449efb783a9956b97355b0a5c9b3763fff33dd31",
        "payload_size": 9450984,
        "compiler": "ee-gcc 3.2-ee-040921",
    },
}

DEFAULT_OBJDIFF = os.environ.get("OBJDIFF", str(Path.home() / "eecc" / "objdiff-cli"))


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def die(msg: str, code: int = 2) -> "None":
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(code)


def run(cmd: list[str], cwd: Path, **kw) -> int:
    print("+ " + " ".join(str(c) for c in cmd) + f"   (cwd={cwd})")
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd), **kw).returncode


# --------------------------------------------------------------------------- #
# 布局解析
# --------------------------------------------------------------------------- #
class Ctx:
    def __init__(self, root: Path, layout: str, name: str | None):
        self.root = root.resolve()
        self.layout = self._layout(layout)
        self.tools = (self.root / "tools") if self.layout == "flat" else (self.root.parent / "tools")
        self.asm = self.root / "asm"
        self.build = self.root / "build"
        self.src = self.root / "src"
        self.matched = self.root / "src" / "matched"
        self.config = self.root / "config"
        self.name = name or self._detect_name()
        self.payload = self.build / f"{self.name}.bin"
        self.hybrid_payload = self.build / "hybrid" / f"{self.name}.bin"
        self.build_config = self.build / "config.json"

    def _layout(self, layout: str) -> str:
        if layout != "auto":
            return layout
        return "flat" if (self.root / "tools").is_dir() else "repo"

    def _detect_name(self) -> str:
        # 1) build/config.json（configure 写过）
        bc = self.build / "config.json"
        if bc.is_file():
            try:
                n = json.loads(bc.read_text(encoding="utf-8")).get("name")
                if n:
                    return n
            except (OSError, ValueError):
                pass
        # 2) 已知目标名的 splat yaml
        for n in KNOWN_TARGETS:
            if (self.root / f"{n}.yaml").is_file():
                return n
        # 3) flat 布局的 splat.yaml
        if (self.root / "splat.yaml").is_file():
            # 公开布局：目标名由 --name 或 build/config.json 给；缺省用目录名兜底
            return self.root.name
        # 4) 任意 yaml
        ys = sorted(p.stem for p in self.root.glob("*.yaml") if p.name != "objdiff.json")
        return ys[0] if ys else "payload"

    def expect(self) -> dict:
        """期望的载荷 sha1 / size：build/config.json > 已知目标表。"""
        if self.build_config.is_file():
            try:
                d = json.loads(self.build_config.read_text(encoding="utf-8"))
                if d.get("payload_sha1"):
                    return {"payload_sha1": d["payload_sha1"],
                            "payload_size": d.get("payload_size"),
                            "name": d.get("name", self.name)}
            except (OSError, ValueError):
                pass
        return dict(KNOWN_TARGETS.get(self.name, {}), name=self.name)

    def objdiff_cli(self) -> str:
        if Path(DEFAULT_OBJDIFF).exists() or shutil.which(DEFAULT_OBJDIFF):
            return DEFAULT_OBJDIFF
        die(f"找不到 objdiff-cli（{DEFAULT_OBJDIFF}）；用 OBJDIFF=<path> 指定", 2)

    def dump(self) -> dict:
        return {
            "layout": self.layout,
            "project_root": str(self.root),
            "tools_dir": str(self.tools),
            "name": self.name,
            "splat_yaml": str(next((self.root / f"{n}.yaml" for n in (self.name, "splat.yaml")
                                    if (self.root / f"{n}.yaml").is_file()), self.root / "splat.yaml")),
            "asm": str(self.asm),
            "build": str(self.build),
            "src": str(self.src),
            "src_matched": str(self.matched),
            "config": str(self.config),
            "payload": str(self.payload),
            "hybrid_payload": str(self.hybrid_payload),
            "objdiff_cli": DEFAULT_OBJDIFF,
        }


def make_ctx(args) -> Ctx:
    root = Path(args.root)
    if not root.is_dir():
        die(f"--root 不是目录：{root}", 3)
    return Ctx(root, args.layout, getattr(args, "name", None))


# --------------------------------------------------------------------------- #
# 子命令
# --------------------------------------------------------------------------- #
def cmd_check_config(args) -> int:
    ctx = make_ctx(args)
    info = ctx.dump()
    checks = ["asm", "build", "src", "src_matched", "config"]
    info["exists"] = {k: Path(info[k]).is_dir() for k in checks}
    info["exists"]["build.sh"] = (ctx.root / "build.sh").is_file()
    info["exists"]["build_hybrid.sh"] = (ctx.root / "build_hybrid.sh").is_file()
    info["exists"]["objdiff.json"] = (ctx.root / "objdiff.json").is_file()
    info["exists"]["payload"] = ctx.payload.is_file()
    info["expected"] = ctx.expect()
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(f"layout        : {info['layout']}")
        for k in ("project_root", "tools_dir", "name", "splat_yaml", "asm", "build", "src",
                  "src_matched", "config", "payload", "hybrid_payload", "objdiff_cli"):
            print(f"{k:14s}: {info[k]}")
        for k, v in info["exists"].items():
            print(f"  exists[{k:15s}] = {v}")
        exp = info["expected"]
        print(f"expected      : sha1={exp.get('payload_sha1')} size={exp.get('payload_size')}")
    return 0


def cmd_configure(args) -> int:
    ctx = make_ctx(args)
    if not args.game:
        if ctx.layout == "repo":
            print(f"no-op：{ctx.layout} 布局沿用现有 config（{ctx.config}/ 与 {ctx.name}.yaml），无需 configure")
            return 0
        die("flat 布局必须给 --game <ELF 路径>", 3)
    game = Path(args.game)
    if not game.is_file():
        die(f"--game 不存在：{game}", 3)
    actual = sha1_file(game)
    size = game.stat().st_size
    exp = ctx.expect()
    expect_sha = args.expect_sha1 or exp.get("game_sha1")
    expect_size = args.expect_size
    if not expect_sha:
        die(f"目标 {ctx.name} 未登记原版 ELF sha1；请用 --expect-sha1（也可 --name 指定目标）", 3)
    print(f"game   : {game}  ({size} B)")
    print(f"sha1   : {actual}")
    print(f"expect : {expect_sha}")
    if actual != expect_sha:
        die(f"原版 ELF sha1 不符：期望 {expect_sha} 实际 {actual}", 1)
    if expect_size is not None and size != int(expect_size):
        die(f"原版 ELF 大小不符：期望 {expect_size} 实际 {size}", 1)
    ctx.build.mkdir(parents=True, exist_ok=True)
    cfg = {
        "layout": ctx.layout,
        "name": ctx.name,
        "game_elf": str(game),
        "game_sha1": actual,
        "game_size": size,
        "payload_sha1": exp.get("payload_sha1"),
        "payload_size": exp.get("payload_size"),
        "compiler": exp.get("compiler"),
    }
    ctx.build_config.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"写出 {ctx.build_config}")
    return 0


def assert_payload(path: Path, label: str, exp: dict) -> None:
    if not path.is_file():
        die(f"{label}：未产出载荷 {path}（构建失败或名字不对）", 1)
    actual_sha = sha1_file(path)
    actual_size = path.stat().st_size
    print(f"  {label} 实际 : sha1={actual_sha}  size={actual_size}")
    print(f"  {label} 期望 : sha1={exp.get('payload_sha1')}  size={exp.get('payload_size')}")
    if exp.get("payload_sha1") and actual_sha != exp["payload_sha1"]:
        die(f"{label} 棘轮变红：sha1 {actual_sha} != {exp['payload_sha1']} —— 立即定位，不要带红棘轮继续", 1)
    if exp.get("payload_size") and actual_size != int(exp["payload_size"]):
        die(f"{label} 棘轮变红：size {actual_size} != {exp['payload_size']}", 1)
    print(f"  ✅ {label} 为绿：载荷逐字节一致")


def stage_script(ctx: Ctx, stage: str) -> Path:
    return ctx.root / {"m1": "build.sh", "hybrid": "build_hybrid.sh", "m2": "build_m2.sh"}[stage]


def _run_stage(ctx: Ctx, stage: str) -> None:
    script = stage_script(ctx, stage)
    if not script.is_file():
        die(f"缺少 {script}（--root/--layout 解析不对？跑 check-config 看解析结果）", 2)
    env = dict(os.environ)
    if getattr(ctx, "jobs", None):
        env["JOBS"] = str(ctx.jobs)
    print(f"── {stage}：{script.name} ──")
    if run(["bash", script.name], cwd=ctx.root, env=env) != 0:
        die(f"{script.name} 执行失败", 1)


def cmd_build(args) -> int:
    ctx = make_ctx(args)
    ctx.jobs = args.jobs
    exp = ctx.expect()
    print(f"== decomp_build build（root={ctx.root} layout={ctx.layout} name={ctx.name} stage={args.stage}）==")
    if args.stage in ("all", "m1"):
        _run_stage(ctx, "m1")
        assert_payload(ctx.payload, "M1", exp)
    if args.stage in ("all", "hybrid"):
        _run_stage(ctx, "hybrid")
        assert_payload(ctx.hybrid_payload, "M2.5 混合", exp)
        m1 = ctx.payload
        if m1.is_file():
            if not _cmp(m1, ctx.hybrid_payload):
                die("混合产物与 M1 产物存在字节差异（cmp 不一致）", 1)
            print("  ✅ M2.5 与 M1 产物 cmp 无差异")
        else:
            print("  （无 M1 产物，跳过 cmp）")
    if args.stage == "m2":
        _run_stage(ctx, "m2")
    print("== build 通过 ==")
    return 0


def _cmp(a: Path, b: Path) -> bool:
    return a.read_bytes() == b.read_bytes()


def cmd_report(args) -> int:
    ctx = make_ctx(args)
    out = Path(args.out) if args.out else ctx.build / "report.json"
    out = out if out.is_absolute() else (Path.cwd() / out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cli = ctx.objdiff_cli()
    if args.full:
        gen = ctx.tools / "build" / "gen_objdiff_full.py"
        if not gen.is_file():
            die(f"--full 需要 {gen}", 2)
        if run([sys.executable, gen, "--project", str(ctx.root),
                "--code-only", "--objdiff", cli], cwd=ctx.root) != 0:
            die("gen_objdiff_full.py 失败", 1)
        proj_dir = ctx.build / "objdiff-code"
    else:
        if not (ctx.root / "objdiff.json").is_file():
            die(f"缺少 {ctx.root}/objdiff.json；加 --full 生成全量配置，或先跑 build/gen_objdiff_full.py", 2)
        proj_dir = ctx.root
    print(f"── report：objdiff-cli report generate -p {proj_dir} -o {out} ──")
    if run([cli, "report", "generate", "-p", str(proj_dir), "-o", str(out)], cwd=ctx.root) != 0:
        die("objdiff-cli report generate 失败", 1)
    data = json.loads(out.read_text(encoding="utf-8"))
    m = data.get("measures", {})
    print(f"  matched_code={m.get('matched_code')}/{m.get('total_code')} "
          f"({m.get('matched_code_percent')}%)  "
          f"matched_functions={m.get('matched_functions')}/{m.get('total_functions')} "
          f"({m.get('matched_functions_percent')}%)  units={m.get('total_units')}")
    return 0


def _matched_symbols(ctx: Ctx) -> set:
    fp = ctx.config / "matched_symbols.txt"
    if not fp.is_file():
        die(f"缺少 {fp}", 2)
    out = set()
    for line in fp.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.add(s)
    return out


def cmd_delta(args) -> int:
    ctx = make_ctx(args)
    if not args.base:
        die("delta 必须给 --base <git-ref>", 3)
    matched = _matched_symbols(ctx)
    rel_src = os.path.relpath(ctx.matched, ctx.root)
    cp = subprocess.run(["git", "-C", str(ctx.root), "diff", "--name-only", args.base, "--", rel_src],
                        capture_output=True, text=True)
    if cp.returncode != 0:
        die(f"git diff 失败（base={args.base}）：{cp.stderr.strip()}", 2)
    changed = [l for l in cp.stdout.splitlines() if l.strip().endswith(".c")]
    if not changed:
        print(f"delta：相对 {args.base} 没有改动的匹配源（{rel_src}/），无需 objdiff")
        return 0
    cli = ctx.objdiff_cli()
    out_dir = ctx.build / "delta"
    out_dir.mkdir(parents=True, exist_ok=True)
    bad, missing = [], []
    for rel in changed:
        sym = Path(rel).stem
        if sym not in matched:
            print(f"  skip {rel}（不在 config/matched_symbols.txt 里）")
            continue
        target = ctx.build / "asm" / "cod" / f"{sym}.o"
        base = ctx.build / "hybrid" / "obj" / f"{sym}.o"
        if not target.is_file() or not base.is_file():
            missing.append(f"{sym}（target={target} base={base}）")
            continue
        rep = out_dir / f"{sym}.json"
        rc = run([cli, "diff", "-1", str(target), "-2", str(base), "-o", str(rep), "--format", "json"],
                 cwd=ctx.root)
        if rc != 0:
            bad.append(f"{sym}（objdiff 退出码 {rc}）")
            continue
        pct = _fn_percent(rep, sym)
        if pct is None:
            bad.append(f"{sym}（报告里找不到函数符号）")
        elif pct != 100.0:
            bad.append(f"{sym}（{pct:.1f}% ≠ 100%）")
        else:
            print(f"  ✅ {sym} 100%")
    if missing:
        print("FAIL: 以下匹配源缺 objdiff 产物（先跑 `decomp_build.py build`）：", file=sys.stderr)
        for x in missing:
            print(f"  - {x}", file=sys.stderr)
        return 2
    if bad:
        print("FAIL: 以下匹配源未达到 100%：", file=sys.stderr)
        for x in bad:
            print(f"  - {x}", file=sys.stderr)
        return 1
    print(f"delta 通过：{len(changed)} 个改动匹配源全部 100%")
    return 0


def _fn_percent(report: Path, sym: str):
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for side in ("left", "right"):
        for s in data.get(side, {}).get("symbols", []):
            if s.get("kind") == "SYMBOL_FUNCTION" and s.get("name") in (sym, f"{sym}_c"):
                return float(s.get("match_percent") or 0.0)
    # 单函数对象：退化为第一个函数
    for side in ("left", "right"):
        for s in data.get(side, {}).get("symbols", []):
            if s.get("kind") == "SYMBOL_FUNCTION":
                return float(s.get("match_percent") or 0.0)
    return None


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        prog="decomp_build.py",
        description="布局无关的匹配反编译构建驱动（repo=私有主仓库 / flat=公开仓库）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="项目目录（repo 布局如 routebjp；flat 布局如 .）")
    ap.add_argument("--layout", choices=["auto", "repo", "flat"], default="auto",
                    help="布局：repo=项目根在仓库子目录、工具在 <root>/../tools；flat=项目根=仓库根、工具在 <root>/tools")
    ap.add_argument("--name", default=None, help="目标名（默认按 <name>.yaml / build/config.json 探测）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check-config", help="打印解析出的路径与存在性")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_check_config)

    p = sub.add_parser("configure", help="校验原版 ELF sha1 并写 <root>/build/config.json")
    p.add_argument("--game", default=None, help="原版 ELF 路径")
    p.add_argument("--expect-sha1", default=None, help="期望的原版 ELF sha1（未知目标必填）")
    p.add_argument("--expect-size", default=None, help="期望的原版 ELF 大小")
    p.set_defaults(func=cmd_configure)

    p = sub.add_parser("build", help="M1 / hybrid / m2 构建并断言棘轮（失败非 0）")
    p.add_argument("--stage", choices=["all", "m1", "hybrid", "m2"], default="all")
    p.add_argument("--jobs", default=None, help="并行度（透传 JOBS 给构建脚本）")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("report", help="objdiff 报告")
    p.add_argument("--out", default=None, help="报告输出（默认 <root>/build/report.json）")
    p.add_argument("--full", action="store_true", help="先跑 tools/build/gen_objdiff_full.py 生成全量配置")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("delta", help="只对 git diff 的改动匹配源逐个 objdiff，要求 100%%")
    p.add_argument("--base", default=None, help="git ref（如 origin/main）")
    p.set_defaults(func=cmd_delta)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
