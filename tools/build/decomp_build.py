#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layout-independent build driver. The private main repository and the public repository share it.

The driver collects the path assumptions of `build.sh` and `build_mixed.sh` in
one place. Those two scripts stay as thin wrappers. The driver resolves the
project root, the payload name, the expected SHA1, and the objdiff setup from
`--root` and `--layout`.

Subcommands
-----------
  configure --game <ELF>
      Check the SHA1 of the retail ELF. Write `<root>/build/config.json`.
      With `--layout repo` and no `--game`, this command does nothing. The
      private repository keeps its current configuration.
  build [--stage all|baseline|assemble|mixed|fast]
      Run the baseline build. Run the payload check. Run the mixed build. Run
      the payload check again. Each mismatch prints the expected value and the
      actual value, then the command returns a non-zero code. The mixed build
      also compares its payload with the baseline payload.
      `all`, `baseline`, and `mixed` are the full pipeline. `assemble` stops the
      baseline after the assembler (no link, no baseline payload). `fast` does
      that, then runs the mixed build and checks the mixed payload only. CI uses
      `fast` for a pure-source pull request and `all` everywhere else.
  report [--out JSON] [--full]
      Generate the objdiff report. The default output is
      `<root>/build/report.json`. With `--full`, the command first runs
      `tools/build/gen_objdiff_full.py` and writes a full objdiff.json.
  delta --base <git-ref>
      Compare each changed matched source with objdiff. Each function must
      match 100 percent. A mismatch returns a non-zero code. A missing object
      returns 2. Run the build first.
  check-config
      Print each resolved path and its presence. Use this command to check the
      layout.

Layout
------
  --layout repo   Main repository. Use `--root matching-jp`. The project root is
                  matching-jp/ with asm/, build/, src/matched/, config/, and
                  SLPS_258.19.yaml. The tools are in `<root>/../tools`.
  --layout flat   Public repository. Use `--root .`. The project root is `.`
                  with asm/, build/, src/matched/, config/, and splat.yaml.
                  The tools are in `<root>/tools`.
  --layout auto   Default. If the project root holds `tools/`, the layout is
                  flat. If not, the layout is repo.

Exit codes: 0 success, 1 failed check, 2 missing input or missing tool, 3 usage error.
The toolchain stays outside the workspace. See docs/kb/ENV.md. The script
`<root>/build.sh` finds as and ld. The objdiff-cli default is
`~/eecc/objdiff-cli`. Set OBJDIFF to use another path.

布局无关的构建驱动（私有主仓库与公开仓库共用一套入口）。

设计目标
--------
把 `matching-jp/build.sh` 与 `build_mixed.sh` 里的路径假设收敛到本脚本。
那两个脚本仍是薄包装，但项目根、载荷名、期望 sha1 与 objdiff 配置
全部由本脚本按 `--root` 与 `--layout` 解析，主仓库与公开仓库共用同一套命令。

子命令
------
  configure     校验原版 ELF 的 sha1，写 `<root>/build/config.json`。
  build         跑 baseline 构建、载荷校验、mixed 构建与第二次校验。
                `--stage assemble` 只装配（不链接、不校验基线载荷）；`--stage fast` 在此基础上
                再跑 mixed 构建，只校验混合载荷 —— CI 对纯源码 PR 用 fast，其余一律 all。
  report        用 objdiff-cli 生成报告；`--full` 先生成全量 objdiff.json。
  delta         只对 git diff 里改动的已匹配源逐个 objdiff，要求 100%。
  check-config  打印解析出的全部路径与存在性，便于自检。

布局约定
--------
  repo  项目根在仓库子目录（如 matching-jp/），工具在 `<root>/../tools`。
  flat  项目根就是仓库根，工具在 `<root>/tools`。
  auto  项目根下有 `tools/` 判为 flat，否则判为 repo。

退出码：0 成功；1 校验失败；2 前置缺失；3 用法错误。
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
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
import matched_ledger

