# 术语表

[English](GLOSSARY.md) | [简体中文](GLOSSARY.zh-CN.md)

本项目文档与匹配反编译社区使用的术语。一个术语可能先于解释它的页面出现；以被指向的页面为准。

## 1. 平台与硬件

| 术语 | 含义 |
| --- | --- |
| **EE** | Emotion Engine，PS2 主 CPU：MIPS III / R5900 派生，含 128 位 MMI 指令与两个向量单元 |
| **IOP** | PS2 的 I/O 处理器，R3000A 核；游戏把 IRX 模块加载进去 |
| **VU0 / VU1** | 两个向量单元。VU0 可作内联 COP2 宏指令或独立微程序；VU1 主要跑图形微码 |
| **GS** | Graphics Synthesizer，PS2 图形硬件 |
| **SPU2** | PS2 声音处理单元 |
| **SIF / DMA** | EE 与 IOP 之间的通道 |
| **R5900** | EE 的 CPU 核。反汇编器需要 R5900 支持（例如 Ghidra 的 `r5900:LE:32:default`）才能正确解码 |
| **R3000A** | IOP 的 CPU 核 |
| **MMI** | Multimedia Instructions，EE 的 128 位指令组 |
| **COP2** | 协处理器 2 指令空间。在 EE 上承载向量单元搬运（`lqc2`、`qmfc2` 等） |
| **HLE** | High-Level Emulation：不模拟硬件，直接在宿主上实现被调库的行为。它不同于匹配反编译；本仓库不用 |

## 2. 光盘格式与模块

这些都在 [FORMATS.zh-CN.md](FORMATS.zh-CN.md) 里详述。

| 术语 | 含义 |
| --- | --- |
| **ERX** | Gust 的动态模块格式：32 位 MIPS ELF（`e_type = 0xFF91`）。本作 11 个 |
| **`.erx.lib`** | 主程序里的导出符号注册表段；本项目的具名符号来自它 |
| **RPK / AFS** | 大资产容器（`RPK.BIN`）及其内部归档格式。本作的 AFS 是 Gust 紧凑变体，不是标准 CRI 的 |
| **LZR** | `RPK.BIN` 内使用的压缩块格式 |
| **`.evd`** | 事件脚本容器，也是游戏文本的最大来源 |
| **IRX / `.irx.lzr`** | IOP 模块，运行时加载 |
| **CRI / CRI-MW** | 第三方中间件（ADX 音频、Sofdec 影片）。用 `ee-gcc 2.96` 编译，不是 3.2 |
| **ADX / SFD** | CRI 音频 / CRI 视频（`SFD` 是裸 MPEG-1 Program Stream） |
| **DVP** | 主程序里的 VU1 微码 overlay 段（`.DVP.*`） |

## 3. 匹配反编译

| 术语 | 含义 |
| --- | --- |
| **匹配反编译** | 反推出的 C 源码用**原编译器**编译后，与零售函数**字节一致**。它是唯一能自动验证的反向工程形式 |
| **匹配函数** | 重建对象与零售对象逐字节一致的函数。主进度只统计源码是 C 的匹配函数 |
| **转录（transcription）** | 把目标指令逐条抄进汇编块，而不是反推 C。对象逐字节一致，但没有恢复出 C。单独计数，见 [TRANSCRIPTION.zh-CN.md](../TRANSCRIPTION.zh-CN.md) |
| **伪匹配（fakematch）** | 原开发者的源码不可能产生的字节匹配。社区视为无效 |
| **splat** | 二进制拆分器（源于 N64 项目，支持 PS2），产出逐函数汇编与链接脚本 |
| **spimdisasm** | splat 底层的 MIPS 反汇编器 |
| **m2c** | 从汇编起草 C 的反编译器。对本作的 MMI/COP2 代码提升效果很差 |
| **permuter** | `decomp-permuter`：对小块指令重排做自动搜索，逐档编译比对。用来收口近失候选 |
| **objdiff** | 逐函数字节比对工具；它的报告是本项目的进度来源 |
| **decomp.me / decomp.dev** | 社区协作平台 / 读取 objdiff 报告的进度追踪站 |
| **TU** | 翻译单元，一个编译输入。「哪些函数属于同一个 TU」是匹配的关键约束 |
| **GP / FP** | 通用寄存器组 / 浮点寄存器组。两组之间的分配竞争是大函数差异的主要来源 |
| **基线（baseline）** | 把整棵拆分树重新汇编并链接，证明拆分忠实 |
| **混合构建（mixed build）** | 用我们写的 C 替换已匹配函数、其余仍用汇编，再链接校验载荷 |
| **载荷（payload）** | 可执行文件可加载段按文件偏移拼接的结果；与零售载荷逐字节比对 |
| **per-symbol 段** | 每个匹配函数放进自己的 `.text` 段 `func_XXXXXX`（数据同理），从而能单独替换一个函数 |

## 4. 项目约定

| 术语 | 含义 |
| --- | --- |
| **主口径（main metric）** | 头条百分比：匹配源码是重建 C 的匹配函数 |
| **转录口径（transcription metric）** | 用逐条汇编转录匹配的函数，单独小计；永不并入主口径 |
| **matching-gate** | 重建载荷并用零售二进制校验改动的 CI 工作流 |
| **进度报告** | `progress/SLPS_258.19_report.json`，由一次已验证构建写出；decomp.dev 读它 |
| **基线报告** | `progress/baseline.json`，上次发布的报告。CI 拒绝发布更差的报告 |

## 5. 缩写

| 缩写 | 全称 |
| --- | --- |
| EE | Emotion Engine |
| IOP | I/O Processor |
| VU0 / VU1 | Vector Unit 0 / 1 |
| GS | Graphics Synthesizer |
| SPU2 | Sound Processing Unit 2 |
| SIF | Sub-system Interface |
| DMA | Direct Memory Access |
| R5900 / R3000A | EE / IOP 的 CPU 核型号 |
| MMI | Multimedia Instructions |
| COP2 | Coprocessor 2 |
| HLE | High-Level Emulation |
| ERX | Gust 动态模块格式 |
| RPK | Gust 资产容器格式 |
| AFS | 内部归档格式 |
| LZR | 压缩块格式 |
| EVD | 事件脚本容器 |
| IRX | IOP 模块格式 |
| CRI | CRI Middleware |
| ADX / SFD | CRI 音频 / 视频格式 |
| TU | Translation Unit |
| GP / FP | 通用 / 浮点寄存器组 |
| CI | Continuous Integration |

## 6. 另见

- [KNOWN-BLOCKERS.zh-CN.md](KNOWN-BLOCKERS.zh-CN.md) —— 会产生假结果的陷阱。
- [compiler/README.zh-CN.md](compiler/README.zh-CN.md) —— 代码生成手册。
- [FORMATS.zh-CN.md](FORMATS.zh-CN.md) —— 上面提到的格式，详解。
