# 本仓库的工具

[English](TOOLS.md) | [简体中文](TOOLS.zh-CN.md)

本页列出 `tools/` 下的全部工具，并说明外部贡献者需要哪些。

## 1. 贡献者用的链

外部贡献者只需要一条链：

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build
make report
make delta BASE=origin/main
make check
```

`configure.py` 检查原版可执行文件并写出构建配置；`make` 调用 `tools/build/decomp_build.py` 与报告工具。
这条链只需要你自备的游戏光盘与原版工具链。

## 2. 工具清单

外部克隆可以跑「Contributor 需要」的工具。「Maintainer internal」的工具需要私有的原版 ELF、Ghidra 产物或证据目录，外部克隆跑不了。

| 路径 | 用途 | 受众 |
| --- | --- | --- |
| `Makefile` | 构建入口，调用构建驱动与报告工具 | Contributor 需要 |
| `configure.py` | 检查原版可执行文件并写出构建配置 | Contributor 需要 |
| `tools/build/decomp_build.py` | 构建驱动：切分载荷、汇编、链接并校验结果 | Contributor 需要 |
| `tools/build/export_symbols.py` | 把 `.erx.lib` 导出表转成反编译符号表 | Maintainer internal |
| `tools/build/gen_match_meta.py` | 写出 `config/match_meta.tsv`，即每个 C 匹配的机器可读台账 | Maintainer internal |
| `tools/build/gen_objdiff_full.py` | 生成进度报告用的全量 objdiff unit 清单 | Contributor 需要 |
| `tools/build/gen_splat_yaml.py` | 写出带 per-function 子段的 splat 配置 | Maintainer internal |
| `tools/build/gen_symbol_addrs.py` | 把 Ghidra 函数边界与 `.erx.lib` 名字并成 `symbol_addrs.txt` | Maintainer internal |
| `tools/build/matched_ledger.py` | 解析匹配台账，供报告工具与增量检查使用 | Contributor 需要 |
| `tools/check/check_public_repo.py` | 校验发布记录、禁止材料与报告规则 | Contributor 需要 |
| `tools/check/test_matched_ledger.py` | 测试台账解析与增量检查 | Contributor 需要 |
| `tools/check/test_tool_paths.py` | 测试每个工具都能正确解析项目路径 | Contributor 需要 |
| `tools/ci/splat-requirements.txt` | 列出 CI 使用的公开 `splat` 版本 | Contributor 需要 |
| `tools/project/at2_paths.py` | 按仓库布局解析项目路径 | Contributor 需要 |
| `tools/project/auto_match_ghidra.py` | 用 Ghidra 产物起草 C 源，只收 objdiff 100% 的结果 | Maintainer internal |
| `tools/project/auto_match_m2c.py` | 用 m2c 起草 C 源，只收 objdiff 100% 的结果 | Maintainer internal |
| `tools/project/auto_match_permuter.py` | 用 decomp-permuter 收敛近失函数 | Maintainer internal |
| `tools/project/auto_match_stub.py` | 为 syscall / break 类函数手写汇编 | Maintainer internal |
| `tools/project/auto_match_trivial.py` | 按指令形状匹配 trivial 函数 | Maintainer internal |
| `tools/project/auto_match_wrapper.py` | 用两种栈帧模板匹配薄包装函数 | Maintainer internal |
| `tools/project/compiler_id_test_jp.sh` | 判别某个日版目标函数由哪个编译器产出 | Maintainer internal |
| `tools/project/compile_sources.py` | 只重编「源或标志变了」的对象 | Contributor 需要 |
| `tools/project/erx_tables.py` | 解析 `.erx.lib` 导出表与 `.erx.stub` 导入表 | Maintainer internal |
| `tools/project/extract_payload.py` | 从原版可执行文件抽取载荷 | Contributor 需要 |
| `tools/project/gen_splat_yaml_jp.py` | 写出带 per-function 子段的日版 splat 配置 | Maintainer internal |
| `tools/project/gen_symbol_addrs_jp.py` | 用 Ghidra 数据与 `.erx.lib` 名字写出日版 `symbol_addrs.txt` | Maintainer internal |
| `tools/project/ghidra_draft.py` | 把 Ghidra 伪 C 变成单个函数的可编译草稿 | Maintainer internal |
| `tools/project/infer_sig.py` | 从调用点反推函数的参数与返回类型 | Maintainer internal |
| `tools/project/jtbl_draft.py` | 给跳转表池做画像与抽样 | Maintainer internal |
| `tools/project/jtbl_patch.py` | 把自产跳转表的引用改指到零售二进制里的数据符号 | Contributor 需要 |
| `tools/project/m2c_draft.py` | 从单个汇编文件生成 m2c C 草稿 | Maintainer internal |
| `tools/project/p1a_pseudoc_probe.py` | 实测 Ghidra 伪 C 能否当匹配草稿 | Maintainer internal |
| `tools/project/screen_flags.py` | 把大量候选草稿合进一个编译单元，再逐符号取分 | Maintainer internal |
| `tools/project/shape_lq_sq.py` | 为 MMI 池合成 `lq` / `sq` 向量形状 | Maintainer internal |
| `tools/project/split_asm.py` | 从汇编文件里摘出一个函数，供混合构建使用 | Contributor 需要 |
| `tools/publish_report.py` | 把验证过的报告写进 `progress/` 并更新 `PUBLISHED.json` | Contributor 需要 |
| `tools/report/disasm_stats.py` | 统计 PS2 EE 主程序的汇编分布 | Maintainer internal |
| `tools/report/gen_function_report.py` | 生成逐函数的 objdiff 进度报告 | Contributor 需要 |
| `tools/report/match_workqueue.py` | 按难度把主程序函数排成工作队列 | Maintainer internal |
| `tools/report/r5900_stats.py` | 从原始指令字统计 R5900 指令分布 | Maintainer internal |

## 3. 本批次改动

2026-10-11，有 4 个脚本移出公开仓库。外部克隆无法运行它们。它们现在放在私有伴生仓库的 `tools/legacy/` 目录。

| 脚本 | 移出原因 | 现在的位置 |
| --- | --- | --- |
| `build_m2.sh` | 第 17 行编译 `src/m2_probe.c`，而公开 `src/` 下只有 `matched/` | `tools/legacy/build_m2.sh` |
| `tools/build/m2_extract.py` | 只有 `build_m2.sh` 调用它，公开树里没有其他引用 | `tools/legacy/m2_extract.py` |
| `tools/report/c_route_measure.py` | 路线 C 调研需要美版 `SLUS_217.88` 与它的 ISO | `tools/legacy/c_route_measure.py` |
| `tools/report/progress_report.py` | 只读 `routeb/`，而公开树里没有 `routeb/` 目录 | `tools/legacy/progress_report.py` |

这 4 个文件在 git 历史 `cd1f47a` 里仍然可以取回。

有两个工具改了名字：

- `build_hybrid.sh` 现在叫 `build_mixed.sh`。
- `tools/report/m3_workqueue.py` 现在叫 `tools/report/match_workqueue.py`。

公开仓库的可复现路径是 `make build`，再用 `build_mixed.sh`，再用 `make report`。
