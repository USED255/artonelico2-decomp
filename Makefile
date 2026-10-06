# 公开仓库构建入口（社区惯例：configure.py + make）
#
# 这里只放「怎么构建 / 怎么出报告 / 怎么自检」，具体逻辑在 tools/build/decomp_build.py。
# 依赖：自备正版光盘的 SLPS_258.19 + 原版 EE 工具链（见 docs/BUILD.md、toolchain.lock.json）。
SHELL := /bin/bash
PY ?= python3
NAME ?= SLPS_258.19
DRIVER := $(PY) tools/build/decomp_build.py --root . --layout flat --name $(NAME)
GAME ?= orig/SLPS_258.19

.DEFAULT_GOAL := help

.PHONY: help configure rom split build report delta check clean

help:
	@echo "Ar tonelico II matching decompilation —— 可用目标"
	@echo "  make configure GAME=<路径>   检查输入（原版 ELF / 工具链）并写构建配置"
	@echo "  make rom                     从原版 ELF 派生棘轮基准载荷（SLPS_258.19.rom）"
	@echo "  make split                   splat split：生成 asm/ 与 include/"
	@echo "  make build                   split → 汇编基线 → 链接 → 混合构建 → 断言载荷 sha1"
	@echo "  make report                  生成 objdiff 进度报告（progress/SLPS_258.19_report.json）"
	@echo "  make delta BASE=<git-ref>    只检查本次改动过的 src/matched/*.c 是否 100% 匹配"
	@echo "  make check                   仓库自检（导出清单 / 不可公开类别 / 报告不变量）"
	@echo "  make check-pr BASE=<ref>     贡献模式：只允许白名单内的新增/修改（PR 用）"
	@echo "  make clean                   清理构建产物"

configure:
	@$(DRIVER) configure --game "$(GAME)"

rom:
	@test -f orig/SLPS_258.19 || { echo "缺 orig/SLPS_258.19（自备正版光盘中的主程序）"; exit 1; }
	@test -f SLPS_258.19.rom || $(PY) tools/project/extract_payload.py orig/SLPS_258.19 SLPS_258.19.rom
	@sha1sum SLPS_258.19.rom

split: rom
	@test -f include/macro.inc || splat split splat.yaml
	@test -f include/macro.inc && echo "splat split 就绪：asm/ + include/" || { echo "splat split 失败"; exit 1; }

build: split
	@$(DRIVER) build

report:
	@AS="$${BINUTILS:-$$HOME/eecc/ps2binutils}/mips-ps2-decompals-as"; \
	 $(PY) tools/report/gen_function_report.py --project . --jobs 4 --as "$$AS" \
	   --objdiff "$${OBJDIFF:-$$HOME/eecc/objdiff-cli}" \
	   --report-out progress/SLPS_258.19_report.json

delta:
	@$(DRIVER) delta --base "$(BASE)"

check:
	@$(PY) tools/check/check_public_repo.py --check

check-pr:
	@test -n "$(BASE)" || { echo "用法：make check-pr BASE=<git-ref>（比较该 ref 与 HEAD）"; exit 2; }
	@$(PY) tools/check/check_public_repo.py --pr "$(BASE)"

clean:
	@rm -rf build asm
	@echo "已清理 build/ 与 asm/（不动 src/、config/、progress/）"
