# 魔塔大陆2：响彻世界的少女的创造诗 —— 匹配反编译

[English](README.md) | [简体中文](README.zh-CN.md)

[![Progress](https://decomp.dev/USED255/artonelico2-decomp.svg?mode=shield)](https://decomp.dev/USED255/artonelico2-decomp)

本仓库包含 PS2 游戏 **《魔塔大陆2：响彻世界的少女的创造诗》**（`Ar tonelico II`，日版零售 `SLPS_258.19`）的**逆向 C 源码**。

`src/matched/` 下的源码用**原版编译器工具链**编译。构建过程把结果与零售二进制**逐字节**比较。
两个字节序列相同时，该函数判定为**已匹配**。

**欢迎贡献**（见 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)）。

## 进度

截至 2026-10-25（[progress/baseline.json](progress/baseline.json)，构建版本 `d41a5de`，
报告 `sha256:307fcf819c07…`，载荷 `sha1:7cc42d275750600d…`）：

- 已匹配函数：**4,281 / 10,923（39.19%）**
- 已匹配代码：**233,156 / 2,276,780 字节（10.24%）**

主口径只算重建的 C，详见 [docs/TRANSCRIPTION.zh-CN.md](docs/TRANSCRIPTION.zh-CN.md)。

比基线更差的报告，CI 不会发布。进度历史：<https://decomp.dev/USED255/artonelico2-decomp>。

## 构建

以下材料由你自备，本仓库不包含：

1. `SLPS_258.19`，来自你自己的游戏光盘。
2. 原版 EE 编译器工具链。它属于 Sony，**不可再分发**。
3. `splat` 与 `objdiff-cli`，这两个是公开工具。

先读 [docs/BUILD.zh-CN.md](docs/BUILD.zh-CN.md)，再执行：

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build      # 汇编、链接、校验载荷哈希
make report     # 生成进度报告
```

## 文档

全部文档索引见 [docs/README.zh-CN.md](docs/README.zh-CN.md)。[知识库](docs/knowledge-base/README.zh-CN.md)
收录不随进度变化的参考资料：

| | |
| --- | --- |
| [docs/BUILD.zh-CN.md](docs/BUILD.zh-CN.md) | 如何配置与构建 |
| **[docs/knowledge-base/compiler/README.zh-CN.md](docs/knowledge-base/compiler/README.zh-CN.md)** | **EE GCC 3.2 代码生成手册**——每条 law 都以源码为骨、对锚出厂 `cc1`、并用行为复核 |
| [docs/knowledge-base/KNOWN-BLOCKERS.zh-CN.md](docs/knowledge-base/KNOWN-BLOCKERS.zh-CN.md) | 本工具链收不了的东西，以及停止条件 |
| [docs/knowledge-base/FORMATS.zh-CN.md](docs/knowledge-base/FORMATS.zh-CN.md) | 光盘上的资产与模块格式（实测） |
| [docs/knowledge-base/TOOLCHAIN.zh-CN.md](docs/knowledge-base/TOOLCHAIN.zh-CN.md) | 哪个编译器编了什么、如何核验你手上的副本 |
| [docs/knowledge-base/GLOSSARY.zh-CN.md](docs/knowledge-base/GLOSSARY.zh-CN.md) | 本项目使用的术语与缩写 |

手册的工具在 `tools/compiler/`。每页都有英文版（同名 `.md`）。

## 法律

- 本仓库不含游戏代码、不含游戏资产、不含 ROM 镜像。**你必须自备正版游戏**。
- 逆向源码是我们的作品，许可证为 GPL-3.0，见 [LICENSE](LICENSE)。
- 请读 [docs/PUBLICATION-POLICY.zh-CN.md](docs/PUBLICATION-POLICY.zh-CN.md)。
- 本项目与 GUST、Banpresto、NIS 无隶属关系。
