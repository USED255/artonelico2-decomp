# 编译器行为条目（laws）· ee-gcc 3.2-ee-040921

[English](LAWS.md) · [手册索引](README.md) · 机器可读：[`laws.json`](laws.json)

本页记录**编译器怎么做**；由此推出的源写法杠杆在 [FIELD-GUIDE.md](FIELD-GUIDE.md)，定位流程在 [DIAGNOSTICS.md](DIAGNOSTICS.md)。
英文版每条含完整模板（tier / 源码锚点 / 二进制锚点 / receipt / falsifies / scope）；本中文版按增量维护，先给条目与结论。

**核验状态**：本手册引用的 **13 个二进制锚点**已全部用 `tools/compiler/ee-gcc-anchor.py` 对出厂 `cc1` 复核，地址全部一致（另两条 law 无二进制锚点，属 `T3`）。工具链变动后请重跑此检查。
注意一个**重名陷阱**：`find_reg` 在出厂 cc1 里有两个——`0x08134570`（`reload1.c:1685`）与 `0x081acd64`（`global.c:1329`）——**一律按地址消歧，不要按名字**。

**证据路径约定**：每条 law 的 `evidence` 写明 receipt 在哪。**裸路径**表示在本仓库内；`private:` 指向项目的**私有研究仓库**（原始证据 dump，故不公开）；`party:` 指向私有仓库里**本项目自己的研究报告**。
`tools/check/test_compiler_tools.py` 会强制校验所有**裸路径**存在。

**量测条件**：`scope` 写明该次测量用的旗标。本手册多数探针用 `-O2 -G0`；但**项目本身不带 `-G`**
（`MATCHED_CFLAGS` = `-O2 -falign-functions=4 -ffunction-sections`），因此走 MIPS 默认值 8。
与**寻址物化**有关的条目（L-EE-011、L-EE-014）对 `-G` 敏感，分配与调度类不敏感。

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

## L-EE-013 · 有符号性决定 `slt`/`sltu`；比寄存器窄的类型加 `andi` 或 `sll`+`sra`；`xori` 是**相等**标志

| 表达式 | `int` / `long long` | `unsigned` | `signed char` / `short` | `unsigned char` / `short` |
| --- | --- | --- | --- | --- |
| `x < 100` | `slt` | `sltu` | `sll` `sra` `slt` | `andi` `sltu` |
| `x == 5` | `xori` `sltu …,1` | 同左 | `sll` `sra` `xori` `sltu` | `andi` `xori` `sltu` |
| `x != 0` | `sltu` | `sltu` | `sll` `sra` `sltu` | `andi` `sltu` |

**T3**（只有行为证据；比较模式在 EE 后端，本机没有该源码）｜receipt：48 个合成函数（8 类型 × 5 模式 × 2 上下文）@ `-O2 -G0`｜
falsifies：「`slt`/`sltiu` 与 `xori` 可区分窄无符号类型」（dds-decomp，2.96，无许可证）——`xori` 是**相等**判断；窄类型表现为 `andi` 掩码（无符号）或 `sll`+`sra` 扩展（有符号）。
**杠杆**：把比较前那条扩展指令当作**类型的形状**读；把类型加宽或改有符号性，移动的正是这条指令。

## L-EE-014 · 小数据寻址由 `-G` 决定

**T2**｜源码锚点 `config/mips/mips.h:4579`（`MIPS_DEFAULT_GVALUE` = **8**；后端用 `mips_section_threshold`，EE 行 `config/mips/mips5900.c:226`，`-1` 表示未设）｜
二进制锚点 `mips_section_threshold @ 0x0823ed20`（文件里存 `-1` 哨兵）、`g_switch_value @ 0x0830d0c0`｜
receipt（同一夹具四种设置）：

| 探针 | `-G0` | `-G4` | `-G8` | 默认 |
| --- | --- | --- | --- | --- |
| 4 B 全局/静态 | 绝对 | 小数据 | 小数据 | 小数据 |
| 8 B `double` | 绝对 | 绝对 | 小数据 | 小数据 |
| 32 B 数组 | 绝对 | 绝对 | 绝对 | 绝对 |
| `static const int` 读取 | 折叠为立即数 | — | — | — |
| 浮点常量 `$LCn` | 绝对 | 绝对 | 绝对 | 绝对 |

