# 文档

[English](README.md) | [简体中文](README.zh-CN.md)

从哪读起，取决于你要做什么。

| 我想…… | 读 |
| --- | --- |
| 构建本项目 | [BUILD.zh-CN.md](BUILD.zh-CN.md) |
| 知道什么可以公开 | [PUBLICATION-POLICY.zh-CN.md](PUBLICATION-POLICY.zh-CN.md) |
| **理解编译器为什么生成这段代码** | **[compiler/README.zh-CN.md](compiler/README.zh-CN.md)** —— EE GCC 3.2 代码生成手册 |
| 修一个「能编过但匹配不上」的函数 | [compiler/DIAGNOSTICS.zh-CN.md](compiler/DIAGNOSTICS.zh-CN.md)，再读 [compiler/FIELD-GUIDE.zh-CN.md](compiler/FIELD-GUIDE.zh-CN.md) |
| 看手册的规则及其证据 | [compiler/LAWS.zh-CN.md](compiler/LAWS.zh-CN.md) |
| 看一个函数从头到尾（含被否掉的改动） | [compiler/CASE-STUDY.zh-CN.md](compiler/CASE-STUDY.zh-CN.md) |
| 知道有哪些编译器源码、规则怎么对锚 | [compiler/SOURCE-STUDY.zh-CN.md](compiler/SOURCE-STUDY.zh-CN.md) |
| 让 agent 使用手册 | [compiler/AGENT-SKILL.zh-CN.md](compiler/AGENT-SKILL.zh-CN.md) |

手册每页都有英文版（同名 `.md`）。手册是**数据驱动**的：[`compiler/laws.json`](compiler/laws.json) 是机器可读索引；
`make check` 会校验 law、对**你机器上的** `cc1` 复核每个二进制锚点，并对手册文档化的每条命令做冒烟测试。

仓库级入口：[README.zh-CN.md](../README.zh-CN.md)、[CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md)、
[tools/README.zh-CN.md](../tools/README.zh-CN.md)。
