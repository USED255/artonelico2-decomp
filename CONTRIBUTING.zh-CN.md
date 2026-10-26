# 参与贡献

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

**欢迎贡献。** 本页说明：我们需要什么、怎么提交、提交之后会发生什么。

不需要事先申请。如果你想改的东西比较大，可以先开 issue 讨论。

## 1. 我们需要什么

| 贡献类型 | 例子 |
| --- | --- |
| **一个已匹配函数** | 在 `src/matched/` 新增一个文件，编译后与零售函数**逐字节一致**。这是最有价值的贡献。 |
| **工具修复** | 改 `tools/` 里的脚本或文档里的错误。 |
| **文档** | 订正，或新增一种语言的翻译。英文文档仍是主文档。 |
| **问题报告** | 构建失败，或发现本仓库含不该有的材料。 |

## 2. 动手之前

先读 [docs/BUILD.zh-CN.md](docs/BUILD.zh-CN.md)。**游戏与原版编译器工具链由你自备**，本仓库不包含它们。

在本机自查：

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build                       # 载荷哈希必须保持不变
make delta BASE=origin/main      # src/matched/ 里本次改动的文件必须 100% 匹配
make check                       # 仓库自检
```

## 3. 如何匹配一个函数

匹配是一个循环，不是一步到位。循环是这样：

1. **选函数**：挑一个没匹配上的小函数，读它的零售汇编，再读它周围的数据。
2. **写出应该能生成它的 C**：复现编译器看到的源码形状——类型、语句顺序、值的复用方式。
   指令选择会跟着来。
3. **编译并比对**：跑 `make delta BASE=<基点>`，改动文件必须报 100%；不到就去看 `objdiff` 的差异。
4. **先诊断，再猜**：先找出两条指令流第一次分叉的位置，再查它背后的编译器规则。
   [DIAGNOSTICS](docs/knowledge-base/compiler/DIAGNOSTICS.zh-CN.md) 把残差路由到负责它的 pass，
   [FIELD-GUIDE](docs/knowledge-base/compiler/FIELD-GUIDE.zh-CN.md) 列出能移动读数的源写法；
   `python3 tools/compiler/laws-query.py` 回答「这个编译器在 pass X 怎么做」。
5. **改写之前先扫档**：胜出的优化档不一定是记录里的那一档；下结论说源码不对之前，先把
   `-O1`、`-O2`、`-O3`、`-Os` 都试一遍。会产生假结果的陷阱、以及匹配不了的函数，见
   [KNOWN-BLOCKERS](docs/knowledge-base/KNOWN-BLOCKERS.zh-CN.md)，按它的停止条件停下。
6. **交证据**：加文件、跑第 2 节的命令，然后提 PR，附上 objdiff 结果。

只靠照抄零售指令匹配上的函数是**转录**，不算匹配；它单独计数，见
[docs/TRANSCRIPTION.zh-CN.md](docs/TRANSCRIPTION.zh-CN.md)。

## 4. 提 PR

1. Fork 本仓库。
2. 建分支，加/改文件。
3. 跑第 2 节的命令。
4. 向 `main` 提 PR。
5. 在描述里给出**证据**：用了什么工具、什么命令、什么结果。匹配函数请给出 objdiff 结果（100%）。

## 5. CI 会做什么

| workflow | 你的 PR |
| --- | --- |
| `validate` | 跑**贡献模式**：允许白名单路径内的新增与修改；拒绝白名单外的改动、非文本文件、超过 1 MiB 的文件。本仓库自己的分支还可以重命名或删除文件；外部 fork 的 PR 仍只能新增或修改。 |
| `matching-gate` | 需要原版可执行文件与 Sony 工具链。**fork 的 PR 拿不到**，该 job 只跑 notice 步骤；之后由维护者复验你的 commit，或者用你的 PR 编号手动触发该 workflow。同仓库 PR 会按改动集合选模式：纯文档与纯测试完全不构建；只改 `src/matched/**`、`config/**`（不含 `splat split` 读的那两个文件）与进度报告时，装配基线并跑混合构建、逐函数检查与报告，但跳过单独的基线链接；任何触碰构建输入、或改动「决定门禁怎么跑」的工具/工作流的提交，都跑完整流水线。见 [docs/BUILD.zh-CN.md](docs/BUILD.zh-CN.md) 第 4 节。 |

## 6. CI 之后

维护者评审后合并你的改动（你的作者信息保留在历史里）。

## 7. 路径规则

可以新增或修改：

- `src/matched/`（`.c` 与 `.h`）；
- `tools/`（脚本）；
- `docs/` 与根目录的 `.md`；
- `LICENSE`、`.gitignore`、`Makefile`、`configure.py`、`toolchain.lock.json`、`.github/workflows/`。

以下路径**只读**，改动会被 `validate` 拒绝：

| 路径 | 原因 |
| --- | --- |
| `progress/` | 进度报告由经过验证的构建产出 |
| `PUBLISHED.json` | 发布记录；由 `tools/maintainer/publish_report.py` 在一次已验证的构建后写入 |

一个例外：**维护者**（同仓库 PR 的 `OWNER` / `MEMBER` / `COLLABORATOR`）可以开一个**发布 PR**，
它只改 `progress/**` 与 `PUBLISHED.json`。此时 `validate` 不再拒绝，而是**校验这次发布**：记录必须与
它指名的文件一致、`payload_verified` 必须为真、基线必须带「与所发布报告绑定且通过」的 provenance、
且数字不得回退。把发布文件与其它改动混在一个 PR 里会被拒绝。

其它路径都可以改。`config/`、`splat.yaml` 与三个构建脚本，**建议先开 issue 说明**再动手 —— 它们会影响整个构建。

**新增函数注意**：你**不需要**改 `config/matched_symbols.txt`；维护者会替你补条目。`config/matched_symbols.txt` 与 `config/symbol_addrs.txt` 是**只读配置**，由维护者代填。详见 [config/README.zh-CN.md](config/README.zh-CN.md)。

## 8. 写作风格

本仓库的文档统一使用 **ASD-STE100** 风格。

ASD-STE100 的词典有版权，**不得复制进本仓库**。规范见 <https://www.asd-ste100.org/>。

## 9. 许可证

本仓库是 GPL-3.0。你提交贡献，即同意**以同一许可证发布**它。你保留自己作品的著作权。

## 10. 报告政策问题

先读 [docs/PUBLICATION-POLICY.zh-CN.md](docs/PUBLICATION-POLICY.zh-CN.md)。
如果你发现本仓库含有**不该出现**的材料，请开 issue。我们把这类报告当**阻塞项**：先移除材料，再谈其它。