# --------------------------------------------------------------------------- #
# Known targets (version -> expected values). An unknown target needs an
# explicit --expect-sha1. The source of truth is docs/kb/facts.json. These
# values are build defaults only.
#
# 已知目标（版本 -> 期望值）；未知目标必须用 --expect-sha1 显式给出。
# 事实源是 docs/kb/facts.json，此处只做构建期默认值。
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
        "game_sha1": None,  # the full-file SHA1 of the US retail ELF is not registered; use --expect-sha1
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
# Layout resolution
#
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
        self.mixed_payload = self.build / "mixed" / f"{self.name}.bin"
        self.build_config = self.build / "config.json"

    def _layout(self, layout: str) -> str:
        if layout != "auto":
            return layout
        return "flat" if (self.root / "tools").is_dir() else "repo"

    def _detect_name(self) -> str:
        # 1) build/config.json (configure writes it)  configure 写过的 build/config.json
        bc = self.build / "config.json"
        if bc.is_file():
            try:
                n = json.loads(bc.read_text(encoding="utf-8")).get("name")
                if n:
                    return n
            except (OSError, ValueError):
                pass
        # 2) a splat yaml with a known target name  已知目标名的 splat yaml
        for n in KNOWN_TARGETS:
            if (self.root / f"{n}.yaml").is_file():
                return n
        # 3) splat.yaml in the flat layout  flat 布局的 splat.yaml
        if (self.root / "splat.yaml").is_file():
            # Public layout: --name or build/config.json gives the target name, and the directory name is the fallback.
            # 公开布局：目标名由 --name 或 build/config.json 给；缺省用目录名兜底
            return self.root.name
        # 4) any yaml  任意 yaml
        ys = sorted(p.stem for p in self.root.glob("*.yaml") if p.name != "objdiff.json")
        return ys[0] if ys else "payload"

    def expect(self) -> dict:
        """Return the expected payload SHA1 and size. build/config.json wins over the known-target table.

        返回期望的载荷 sha1 与大小：build/config.json 优先于已知目标表。
        """
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
        die(f"objdiff-cli not found ({DEFAULT_OBJDIFF}). Set OBJDIFF=<path>.", 2)

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
            "mixed_payload": str(self.mixed_payload),
            "objdiff_cli": DEFAULT_OBJDIFF,
        }


def make_ctx(args) -> Ctx:
    root = Path(args.root)
    if not root.is_dir():
        die(f"--root is not a directory: {root}", 3)
    return Ctx(root, args.layout, getattr(args, "name", None))


# --------------------------------------------------------------------------- #
# Subcommands
#
# 子命令
# --------------------------------------------------------------------------- #
def cmd_check_config(args) -> int:
    ctx = make_ctx(args)
    info = ctx.dump()
    checks = ["asm", "build", "src", "src_matched", "config"]
    info["exists"] = {k: Path(info[k]).is_dir() for k in checks}
    info["exists"]["build.sh"] = (ctx.root / "build.sh").is_file()
    info["exists"]["build_mixed.sh"] = (ctx.root / "build_mixed.sh").is_file()
    info["exists"]["objdiff.json"] = (ctx.root / "objdiff.json").is_file()
    info["exists"]["payload"] = ctx.payload.is_file()
    info["expected"] = ctx.expect()
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(f"layout        : {info['layout']}")
        for k in ("project_root", "tools_dir", "name", "splat_yaml", "asm", "build", "src",
                  "src_matched", "config", "payload", "mixed_payload", "objdiff_cli"):
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
            print(f"no-op: the {ctx.layout} layout keeps the current config ({ctx.config}/ and {ctx.name}.yaml); configure is not necessary")
            return 0
        die("The flat layout needs --game <ELF path>.", 3)
    game = Path(args.game)
    if not game.is_file():
        die(f"--game does not exist: {game}", 3)
    actual = sha1_file(game)
    size = game.stat().st_size
    exp = ctx.expect()
    expect_sha = args.expect_sha1 or exp.get("game_sha1")
    expect_size = args.expect_size
    if not expect_sha:
        die(f"No retail ELF SHA1 is registered for target {ctx.name}. Use --expect-sha1. You can also set --name.", 3)
    print(f"game   : {game}  ({size} B)")
    print(f"sha1   : {actual}")
    print(f"expect : {expect_sha}")
    if actual != expect_sha:
        die(f"Retail ELF SHA1 mismatch: expected {expect_sha}, actual {actual}", 1)
    if expect_size is not None and size != int(expect_size):
        die(f"Retail ELF size mismatch: expected {expect_size}, actual {size}", 1)
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
    print(f"wrote {ctx.build_config}")
    return 0