`绝对` = `lui %hi` + `%lo`；`小数据` = 裸符号（`lw $2,g_int`），汇编后是 `R_MIPS_GPREL16`。
falsifies：「`-G0` 下的量测能代表项目构建」——项目不带 `-G`，默认是 8。
**杠杆**：比全局变量前先把 `-G` 对齐到目标构建；≤ 8 B 且非常量的对象走 `gp_rel`，大对象与所有常量走绝对寻址。

**边界（实测）**：对象大小 **≤ G（含等号）** 即合格——4 字节对象在 `-G4` 合格、9 字节对象要到 `-G9`；
**默认（不带 `-G`）与 `-G8` 逐项相同**。未初始化的小对象进 `.scommon`（链接期并入 `.sbss`），初始化的进 `.sdata`。
`-G0` 下**哪些声明形式**合格见 [L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss)。

## L-EE-015 · 传出参数区兼作「调用后还要用」的值的存放处

| 传出的是什么 | 调用之后 | 帧开销 |
| --- | --- | --- |
| **4 字节聚合体**（栈传参） | 从**传出槽重读**（`lh $15,48($sp)`） | **0** |
| **标量**（栈传参） | 放在 callee-saved 寄存器（`sd $16,64($sp)`） | **8 B** |

**T2**｜源码锚点 `calls.c:4284`（`store_one_arg`）｜二进制锚点 `store_one_arg @ 0x08087038`、`load_register_parameters @ 0x08083d64`、`emit_push_insn @ 0x080bf178`｜
receipt（`-Os -G0`，参数多于 8 个 ⇒ 第 9 个落在传出区）：聚合体版 `vars = 0`；标量版付一个保存槽；真机函数中观察到与聚合体版相同的形状｜
falsifies：「凡是既要传给调用、调用后又要用的值，都必须溢出或占一个 callee-saved 寄存器」。
**杠杆**：把**同一个聚合体表达式**既传给调用、又在调用后使用；为它引入一个局部副本会多出一个活跃对象、多花一个槽。

## L-EE-016 · EE 寄存器文件：**140 个硬寄存器、29 个类**

从**运行中**的 `cc1` 读出（gdb 挂在 `local_alloc`，此时 `init_reg_sets_1` 已填表）：

| 寄存器 | 类 |
| --- | --- |
| 0–31 | `GR_REGS`（通用） |
| 32–63 | `FP_REGS` |
| 64–67 | `HI/LO/HI1/LO1`（EE 的第二套乘除单元） |
| 68 / 69–70 / 71 | `ST_REGS` / `ELIM_REGS` / `FP_ACC_REG` |
| 72–75 | 保留（在 `fixed_reg_set` 里，不属于任何类） |
| 76 / 77–79 | `VU0_ACC_REG` / `VU0_Q_REG`、`VU0_I_REG`、`VU0_R_REG` |
| 80–111 | `COP0_REGS` |
| 112–143 | `VU0_REGS` |

`ALL_REGS` 共 **140** 个（`FIRST_PSEUDO_REGISTER`），`N_REG_CLASSES` = **29**，`HARD_REG_SET` = 192 位。
GPR 里被 `fixed_reg_set` 固定的是 `0,1,26,27,28,29,31`；`call_used_reg_set` 剩下 `2–15,24,25` 为调用者保存
⇒ **可分配的 callee-saved GPR 恰好是 `{16..23, 30}`**（8 个 `$s0`–`$s7` + `$fp`），加上 `$ra` 正好 **10 个保存槽**，与 [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) 的实测上限吻合。

**T1**｜源码锚点 `config/mips/mips5900.c`｜二进制锚点 `reg_class_contents @ 0x08309140`、`reg_class_size @ 0x083094c0`、`fixed_reg_set @ 0x0830a310`、`call_used_reg_set @ 0x083093f8`｜
receipt：上表（活进程读出）。这些数组在 `.bss`、启动时填充，**静态读为 0**｜
falsifies：「EE 寄存器文件可以按 mainline MIPS 近似」，以及「这些表读不出来」。
**杠杆**：只在 `reg_class_contents[类] − fixed_reg_set` 内分配；跨调用的 allocno 再去掉 `call_used_reg_set`。

## L-EE-017 · 出厂的 `find_reg` **不是** mainline 那个——两级阶梯，且**决策是副作用**

出厂二进制自己的调试信息给出签名，与 mainline 不同：

