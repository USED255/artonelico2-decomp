# 验证 —— 这些结论是在什么环境上测出来的，以及怎么重跑

本手册里每一条行为结论都是**测出来的**，不是回忆出来的，而且测量钉定在**具体的工具链**上。
本页记录该工具链，以便你复现这些校验；同时明确说明每条校验**验证什么**、**在什么情况下静默跳过**。

## 两个编译器

| | 3.2 | 2.96 |
| --- | --- | --- |
| 版本串 | `ee-gcc (GCC) 3.2-ee-040921` | `2.96-ee-001003-1` |
| `cc1` | `…/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1` | `…/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cc1` |
| `cc1` sha256 | `0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d` | `59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5` |
| `cc1` 大小 | 7 201 720 | 5 526 661 |

游戏代码是 3.2，CRI 中间件是 2.96。代码与常量都**锚定在二进制 `cc1` 上**：
凡引用符号或常量，[`ee-gcc-anchor.py`](../tools/compiler/ee-gcc-anchor.py) 都在**这个**二进制里解析，
校验套件每次运行都会重新解析。

**如果你的 `cc1` 哈希不同**，二进制锚点就可能移动——地址、结构体大小、枚举值都是**该二进制**的属性。
请重跑锚点套件；把「地址移动」当作「你在看另一个构建」的信号，而不是当作「law 错了」。

## 汇编器与反汇编器

这里的 `objdump` 是 **GNU Binutils 2.40**（`mips-ps2-decompals-objdump`）——是**较新的** binutils，不是原始 SDK 工具。
这很重要：本手册记载的若干助记符拼写是**该反汇编器**的选择，而不是指令本身的名字——

* `daddu $d,$s,$0` 被印成 **`move`**（[L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu)）；
* 本编译器**不用** `addu` 形式的拷贝；
* `li` 是对小 `ADDIU`/`ORI` 的打印，两条指令的形式则直接印 `lui` + `ori`；
* 对 `$0` 的 `beql`/`bnel` 印成 `beqzl`/`bnezl`（[L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not)）；
* `ulw`/`usw` **在对象里从不出现**——它们是汇编伪指令，展开为 `lwr`+`lwl`（[L-EE-044](LAWS.md#l-ee-044--unaligned-access-three-sources-and-ulwusw-do-not-exist-in-the-object)）。

换一个 binutils 可能印法不同。凡**要紧的地方**，law 都在**编码**层面表述，校验套件也**直接验编码**
（`move` 是 funct `0x2d`；`li` 是 opcode `0x09` 或 `0x0d`）。

## 怎么全部重跑

```sh
make check                                  # 仓库校验 + law 数据 + 锚点 + 工具冒烟
python3 tools/check/test_compiler_laws.py   # laws.json <-> LAWS.md、锚点、覆盖率、漂移守卫
python3 tools/check/test_compiler_tools.py  # 每个工具的自测（本机缺什么就跳过什么）
python3 tools/compiler/ee-gcc-observe.py --selftest   # 全部夹具，用本机编译器
python3 tools/compiler/ee-gcc-observe.py --matrix     # 夹具在 -O0/-O1/-O2/-Os/-O3 下的表现
python3 tools/compiler/ee-gcc-coverage.py --selftest  # 覆盖率分类器（不需要工具链）
```

### 每套校验验什么、跳过什么

| 套件 | 验证 | 何时跳过 |
| --- | --- | --- |
| `test_compiler_laws.py` | 每条 law 都有页内小节与 `laws.json` 条目；每个锚点可解析；页内与跨页锚点全部可解析；每条 law 都能从速查表到达；文档里的夹具数等于工具的夹具数；每个 `tools/compiler/*.py` 都在技能页被点名；两条字节级编码 | **从不**——纯数据，加上本机存在的 `cc1`/`objdump` |
| `test_compiler_tools.py` | 每个工具的 `--selftest`；夹具套件必须报 `0 failed`；2.96 交叉校验 | 本机缺少的工具、`cc1`、2.96 编译器或 `objdump`（报 `skip`，**从不**当作通过） |
| `--matrix` | 哪些规则在哪些档位成立 | 不跳过；某个档位让某夹具失败是**合法结果**，矩阵会报出来而不是掩盖 |

矩阵是这套装置里**有意为之**的一部分：它已经抓到过本手册自己的若干错误——档位相关的 `mult1`、
关于循环回边的过度泛化、以及一个读错对象物的对齐校验。**「在 `-O2` 成立、在 `-Os` 悄悄不成立」的主张，
是在这里被抓出来的，不是在散文里。**

## 手册钉定在什么上

* **档位**：除 law 另有说明，一律 `-O2 -G0`；档位矩阵记录了规则变化的地方。
* **对齐**：本项目用 `-falign-functions=4 -ffunction-sections`（[L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)），
  **不带** `-G`、**不带** `-mlong*`；如果 `build_mixed.sh` 的 `MATCHED_CFLAGS` 默认值与手册声明的旗标不一致，仓库校验会变红。
* **源码**：语义基准是 **mainline gcc-3.2.3**；Sony 出厂树**不可得**，所以一切 EE 特有行为都是**测的**而非读的
  （[SOURCE-STUDY](SOURCE-STUDY.md)）。
* **Tier**：`T1` = 已在出厂 `cc1` 中定位并在二进制里复核；`T2` = 实测行为；`T3` = 背景或否定性知识。
  law 的 tier 就是「可信度有多少」的诚实陈述。

**实时观测（可选）。** `tools/compiler/ee-gcc-observe-alloc.py` 在 `gdb` 下驱动 `cc1`。本手册只在钉定的
`cc1` 上用 gdb 16.3 实测过；换构建时 hook 地址按该二进制的符号解析，8 字节入口 guard 会跳过并给出警告。
没有 gdb 时工具直接报错退出，检查套件把它的自检记为 **SKIP**（绝不记成 pass）。

## 报告失败

如果你的机器上某个校验失败，有用的报告是：**哪个校验**、**`cc1` 的 sha256**、**objdump 版本**。
锚点移动 ⇒ 那是另一个构建；夹具只在某个档位失败 ⇒ 那是一条**手册还没记录的档位依赖**——这是**发现**，不是噪声。