def assert_payload(path: Path, label: str, exp: dict) -> None:
    if not path.is_file():
        die(f"{label}: no payload at {path}. The build failed or the name is wrong.", 1)
    actual_sha = sha1_file(path)
    actual_size = path.stat().st_size
    print(f"  {label} actual: sha1={actual_sha}  size={actual_size}")
    print(f"  {label} expect: sha1={exp.get('payload_sha1')}  size={exp.get('payload_size')}")
    if exp.get("payload_sha1") and actual_sha != exp["payload_sha1"]:
        die(f"{label} payload check failed: sha1 {actual_sha} != {exp['payload_sha1']}. Find the cause before you continue.", 1)
    if exp.get("payload_size") and actual_size != int(exp["payload_size"]):
        die(f"{label} payload check failed: size {actual_size} != {exp['payload_size']}", 1)
    print(f"  OK: {label} matches byte for byte")


def stage_script(ctx: Ctx, stage: str) -> Path:
    return ctx.root / {"baseline": "build.sh", "assemble": "build.sh", "mixed": "build_mixed.sh"}[stage]


def _run_stage(ctx: Ctx, stage: str) -> None:
    script = stage_script(ctx, stage)
    if not script.is_file():
        die(f"Missing {script}. Check the --root and --layout values with check-config.", 2)
    env = dict(os.environ)
    if getattr(ctx, "jobs", None):
        env["JOBS"] = str(ctx.jobs)
    # `assemble` runs build.sh only up to the assembled baseline (no link, no payload extraction).
    # Set the flag explicitly for every stage so an inherited BASELINE_ASSEMBLE_ONLY=1 in the
    # caller's shell cannot silently change what a stage does.
    # `assemble` 只跑到装配为止（不链接、不抽载荷）。对每个 stage 显式赋值，避免调用者 shell 里
    # 残留的 BASELINE_ASSEMBLE_ONLY=1 悄悄改变某一阶段的行为。
    env["BASELINE_ASSEMBLE_ONLY"] = "1" if stage == "assemble" else "0"
    print(f"-- {stage}: {script.name} --")
    if run(["bash", script.name], cwd=ctx.root, env=env) != 0:
        die(f"{script.name} failed", 1)


def cmd_build(args) -> int:
    ctx = make_ctx(args)
    ctx.jobs = args.jobs
    exp = ctx.expect()
    print(f"== decomp_build build (root={ctx.root} layout={ctx.layout} name={ctx.name} stage={args.stage}) ==")
    if args.stage in ("all", "baseline"):
        _run_stage(ctx, "baseline")
        assert_payload(ctx.payload, "baseline build", exp)
    if args.stage in ("assemble", "fast"):
        # assemble: the pure-asm baseline without its link. `fast` then runs the mixed build below.
        # assemble：只装配的纯汇编基线；`fast` 会接着跑下面的混合构建。
        _run_stage(ctx, "assemble")
    if args.stage in ("all", "mixed", "fast"):
        _run_stage(ctx, "mixed")
        assert_payload(ctx.mixed_payload, "mixed build", exp)
        baseline_payload = ctx.payload
        if baseline_payload.is_file():
            if not _cmp(baseline_payload, ctx.mixed_payload):
                die("The mixed payload differs from the baseline payload.", 1)
            print("  OK: the mixed payload and the baseline payload are identical")
        else:
            print("  (no baseline payload; skip the comparison)")
    print("== build passed ==")
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
            die(f"--full needs {gen}", 2)
        if run([sys.executable, gen, "--project", str(ctx.root),
                "--code-only", "--objdiff", cli], cwd=ctx.root) != 0:
            die("gen_objdiff_full.py failed", 1)
        proj_dir = ctx.build / "objdiff-code"
    else:
        if not (ctx.root / "objdiff.json").is_file():
            die(f"Missing {ctx.root}/objdiff.json. Add --full to generate the full config, or run build/gen_objdiff_full.py first.", 2)
        proj_dir = ctx.root
    print(f"-- report: objdiff-cli report generate -p {proj_dir} -o {out} --")
    if run([cli, "report", "generate", "-p", str(proj_dir), "-o", str(out)], cwd=ctx.root) != 0:
        die("objdiff-cli report generate failed", 1)
    data = json.loads(out.read_text(encoding="utf-8"))
    m = data.get("measures", {})
    print(f"  matched_code={m.get('matched_code')}/{m.get('total_code')} "
          f"({m.get('matched_code_percent')}%)  "
          f"matched_functions={m.get('matched_functions')}/{m.get('total_functions')} "
          f"({m.get('matched_functions_percent')}%)  units={m.get('total_units')}")
    return 0


def _ledger(ctx: Ctx) -> dict:
    """Ledger index. The only parser is tools/build/matched_ledger.py.

    台账索引（唯一解析实现见 tools/build/matched_ledger.py）。
    """
    index = matched_ledger.parse_ledger(ctx.config / "matched_symbols.txt")
    if not index:
        die(f"The ledger is empty or missing: {ctx.config / 'matched_symbols.txt'}", 2)
    return index


