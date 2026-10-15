# 源码研究 —— 我们有什么源码、没有什么、以及怎么对锚

[English](SOURCE-STUDY.md) · [手册索引](README.md) · [laws](LAWS.md) · [pass 地图](PASSES.zh-CN.md)

本手册每条 law 都写明规则的出处。这一页记录「出处」到底是什么，让读者能分清**已核验的规则**与**实测的规则**。

## 1. 有什么

| 源码 | 状态 | 用途 |
| --- | --- | --- |
| **mainline gcc-3.2.3** | 有（`sha256 9229434c…`） | 通用 pass 的**语义**参照：分配、活跃、调度、常量 |
| **mainline gcc-3.2.2** | 有（`sha256 7035a828…`） | 对照：两版对比说明下面的位移属于 EE 快照，不是点版本 |
| **出厂 `cc1`** | 有工具链即有 | **权威**：行号、结构布局、常量；未 strip 且带 DWARF |
| **社区 EE 补丁**（`gcc-3.2.2-PS2.patch`、`gcc-3.2.3-PS2.patch`） | 有（在社区工具链脚本的 git 历史里） | 仅作 **EE 指令语义**参照（MMI、VU 宏模式、R5900 约束）。**不是**出厂树，见 §4 |
| **Sony `config/mips/mips5900.c`** | **没有** | 出厂后端有它（152 个函数），EE 寄存器模型就在里面 |
| **Sony 3.2-ee-040921 源树** | **没有** | — |
| **Jürgen Urban 的 R5900 补丁（2013）** | 有（[gcc-patches 附件](https://gcc.gnu.org/pipermail/gcc-patches/2013-January/356066.html)） | 只做 ISA 使能（`-mno-llsc`、`trunc.w.s`），**不定义寄存器类** |

## 2. 没有出厂树时怎么对锚

出厂 `cc1` 就是权威。`tools/compiler/ee-gcc-anchor.py` 把符号变成地址、源码行、结构布局或常量：

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8
```

`T1` 需要同时具备源码规则、二进制锚点与一致行为。源码不可得时，条目降为 `T2`（二进制锚点或源码规则 + 行为）或 `T3`（只有行为），并在条目里写明。

## 3. 行号不可搬运

出厂编译器**不是**原版 gcc-3.2.3。实测的每文件中位位移（EE 定义行 − mainline 定义行）：

| 文件 | 位移 | 读法 |
| --- | ---: | --- |
| `global.c` | **+341** | 已改（分配、着色） |
| `regmove.c` | **+1920** | 已改 |
| `haifa-sched.c` | **+263** | 已改（调度） |
| `gcse.c` | **+137** | 已改 |
| `reload1.c`、`calls.c`、`local-alloc.c`、`regclass.c`、`ifcvt.c`、`combine.c`、`flow.c`、`reorg.c` | 0 … −13 | 基本等同 mainline |
| `cse.c`、`jump.c`、`function.c`、`loop.c` | −22 … −68 | 点版本量级 |

与 gcc-3.2.2 对照，每个中位最多差 1 行 ⇒ 位移属于 EE 快照。**引用行号一律用 `addr2line` 报出的值**（[L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)）。

## 4. 为什么社区 EE 补丁不是出厂树

社区工具链历史里有 `patches/gcc-3.2.2-PS2.patch`（184,804 B，32 文件）与 `patches/gcc-3.2.3-PS2.patch`（160,132 B，26 文件），确实加了 EE 支持（`core-mmi.h`、`core-vumm.h`、`r5900.h`、`crti5900.asm`、`t-r5900`，并改 `mips.c`/`mips.h`/`mips.md`）。

但**寄存器模型是另一套**：

| 寄存器类 | 社区 3.2.2 补丁 | 出厂 `cc1` 的 dump |
| --- | --- | --- |
| `VU0_Q_REG`、`VU0_I_REG`、`VU0_GR_AND_QI_REGS` | 无 | 有 |
| `COP0_AND_GR_REGS` | 无 | 有 |
| `FP_ACC_REG` | 无 | 有 |
| `HILO_REGS` | 无 | 有 |
| `HI1_REG`、`LO1_REG`、`ST_REGS` | 有 | — |
| `HARD_REG_SET` 宽度 | 3 字（≈96 位） | **24 B = 192 位** |
| `FIRST_PSEUDO_REGISTER` | 76 → **79** | 远大于 79 |

⇒ 补丁只能当**EE 指令语义**的参照，不能用来做寄存器文件、寄存器类与分配器。那部分只能从二进制读——这也是着色模型仍未解决的原因（见 [LAWS.md](LAWS.md) 的 Open items）。

## 5. 还缺什么、什么能补上

* 精确的 `FIRST_PSEUDO_REGISTER` 与类内容。类表（`reg_class_contents`、`reg_class_size`、`fixed_reg_set`、`call_used_reg_set`）是**运行时初始化**（`.bss`），静态读出来是 0。从活进程里读是直接路径；Sony 源码能静态回答。
* `global.c`、`regmove.c`、`haifa-sched.c`、`gcse.c` 那几处补丁的内容。
* 社区补丁**可用**的地方：后端的 EE 指令语义。从它得到的规则在出厂二进制确认之前一律是 `T3`。

### 5.1 已经搜过、不要重复的路线

| 路线 | 结果 |
| --- | --- |
| 社区工具链 git 历史 | 找到 `gcc-3.2.2-PS2.patch` 与 `gcc-3.2.3-PS2.patch`（见 §4） |
| Wayback 的 ps2dev 工具链页（2008） | 确认社区工具链 = gcc-3.2.2 + 补丁 |
| GitHub 代码搜索 `filename:mips5900.c` | **0 结果** |
| Software Heritage 搜 `ee-gcc` | 无相关命中 |
| gcc-patches：Jürgen Urban《Support for MIPS r5900》(2013) | 补丁已取到；只做 ISA 使能，**无寄存器类** |
| Internet Archive：**PS2 Linux Kit 两张 DVD** | 已定位并**远读**（用 ISO9660 目录表 + HTTP Range，不下载整盘）。Disc 1 = 安装盘；Disc 2 = 软件树。`/SCEI/RPMS` 里是 **EE 工具链二进制**（`GCC-29`、`GCC-C++`、`GCC-G77`、`GCC-OBJ`、`BINUTILS`）；`/SCEI` 下**没有 SRPMS**，根级 `/SRPMS`、`/SOURCES` 属发行版。**套件盘不含 EE 编译器源码。**（`SOURCES/EE-031_1.GZ` 是 `ee` 文本编辑器，不是 Emotion Engine。） |
| `mips5900.c` / `ee-gcc 3.2-ee-040921` 源码（常规检索） | 无命中 |

**2.9 代确实有 Sony 的官方发布**：GitHub 的 [`GirianSeed/ee-gcc`](https://github.com/GirianSeed/ee-gcc/releases) 放出了 4 个 Sony `ee-gcc` 源码包（全为 2.9 代，1999）。
其打包形态就是要找的目标形态：`config.sh` 里 `--prefix=/usr/local/sce/ee/gcc --target=ee`（**与本工具链 DWARF 里报告的前缀与 target 完全一致**）、
`COPYING`/`COPYING.LIB`/`COPYING.NEWLIB`、`sce-patch/patch`（Sony 的 context diff）、`src/src.tar.gz`。⇒ Sony **确实**以 GPL 发布过 EE GCC 源码。

但那不是出厂 3.2 树：该补丁**没有改** `config/mips/mips.md`，也没有 `mips5900.c`、没有 `mips5900_*` 模式名、没有 VU0/COP0/ACC 寄存器类。
EE 的**代码生成**是 3.x 代才做进去的——那正是仍缺的部分。

**阶段性结论：没有任何公开源码包含 EE 寄存器模型**（192 位 `HARD_REG_SET`、`VU0_*`、`COP0_AND_GR_REGS`、`FP_ACC_REG`、`HILO_REGS`）。找到的公开 EE 补丁寄存器文件都**更小且不同**。这就是寄存器类与着色类条目是 `T2`/`T3` 的原因，也是「直接读运行时表」这条路的依据。