```
出厂    global.c:1336   find_reg (num, losers, alt_regs_p, accept_call_clobbered, retrying)
mainline global.c       find_reg (struct allocno *allocno, HARD_REG_SET *allocnos_live)
```

同一轮的另两点观测（gdb 轨迹 + 反汇编）：

* 它是**两级阶梯**，而且阶梯出现**两次**：

| 级 | 地址 | 所在函数 | EE 源码行 |
| --- | --- | --- | --- |
| 1（`alt_regs_p=0`） | `0x81aa4ba` | `global_alloc` | `global.c:400` |
| 2（`alt_regs_p=1`） | `0x81aa520` | `global_alloc` | `global.c:407` |
| 1（`alt_regs_p=0`） | `0x81aad68` | `global_init` | `global.c:772` |
| 2（`alt_regs_p=1`） | `0x81aadbe` | `global_init` | `global.c:777` |

  另外 `find_reg` 会在 `global.c:1540` **递归调用自己**（`retrying` 就是干这个的）。实测外部调用中 `losers` 为 NULL、其余标志为 0。
* **返回值被丢弃**：外部调用点后的第一条指令立刻覆盖 `%eax`（`0x81aad6d`、`0x81aa4bf`）。调用者随后读一个**有符号 16 位**的
  逐寄存器数组（`cmpw` + `js`）来判断「没拿到寄存器」；表就是 **`reg_renumber`**（`0x82ea1ec`，`short` 数组）；
  有一条路径还会查 `reg_alternate_class`。⇒ 选择是**副作用**，
  我此前在 `%eax` 里读到的 `-1` 只是残留值。

