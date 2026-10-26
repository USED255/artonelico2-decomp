# 知识库

[English](README.md) | [简体中文](README.zh-CN.md)

收录与本作及其工具链有关的参考资料。操作类文档（构建、政策、转录口径、贡献）在上一级
[docs/](../README.zh-CN.md)。

## 1. 编译器手册

[EE GCC 3.2 代码生成手册](compiler/README.zh-CN.md)记录**生成游戏代码的那个编译器**在本项目编译
旗标下的行为。手册自己的索引列出每一页：law、pass 图、诊断流程、案例、ABI 页与工具。

`laws.json` 是机器可读副本。`make check` 校验它，并对**你机器上的** `cc1` 复核每个二进制锚点。

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
