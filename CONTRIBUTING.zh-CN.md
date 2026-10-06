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

## 3. 提 PR

1. Fork 本仓库。
2. 建分支，加/改文件。
3. 跑第 2 节的命令。
4. 向 `main` 提 PR。
5. 在描述里给出**证据**：用了什么工具、什么命令、什么结果。匹配函数请给出 objdiff 结果（100%）。

## 4. CI 会做什么

| workflow | 你的 PR |
| --- | --- |
| `validate` | 跑**贡献模式**：允许白名单路径内的新增与修改；拒绝白名单外的改动、删除、非文本文件、超过 1 MiB 的文件。 |
| `matching-gate` | 需要原版可执行文件与 Sony 工具链。**fork 的 PR 拿不到**，该 job 会跳过；之后由维护者复验你的 commit，或者用你的 PR 编号手动触发该 workflow。 |

## 5. CI 之后

维护者评审后合并你的改动（你的作者信息保留在历史里）。

## 6. 路径规则

可以新增或修改：

- `src/matched/`（`.c` 与 `.h`）；
- `tools/`（脚本）；
- `docs/` 与根目录的 `.md`；
- `LICENSE`、`.gitignore`、`Makefile`、`configure.py`、`toolchain.lock.json`、`.github/workflows/`。

以下路径**只读**，改动会被 `validate` 拒绝：

| 路径 | 原因 |
| --- | --- |
| `progress/` | 进度报告由经过验证的构建产出 |
| `PUBLISHED.json` | 发布记录；由 `tools/publish_report.py` 在一次已验证的构建后写入 |

其它路径都可以改。`config/`、`splat.yaml` 与三个构建脚本，**建议先开 issue 说明**再动手 —— 它们会影响整个构建。

**新增函数注意**：你**不需要**改 `config/matched_symbols.txt`；维护者会替你补条目。

## 7. 写作风格

本仓库的**英文**文档统一使用 **ASD-STE100** 风格（Simplified Technical English，简化技术英语）：

1. 一句话写一个意思。
2. 步骤句不超过 20 个词；描述句不超过 25 个词。
3. 一个段落最多 6 句。
4. 用主动语态；指令用祈使句。
5. 只用简单时态；不用缩写形式；不用分号。
6. 不写 `e.g.` / `i.e.` / `etc.`，改写成 `for example` / `that is` / `and more`。
7. **一词一义**：同一个东西始终用同一个词。
8. 不用习语、俚语和含糊的评价词。
9. 能查 ASD-STE100 的批准词典时，照词典写。

ASD-STE100 的词典有版权，**不得复制进本仓库**。规范见 <https://www.asd-ste100.org/>。

**其他语言**的文档遵循同一套原则：短句、主动语态、一词一义、不用口语。

## 8. 许可证

本仓库是 GPL-3.0。你提交贡献，即同意**以同一许可证发布**它。你保留自己作品的著作权。

## 9. 报告政策问题

先读 [docs/PUBLICATION-POLICY.zh-CN.md](docs/PUBLICATION-POLICY.zh-CN.md)。
如果你发现本仓库含有**不该出现**的材料，请开 issue。我们把这类报告当**阻塞项**：先移除材料，再谈其它。