同一段反汇编还确认 `sizeof(struct allocno) == 144`：allocno 数组用「×9 再 <<4」索引（[L-EE-003](LAWS.md#l-ee-003--register-pressure-is-wider-on-ee-struct-allocno-is-144-b-hard_reg_set-is-192-bits)）。

**T1**｜源码锚点 `global.c:1336`（DWARF）｜二进制锚点 `find_reg @ 0x081acd64`（global.c）与 `find_reg @ 0x08134570`（reload1.c，按地址消歧）｜
falsifies：「按 mainline 的 `find_reg` 写的重放能复现出厂决策」，以及「`find_reg` 会**返回**选中的寄存器」。
**杠杆**：把分配建成「`alt_regs_p` 0→1 两级阶梯 + 结果走副作用」；「没拿到寄存器」按逐寄存器的负值判断。


---

## L-EE-018 · 全局分配：候选集与选择规则

按测量拟合出的规则：

1. **池** = `reg_class_contents[类] − fixed_reg_set`；**跨调用**的 allocno 再去掉 `call_used_reg_set`（[L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)）。
2. **禁止** = 该 allocno 的 `hard_reg_conflicts` ∪ **已放置且与其冲突**的 allocno 所占的寄存器。
   **不要**把所有已分配的寄存器都禁掉——那是在冲突表已表达之处重复计算，会掉约 6 个点。
3. **选择** = 首选列表里第一个仍可用的寄存器；否则取**编号最小**的候选。
4. **两趟**：第一趟额外避开**别人**首选的寄存器（EE 独有字段 `regs_someone_prefers`），第二趟放开——这正是观测到的
   阶梯里 `alt_regs_p` 在切换的东西（[L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect)）。

| 规则 | 留出集复现率（527 个 allocno） |
| --- | ---: |
| 按 mainline 写的两趟重放（v2） | 9.1% |
| 首选优先 + 禁全部已分配（此前最好） | 34.3% |
| 运行时真值表 + v2 规则（v4） | 9.9% |
| 本规则（v5） | **41.0%** |
| 本规则 + 第 4 步两趟（v6） | **46.5%** |
| v6 + 动态冲突集取真值 | **82.7%** |

**T2**｜源码锚点 `global.c:400`（[L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect) 的阶梯；规则本身是**实测**而非读出）｜二进制锚点 `reg_renumber @ 0x082ea1ec`、`allocno @ 0x082e8a54`、`allocno_order @ 0x082e8a58`｜
falsifies：「把所有已分配的寄存器都禁掉是安全的」（掉约 6 点），以及「mainline 的两趟扫描就是出厂算法」（12.8%）。
**杠杆**：按上面的池与禁止集预测分配；**剩余误差主要是级联**——早期一次选错会污染后面的冲突集（41.0% → 82.7%）。

**首选语义（精确量测）**：427 个带首选列表的 allocno 中，**323 个取「候选内第一个首选」，取更后面首选的为 0**——「取候选内第一个首选」就是全部规则。
没有首选时，选中的**不是**最小候选（461 例中有 334 例如此，且真值**都在候选集内**），说明另有东西决定扫描。

**怎么区分「真规则」与「补偿假象」**：第 4 步端到端 +5.5 点，但在 oracle 上下文下**不变**（82.7% → 82.7%），且同时吻合 EE 独有的结构体字段与观测到的阶梯 ⇒ 是**规则**；
下面那条被否证的「旋转起点」端到端也好看，但在 oracle 下**掉 3 点**——这正是「补偿自身误差」的判据。

**一个被否证的假设——「旋转起点」**：从 `pseudo % 32` 起扫描能把全语料从 38.9% 抬到 49.1%，看着像真规则；**但不是**——
把动态冲突集换成真值后，旋转 **60.5%**，反而不如不旋转的 **63.5%**。它只是在补偿这个重放自身的误差。**不要采用它。**

**第二个被否证的假设——用活跃区间建占用集**：从 `16.life` dump 的**块级**活跃集重建冲突集只有 **30.6%**，而 dump 的 `conflicts` 列表是 **42.1%**——
块级粒度会把「同一块内不同时点活跃」的 allocno 误判为冲突。⇒ 来自**指令级活跃**的 dump 列表仍是更好的占用源。
至此已试并否证两条杠杆（旋转起点、活跃区间占用集）；到 oracle 上界（82.7%）的剩余缺口是**级联**，需要指令级活跃范围或出厂源码才能跨过。

**地址语义（live 实测）**：`allocno_order[i]` 存的是 **allocno 下标**，`allocno[下标].reg` 是 **pseudo**，
因此 dump 的 `;; N regs to allocate:` 列表**已经是按分配顺序打印的 pseudo**（实测 `[3,1,2,0,…]` 映射为打印的 `152 150 151 149 …`）。
用外部代理重排（`n_refs` 降序 41.8%、`live_length` 升序 42.0%，对照打印序 38.9%）只是换了误差模式，**不是更正确的规则**：
**顺序不是杠杆，单次判断的精确性才是。**

---

## L-EE-019 · 浮点规则**随版本不同**：2.96 内联，3.2 走池

本项目用**两个**编译器：游戏代码用 `3.2-ee-040921`，CRI 中间件用 `2.96-ee-001003-1`。多数规则可迁移，**浮点常量规则不能**。

`float f(void) { return V; }` 的对象码（`-O2 -G0`）：

| V | 3.2 | 2.96 |
| --- | --- | --- |
| `0.0f` | `mtc1`（零寄存器） | `mtc1` |
| `0.5f`、`1.0f`、`2.5f`、`-1.0f`、`100.0f` | `lui addiu lwc1` —— **池** | `lui mtc1` —— **内联**（低位 16 位为 0） |
| `0.01f`、`3.14f`、`123.456f`、`1e30f` | **池** | `lui ori mtc1` —— **内联** |

双精度**两版一致**：`0.0` 用 `move`；低位 32 位为 0 时 `li`+`dsll32`；否则走池（`lui`+`ld`）（[L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)）。

在 2.96 上回测**一致**的规则：窄类型比较习语（[L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality)）、
switch 阈值（[L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count)）、`-G0` 绝对寻址（[L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g)）。

**T3**（只有行为证据；两个后端都没有源码与二进制锚点）｜receipt：上两张表，取自**对象码**——2.96 的 `.s` 里写的是 `li.s` 伪指令，会被误导｜
falsifies：「一个编译器的常量规则可以迁移到另一个」｜**杠杆**：改浮点常量写法前，先确认那段源码由哪个编译器构建。

---

## L-EE-020 · pass 流水线随 `-O` 档变化

`ee-gcc -<档> -G0 -da -c` 编一个循环夹具：

| 档 | dump 份数 | 相对 `-O2` 缺哪些 |
| --- | ---: | --- |
| `-O0` | **9** | 01.sibling、08.null、09.cse、11.gcse、12.loop、14.bp、15.cse2、17.combine、18.ce、19.regmove、20.sched、21.range、27.rnreg、28.ce2、29.sched2、31.bbro、33.dbr |
| `-O1` | **20** | **01.sibling、11.gcse、19.regmove、20.sched、21.range、29.sched2** |
| `-O2` | **26** | — |
| `-Os` | **26** | 与 `-O2` 相同 |

**决策规则不随档位改变**：`-O1` 下 `0.5f` 仍走常量池、低位字为零的 `double` 仍用 `li`+`dsll32`、6 路稠密 switch 仍成表——
变的只是指令顺序与寄存器移动，而这正是那 6 个缺失 pass 干的活。这就是项目里有些函数**只有 `-O1` 才 100%** 的原因之一。

**T1**｜源码锚点 `toplev.c:3316`（流水线驱动处）｜二进制锚点 `global_alloc @ 0x081aa2c4`、`rest_of_compilation @ 0x0815a854`｜
receipt：上表 + 四条规则在 `-O1`/`-O2` 的对照｜falsifies：「一份 pass 清单能描述这个编译器」。
**杠杆**：比对代码形状前先确认 `-O` 档；并且**只对编译成功的编译数 dump 份数**——源码被拒（例如 C89 下的 C99 `for` 声明）只会留下 2 份，
此时「少了 dump」可能只是编译提前终止。

---

## L-EE-021 · `gp_rel` 要求对象**在本编译单元内定义**并放进 `.sdata`/`.sbss`

[L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g) 给的是 `-G` 阈值；这里补另一半：**哪些声明形式**会成为小数据。

| 声明（在本单元内有定义） | `-G0` | 默认（`-G8`） |
| --- | --- | --- |
| `int g;` | `lui %hi` 绝对 | **裸符号** —— `gp_rel` |
| `int g __attribute__((weak));` | **绝对** —— `weak` 本身没用 | 裸符号 |
| `int g __attribute__((section(".sbss")));` | **裸符号** ✔ | 裸符号 |
| `int g __attribute__((section(".sdata"))) = 7;` | **裸符号** ✔ | 裸符号 |
| `extern int g;`（本单元无定义） | 绝对 | **绝对** |
| `extern int g __attribute__((section(".sbss")));` | 绝对 | **绝对** |

⇒ 在 `-G0`（CRI 源用的旗标）下，拿到 `gp_rel` 的唯一办法是**在本单元定义**并放进 `.sdata`/`.sbss`；
**`weak` 不是关键**；而 `extern` 声明**永远**做不到——定义必须在同一编译单元。

`objdump -t` 确认段归属：`section(".sbss")` 进 `.sbss`、`section(".sdata")` 进 `.sdata`；无属性的 weak 对象进 `.bss`。

**T2**｜源码锚点 `varasm.c`（小数据判定；出厂树中未能读到行号）｜二进制锚点 `mips_section_threshold @ 0x0823ed20`、`g_switch_value @ 0x0830d0c0`｜
falsifies：「产生 `gp_rel` 的是 **weak** 小数据定义」——真正起作用的是 **section 属性**。
**杠杆**：目标用裸符号、候选用 `lui %hi` 时，把对象**在本单元**定义进 `.sdata`/`.sbss`（项目里 gp_rel 类候选就是这么做的）；`extern` 做不到。

---

## L-EE-022 · 函数对齐：默认 **8 字节**，`-falign-functions=4` 降到 4

四个 12 字节函数，`-O2 -G0`：

| 旗标 | 汇编里的对齐指令 | 符号偏移 | `.text` |
| --- | --- | --- | ---: |
| 无 | `.align 2` + **`.p2align 3,,7`**（8 字节） | 0x0, 0x10, 0x20, 0x30 | **0x40** |
| `-falign-functions=4` | 只有 `.align 2` | 0x0, 0xc, 0x18, 0x24 | **0x30** |
| `-ffunction-sections` | 每函数一个 `.text.N`，段内仍有 `.p2align 3` | 各段内 0 | 各 0x10 |
| **`-falign-functions=4 -ffunction-sections`**（本项目实际） | `.text.N` + 只有 `.align 2` | 各段内 0 | **各 0xc —— 零填充** |

⇒ 默认对齐是 **8 字节**，12 字节函数被填到 16；`-falign-functions=4` 降到 4 后**紧密排列**。
**`-ffunction-sections` 单独并不能去掉 8 字节对齐**。

**T2**｜源码锚点 `varasm.c`（对齐指令；未从出厂树读到行号）｜常量：发出的 `.p2align 3,,7` 与 `.align 2`｜
falsifies：「`-ffunction-sections` 单独就能去掉函数间填充」，以及「默认函数对齐是 4 字节」。
**杠杆**：objdiff 报**大小/偏移**不符而指令一致时，先查对齐旗标，别急着改源码。

---

## L-EE-023 · 在项目旗标下只有带 `inline` 的声明会被内联

`-G0`，判据是汇编里 `jal helper` 与 `helper:` 是否还在：

| 声明 | -O0 | -O1 | -O2 | -O3 / `-O2 -finline-functions` |
| --- | --- | --- | --- | --- |
| `static int helper(...)` | 调用 | 调用 | **调用** | 内联 |
| `static inline int helper(...)` | 调用 | **内联** | **内联** | 内联 |
| `inline int helper(...)` | 调用 | **内联** | **内联** | 内联 |
| `static __attribute__((always_inline))` | 调用 | 调用 | **调用** | 内联 |
| `static inline __attribute__((always_inline))` | **内联** | 内联 | 内联 | 内联 |

在项目旗标（`-O2`，**不带** `-finline-functions`）下，普通 `static` 助手函数**永远保留调用**——即使它很小、且只被调用一次
（按 1–12 条语句 × 1/3 次调用遍历，没有任何尺寸会内联）。`always_inline` **必须配合 `inline`** 才生效（与 3.2 手册一致）；配合后在 `-O0` 也内联。

**T2**｜源码锚点：内联器（`cgraphunit.c`/`integrate.c`；未从出厂树读到行号）｜常量：`-O2` 下 `-finline-functions` 关、`-O3` 开｜
falsifies：「`-O2` 会内联只调用一次的小 static 函数」与「`always_inline` 单独生效」。
**杠杆**：目标里助手被展开、候选却发 `jal` ⇒ 给助手加 `inline`（或确认该单元是否用了 `-O3`/`-finline-functions`）。

---

## L-EE-024 · 被保存的 `$fp` **不是**帧指针

| 夹具（`-O2 -G0`） | `.frame` 首操作数 | 帧 |
| --- | --- | ---: |
| 局部变量全进寄存器 | `$sp,0` | 0 |
| 8 个跨调用值 | **`$sp`,80** | 80 —— `$fp` 被保存，但只是寄存器 |
| `__builtin_alloca` | **`$fp`,64** | 64 —— 真帧指针 |
| VLA（`int v[n]`） | **`$fp`,96** | 96 —— 真帧指针 |
| 8 个值 + `-fno-omit-frame-pointer` | **`$fp`,96** | **96**（原 80） |
| 8 个值 + `-fomit-frame-pointer` | `$sp`,80 | 80 —— 与默认相同 |

1. **本机 `-O2` 默认省略帧指针**（显式 `-fomit-frame-pointer` 与默认逐项相同）。
2. 普通函数里被保存的 `$fp` 只是**第 10 个被调用者保存寄存器**（[L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)）——
   判据是 **`.frame` 的首操作数**：`$sp` = 没有帧指针，`$fp` = 有。
3. `.frame $fp,…` 来自 **alloca/VLA** 或 **`-fno-omit-frame-pointer`**；后者即使没有动态栈也会**多 16 字节**（上例 80 → 96），objdiff 会显示为大小/偏移不符。

**T2**｜源码锚点 `function.c`（序言/帧指针选择；未从出厂树读到行号）｜常量：同一夹具 80 vs 96｜
falsifies：「序言里保存了 `$fp` 就说明用了帧指针」。
**杠杆**：读 `.frame` 首操作数；当目标帧在同样保存槽下**正好大 16 字节**时，怀疑 `-fno-omit-frame-pointer` 或动态栈。

---

## L-EE-025 · 循环是倒计数、且不被展开

`for (i = 0; i < N; i++) s += a * i;`（`-O2 -G0`）：

```asm
        move    $2,$0            # s
        move    $14,$0
        li      $15,7            # N-1  ← 立即数倒计数
$L6:
        addu    $2,$2,$14
        addu    $15,$15,-1
        bgez    $15,$L6
        addu    $14,$14,$4
```

**N = 4、8、20 都是 8 条指令**——只有立即数变 ⇒ 循环**滚动且倒计数**。变次（`i < n`）同样倒计数，但计数器来自参数：
`blez` 守卫、`addu $5,$5,-1`、`bne $5,$0`。

| 档 | 定次 8 的指令数 |
| --- | ---: |
| `-O1` | 9 |
| `-O2` | 8 |
| `-O3` | 8 |
| `-O2 -funroll-loops` | **12** |

⇒ **本机 `-O2` 与 `-O3` 都不展开**；要展开必须显式给 `-funroll-loops`，或源码手工展开。

**T2**｜源码锚点：循环/强度削减 pass（`loop.c`；未从出厂树读到行号）｜常量：三个定次数都是 8 条指令、`-funroll-loops` 时 12 条｜
falsifies：「`-O3` 会展开循环」与「定次上界会保留递增比较」。
**杠杆**：目标循环体被重复时，先查 `-funroll-loops`（或源码手工展开），再改循环结构；目标不是倒计数形态时，说明源码循环形状不同。

---

## L-EE-026 · 常量池按**函数**划分

`-O2 -G0` 下常量放在 `.rdata`，**每个函数一个块**，条目按自然尺寸对齐（float/word 用 `.align 2`，double 用 `.align 3`）。

| 情形 | 条目数 |
| --- | --- |
| 同一函数内 `0.5f` 用 3 次 | **1**（`$LC0`）——函数内去重 |
| 两个函数各返回 `0.5f` | **2**（`$LC0`、`$LC1`，值都是 `.word 1056964608`）——**不跨函数共享** |

条目按**首次使用顺序**编号：`if (k) return 2.5f; return 0.5f;` 得到 `$LC0` = 2.5f、`$LC1` = 0.5f，**不按值排序**。

**T2**｜源码锚点 `varasm.c`（常量池输出；未从出厂树读到行号）｜常量：上面两个 `.word` 值｜
falsifies：「相同常量会在整个编译单元内共享」与「池按值排序」。
**杠杆**：目标在两个函数间共享某常量（或你共享了、目标没有）⇒ 差异在**源码的函数边界**，不是常量本身；
若**顺序**不同，比对**首次使用顺序**；并记住 double 会插入 `.align 3`，把后续条目整体推移。

---

## L-EE-027 · 字符串按**编译单元**合并，不按函数

两个函数各返回 `"hello"`，只产生**一份** `.ascii "hello\000"`——`-O0`、`-O1`、`-O2`、`-Os` 都一样；
对象的重定位显示两者引用同一处。⇒ 字符串合并是**无条件**的，且与常量池**相反**：
常量池里同一个 float 在两个函数中各得一份（[L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function)）。

另外两点容易被汇编误导：

* 汇编写的是 `.rdata` + `.align 3`（8 字节）+ 显式 `\000`，而**对象里的段名是 `.rodata`**（`objdump -h`：size 0x28、algn `2**3`）。
  在对象或 dump 里找 `.rdata` 段是**找不到**的；
* **没有后缀共享**：`"world"` 与 `"hello world"` 是两个独立条目。

**T2**｜源码锚点 `varasm.c`（`const_str_htab`；未从出厂树读到行号）｜常量：`.ascii` 只出现一次、段名 `.rodata`｜
falsifies：「把常量池的 per-function 规则推广到字符串」与「对象里有 `.rdata` 段」。
**杠杆**：两个函数对同一字符串不一致时，看**编译单元边界**（跨 TU 永不合并）；读数据偏移时看 `.rodata`。

---

## 仍未解决

* `$L` 计数器精确公式（多标签函数）。
* ~~EE 构建的 `FIRST_PSEUDO_REGISTER`~~ —— **已结清：140**，从活 `cc1` 读出（[L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)）。
* **着色已部分建模。** [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer) 用实测出的候选/选择规则复现留出集 **46.5%** 的决策（此前启发式 34.3%、按 mainline 写的两趟重放 9.1%）；把动态冲突集换成真值后同一规则达 **82.7%** ⇒ 剩余误差主要是**级联**，不是单次判断错。
  [L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect) 解释了为什么照搬 mainline 不行：出厂的 `find_reg` 带 `losers` 与三个标志、并按重试阶梯调用（`alt_regs_p` 在切换）。
  下一步：钉住**处理顺序**（`allocno_compare`）与阶梯的精确语义。