def _git_changed(ctx: Ctx, base: str, *paths: str) -> list[str]:
    cp = subprocess.run(["git", "-C", str(ctx.root), "diff", "--name-only", base, "--", *paths],
                        capture_output=True, text=True)
    if cp.returncode != 0:
        die(f"git diff failed (base={base}): {cp.stderr.strip()}", 2)
    return [l.strip() for l in cp.stdout.splitlines() if l.strip()]


# A change to one of these inputs affects functions that the file name cannot
# identify. Compare all registered functions one by one.
#
# 这些输入一变，受影响函数无法靠文件名推断，因此按全量逐一比对处理。
SHARED_INPUTS = ("config/matched_symbols.txt", "config/source_flags.tsv", "config/reloc_addrs.txt",
                 "config/linker_script_extra.ld", "config/symbol_addrs.txt",
                 "splat.yaml", "build.sh", "build_mixed.sh")
FULL_ON_CHANGE = tuple(p for p in SHARED_INPUTS if p != "config/source_flags.tsv")


def _delta_objects(ctx: Ctx, sym: str, src: str) -> tuple[Path, Path]:
    """Find the target object and the base object of one function. A single-function object wins.

    尽力找到该函数的目标对象与编译对象（单函数抽取物优先）。
    """
    targets = [ctx.build / "units" / f"{sym}.target.o", ctx.build / "asm" / "cod" / f"{sym}.o",
               ctx.build / "asm" / "cod" / f"{src}.o"]
    bases = [ctx.build / "mixed" / "obj" / f"{src}.o", ctx.build / "mixed" / "obj" / f"{sym}.o"]
    t = next((x for x in targets if x.is_file()), targets[0])
    b = next((x for x in bases if x.is_file()), bases[0])
    return t, b


