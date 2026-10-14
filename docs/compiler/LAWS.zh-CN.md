# 编译器行为条目（laws）· ee-gcc 3.2-ee-040921

[English](LAWS.md) · [手册索引](README.md) · 机器可读：[`laws.json`](laws.json)

本页记录**编译器怎么做**；由此推出的源写法杠杆在 [FIELD-GUIDE.md](FIELD-GUIDE.md)，定位流程在 [DIAGNOSTICS.md](DIAGNOSTICS.md)。
英文版每条含完整模板（tier / 源码锚点 / 二进制锚点 / receipt / falsifies / scope）；本中文版按增量维护，先给条目与结论。

**最重要的一条纪律**：引用行号时，一律用 `addr2line` 在**出厂 `cc1`** 上读出的那个行号；mainline 行号只能作为带位移的对照。

---

## L-EE-001 · 全局分配顺序 = `allocno_compare`

```
pri = (int)( (floor_log2(n_refs) * freq) / live_length * (10000 / REG_FREQ_MAX) * size )
```

因子 `10000 / REG_FREQ_MAX` 是 **10**（`REG_FREQ_MAX == 1000`）。同分按 allocno 序号升序。
**T1**｜源码锚点 `global.c:614`（出厂二进制把同一函数解析到 `global.c:789`，位移 +175）｜
二进制锚点 `allocno_compare @ 0x081ab288`，字段偏移 `size=4` / `n_refs=12` / `freq=16` / `live_length=20`，常量 `double 10.0 @ 0x0821e360`｜
receipt：75 函数 / 1,079 allocno / 1,004 相邻对，精确序列 33/75、平均 τ 0.873、逆序 26（2.6%）｜
falsifies：dds 的 `floor_log2(refs) * refs * hard_reg_width` 形状（本机 4 组对照全部否证）｜
scope：`3.2-ee-040921` @ `-O2 -G0`，未在 2.96 上测。

## L-EE-002 · `allocno.size` 单位是**字**，且只在 ≠ 1 时才打印

`PSEUDO_REGNO_SIZE` 把模式大小除以 `UNITS_PER_WORD`：`SImode` = 1 字，`DImode` / `DFmode` = 2 字。
`;; N regs to allocate:` 只在 `size != 1` 时追加 `(N)`。
**T1**｜源码锚点 `regs.h:116`、打印条件 `global.c:1937`（EE 为 `global.c:2265`）｜
二进制锚点 `allocno_compare @ 0x081ab288`（`fimull 0x4(...)`）｜
receipt：全部语料 **0 处** `(N)`，含确实进入全局分配的 DFmode allocno｜
falsifies：「size 是字节」（R28 的工具代入 lreg 的 `N bytes`；两者差常数 4 倍，故不改排序，但单位写错）。

## L-EE-003 · EE 的寄存器压力更宽：`struct allocno` 144 B、`HARD_REG_SET` 192 位

**T1**｜源码锚点 `global.c:96`（EE 的 DWARF 声明行；mainline 在 87，字段名与顺序相同）｜
二进制锚点 `allocno_compare @ 0x081ab288`；`byte_size = 144`，成员步长 24 B，`hard_reg_conflicts @24` / `hard_reg_preferences @48` / `hard_reg_copy_preferences @72`｜
receipt：DWARF 尺寸 + 反汇编步长 144 B（`lea (%edi,%edi,8)` 后 `shl $0x4`）｜
falsifies：「mainline 的 `HARD_REG_SET` 宽度也适用于 EE」。

## L-EE-004 · EE 有自己的后端文件 `config/mips/mips5900.c`

**T1**｜源码锚点：mainline 3.2.3 的 `config/mips/` 下**没有**这个文件（已核对）｜
二进制锚点 `uns_arith_operand @ 0x0817178c`（该文件共 **152** 个函数）｜
receipt：出厂 cc1 内嵌 135 条源文件路径，`mips5900.c` 在其中。

## L-EE-005 · `REG_FREQ` 逐寄存器 note 累加；`REG_FREQ_MAX = 1000`

