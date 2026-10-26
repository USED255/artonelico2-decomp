# 文档

[English](README.md) | [简体中文](README.zh-CN.md)

从哪读起，取决于你要做什么。

## 1. 仓库工作

| 我想…… | 读 |
| --- | --- |
| 构建本项目 | [BUILD.zh-CN.md](BUILD.zh-CN.md) |
| 知道什么可以公开 | [PUBLICATION-POLICY.zh-CN.md](PUBLICATION-POLICY.zh-CN.md) |
| 理解转录口径 | [TRANSCRIPTION.zh-CN.md](TRANSCRIPTION.zh-CN.md) |
| 贡献一个匹配函数 | [../CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md) |

## 2. 参考资料

[知识库](knowledge-base/README.zh-CN.md)收录不随进度变化的内容：编译器怎么工作、光盘里有什么、
哪些函数匹配不了。

| 我想…… | 读 |
| --- | --- |
| 理解编译器为什么生成这段代码 | [knowledge-base/compiler/README.zh-CN.md](knowledge-base/compiler/README.zh-CN.md) |
| 知道哪些匹配不了、什么时候该停 | [knowledge-base/KNOWN-BLOCKERS.zh-CN.md](knowledge-base/KNOWN-BLOCKERS.zh-CN.md) |
| 了解光盘上的资产与模块格式 | [knowledge-base/FORMATS.zh-CN.md](knowledge-base/FORMATS.zh-CN.md) |
| 确认游戏代码由哪个编译器生成 | [knowledge-base/TOOLCHAIN.zh-CN.md](knowledge-base/TOOLCHAIN.zh-CN.md) |
| 决定用 C 还是 C++ | [knowledge-base/LANGUAGE.zh-CN.md](knowledge-base/LANGUAGE.zh-CN.md) |
| 查一个术语或缩写 | [knowledge-base/GLOSSARY.zh-CN.md](knowledge-base/GLOSSARY.zh-CN.md) |
| 浏览整个知识库 | [knowledge-base/README.zh-CN.md](knowledge-base/README.zh-CN.md) |

每份文档都有英文版（同名 `.md`）。手册是**数据驱动**的：
[`knowledge-base/compiler/laws.json`](knowledge-base/compiler/laws.json) 是机器可读索引；
`make check` 会校验 law、对**你机器上的** `cc1` 复核每个二进制锚点，并对手册文档化的每条命令做冒烟测试。

仓库级入口：[README.zh-CN.md](../README.zh-CN.md)、[CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md)、
[tools/README.zh-CN.md](../tools/README.zh-CN.md)。
