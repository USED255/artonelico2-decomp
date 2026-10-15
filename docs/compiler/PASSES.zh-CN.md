# pass 地图 —— ee-gcc 3.2 / 2.96

[English](PASSES.md) · [手册索引](README.md) · [laws](LAWS.md)

`ee-gcc` 支持 `-da`，会为每个 pass 写一份 RTL dump，命名为 `<file>.<NN>.<pass>`。
本项目两个编译器的编号不同，所以 pass 表**只在同一个编译器内**有效。按 pass **名**比较，永远不要按编号。

## dump 清单

| `ee-gcc 3.2-ee-040921`（26 份） | `ee-gcc 2.96-ee-001003-1`（22 份） |
| --- | --- |
| `00.rtl` `01.sibling` `03.jump` `08.null` `09.cse` `10.addressof` `11.gcse` `12.loop` `13.cfg` `14.bp` `15.cse2` `16.life` `17.combine` `18.ce` `19.regmove` `20.sched` `21.range` `22.lreg` `23.greg` `24.postreload` `25.flow2` `27.rnreg` `28.ce2` `29.sched2` `31.bbro` `33.dbr` | `00.rtl` `01.sibling` `02.jump` `03.cse` `04.addressof` `08.gcse` `09.loop` `10.cse2` `11.cfg` `13.life` `14.combine` `15.ce` `16.regmove` `17.sched` `19.lreg` `20.greg` `21.flow2` `22.ce2` `25.sched2` `27.jump2` `28.mach` `29.dbr` |

3.2 的 `03.jump` 在 2.96 是 `02.jump`。在一边锚定的规则，必须到另一边重新测。

## 哪些 law 在哪个优化档成立

手册的 receipt 都取自 `-O2 -G0`。某条规则在别的档是否仍成立是**实测问题**，夹具套件一条命令就能回答：

```sh
python3 tools/compiler/ee-gcc-observe.py --matrix
```

