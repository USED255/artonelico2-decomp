# 工具链身份

[English](TOOLCHAIN.md) | [简体中文](TOOLCHAIN.zh-CN.md)

匹配构建只有一个硬要求：字节一致。而字节一致从编译器开始。本页记录哪个编译器编了什么，以及
怎么核验你手上的副本。

本仓库不含 Sony 工具链，也不提供它的下载链接。工具链是专有软件；请自备：来自你自己的授权 SDK，
或你有权使用的副本。

## 1. 两个编译器编出了这个游戏

| 代码 | 编译器 | 证据 |
| --- | --- | --- |
| 游戏代码（主 `.text`） | `ee-gcc 3.2-ee-040921` | SDK 3.0.3 世代的编译器；见 [toolchain.lock.json](../../toolchain.lock.json) 与[编译器手册](compiler/VERIFY.zh-CN.md) |
| CRI 中间件（ADX 音频、Sofdec 影片） | `ee-gcc 2.96-ee-001003-1` | 九处 `Append: GCC2096 SCE3100` 横幅串紧跟 CRI 模块横幅 |
| IOP 模块 | IOP 编译器 2.8.1 世代 | IRX 是独立二进制；主构建把它们当数据用 |

游戏代码与 CRI 模块由**不同编译器**编出。只在一个编译器下匹配上的函数是正常现象；两者之间哪些
规则通用，见 [CROSS-2.96.zh-CN.md](compiler/CROSS-2.96.zh-CN.md)。

## 2. 为什么必须同版编译器

`ee-gcc` 是 Sony 基于 Cygnus GNUPro 的分支，不是 FSF 原版发布。它加了 EE ABI、`-mno-abicalls`、
`.mdebug.eabi64`、ERX 支持与自己的指令选择。两个都自称「GCC 3.2」的构建不能互换：

- 当前的 `ps2dev` 工具链（binutils + GCC 15）面向同一颗 CPU，但生成的代码不同。拿来做工具实验
  可以，做字节匹配没用。
- FSF 原版 GCC 3.2 的 MIPS 目标 ABI 与重定位都不同。
- 即使在 Sony 这条线上，版本之间也不等价：3.2 与 2.96 的 pass 编号不同，手册因此单列一页对照。

所以匹配的意思是：零售版的源码形状 + 零售版编译器 + 零售版旗标。

## 3. 构建旗标

游戏构建用这些旗标编译 C：

```
-O2 -falign-functions=4 -ffunction-sections
```

两个细节最容易浪费时间：

- 胜出的优化档**不一定**是记录里的那一档。下结论说源码形状不对之前，先把 `-O1`、`-O2`、`-O3`、
  `-Os` 都扫一遍。[KNOWN-BLOCKERS.zh-CN.md](KNOWN-BLOCKERS.zh-CN.md) 把这条列为陷阱。
- 由 CRI 编译器编的源码需要 `-G0`：小数据（gp 相对）阈值与主构建不同。见
  [config/README.md](../../config/README.md)。

汇编器用 decompals 的 GNU binutils 2.40 分支。官方 binutils 2.45 会拒绝 `$t4` 到 `$t7` 的寄存器
别名。

## 4. 核验手上的副本

1. **版本串**：游戏编译器 `ee-gcc --version` 必须打印 `ee-gcc (GCC) 3.2-ee-040921`；CRI 编译器打印
   `2.96-ee-001003-1`。
2. **钉定哈希**：[toolchain.lock.json](../../toolchain.lock.json) 记录 CI 用到的每个工具链归档的
   sha256，CI 构建前逐个核验。
3. **编译器二进制**：[compiler/VERIFY.zh-CN.md](compiler/VERIFY.zh-CN.md) 记录两个 `cc1` 的 sha256。
   这是最强的检查：版本串容易弄错，二进制哈希不会。
4. **行为**：手册的校验会对你的编译器重跑行为探针。跑 `make check`：需要工具链的部分在工具链
   存在时运行，不存在时干净跳过。

## 5. 工具链在这里做不到什么

零售可执行文件里有些节不是 C 编译器产出的：`.DVP.*`（VU1 微码）与 `.erx.*`（ERX 模块机制）由
Sony 的其它工具生成。GNU `ld` 不会生成它们。

本项目不试图重建容器：它沿用零售 ELF 容器，只把**载荷**（可加载段按文件偏移拼接）逐字节校验。
验收口径见 [BUILD.zh-CN.md](../BUILD.zh-CN.md) 与 [TRANSCRIPTION.zh-CN.md](../TRANSCRIPTION.zh-CN.md)。

## 6. 相关页面

- [compiler/README.zh-CN.md](compiler/README.zh-CN.md) —— 代码生成手册本体。
- [compiler/VERIFY.zh-CN.md](compiler/VERIFY.zh-CN.md) —— 钉定的工具链，以及每套校验验什么。
- [compiler/CROSS-2.96.zh-CN.md](compiler/CROSS-2.96.zh-CN.md) —— 编 CRI 代码的 2.96 编译器。
- [../BUILD.zh-CN.md](../BUILD.zh-CN.md) —— 你需要自备的项，以及构建命令。
