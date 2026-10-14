# EE GCC 3.2 代码生成手册

[English](README.md) · [laws](LAWS.zh-CN.md) · [源码研究](SOURCE-STUDY.zh-CN.md) · [agent 技能](AGENT-SKILL.zh-CN.md) · [pass 地图](PASSES.zh-CN.md) · [诊断流程](DIAGNOSTICS.zh-CN.md) · [杠杆表](FIELD-GUIDE.zh-CN.md) · 机器可读索引：[`laws.json`](laws.json)

**对出厂编译器核验过**：本手册引用的 **13 个**二进制锚点已全部对出厂 `cc1` 复核、地址一致；
`python3 tools/check/test_compiler_laws.py` 会强制分级前置条件，并在本机有工具链时逐条复核锚点。

本手册记录 **`ee-gcc 3.2-ee-040921`** 的行为——本项目 PS2 Emotion Engine 代码所用的编译器，
构建参数为 `-O2 -falign-functions=4 -ffunction-sections`。

写作目的是**匹配反编译**：匹配要求逐字节相同，所以「编译器为什么发这条指令」是最费时间的问题。
每条 law 回答一个这样的问题并给出证据；每条杠杆给出「源写法 → 预期读数移动」。

## 内容

| 页面 | 写的是什么 |
| --- | --- |
| [LAWS.md](LAWS.zh-CN.md) | 编译器**怎么做**：分配顺序、结构宽度、频率口径、EE 专有后端。每条带 tier、源码锚点、二进制锚点、receipt、scope |
| [PASSES.md](PASSES.zh-CN.md) | 3.2 的 26 份 `-da` dump（2.96 是 22 份）、各自归哪个源文件、出厂源码与 mainline 的位移 |
| [DIAGNOSTICS.md](DIAGNOSTICS.zh-CN.md) | 从「diff 不对」走到「这个 pass 负责」：第一分叉流程、两个假信号、什么时候别用模型 |
| [FIELD-GUIDE.md](FIELD-GUIDE.zh-CN.md) | 能移动读数的源写法，以及每种写法移动哪个读数 |
| [SOURCE-STUDY.zh-CN.md](SOURCE-STUDY.zh-CN.md) | 有哪些源码、没有哪些、规则怎么对锚，以及为什么社区 EE 补丁是另一棵树 |
| [AGENT-SKILL.md](AGENT-SKILL.zh-CN.md) | agent（或赶时间的人）跑的循环：测量 → 定位 pass → 查 law → 用杠杆 → 复测 |
| [`laws.json`](laws.json) | 同一批 law 的机器可读版本，供工具与 agent 查询 |

## 证据分级

匹配社区里最常见的问题，是**自信、合理、但错误**的规则。分级就是为了让这种事可见：

| 级别 | 需要同时满足 |
| --- | --- |
| **T1** | 从编译器源码读到规则 **且** 在同一段代码在出厂二进制里定位到（符号 / 地址 / 常量 / 结构偏移）**且** 行为一致 |
| **T2** | 源码规则 **或** 二进制锚点，加行为一致 |
| **T3** | 只有行为证据 |

`T1` 要求两个锚点，是因为**出厂编译器不是 mainline 源码**：已经实测到两处差异（L-EE-003、L-EE-004），
而另一处**疑似**差异查源码后证明是我自己误读了注释（L-EE-005）。这类错误分级能拦住，靠文风拦不住。

每条 law 还带 **scope**（实际覆盖到什么范围）。本手册**不作「不可能」断言**：关闭的杠杆记录的是搜过的空间。

## 两个锚点

出厂 `cc1` **未 strip 且带 DWARF**，所以出厂二进制本身就是一等证据来源。自备工具链后：

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1

python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" selftest
```

`python3 tools/check/test_compiler_laws.py` 校验 `laws.json` 与 `LAWS.md` 双向一致、分级前置条件成立，
并在本机存在 `cc1` 时逐条核对二进制锚点。

## 范围与诚实边界

* 全部结论只属于 **`ee-gcc 3.2-ee-040921`**。`ee-gcc 2.96-ee-001003-1` 编译本项目的 CRI 中间件，pass 编号不同，本手册不替它下结论。
* mainline **gcc-3.2.3** 只作**语义**参照，不作行号参照；逐函数位移见 L-EE-006。
* 本仓库不含游戏资产、游戏反汇编与编译器二进制。锚点是编译器内部符号、地址、行号与常量，属符号级事实。
* 手册是版本化且持续维护的：攻击大函数时发现的新机制，应当以 law 或杠杆的形式带证据回到这里。