| 档 | 通过夹具 | 说明 |
| --- | ---: | --- |
| `-O0` | 22/39 | 无优化：用帧指针、常量不合并也不去重、窄类型比较不掩码、循环不强度削减 |
| `-O1` | 36/39 | **没有尾调用**（[L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2)），且定次循环保留**递增 `slt`**（[L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled)） |
| **`-O2`** | **39/39** | receipt 的基准档 |
| **`-Os`** | **39/39** | 本项目**大多数文件**用的档（[L-EE-034](LAWS.md#l-ee-034---os-is-this-projects-most-common-level-and-the-rules-hold-there)） |
| `-O3` | 38/39 | 普通 `static` 助手会被内联（[L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined)） |

本项目只涉及后四档——源按 `-Os`（687）、`-O1`（542）、`-O2`（264）、`-O3`（98）构建，**没有 `-O0`**。
⇒ **`-O2` 与 `-Os` 可照搬全部规则；`-O1` 的差别在循环形态；`-O3` 的差别在内联门槛。**

## 清单随优化档变化

`-da` 为每个**跑过**的 pass 写一份 dump，而跑哪些 pass 取决于 `-O`（[L-EE-020](LAWS.md#l-ee-020--the-pass-pipeline-is--o-sensitive)）。在一个循环夹具上：

| 档 | dump 份数 | 相对 `-O2` 缺哪些 |
| --- | ---: | --- |
| `-O0` | 9 | 除 00.rtl、03.jump、10.addressof、13.cfg、16.life、22.lreg、23.greg、24.postreload、25.flow2 之外的都不跑 |
| `-O1` | 20 | **01.sibling、11.gcse、19.regmove、20.sched、21.range、29.sched2** |
| `-O2` | 26 | — |
| `-Os` | 26 | 与 `-O2` 相同 |

这就是「某函数在 `-O1` 能匹配、在 `-O2` 不能」的原因之一：**`-O1` 不跑调度与寄存器移动**，即使所有决策规则一致，指令顺序也不同。
另外：**只对编译成功的编译数 dump**——源码被拒时只会留下部分 dump。

## 哪个源文件拥有哪个 dump

来源：dump 自身的文本、出厂 `cc1` 里的符号经 `addr2line` 解析、以及 mainline 定义行。映射是**逐条断言**的，不是假定的。

| Dump | 归属源文件（mainline） | 本手册用到的锚点 |
| --- | --- | --- |
| `00.rtl` `01.sibling` | `expr.c`、`function.c`、`calls.c`、`stmt.c`、`stor-layout.c` | — |
| `03.jump` | `jump.c` | — |
| `08.null` | `toplev.c`（空 pass） | — |
| `09.cse` `15.cse2` | `cse.c` | — |
| `10.addressof` | EE 专有 pass；到出厂 `cc1` 里找它的打印点 | — |
| `11.gcse` | `gcse.c` | — |
| `12.loop` | `loop.c` | — |
| `13.cfg` | `cfg*.c` | — |
| `14.bp` | `predict.c` / `profile.c` | — |
| `16.life` | `flow.c` | `life_analysis @ 0x080ce2d8` |
| `17.combine` | `combine.c` | `combine_instructions @ 0x08185f84` |
| `18.ce` `28.ce2` | `ifcvt.c` | — |
| `19.regmove` | `regmove.c` | `regmove_optimize @ 0x081c4640` |
| `20.sched` `29.sched2` | `haifa-sched.c`、`sched-*.c` | `schedule_block @ 0x081b15d8` |
| `21.range` | 出厂 `cc1` 里的区间/活跃区间辅助函数 | — |
| `22.lreg` | `local-alloc.c` | `local_alloc @ 0x0810a2f4` |
| `23.greg` | `global.c` | `global_alloc @ 0x081aa2c4`、`allocno_compare @ 0x081ab288`、`find_reg @ 0x081acd64` |
| `24.postreload` | `reload1.c`、`reload.c` | `find_reg @ 0x08134570` |
| `25.flow2` | `flow.c` | — |
| `27.rnreg` | 寄存器编号相关辅助函数 | — |
| `31.bbro` | `bb-reorder.c` | — |
| `33.dbr` | `reorg.c` | `dbr_schedule @ 0x081cd510` |
| 后端 | `config/mips/mips5900.c`（152 个函数）、`mips.md` | `uns_arith_operand @ 0x0817178c` |

## 出厂源码与 mainline 差多远

出厂 `cc1` 不是用原版 gcc-3.2.3 构建的。下表给出每个源文件的**中位位移**
（`EE 定义行 − mainline gcc-3.2.3 定义行`）。中位为正且大 ⇒ EE 在文件里插入了代码；为负 ⇒ mainline 有 EE 没有的行。

| 源文件 | 中位位移 | 读法 |
| --- | ---: | --- |
| `global.c` | **+341** | 重改（分配、着色） |
| `regmove.c` | **+1920** | 重改 |
| `haifa-sched.c` | **+263** | 重改（调度） |
| `gcse.c` | **+137** | 有改动 |
| `calls.c` | 0 | 与 mainline 同源 |
| `reload1.c` | 0 | 与 mainline 同源 |
| `local-alloc.c` | −4 | 与 mainline 同源 |
| `ifcvt.c` | −6 | 与 mainline 同源 |
| `combine.c` | −8 | 与 mainline 同源 |
| `flow.c` | −13 | 与 mainline 同源 |
| `reorg.c` | −13 | 与 mainline 同源 |
| `regclass.c` | −2 | 与 mainline 同源 |
| `cse.c` | −22 | 点版本量级的差异 |
| `jump.c` | −47 | 点版本量级的差异 |
| `function.c` | −55 | 点版本量级的差异 |
| `loop.c` | −68 | 点版本量级的差异 |
| `expr.c` | +4 | 混合；逐函数核 |

换成 **gcc-3.2.2** 复测，每个中位最多差 1 行，所以上面的位移属于 EE 快照，不是点版本造成的。

**用法**：引用行号时用 `addr2line` 在你自己的 `cc1` 上读出的那个值。mainline 只提供规则的**语义**，
它的行号按实测位移校正后再参考。位移小的文件可以并排读 mainline；位移大的必须用反汇编确认
（见 [L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)）。