`flow.c` 对每个寄存器 note 累加一次块频率，所以一条指令内对同一寄存器的读改写算两次。
**T1**｜源码锚点 `flow.c:2733`（另见 `flow.c:3413`、`flow.c:3578`）、`regs.h:79`｜
二进制锚点 `life_analysis @ 0x080ce2d8`、常量 `10.0 @ 0x0821e360`｜
falsifies：「因子是 1」的误读（已登记为私有仓库的 P-108）。**读 `#define`，不要读注释。**

## L-EE-006 · 行号**不可**在源码树之间搬运

**T1**｜receipt（位移中位数，EE 行 − mainline gcc-3.2.3 行）：`global.c` +341、`gcse.c` +137、
`haifa-sched.c` +263、`regmove.c` +1920、`reload1.c` 0、`local-alloc.c` −4、`cse.c` −22、`jump.c` −47、
`loop.c` −68、`function.c` −55、`ifcvt.c` −6。
与 gcc-3.2.2 对照时每个中位数最多差 1 行 ⇒ 位移属于 EE 快照，不是点版本差异。

## L-EE-007 · TU 级没有 codegen 状态，只有 `$L` 编号

**T3**（受控实验，暂无源码/二进制锚点）｜receipt：6 种 TU 配置、绝对地址与跳转表相对量归一化后，
指令序列 / `.sdata` / 跳转表**完全相同**，只有 `$L` 编号按前置带标签函数 +1（且不改字节）｜
falsifies：「往同一 TU 加无关函数会扰动目标函数」。

## L-EE-008 · `23.greg` 里 `regs to allocate` 是局部分配**残留**，`conflicts` 列的是**全部** allocno

`;; N regs to allocate:` 会跳过已有寄存器的 allocno（`reg_renumber >= 0`）；`;; N conflicts:` **不跳**，
列出每一个 allocno。
**T1**｜源码锚点 `global.c:1926`（计数循环在 1922 跳过；1945 的冲突循环没有这个判断），出厂二进制把 `dump_conflicts` 解析到 `global.c:2265`｜
二进制锚点 `dump_conflicts @ 0x081af134`｜
receipt：166 个函数里冲突行列出 **10,450** 个 allocno，而 `regs to allocate` 只有 **1,079** 个；两者在 **166/166** 个函数里都不同（`fx_arith`：8 vs 0）｜
falsifies：「冲突行只列等寄存器的 allocno」。把多出来的号当成硬寄存器是**实测过的失败模式**（我第一次着色重放的候选集就是这么错的）。

## L-EE-009 · 延迟槽基本都被填上；剩下的 `nop` 是函数末尾的 `jr ra`

**T2**｜源码锚点 `reorg.c:3582`（`dbr_schedule`；出厂二进制解析到 `reorg.c:3571`），填充函数是 `fill_simple_delay_slots` / `fill_slots_from_thread`｜
二进制锚点 `dbr_schedule @ 0x081cd510`｜
receipt：10 个合成函数 / 29 个分支 @ `-O2 -G0`：**填 24 条（82.8%）**、编译器**没有主动发一条 nop**、5 条后面是标签或函数结尾。对象级复核 `f_dowhile`：`bgtz` 槽是 `addiu`，函数末尾 `jr ra` 槽是 `nop`。槽内指令统计：`addu` 9、`li` 6、`move` 5，`lw`/`sll`/`lui`/`ld` 各 1｜
falsifies：「延迟槽是 nop = 调度器没得可移」——这一层编译器根本不发 nop，剩下的是汇编器补的。
**杠杆**：把延迟槽差异当**调度**问题处理——先重组语句、看分支后继能提供什么，再去改表达式。

## L-EE-010 · `switch` 生成跳转表的条件：`case 数 >= 5` **且** `跨度 <= 10 × case 数`

`expand_end_case_type`：`count < case_values_threshold ()` 或跨度超过 case 数 10 倍时退化为比较链，否则调用 `try_tablejump`。
`CASE_VALUES_THRESHOLD = (HAVE_casesi ? 4 : 5)`，实测阈值是 **5** ⇒ 本后端没有 `casesi`。

```
case 数 >= 5  且  (max - min) <= 10 × case 数   → 跳转表
否则                                          → 比较链
```

