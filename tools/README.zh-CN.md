# 本仓库的工具

[English](README.md) | [简体中文](README.zh-CN.md)

本页列出 `tools/` 下的全部工具，并说明外部贡献者需要哪些。

## 1. 目录布局

`tools/` 分成两部分。

- `tools/build/`、`tools/project/`、`tools/report/`、`tools/check/`、`tools/ci/`
  属于**贡献者链**，外部克隆可以运行。
- `tools/maintainer/` 属于**维护者内部**。这类工具需要私有侧的原版 ELF、Ghidra
  产物或证据目录。外部克隆跑不通。

外部贡献者只需要一条链：

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build
make progress
make report
make delta BASE=origin/main
make check
```

`configure.py` 检查原版可执行文件并写出构建配置。`make` 调用
`tools/build/decomp_build.py` 与报告工具。这条链只需要你自备的游戏光盘与原版工具链。

## 2. 工具清单

外部克隆可以跑「Contributor 需要」的工具。「Maintainer internal」的工具需要私有的
原版 ELF、Ghidra 产物或证据目录，外部克隆跑不了。

| 路径 | 用途 | 受众 |
| --- | --- | --- |
| `Makefile` | 构建入口，调用构建驱动与报告工具 | Contributor 需要 |
| `configure.py` | 检查原版可执行文件并写出构建配置 | Contributor 需要 |
| `tools/build/decomp_build.py` | 构建驱动：切分载荷、汇编、链接并校验结果 | Contributor 需要 |
| `tools/build/gen_objdiff_full.py` | 生成进度报告用的全量 objdiff unit 清单 | Contributor 需要 |
| `tools/build/matched_ledger.py` | 解析匹配台账，供报告工具与增量检查使用 | Contributor 需要 |
| `tools/check/check_public_repo.py` | 校验发布记录、禁止材料（禁材类别 + 尺寸兜底）与报告规则；所有 git 调用用 `-z`，贡献模式拒绝「不是普通文件」的路径 | Contributor 需要 |
| `tools/check/test_matched_ledger.py` | 测试台账解析与增量检查 | Contributor 需要 |
| `tools/check/test_public_repo.py` | 测试禁材模式、尺寸兜底、git `-z` 路径处理与贡献模式的 fail-closed 规则 | Contributor 需要 |
| `tools/check/test_at2_io.py` | 测试共用的名字/路径/原子写助手 | Contributor 需要 |
| `tools/check/test_tool_paths.py` | 测试每个工具都能正确解析项目路径 | Contributor 需要 |
| `tools/check/test_classify_change.py` | 测试 CI 模式分类器 | Contributor 需要 |
| `tools/check/test_splat_snapshot.py` | 测试 splat 产物打包/还原工具 | Contributor 需要 |
| `tools/ci/classify_change.py` | 按改动集合判定 `matching-gate` 的模式（skip / fast / full） | Contributor 需要 |
| `tools/ci/splat_snapshot.py` | 把 `splat split` 的输出与汇编产物打包进私有伴生仓库，并在 CI 里还原；还原会先在暂存目录校验内容摘要，通过后才碰检出 | Maintainer internal |
| `tools/ci/splat-requirements.txt` | 列出 CI 使用的公开 `splat` 版本 | Contributor 需要 |
| `tools/project/at2_io.py` | 共用助手：安全符号名、证明留在根内的子路径、原子写、带守护的 JSON 读取 | Contributor 需要 |
| `tools/project/at2_paths.py` | 按仓库布局解析项目路径 | Contributor 需要 |
| `tools/project/compile_sources.py` | 只重编「源或标志变了」的对象 | Contributor 需要 |
| `tools/project/extract_payload.py` | 从原版可执行文件抽取载荷 | Contributor 需要 |
| `tools/project/jtbl_patch.py` | 把自产跳转表的引用改指到零售二进制里的数据符号 | Contributor 需要 |
| `tools/project/split_asm.py` | 从汇编文件里摘出一个函数，供混合构建使用 | Contributor 需要 |
| `tools/report/gen_function_report.py` | 生成逐函数的 objdiff 进度报告 | Contributor 需要 |
| `tools/report/progress_report.py` | 按符号表字节数给出静态进度上界，并列出剩余最大的函数。用 `make progress` | Contributor 需要 |
| `tools/maintainer/publish_report.py` | 把验证过的报告写进 `progress/` 并更新 `PUBLISHED.json` | Maintainer internal |
| `tools/maintainer/build/export_symbols.py` | 把 `.erx.lib` 导出表转成反编译符号表 | Maintainer internal |
| `tools/maintainer/build/gen_match_meta.py` | 写出 `config/match_meta.tsv`，即每个 C 匹配的机器可读台账 | Maintainer internal |
| `tools/maintainer/build/gen_splat_yaml.py` | 写出带 per-function 子段的 splat 配置 | Maintainer internal |
| `tools/maintainer/build/gen_symbol_addrs.py` | 把 Ghidra 函数边界与 `.erx.lib` 名字并成 `symbol_addrs.txt` | Maintainer internal |
| `tools/maintainer/project/auto_match_ghidra.py` | 用 Ghidra 产物起草 C 源，只收 objdiff 100% 的结果 | Maintainer internal |
| `tools/maintainer/project/auto_match_m2c.py` | 用 m2c 起草 C 源，只收 objdiff 100% 的结果 | Maintainer internal |
| `tools/maintainer/project/auto_match_permuter.py` | 用 decomp-permuter 收敛近失函数 | Maintainer internal |
| `tools/maintainer/project/auto_match_stub.py` | 为 syscall / break 类函数手写汇编 | Maintainer internal |
| `tools/maintainer/project/auto_match_trivial.py` | 按指令形状匹配 trivial 函数 | Maintainer internal |
| `tools/maintainer/project/auto_match_wrapper.py` | 用两种栈帧模板匹配薄包装函数 | Maintainer internal |
| `tools/maintainer/project/compiler_id_test_jp.sh` | 判别某个日版目标函数由哪个编译器产出 | Maintainer internal |
| `tools/maintainer/project/erx_tables.py` | 解析 `.erx.lib` 导出表与 `.erx.stub` 导入表 | Maintainer internal |
| `tools/maintainer/project/gen_splat_yaml_jp.py` | 写出带 per-function 子段的日版 splat 配置 | Maintainer internal |
| `tools/maintainer/project/gen_symbol_addrs_jp.py` | 用 Ghidra 数据与 `.erx.lib` 名字写出日版 `symbol_addrs.txt` | Maintainer internal |
| `tools/maintainer/project/ghidra_draft.py` | 把 Ghidra 伪 C 变成单个函数的可编译草稿 | Maintainer internal |
| `tools/maintainer/project/infer_sig.py` | 从调用点反推函数的参数与返回类型 | Maintainer internal |
| `tools/maintainer/project/jtbl_draft.py` | 给跳转表池做画像与抽样 | Maintainer internal |
| `tools/maintainer/project/m2c_draft.py` | 从单个汇编文件生成 m2c C 草稿 | Maintainer internal |
| `tools/maintainer/project/p1a_pseudoc_probe.py` | 实测 Ghidra 伪 C 能否当匹配草稿 | Maintainer internal |
| `tools/maintainer/project/screen_flags.py` | 把大量候选草稿合进一个编译单元，再逐符号取分 | Maintainer internal |
| `tools/maintainer/project/shape_lq_sq.py` | 为 MMI 池合成 `lq` / `sq` 向量形状 | Maintainer internal |
| `tools/maintainer/report/disasm_stats.py` | 统计 PS2 EE 主程序的汇编分布 | Maintainer internal |
| `tools/maintainer/report/match_workqueue.py` | 按难度把主程序函数排成工作队列 | Maintainer internal |
| `tools/maintainer/report/r5900_stats.py` | 从原始指令字统计 R5900 指令分布 | Maintainer internal |
