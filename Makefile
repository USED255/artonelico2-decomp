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

.DEFAULT_GOAL := help

.PHONY: help configure rom split build report delta check check-tools check-pr clean

help:
	@echo "Ar tonelico II matching decompilation - available targets"
	@echo "  make configure GAME=<path>   check the input (retail ELF and toolchain), then write the build configuration"
	@echo "  make rom                     derive the reference payload from the retail ELF (SLPS_258.19.rom)"
	@echo "  make split                   run splat split, which writes asm/ and include/"
	@echo "  make build                   split, assemble the baseline build, link, run the mixed build, assert the payload sha1"
	@echo "  make report                  write the objdiff progress report (progress/SLPS_258.19_report.json)"
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

report:
	@AS="$${BINUTILS:-$$HOME/eecc/ps2binutils}/mips-ps2-decompals-as"; \
	 $(PY) tools/report/gen_function_report.py --project . --jobs 4 --as "$$AS" \
	   --objdiff "$${OBJDIFF:-$$HOME/eecc/objdiff-cli}" \
	   --report-out progress/SLPS_258.19_report.json

delta:
	@$(DRIVER) delta --base "$(BASE)"

check: check-tools
	@$(PY) tools/check/check_public_repo.py --check

check-tools:
	@$(PY) tools/check/test_tool_paths.py

check-pr:
	@test -n "$(BASE)" || { echo "usage: make check-pr BASE=<git-ref> (compare that ref with HEAD)"; exit 2; }
	@$(PY) tools/check/check_public_repo.py --pr "$(BASE)"

clean:
	@rm -rf build asm
	@echo "removed build/ and asm/ (src/, config/, and progress/ are unchanged)"