**T1**｜源码锚点 `stmt.c:5401`（判定）与 `expr.c:10486`（常量）；`try_tablejump` 在 `stmt.c:5509` 调用｜
二进制锚点 `expand_end_case_type @ 0x08154e0c`（`stmt.c:5238`）、`case_values_threshold @ 0x080cad50`（`expr.c:10431`）、`try_tablejump @ 0x080cae48`（`expr.c:10595`）｜
receipt：11 个合成 switch，**11/11 与规则一致**（dense 3/4 → 比较链；dense 5/6/7/8/10/16 → 表，**表项数 == case 数**；`{0,1,2,100,1000}` → 比较链；`{0,10,20,30,40}` → **41 项**表；`{0,1,2,3,4,100,200,300}` → 比较链）｜
falsifies：「≥5 个不同 case 就生成跳转表」（dds-decomp，2.96，无许可证）——5 是必要不充分，还要满足跨度条件。
**杠杆**：写 `switch` 前先数 case 与跨度；把值收拢，或在 `switch` 前加范围守卫，都会改变判定。

## L-EE-011 · 浮点常量走常量池；双精度在**低位 32 位为零**时内联构造

| 常量 | 形态 |
| --- | --- |
| `0.0f` | 内联 `mtc1 $0` |
| 其它 `float` | 常量池：`lui %hi($LCn)` + `addiu %lo($LCn)` + `l.s` |
| `0.0`（double） | `move $2,$0` |
| 低位 32 位为零的 double（`0.5`/`1.0`/`1.5`/`2.5`/`2^52`） | 内联 `dli` + `dsll` |
| 其它 double（`0.01`/`π`/`1.0000000001`） | 常量池 + `l.d` |

**T2**｜源码锚点 `config/mips/mips5900.c:1638`（EE 后端有 mainline 没有的 `mips_move_1word`；该文件不在本机，故规则是**实测**而非读出的）｜
二进制锚点 `mips_move_1word @ 0x0817298c`（只是指向 EE 后端的指针，不等于核验了规则）｜
receipt：14 个 float + 9 个 double @ `-O2 -G0`，全部与上表一致；**低位半字为零的 float（`0.5f`/`1.0f`/`2.5f`/`1.5f`）照样走池**｜
falsifies：IDO 5.3 的「浮点常量低位半字决定内联还是池」（n64-decomp-workbench L62，CC0）——在 ee-gcc 3.2 上这个分裂**只对双精度成立**。

## L-EE-012 · 帧构成 = `[vars][传出参数][每个保存寄存器 8 B]`，保存寄存器在 10 个处饱和

**T2**｜源码锚点 `global.c:991`（`find_reg`；出厂二进制解析到 `global.c:1329`）｜二进制锚点 `find_reg @ 0x081acd64`｜
receipt（合成剂量-响应，`-O2 -G0`，k 个跨调用活跃值）：

| k | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 18 | 24 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 帧 | 32 | 48 | 64 | 80 | 96 | 96 | 112 | 128 | 144 |
| `regs=` | 4 | 6 | 8 | 10 | 10 | 10 | 10 | 10 | 10 |
| `vars=` | 0 | 0 | 0 | 0 | 16 | 16 | 32 | 48 | 64 |

**每保存一个寄存器 8 B，保存区上限 10 个（80 B）**；再多的值只能进 `vars`。观察到的保存寄存器是 `$s0`–`$s7`（16–23）、`$fp`（30）、`$ra`（31）。
**命名陷阱**：本工具链的 objdump 把寄存器 30 显示成 `s8`，而编译器自己的汇编写 `$fp`——不要按反汇编里的名字推编号｜
receipt（真机 `func_001d4b88`）：零售帧 144 = vars 16 + args 48 + 10 个保存（80 B）；候选帧 176 = vars **48** + args 48 + **同样 10 个保存**——两边 prologue 都保存 `s0`–`s8` 与 `ra`｜
falsifies：「候选帧更大 = 保存了更多寄存器」——该函数上 +32 B **全在变量区**。
**杠杆**：先分解帧（vars / args / 8×regs），再朝差异所在的那一块下手。

---

## 仍未解决

* `$L` 计数器的精确公式（多标签函数未测）。
* 分类别着色重放：已记录的 26.1% 精度早于本次 EE `find_reg` 锚点。
* `freq` 需在真实多基本块函数上核对，而不只是读源码。
