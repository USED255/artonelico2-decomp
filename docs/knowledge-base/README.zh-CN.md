# 知识库

[English](README.md) | [简体中文](README.zh-CN.md)

收录与本作及其工具链有关的参考资料。操作类文档（构建、政策、转录口径、贡献）在上一级
[docs/](../README.zh-CN.md)。

## 1. 编译器手册

[EE GCC 3.2 代码生成手册](compiler/README.zh-CN.md)记录**生成游戏代码的那个编译器**在本项目编译
旗标下的行为。每条都带分级、源码锚点、二进制锚点、receipt 与 scope。`make check` 校验这些数据，
并对**你机器上的** `cc1` 复核每个二进制锚点。

| 页面 | 内容 |
| --- | --- |
| [compiler/README.zh-CN.md](compiler/README.zh-CN.md) | 手册索引、证据分级与工具 |
| [compiler/LAWS.zh-CN.md](compiler/LAWS.zh-CN.md) | 编译器做什么：分配顺序、结构体宽度、频率记账、EE 后端 |
| [compiler/QUICK-REFERENCE.zh-CN.md](compiler/QUICK-REFERENCE.zh-CN.md) | 从眼前的形状出发，找到解释它的 law |
| [compiler/DIAGNOSTICS.zh-CN.md](compiler/DIAGNOSTICS.zh-CN.md) | 从「diff 不对」走到「哪个 pass 负责」 |
| [compiler/FIELD-GUIDE.zh-CN.md](compiler/FIELD-GUIDE.zh-CN.md) | 能移动读数的源写法 |
| [compiler/CASE-STUDY.zh-CN.md](compiler/CASE-STUDY.zh-CN.md) | 一个函数从头到尾，含一个被否掉的改动 |
| [compiler/CASE-STUDY-LARGE.zh-CN.md](compiler/CASE-STUDY-LARGE.zh-CN.md) | 大函数：用帧读数 |
| [compiler/ABI.zh-CN.md](compiler/ABI.zh-CN.md) | 一页读懂调用约定 |
| [compiler/PASSES.zh-CN.md](compiler/PASSES.zh-CN.md) | `-da` 导出，以及每个 pass 归哪个源文件 |
| [compiler/CROSS-2.96.zh-CN.md](compiler/CROSS-2.96.zh-CN.md) | 哪些规则适用于编译 CRI 中间件的 2.96 |
| [compiler/SOURCE-STUDY.zh-CN.md](compiler/SOURCE-STUDY.zh-CN.md) | 有哪些编译器源码，规则怎么对锚 |
| [compiler/COVERAGE.zh-CN.md](compiler/COVERAGE.zh-CN.md) | 手册能解释一个二进制的多少，实测 |
| [compiler/VERIFY.zh-CN.md](compiler/VERIFY.zh-CN.md) | 钉定的工具链，以及每套校验验什么 |
| [compiler/AGENT-SKILL.zh-CN.md](compiler/AGENT-SKILL.zh-CN.md) | 自动化 agent 的循环 |
| [compiler/laws.json](compiler/laws.json) | 同一批 law 的数据版，供工具与 agent 使用 |

## 2. 项目参考

| 页面 | 内容 |
| --- | --- |
| [KNOWN-BLOCKERS.zh-CN.md](KNOWN-BLOCKERS.zh-CN.md) | 本工具链收不了的东西，以及停止条件 |
| [FORMATS.zh-CN.md](FORMATS.zh-CN.md) | 光盘上的资产与模块格式（实测） |
| [TOOLCHAIN.zh-CN.md](TOOLCHAIN.zh-CN.md) | 哪个编译器编了什么、构建旗标、如何核验你手上的副本 |
| [LANGUAGE.zh-CN.md](LANGUAGE.zh-CN.md) | 为什么匹配源码用 C，什么情况下单个 TU 可能需要 C++ |
| [GLOSSARY.zh-CN.md](GLOSSARY.zh-CN.md) | 术语、格式与缩写 |

## 3. 这一块怎么维护

- 新的编译器机制、或能移动读数的杠杆，必须写成 `compiler/` 里的一条 law 或一行 field-guide。
  一次大函数攻关在机制写下来之前不算收尾。
- 新的光盘实测事实进 `FORMATS.md`，新的编译器/构建事实进 `TOOLCHAIN.md`。两处都不写会随进度
  变化的数字。
- 每页都有英文原文与中文对照（`*.zh-CN.md`），以英文页为准。
- 这里不得出现游戏资产、ROM 镜像、照抄的汇编列表或 Sony 工具链。见
  [PUBLICATION-POLICY.zh-CN.md](../PUBLICATION-POLICY.zh-CN.md)。