def cmd_delta(args) -> int:
    ctx = make_ctx(args)
    if not args.base:
        die("delta needs --base <git-ref>", 3)
    index = _ledger(ctx)
    rel_src = os.path.relpath(ctx.matched, ctx.root)
    changed = _git_changed(ctx, args.base, rel_src)
    shared = _git_changed(ctx, args.base, *SHARED_INPUTS)
    if not changed and not shared:
        print(f"delta: no change against {args.base} in {rel_src}/ or the build inputs; nothing to compare")
        return 0

    sources = [x for x in changed if x.endswith(".c")]
    headers = [x for x in changed if x.endswith(".h")]
    affected, unregistered = matched_ledger.resolve_changed(index, sources, rel_src)
    full = any(x in shared for x in FULL_ON_CHANGE)

    for h in headers:                                    # header file: find dependent sources by #include  头文件：按 #include 找依赖源
        name = Path(h).name
        dep = [f"{rel_src}/{c.name}" for c in sorted(ctx.matched.glob("*.c"))
               if f'"{name}"' in c.read_text(encoding="utf-8", errors="replace")]
        extra, _ = matched_ledger.resolve_changed(index, dep, rel_src)
        affected |= extra
        print(f"note: header {h} changed; {len(extra)} symbols collected by #include")

    if "config/source_flags.tsv" in shared:              # compile flags: collect the affected sources  编译参数：收集受影响的源
        cp = subprocess.run(["git", "-C", str(ctx.root), "diff", "-U0", args.base, "--",
                             "config/source_flags.tsv"], capture_output=True, text=True)
        flag_srcs = set()
        for ln in cp.stdout.splitlines():
            if ln.startswith(("+++", "---")) or not ln.startswith(("+", "-")):
                continue
            first = ln[1:].strip().split("\t")[0].strip()
            # Line 1 is the header row. Its key is source-basename, not a source name. Skip it.
            # 第 1 行是表头，键 source-basename 不是源名，跳过。
            if first and first != "source-basename":
                flag_srcs.add(first)
        for x in sorted(flag_srcs):
            extra, _ = matched_ledger.resolve_changed(index, [f"{rel_src}/{x}.c"], rel_src)
            affected |= extra
        print(f"note: config/source_flags.tsv changed; symbols of {len(flag_srcs)} sources collected")

    if full:
        affected = set(index)
        print(f"note: the ledger, the linker script, or a build entry changed; compare all {len(affected)} registered functions one by one")

    if unregistered:
        print(f"skip {len(unregistered)} unregistered files (not in config/matched_symbols.txt; register new files first):")
        for u in unregistered[:10]:
            print(f"  skip {u}")
        if len(unregistered) > 10:
            print(f"  ... {len(unregistered)} in total")

    if not affected:
        print("note: this change affects no registered function; no objdiff run (this is not a full 100 percent)")
        return 0

    cli = ctx.objdiff_cli()
    out_dir = ctx.build / "delta"
    out_dir.mkdir(parents=True, exist_ok=True)
    compared = passed = 0
    bad: list[str] = []
    missing: list[str] = []
    for sym in sorted(affected):
        src = index[sym][0]
        target, base_obj = _delta_objects(ctx, sym, src)
        if not target.is_file() or not base_obj.is_file():
            missing.append(f"{sym} (target={target.name} base={base_obj.name})")
            continue
        rep = out_dir / f"{sym}.json"
        rc = run([cli, "diff", "-1", str(target), "-2", str(base_obj), "-o", str(rep), "--format", "json"],
                 cwd=ctx.root)
        compared += 1
        if rc != 0:
            bad.append(f"{sym} (objdiff exit code {rc})")
            continue
        pct = _fn_percent(rep, sym)
        if pct is None:
            bad.append(f"{sym} (no function symbol in the report)")
        elif pct != 100.0:
            bad.append(f"{sym} ({pct:.1f}% != 100%)")
        else:
            passed += 1
            print(f"  OK: {sym} 100%")

    print(f"\ndelta summary: affected {len(affected)} | compared {compared} | passed {passed} | "
          f"failed {len(bad)} | missing objects {len(missing)} | skipped unregistered {len(unregistered)}")
    if missing:
        print("FAIL: these functions have no objdiff object. Run 'decomp_build.py build' first:", file=sys.stderr)
        for x in missing:
            print(f"  - {x}", file=sys.stderr)
        return 2
    if bad:
        print("FAIL: these functions are below 100 percent:", file=sys.stderr)
        for x in bad:
            print(f"  - {x}", file=sys.stderr)
        return 1
    if compared == 0:
        print("FAIL: functions are affected, but no comparison ran. Are the objects missing?", file=sys.stderr)
        return 2
    if passed != compared:
        print(f"FAIL: passed {passed} != compared {compared}", file=sys.stderr)
        return 1
    print(f"delta passed: compared {compared} functions, all at 100 percent")
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
    # single-function object: fall back to the first function
    for side in ("left", "right"):
        for s in data.get(side, {}).get("symbols", []):
            if s.get("kind") == "SYMBOL_FUNCTION":
                return float(s.get("match_percent") or 0.0)
    return None


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        prog="decomp_build.py",
        description="Layout-independent build driver for the matching decompilation (repo=private main repository / flat=public repository)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="Project directory (the repo layout uses matching-jp; the flat layout uses .)")
    ap.add_argument("--layout", choices=["auto", "repo", "flat"], default="auto",
                    help="Layout: repo = the project root is a subdirectory and the tools are in <root>/../tools; flat = the project root is the repository root and the tools are in <root>/tools")
    ap.add_argument("--name", default=None, help="Target name (default: detect it from <name>.yaml or build/config.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check-config", help="Print the resolved paths and their presence")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_check_config)

    p = sub.add_parser("configure", help="Check the retail ELF SHA1 and write <root>/build/config.json")
    p.add_argument("--game", default=None, help="Retail ELF path")
    p.add_argument("--expect-sha1", default=None, help="Expected retail ELF SHA1 (necessary for an unknown target)")
    p.add_argument("--expect-size", default=None, help="Expected retail ELF size")
    p.set_defaults(func=cmd_configure)

    p = sub.add_parser("build", help="Run the baseline build and the mixed build, then check the payload (non-zero on failure)")
    p.add_argument("--stage", choices=["all", "baseline", "assemble", "mixed", "fast"], default="all",
                   help="all/baseline/mixed = the full pipeline; assemble = the pure-asm baseline without its link; "
                        "fast = assemble without the baseline link, then the mixed build and the mixed payload check")
    p.add_argument("--jobs", default=None, help="Parallelism (pass JOBS to the build script)")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("report", help="objdiff report")
    p.add_argument("--out", default=None, help="Report output (default <root>/build/report.json)")
    p.add_argument("--full", action="store_true", help="First run tools/build/gen_objdiff_full.py to generate the full config")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("delta", help="Compare each changed matched source with objdiff and require 100%%")
    p.add_argument("--base", default=None, help="git ref (for example origin/main)")
    p.set_defaults(func=cmd_delta)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
