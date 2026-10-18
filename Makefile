# Public repository build entry point (community convention: configure.py plus make).
#
# This file defines how to build, how to write reports, and how to run the checks.
# The build logic lives in tools/build/decomp_build.py.
# Requirements: your own legal copy of SLPS_258.19 and the original EE toolchain.
# See docs/BUILD.md and toolchain.lock.json.

# 公开仓库构建入口（社区惯例：configure.py + make）。
#
# 本文件只说明怎么构建、怎么出报告、怎么自检；具体逻辑在 tools/build/decomp_build.py。
# 依赖：自备正版光盘的 SLPS_258.19 与原版 EE 工具链（见 docs/BUILD.md、toolchain.lock.json）。
SHELL := /bin/bash
PY ?= python3
NAME ?= SLPS_258.19
DRIVER := $(PY) tools/build/decomp_build.py --root . --layout flat --name $(NAME)
GAME ?= orig/SLPS_258.19
# Parallelism for the assembler and the compiler. The build scripts read JOBS (default 4).
# Follow the machine instead of a hard-coded 4: the CI runner has 4 vCPU, a bigger machine
# gets a bigger value.
# 汇编器与编译器的并行度。构建脚本读 JOBS（默认 4）；跟随机器核数而不是写死 4。
JOBS ?= $(shell nproc)
export JOBS

.DEFAULT_GOAL := help

.PHONY: help configure rom split build build-fast report progress delta check check-tools check-tests check-compiler check-pr clean

help:
	@echo "Ar tonelico II matching decompilation - available targets"
	@echo "  make configure GAME=<path>   check the input (retail ELF and toolchain), then write the build configuration"
	@echo "  make rom                     derive the reference payload from the retail ELF (SLPS_258.19.rom)"
	@echo "  make split                   run splat split, which writes asm/ and include/"
	@echo "  make build                   split, assemble the baseline build, link, run the mixed build, assert the payload sha1"
	@echo "  make build-fast              assemble the baseline but skip its link, then run the mixed build (the mixed payload is still asserted)"
	@echo "  make report                  write the objdiff progress report to build/ (progress/ is written only by publish_report.py)"
	@echo "  make progress                print the static progress upper bound (no toolchain needed)"
	@echo "  make delta BASE=<git-ref>    check that each changed src/matched/*.c file matches 100 percent"
	@echo "  make check                   run the repository checks (paths, publication record, denied classes, report rules)"
	@echo "  make check-pr BASE=<ref>     contribution mode: allow added or changed files only (for pull requests)"
	@echo "  make clean                   remove the build output"

configure:
	@$(DRIVER) configure --game "$(GAME)"

rom:
	@test -f orig/SLPS_258.19 || { echo "missing orig/SLPS_258.19 (the main program from your own legal disc)"; exit 1; }
	@test -f SLPS_258.19.rom || $(PY) tools/project/extract_payload.py orig/SLPS_258.19 SLPS_258.19.rom
	@sha1sum SLPS_258.19.rom

split: rom
	@test -f include/macro.inc || splat split splat.yaml
	@test -f include/macro.inc && echo "splat split is ready: asm/ + include/" || { echo "splat split failed"; exit 1; }

build: split
	@$(DRIVER) build

# The fast lane of `matching-gate`: assemble the baseline, skip its link and payload extraction,
# then run the mixed build and assert the mixed payload (which is compared against the retail
# payload, so the image is still verified byte for byte). CI selects it from the change itself.
# `matching-gate` 的快路：装配基线、跳过基线链接与载荷抽取，然后跑混合构建并断言混合载荷
# （比的是零售载荷，镜像仍被逐字节验证）。CI 按改动面自动选择它。
build-fast: split
	@$(DRIVER) build --stage fast

# The report and its provenance go to build/. `progress/**` is written only by
# tools/maintainer/publish_report.py, after that tool verified the provenance: a local run must
# never overwrite a published, hash-pinned artifact (R30 finding B2). `--require-c100` makes the
# target fail when a C unit is below 100 percent, so a partial run cannot be mistaken for a
# report worth publishing. Override REPORT_FLAGS= to get an exploratory report.
# 报告与 provenance 写到 build/。`progress/**` 只由 tools/maintainer/publish_report.py 在校验
# provenance 之后写入：本地跑一次不得覆盖已发布、已锁哈希的产物（R30 B2）。`--require-c100`
# 让目标在任一 C 单元不足 100% 时失败，避免把半成品当成可发布报告。要探索性报告用 REPORT_FLAGS=。
REPORT_FLAGS ?= --require-c100
report:
	@AS="$${BINUTILS:-$$HOME/eecc/ps2binutils}/mips-ps2-decompals-as"; \
	 $(PY) tools/report/gen_function_report.py --project . --jobs $(JOBS) --as "$$AS" \
	   --objdiff "$${OBJDIFF:-$$HOME/eecc/objdiff-cli}" $(REPORT_FLAGS) \
	   --report-out build/SLPS_258.19_report.json \
	   --baseline-out build/report_provenance.json

progress:
	@$(PY) tools/report/progress_report.py

delta:
	@$(DRIVER) delta --base "$(BASE)"

check: check-tools check-tests check-compiler
	@$(PY) tools/check/check_public_repo.py --check

check-compiler:
	@$(PY) tools/check/test_compiler_laws.py
	@$(PY) tools/check/test_compiler_tools.py

check-tools:
	@$(PY) tools/check/test_tool_paths.py

# Unit tests of the pure logic the workflows depend on. They are fast and need no toolchain.
# The workflows rely on tools/ci/classify_change.py: a regression there would silently change
# what CI verifies, so its test runs inside `make check`. The other tests guard the same class of
# silent failure: the ledger parser (a delta run that skips entries but still says 100 percent),
# the public-repository checks (the denied-material list and the git -z path handling) and the
# shared path/atomic-write helpers.
# 工作流依赖的纯逻辑单测（快、不需要工具链）。classify_change.py 一旦回归会静默改变 CI 的验证
# 范围，所以它的测试放进 `make check`。其余测试守同一类静默失败：台账解析（跳过条目却报 100%）、
# 公开仓库检查（禁材列表与 git -z 路径处理）、共用路径/原子写助手。
check-tests:
	@$(PY) tools/check/test_obj_gate.py
	@$(PY) tools/check/test_data_patch.py
	@$(PY) tools/check/test_classify_change.py
	@$(PY) tools/check/test_splat_snapshot.py
	@$(PY) tools/check/test_matched_ledger.py
	@$(PY) tools/check/test_public_repo.py
	@$(PY) tools/check/test_at2_io.py

check-pr:
	@test -n "$(BASE)" || { echo "usage: make check-pr BASE=<git-ref> (compare that ref with HEAD)"; exit 2; }
	@$(PY) tools/check/check_public_repo.py --pr "$(BASE)"

clean:
	@rm -rf build asm
	@echo "removed build/ and asm/ (src/, config/, and progress/ are unchanged)"
