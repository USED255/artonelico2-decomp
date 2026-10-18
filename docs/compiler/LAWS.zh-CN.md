# 编译器行为条目（laws）· ee-gcc 3.2-ee-040921

[English](LAWS.md) · [手册索引](README.md) · 机器可读：[`laws.json`](laws.json)

本页记录**编译器怎么做**；由此推出的源写法杠杆在 [FIELD-GUIDE.md](FIELD-GUIDE.md)，定位流程在 [DIAGNOSTICS.md](DIAGNOSTICS.md)。
英文版每条含完整模板（tier / 源码锚点 / 二进制锚点 / receipt / falsifies / scope）；本中文版按增量维护，先给条目与结论。

**核验状态**：本手册引用的 **40 条符号声明**（22 条 law，含 related 锚点）已全部用 `tools/compiler/ee-gcc-anchor.py` 对出厂 `cc1` 复核，地址全部一致；另有 4 条 law 属 `T3`（仅行为证据）。`tools/check/test_compiler_laws.py` 会在本机有工具链时逐条复核；工具链变动后请重跑此检查。
注意一个**重名陷阱**：`find_reg` 在出厂 cc1 里有两个——`0x08134570`（`reload1.c:1685`）与 `0x081acd64`（`global.c:1329`）——**一律按地址消歧，不要按名字**。

**证据路径约定**：每条 law 的 `evidence` 写明 receipt 在哪。**裸路径**表示在本仓库内；`private:` 指向项目的**私有研究仓库**（原始证据 dump，故不公开）；`party:` 指向私有仓库里**本项目自己的研究报告**。
`tools/check/test_compiler_tools.py` 会强制校验所有**裸路径**存在。

**量测条件**：`scope` 写明该次测量用的旗标。本手册多数探针用 `-O2 -G0`；但**项目本身不带 `-G`**
（`MATCHED_CFLAGS` = `-O2 -falign-functions=4 -ffunction-sections`），因此走 MIPS 默认值 8。
与**寻址物化**有关的条目（L-EE-011、L-EE-014）对 `-G` 敏感，分配与调度类不敏感。

**最重要的一条纪律**：引用行号时，一律用 `addr2line` 在**出厂 `cc1`** 上读出的那个行号；mainline 行号只能作为带位移的对照。

---


**档位说明**：以下 receipt 除特别注明外都取自 `-O2 -G0`。某条规则在别的档是否成立是**实测**的，不是假定的——
见 [PASSES.zh-CN.md](PASSES.zh-CN.md#哪些-law-在哪个优化档成立) 的矩阵。本项目主要用 `-Os`（687 个文件）与 `-O1`（542），**没有 `-O0`**。

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

**T2**
**该在哪里看**：汇编清单里的 `.align` **不是**函数对齐（那些属于局部标签与表格）。函数对齐**只在对象里可见**：
`.text` 节默认报 `2**3`，加 `-falign-functions=4` 报 `2**2`，并且节**正好少 8 字节**——两个小函数之间的填充没了。
这是同一类陷阱的**第三例**：汇编清单是线索，**对象才是证据**。
｜源码锚点 `reorg.c:3582`（`dbr_schedule`；出厂二进制解析到 `reorg.c:3571`），填充函数是 `fill_simple_delay_slots` / `fill_slots_from_thread`｜
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

## L-EE-012 · 帧构成 = `[传出参数][vars][每个保存寄存器 8 B]`，保存寄存器在 10 个处饱和

**2026-10-18 实测的布局顺序**：区块实际是 `[传出参数][vars][保存寄存器]` —— 传出实参区在最低偏移，`vars` 紧随其后。
合成探针：无栈传参时 `vars` 在 0..15；有四个栈传参时同一批局部移到 32..63，`args` 占 0..31、保存寄存器从 64 开始。
此前标题把组件顺序写反了；`ee-gcc-spill-map.py` 已按此改正。

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

`ALL_REGS` 共 **140** 个（这是**成员数**，不是伪寄存器边界：编号到 143，72–75 保留），
`N_REG_CLASSES` = **29**，`HARD_REG_SET` = 192 位；**第一个伪寄存器是 144**，这也正是它按 `3 × 64` 位取整的原因。
活读 `debug_reg_names`（`0x0821f280`）只有 0..143 项，下一格已不是名字。
GPR 里被 `fixed_reg_set` 固定的是 `0,1,26,27,28,29,31`；`call_used_reg_set` 剩下 `2–15,24,25` 为调用者保存
⇒ **可分配的 callee-saved GPR 恰好是 `{16..23, 30}`**（8 个 `$s0`–`$s7` + `$fp`），加上 `$ra` 正好 **10 个保存槽**，与 [L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers) 的实测上限吻合。

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

**偏好列表在排序前先被编辑**：`expand_preferences` 先把复制相关的 allocno 偏好合并进来，`prune_preferences` 再去掉冲突、固定、
跨调用的调用者保存与类外寄存器，并填 `regs_someone_prefers`——两步都能用 `ee-gcc-observe-alloc.py --prefs` 观测
（[L-EE-053](LAWS.md#l-ee-053--a-copy-records-a-hard-register-preference-on-whichever-side-is-a-global-pseudo) 记录、[L-EE-054](LAWS.md#l-ee-054--preferences-are-pruned-before-ordering-conflicts-fixed-caller-saved-for-call-crossing-values-and-out-of-class-registers-are-removed) 剪枝）。
上面的候选/选择规则吃的是**剪枝后**的列表，所以 RTL 里看得到的偏好不一定是选择规则看到的那个。

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

## L-EE-025 · `-O2`/`-Os` 下循环是倒计数（`-O1` 保留 `slt`）、且不被展开

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

**随档位变化**：`-O1` 下同一个循环保留**递增**比较——`addu $14,$14,1` / `slt $15,$14,8` / `bnel`——且乘法留在循环内；
所以「循环是不是倒计数」同时也是**档位判据**。`-O2`、`-Os`、`-O3` 才倒计数。

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

## L-EE-028 · 前八个实参走寄存器，其余按 8 字节槽入栈

十六组夹具（1–16 个 `int` 实参，`-O2 -G0`）：

* **第 1–8 个实参走 `$4`–`$11`**，都不碰栈；
* **第 9 个起**每个实参按 **8 字节步长**入栈：`0($sp)`、`8($sp)`、`16($sp)`…（按源码顺序；即便是 `int` 也是 8 字节，不是 4）；
* `.frame` 的 `args=` 是该区**向上取整到 16**：9–10 个 → 16，11–12 → 32，13–14 → 48，15–16 → 64，
  即 `args = round16(8 × max(0, n − 8))`。

**整帧** = `round16(vars + 8 × regs + args)`
（[L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers)）：九个实参时和为 24、帧为 32。

**浮点用另一套额度**：最多 8 个 `float` 实参走 **`$f12`–`$f19`**——所以「8 个 int + 4 个 float」会**同时**占满 `$4`–`$11` 与 `$f12`–`$f15`。
`long long` / `double` 则**各占一个 64 位 GPR**（`dli $4,1`、`dli $5,2` 传两个 `long long`；被调用方用 `daddiu a0,a0,1` 读 `long long z`），**不是寄存器对**。

**T2**｜源码锚点：MIPS 后端的 EABI 实参布局（`config/mips/mips.c`；未从出厂树读到行号）｜常量：8 个寄存器实参、8 字节槽、16 字节取整｜
falsifies：「出参栈槽是 4 字节」与「`args=` 只按 4 字节对齐」。
**杠杆**：从 `args=` 反推调用形状（16 ⇒ 9 或 10 个实参；32 ⇒ 11 或 12 个）；帧差 8 或 24 字节时先想**取整**，别急着加变量。

---

## L-EE-029 · 单精度走硬件，双精度走软浮点

| 运算 | 生成 |
| --- | --- |
| `float` `+`/`*` | `add.s` / `mul.s` —— COP1 |
| `float` 转换 | `mtc1` + `cvt.s.w`、`trunc.w.s` + `mfc1` |
| `double` `+`/`-`/`*`/`/` | **`jal dpadd` / `dpsub` / `dpmul` / `dpdiv`** |
| `double` 比较 | `jal dpcmp` |
| `double` → `int`/`unsigned` | `jal dptoli` / `dptoul` |
| `int`/`float` → `double` | `jal litodp` / `fptodp` |
| `double` → `float` | `jal dptofp` |

以上全是**线下 libgcc 调用** ⇒ 做 `double` 运算的目标里出现的是 `jal dpadd` 这类调用，**不会出现 `add.d`**。
`-mhard-float` **不改变**这一点；`-msoft-float` 会连单精度也变成软浮点；`-O3` 与 `-O2` 相同。

**T2**｜源码锚点：该 port 的 `TARGET_` 宏与 libgcc（`config/mips/mips.h`；未从出厂树读到行号）｜常量：重定位名 `dpadd`、`add.s`｜
falsifies：「这个构建里会出现 `add.d`」与「`-mhard-float` 能启用硬件双精度」。
**杠杆**：`float`/`double` 写错类型的最灵敏指纹——目标 `jal dpadd` 而你 `add.s`（或反之），
通常是字面量 `2.0` 应为 `2.0f`，或变量被声明成了 `double`。

---

## L-EE-030 · 结构体：≤8 字节按值、更大按引用；返回用隐藏指针

从**被调用方**判定（`-O2 -G0`）：

| 聚合类型 | 大小 | 序言 | 约定 |
| --- | ---: | --- | --- |
| `struct { int a; }` | 4 | `move v0,a0` | **按值**在 `$4` |
| `struct { char c[8]; }` | 8 | `sd a0,0(sp)` 后 `lb v0,7(sp)` | **按值** |
| `struct { short a,b,c,d; }` | 8 | `sd a0,0(sp)` 后 `lh v0,0(sp)` | **按值** |
| `struct { int a,b,c; }` | 12 | `lw t7,0(a0)` | **按引用** |
| `struct { int a,b,c,d; }` | 16 | `lw t5,0(a0)` | **按引用** |
| `struct { char c[9]; }` | 9 | `ldl t4,7(a0)` | **按引用** |

边界是 **8 字节（含）**。**返回**聚合时编译器用 `$4` 作隐藏返回指针，**其余实参整体后移一个槽**：

```asm
make8(int x):                 ; S8 make8(int x)
    addiu t7,a1,1             ; x 从 $5 读——$4 是返回槽
    sw    a1,0(a0)
    sw    t7,4(a0)
    move  v0,a0               ; 指针在 $2 返回
```

**T2**｜源码锚点：EE EABI 的聚合部分（`config/mips/mips.c`；未从出厂树读到行号）｜常量：8 字节边界｜
falsifies：「小结构体走寄存器对」与「返回结构体的函数第一个实参在 `$4`」。
**杠杆**：目标序言里 `lw …,0($4)` ⇒ **>8 字节按引用**；`sd $4,0($sp)` 后从栈读 ⇒ **≤8 字节按值**。
目标**返回结构体**时，参数要**往后数一位**——`$4` 是返回指针，这是读目标签名时最容易错的一位。

---

## L-EE-031 · 可变参数函数保存实参寄存器并调用 `__builtin_va_start`

| 函数 | 具名参数 | 保存的实参寄存器 | 个数 |
| --- | ---: | --- | ---: |
| `v1(const char *a, ...)` | 1 | `a1 a2 a3 t0 t1 t2 t3`（`$5`–`$11`） | **7** |
| `v2(const char *a, int b, ...)` | 2 | `a2 a3 t0 t1 t2 t3` | **6** |
| `v5(a,b,c,d,e, ...)` | 5 | `t1 t2 t3` | **3** |

个数 = **8 − 具名参数个数**，每个 **8 字节**槽，位置在被调用者保存区之后（偏移逐函数变化）。
每个变参函数还会调用 **`__builtin_va_start`**（以重定位名出现）——这是「该函数是可变参数」**最硬的证据**。

**没有浮点保存区**：返回 `double` 的变参函数也只保存整数寄存器；调用方把变参 `1.5f` 或 `1.5`
**提升为 double 放进 `a1`**（`li a1,2047` 后 `dsll32 a1,a1,0x13`）——走整数寄存器序列，**不是 `$f12`**
（[L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots)）。

**T2**｜源码锚点：后端序言（`config/mips/mips.c`；未从出厂树读到行号）｜常量：`__builtin_va_start` 重定位、个数 7｜
falsifies：「变参函数有浮点保存区、其浮点实参走 `$f12`」。
**杠杆**：序言里**一串 `sd` 从 `a1`–`t3` 存进连续 8 字节槽** ⇒ *这个函数是可变参数*；
在变参调用点，浮点实参要对 **`$4`–`$11`**，不是 `$f12`。

---

## L-EE-032 · 除法：硬件 `div`、无魔法数、64 位走 libgcc

| 表达式 | 生成 |
| --- | --- |
| `a/b` 有/无符号 | `div` / `divu`，随后 **`beql $r,$0` + `break 7`**（除零检查），再 `mflo` |
两个命名细节：编译器自己的汇编把检查写成 `beql`，objdump 印成 `beqzl`（同一指令）；**常量**除数只有 `break 7`、**没有分支**——
因为除数已知非零 ⇒ 有分支才说明编译器无法证明除数非零。

| `a%b` | 同上，结尾是 **`mfhi`** |
| `a*b`（32 位） | `mult` + `mflo` —— 硬件 |
| `a/8` 有符号 | `slti` + `movn` + `sra` —— 无 `div` |
| `a/8` 无符号 | `srl` |
| `a%8` 有/无符号 | `slti`+`movz`+`sra`+`sll`+`subu` / `andi` |
| **`a/3`、`a/-7`** | **`li $r,3` + `div`** —— **不做倒数乘法** |
| `long long` 的 `/`、`%`、`*` | `jal __divdi3`、`__moddi3`、**`__muldi3`** |
| `unsigned long long` 的 `/`、`%` | `jal __udivdi3`、`__umoddi3` |

两点值得记住：一次运行时除法是**三条指令的整体**（`div`/`divu` + `beqzl`+`break` + `mflo`/`mfhi`），那个陷阱不是独立逻辑；
而且本构建**没有魔法数变换**——非 2 的幂常量除数仍是 `li` + `div`，这可以直接反推源码除的是什么。
所有 64 位运算都是 libgcc 调用，**连乘法也是**（与 32 位的 `mult` 相反）。

**T2**｜源码锚点：MIPS 除法模式与 libgcc 回退（`config/mips/mips.md`；未从出厂树读到行号）｜常量：重定位名与 `break`｜
falsifies：「常量除法会变成乘魔法数」与「64 位乘法是内联的」。
**杠杆**：目标 `li`+`div` ⇒ 源码除的是**非 2 的幂常量**；`slti`/`movn`/`sra` ⇒ 除的是 **2 的幂**；
`jal __divdi3`/`__muldi3` ⇒ 源码用了 **`long long`**（与 `jal dpadd` 指示 `double` 同类）。

---

## L-EE-033 · 数据模型：4 字节指针、**8 字节 `long`**

| 类型 | 尺寸 | | 类型 | 尺寸 |
| --- | ---: | --- | --- | ---: |
| `char` | 1 | | 指针 | **4** |
| `short` | 2 | | `float` | 4 |
| `int` | 4 | | `double` | 8 |
| **`long`** | **8** | | `long double` | **8** |
| `long long` | 8 | | | |

默认就是 **`-mlong64`**（只有 `-mlong32` 才让 `long` 变 4）⇒ `long` 字段用 `ld`/`sd` 读写，
对 `long` 的 64 位算术与 `long long` 一样走 libgcc
（[L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc)）。

对齐 = 自身尺寸，所以 8 字节成员按 8 对齐：

| 结构体 | 偏移 | 尺寸 |
| --- | --- | ---: |
| `{char a; int b;}` | a@0, b@4 | 8 |
| `{char a; short b; int c;}` | a@0, b@2, c@4 | 8 |
| `{char a; double d;}` | a@0, **d@8** | 16 |
| `{char a; long l;}` | a@0, **l@8**（`sd`） | 16 |
| `{char a; long l; int i; void *p;}` | a@0, **l@8**, i@16, p@20 | 24 |

**T2**｜源码锚点：该 port 的尺寸宏（`config/mips/mips.h`；未从出厂树读到行号）｜常量：`long` 8、指针 4、`long double` 8｜
falsifies：「32 位指针的目标必然有 32 位 `long`」（常见 ILP32 直觉）。
**杠杆**：目标里字段用 `ld`/`sd` ⇒ 该字段是 `long`/`long long`/`double`，不是 `int`；
结构体尺寸对不上，通常是 `long` vs `int` 或 8 字节对齐的问题。

---

## L-EE-034 · 本项目**最多**的档位是 `-Os`，且规则在它下面成立

`config/source_flags.tsv` 统计：**`-Os` 687 个文件**、`-O1` 542、`-O2` 264、`-O3` 98 ⇒ 参考档位是 `-Os`，不是 `-O2`。
拿手册自己的夹具在该档跑：

```sh
python3 tools/compiler/ee-gcc-observe.py --selftest --flags="-Os -G0"   # 34 passed / 0 failed
```

⇒ 帧规则、switch 阈值（4 路链、5/6 路表）、内联门槛、浮点/双精度常量形态、除法习语，在 `-Os` 下都与文档一致。
同一套夹具在 `-O1` 与 `-O3` 各失败 1 组，且两次失败**都是手册已经预测的行为**：`-O1` 保留递增比较
（[L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled)）、`-O3` 会内联普通 `static`（[L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined)）。

有一处确实不同：**`-Os` 把函数对齐到 4 字节**，而 `-O2` 发出 `.p2align 3,,7`（8 字节）
（[L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)）。项目的 `-falign-functions=4` 掩盖了这一点，但不带该旗标的单元会不匹配。

**T2**｜源码锚点 `toplev.c:3316`（档位决定流水线，[L-EE-020](LAWS.md#l-ee-020--the-pass-pipeline-is--o-sensitive)）｜常量：`-Os` 687 个文件、4 字节对齐｜
falsifies：「本项目的参考档位是 `-O2`」与「`-Os` 的填充与 `-O2` 相同」。
**杠杆**：断定某条规则不成立前，先用**该单元真实的档位**跑夹具；大小/偏移不符时记得 `-Os` 隐含 4 字节对齐。

---

## L-EE-035 · 位域：低位优先、不跨界、读会收窄、写是掩码读-改-写

| 结构体 | 尺寸 | 布局 |
| --- | ---: | --- |
| `{unsigned a:1; b:3; c:12; d:16;}` | **4** | bit 0、1、4、16 |
| `{int a:1; b:3; c:12; d:16;}` | **4** | 同上 |
| `{unsigned char a:3; b:5;}` | **1** | 容器 = `unsigned char` |
| `{unsigned short a:4; b:12;}` | **2** | 容器 = `unsigned short` |
| `{unsigned a:20; b:20;}` | **8** | **不跨界**——第二个字段从第二个字开始 |

读会**收窄到最小的对齐访问**：

| 字段 | 生成 |
| --- | --- |
| 无符号 3 位 @bit1 | `lw` + `srl 1` + `andi 0x7` |
| 无符号 16 位 @bit16 | 直接 **`lhu $2,2($4)`** |
| **有符号** 12 位 @bit4 | **`lh $2,0($4)` + `sra 4`** |
| `unsigned char` 容器内 5 位 | `lbu` + `srl 3` |

写是**掩码读-改-写**，掩码来自 **64 位立即数**：

```asm
lw   $14,0($4)
li   $15,-65536        # 0xffffffffffff0000
ori  $15,$15,0xf
and  $14,$14,$15       # 清位
sll  $5,$5,4
or   $14,$14,$5        # 置位
sw   $14,0($4)
```

**T2**｜源码锚点 `stor-layout.c` 与后端访问模式（未从出厂树读到行号）｜常量：掩码 −65536、尺寸 4 与 8｜
falsifies：「位域读一定是 `lw`+掩码」与「写是移位插入」。
**杠杆**：`lh`/`lbu` + `sra` ⇒ **有符号**位域；`lw` + `srl` + `andi` ⇒ 无符号；直接 `lhu` ⇒ 对齐的 16 位字段；
`and`/`or` 前出现**负数 `li`** ⇒ 位域**写**。

---

## L-EE-036 · 尾调用就是跳转——但 `-O2` 以下没有

`int t1(int a) { return g(a); }`：

| 档 | 生成 |
| --- | --- |
| `-O0`、**`-O1`** | `jal g` + `j $31` |
| **`-O2`**、`-Os`、`-O3` | **`j g`** —— 没有 `jal`、没有 `jr $31` |

开关是 `-foptimize-sibling-calls`，`-O2` 以下不开：给 `-O1` 加上它就会生成 `j g`，而 `-O2 -fno-optimize-sibling-calls`
会退回 `jal` + `j $31`。**本项目有 542 个文件是 `-O1`** ⇒ 它们**完全没有尾调用**。

试过的每种尾位置在 `-O2` 下都变成跳转：`return g(a)`；带局部变量（`int x=a+1; return g(x)`）；
`if`/`else` **两个分支**各自返回不同调用；`void` 调用；以及 `return g(*p)`。

**T2**｜源码锚点 `calls.c` 与后端 sibcall 模式（未从出厂树读到行号）｜常量：上面两种形态｜
falsifies：「函数的调用都会以 `jal` 出现」与「档位不改变调用形状」。
**杠杆**：目标在你预期是调用的地方**直接跳到外部符号** ⇒ 那是**尾调用**（档位 ≥ `-O2`）；
反过来，`-O1` 下每个调用都保留 `jal` + `j $31`，重建时少了这两条就是档位判断错了。

---

## L-EE-037 · `volatile` 表现为**不被合并的访问**

| 源码 | 无 `volatile` | 有 `volatile` |
| --- | --- | --- |
| `*p = *p + 1; *p = *p + 1;` | **一次** `lw`、`addu …,2`、一次 `sw` | **两组** `lw`/`addu …,1`/`sw` |
| `int a=*p; int b=*p; return a+b;` | **一次** `lw`（CSE） | **两次** `lw` |
| `gi = gi + 1;` | `lw`、`addu 1`、**`j $31`**、`sw` —— store **沉入延迟槽** | `lw`、`addu 1`、**`sw`**、`j $31` —— **顺序保持** |

两条可直接用的判据：

1. **载入次数**：目标里同一地址出现**两条 `lw`** ⇒ 源码通过 `volatile` 指针读了两次（或两次读之间隔着调用）。
   无 `volatile` 时编译器会**合并**。
2. **store 的位置**：无 `volatile` 时 store 常被**沉入**随后的 `j $31` 延迟槽；有 `volatile` 时 `sw` 在**跳转之前**。

`-Os` 下形状完全相同。

**T2**｜源码锚点：volatility 在各 RTL pass 中体现（未从出厂树读到行号）｜常量：合并后的 `addu …,2` 对两次 `addu …,1`｜
falsifies：「重复读一定是分离指令」与「`volatile` 只改顺序、不改次数」。
**杠杆**：重建比目标**少一条 `lw`** ⇒ 怀疑漏了 `volatile`；反之**多加**会多出一条载入，后面全部错位。

---

## L-EE-038 · 聚合拷贝：32 字节内全展开，之上是内联 `ldl/ldr` 循环——**从不调 `memcpy`**

`void f(struct S *d, struct S *s) { *d = *s; }`（`-O2 -G0`）：

| 大小 | 形态 | 指令数 |
| ---: | --- | ---: |
| 4–**32** | **全展开** `lw`/`sw` 对 | 每字 2 条 + 2 |
| **36**–256 | **内联循环**：`ldl`/`ldr` + `sdl`/`sdr`，**每轮 16 字节** | 14–20 |

```asm
        ldl     t3,7(a1)      # 非对齐 64 位装载（低位对）
        ldr     t3,0(a1)      #                  （高位对）
        ldl     t4,15(a1)
        ldr     t4,8(a1)
        sdl     t3,7(a0)
        sdr     t3,0(a0)
        ...
        addiu   a1,a1,16
        bne     a1,t7,4 <f+0x4>
```

**任何被测尺寸（到 256 字节）都没有 `memcpy`/`memmove` 调用**——后端自己展开拷贝。

**T2**｜源码锚点 `expr.c` 与后端 movstr 模式（未从出厂树读到行号）｜常量：32 字节、每轮 16 字节｜
falsifies：「大结构体赋值会变成 `memcpy` 调用」与「拷贝用对齐的 `ld`/`sd`」。
**杠杆**：目标里 `ldl`/`ldr`-`sdl`/`sdr` 循环 ⇒ 拷 **>32 字节**；一串 `lw`/`sw` ⇒ **≤32 字节**。
不要把 **`ld`/`sd`（对齐，用于 `long`/`double`）**与 **`ldl`/`ldr`/`sdl`/`sdr`（非对齐，用于这些循环）**混为一谈。

---

## L-EE-039 · 间接调用是 `jalr`，且**永不**变成尾跳转

| 源码 | 生成 |
| --- | --- |
| `gfp(a)` —— 全局函数指针 | `lw $2,%lo(gfp)($15)` 后 **`jalr $2`** |
| `v->fn(a,b)` —— 结构体字段 | `lw $2,0($4)`、摆参数、**`jalr $2`** |
| `fp(a)` —— 参数 | `move $2,$4` 后 **`jalr $2`** |
| `f()` —— void 指针 | **`jalr $4`** |

目标寄存器是**普通分配的寄存器**（实测 `$2`、`$4`）——**不是** `$25`/`t9`。对象里助记符是 **`jalr`**，
汇编里写 **`jal $31,$reg`**。

**尾调用优化只覆盖直接调用。** 尾位置对比：

```asm
d:  # return g(a);     直接
        sd      $31,0($sp)
        ld      $31,0($sp)
        j       g              # 裸尾跳转
i:  # return gp(a);    间接
        sd      $31,0($sp)
        lw      $2,%lo(gp)($15)
        jal     $31,$2         # 仍然是真调用
        ld      $31,0($sp)
        j       $31            # 仍然要返回
```

`-O1`、`-O2`、`-Os` 形状相同 ⇒ 间接调用**不能**用来判断档位。

**T2**｜源码锚点：MIPS 后端的间接调用模式（未从出厂树读到行号）｜常量：`jalr` 与 `jal $31,$reg`｜
falsifies：「间接尾调用会像直接调用那样变跳转」与「间接调用目标走 `$25`/`t9`」。
**杠杆**：目标里 `jalr` 后接 `j $31` ⇒ 源码用了**函数指针**；若你重建成具名调用，`-O2` 下会变成**裸尾跳转**，形状全变。

---

## L-EE-040 · 比较习语：作为**值**物化、作为**条件**分支

`-O2` 与 `-Os` 在这里**完全相同**。

| 表达式（结果当值用） | 生成 |
| --- | --- |
| `a == b` | `xor` + **`sltu $r,$r,1`** |
| `a != b` | `xor` + **`sltu $r,$0,$r`** |
| `a == 0` / `a != 0` / `!a` | **`sltu $r,$a,1`** / `sltu $r,$0,$a` / `sltu $r,$a,1` |
| `a < b` 有符号 / 无符号 | `slt` / `sltu` |
| `a > b` | `slt`，**操作数交换** |
| `a <= b` | 交换操作数的 `slt(u)` + **`xori $r,$r,0x1`** |
| `a && b` | `sltu $r,$0,$b` + **`movz`** —— **无分支** |
| `a \|\| b` | **有分支**：`bne`、`beq`、`li $2,1` |
| `a<b ? a : b` | `slt` + **`movz`** |

同一个比较**作为条件**时通常**分支**：`if (a == b) return g();` 就是裸 **`bne $4,$5,$L`**，没有 `xor`/`sltu`。
但**当两个分支都是简单值时**，编译器会把 `if` 转成**无分支选择**——`if (a == b) return 1; return 2;` 会变成
`xor $4,$4,$5` 后接 `movn $2,$15,$4`。所以「`xor` 配 `movn`/`movz`」既可能来自三元，也可能来自 `if`。选哪个条件移动**并不固定**——
`-O2` 用 `movn`（常量一种顺序）、`-O1` 用 `movz`（常量相反顺序）——比对时要看**形状**（无分支选择），别盯某一个助记符。

三处「看着几乎对」的地方：

1. `==` **不是** `beq`——当值时是 `xor` + 与 0/1 比较的 `sltu`；
2. `<=` **不是**单条指令——是「操作数交换的 `<`」再 `xori 1`；
3. **`&&` 无分支（`sltu`+`movz`），`||` 有分支**——两者**不对称**；min/max 用 `movz` 而不是分支。

**T2**｜源码锚点：后端的比较与条件移动模式（未从出厂树读到行号）｜常量：`sltu` 与 `xori` 里的 `1`｜
falsifies：「`==` 会编成 `beq`」「`<=` 是单条比较指令」「`&&` 与 `||` 编译方式相同」。
**杠杆**：目标里 `xor`+`sltu` 或 `xori 0x1` ⇒ 该比较的**结果被当成值**用了；裸 `bne`/`beq` ⇒ 它是**条件**。

---

## L-EE-041 · 128 位容器：`lq`/`sq`、寄存器对、且不能按值返回

**本项目有 1141 个重建源文件使用 `mode(V4SI)`**（`s128`/`u128`）——约占三分之一——这里就是这些类型的代码生成。
`-O2` 与 `-Os` 相同。

| 操作 | 生成 |
| --- | --- |
| `v4si x = *p;` | **`lq $2,0($4)`** —— 128 位装载 |
| `*p = v;` | **`sq $5,0($4)`** —— 128 位存储 |
| `*d = *s;`（16 字节） | **`lq $15,0($5)` + `sq $15,0($4)`** —— 一条 128 位搬移 |
| `((int*)p)[i]` / `… = v` | `sll` + `addu` + **`lw`** / **`sw`** |
| 第 0 个元素 | `dsll $4,$4,32` + `dsra $4,$4,32`（在 64 位寄存器上符号扩展取出） |
| 第 1 或第 3 个元素 | **`sq $4,0($sp)`** 后 `lw $2,4($sp)` / `lw $2,12($sp)` |
| 传 `v4si` | 在**寄存器对**里（从 `$4` 起）；转发无需搬运 |

**判别法**——同样 16 字节：

| 源码 | 生成 |
| --- | --- |
| `struct S16 { int a,b,c,d; } *d = *s;` | 展开的 `lw`/`sw` 对（[L-EE-038](LAWS.md#l-ee-038--aggregate-copies-unrolled-to-32-bytes-then-an-inline-ldlldr-loop--never-memcpy)） |
| `v4si *d = *s;` | **`lq` + `sq`** |

⇒ 目标里出现 `lq`/`sq` ⇒ 该处源码用了 **128 位类型**——这正是 m2c 在这些位置生成 `V4SI` 的原因。

**两条硬限制**：128 位值**不能按值返回**（编译报 `output_operand: invalid expression as operand`），
所以目标里按值返回 16 字节的函数只能是**结构体**（隐藏指针，[L-EE-030](LAWS.md#l-ee-030--aggregates-8-bytes-by-value-larger-by-reference-returns-use-a-hidden-pointer)），**不可能**是向量；
并且 **3.2 没有向量算术**（两个向量相加直接报错）——这些类型只是**不透明的 128 位容器**。

**T2**｜源码锚点：EE 特有的 `lq`/`sq` 模式（未从出厂树读到行号）｜常量：助记符 `lq`、`sq`｜
falsifies：「16 字节拷贝一定是 `lw`/`sw` 对」与「128 位值能像结构体那样按值返回」。
**杠杆**：目标里 `lq`/`sq` ⇒ 该处是 128 位类型；若你把 16 字节返回重建成向量，编译器会直接拒绝——请用结构体。

---

## L-EE-042 · `float` 住在 COP1，`double` 住在通用寄存器

**本项目约 41% 的重建文件用到 `f32`（1389）或 `f64`（1390）**，所以「一眼分辨两者」很实用。

| 操作 | `float` | `double` |
| --- | --- | --- |
| 全局装载 | **`l.s $f0,%lo(gf)($15)`** | **`ld $2,%lo(gd)($15)`** —— **GPR** |
| 全局存储 | **`s.s $f12,…`** | **`sd $4,…`** |
| 算术 | `add.s`/`sub.s`/`mul.s`/`div.s` —— COP1 | `jal dpadd`/`dpsub`/`dpmul`/`dpdiv` |
| 比较 | **`c.lt.s` + `bc1t`** | **`jal dpcmp`** + 整数比较 |
| `int` → | `mtc1` + `cvt.s.w` | `jal litodp` |
| → `int` | `cvt.w.s` + `mfc1` | `jal dptoli` |
| float ↔ double | `jal fptodp` / `dptofp` | 同 |
| 与 0 比较 | `mtc1 $0,$f0` + `c.eq.s` | `dpcmp` |

**给目标里的值定类型最快的一条**：`l.s`/`s.s`/`c.*.s`/`bc1t` ⇒ **`float`**；`ld`/`sd` 到 GPR 后接 `jal dp*` ⇒ **`double`**。
并且**不要去找 `l.d` 或 `c.lt.d`**——这个构建里**没有**任何 COP1 双精度指令（与 [L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float) 一致）。

**T2**｜源码锚点：该 port 的模式定义（未从出厂树读到行号）｜常量：`l.s`、`dpadd`、`bc1t`｜
falsifies：「`double` 像 `float` 一样用 COP1」与「double 比较是 `c.lt.d` 指令」。
**杠杆**：这是那 40% 浮点文件的**类型判据**，与 L-EE-011/L-EE-019（常量）、L-EE-029（运算 lowering）互补。

---

## L-EE-043 · 64 位整数是原生运算；只有乘、除、取模走调用

**本项目 41% 的文件用到 `s64`/`u64`。** 与 `double` 不同，64 位**整数**用的是 R5900 原生 64 位 GPR 指令——
`-O1`/`-O2`/`-Os` 实测一致，且本组夹具的**对象里没有任何 libgcc 重定位**。

| 运算 | 生成 |
| --- | --- |
| `a + b` / `a - b` / `a + 1` | **`daddu`** / **`dsubu`** / **`daddiu`** |
| `-a` | `dsubu $r,$0,$a` |
| `a << 4`、`a << n` | **`dsll`** |
| `a >> 4` 有符号 / 无符号 | **`dsra`** / **`dsrl`** |
| `&`、`|`、`^` | `and` / `or` / `xor` |
| `a < b` | **`slt`** —— **内联 64 位比较** |
| `a == b` | `xor` + `sltu …,1`（[L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)） |
| `int` → `long long` | **`move`** —— ABI 已把 32 位实参符号扩展 |
| `long long` → `int` | **`dsll $r,$r,32` + `dsra $r,$r,32`** |
| `unsigned` → `long long` | `dsll …,32` + **`dsrl …,32`** |

⇒ **同一个 64 位类型，运算不同形态就不同**：`daddu`/`dsll`/`slt` 是内联，而**乘/除/取模会变成
`jal __muldi3`/`__divdi3`/`__moddi3`**（[L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc)）。

`dsll …,32` + `dsra …,32` 是**「把 64 位值收窄成 32 位」的固定习语**——与 128 位向量取第 0 个元素
（[L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return)）是同一个，看到它就知道有个 64 位值被降成了 `int`。

**T2**｜源码锚点：EE 特有的 64 位 GPR 模式（mainline MIPS 会调 libgcc；未从出厂树读到行号）｜常量：`daddu`、`dsll`、以及 `dsll`/`dsra` 里的 32｜
falsifies：「64 位整数像 `double` 一样全部线下」与「64 位比较需要辅助函数」。
**杠杆**：目标里 `daddu`/`dsubu`/`dsll`/`dsra`/`dsrl`/`slt` ⇒ 源码用了 **64 位整数类型**（[L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long)）；
`dsll …,32` + `dsra …,32` ⇒ 该值正被**收窄成 32 位**。

---

## L-EE-044 · 非对齐访问：三种来源，而且对象里**没有** `ulw`/`usw`

| 源码 | 汇编 | **对象** |
| --- | --- | --- |
| 指针转换 `*(int*)(p+1)` | `lw $2,1($4)` | **偏移 1 的裸 `lw`** —— 编译器信任转换，不做合成 |
| `memcpy(d,s,4)` | `lwl $12,3($5)` + `lwr $12,0($5)` | `lwl`+`lwr`；写用 `swl`+`swr` |
| `memcpy(d,s,8)` | `ldl`+`ldr` | `ldl`+`ldr`；写用 `sdl`+`sdr` |
| `__attribute__((packed))` 成员 | **`ulw $2,1($4)`** / **`usw $5,1($4)`** | **`lwr`+`lwl` / `swr`+`swl` 对** |

**坑**：`ulw`/`usw` 是**汇编伪指令**。汇编写 `ulw $2,1($4)`，而对象里是

```asm
lwr     v0,1(a0)
jr      ra
lwl     v0,4(a0)      # 注意 +3 偏移
```

⇒ **在反汇编里 grep `ulw`/`usw` 什么也找不到**，只能看到 `lwl`/`lwr` 对。
（同类坑家族：2.96 的 `li.s`、`beql` 被印成 `beqzl`、`jalr` 在汇编里写 `jal $31,$reg`。）

常量大小的 `memcpy` 形成阶梯：1 → `lbu`/`sb`；2 → `lb`/`sb` 各两次；4 → `lwl`/`lwr` + `swl`/`swr`；
8 → `ldl`/`ldr` + `sdl`/`sdr`；16 → 各两组。

**T2**｜源码锚点：EE 特有的非对齐模式（未从出厂树读到行号）｜常量：`lwl` 与伪指令 `ulw`｜
falsifies：「非对齐的指针转换会被编译器处理」与「对象里有 `ulw`/`usw`」。
**杠杆**：`lwl`+`lwr`（或 `swl`+`swr`）对 ⇒ 4 字节非对齐访问，来源可能是**常量 `memcpy`** 或 **packed 成员**
（对象里同形，靠基址与偏移规律区分）；**偏移非 4 倍数的裸 `lw`** ⇒ 源码做了指针转换。

---

## L-EE-045 · 循环回边用 likely 分支，前向分支不用

| 源码 | 分支形态 |
| --- | --- |
| `if (p == 0) return -1;` | **`beq`** —— 普通 |
| `if (x) …`、`if (a && b) …`、if/else 链 | `beq` / `bne` —— 普通 |
| `while (n--) …` | `beq` 守卫 + **`bnel`** 回边 |
| `for (i=0;i<n;i++)` | `blez` 守卫 + **`bnel`** 回边 |
| `do { … } while (n > 0);` | **`bgtzl`** |
| `while (*p == 0) p++;` | `bne` + **`beql`** |

likely 形式的**延迟槽只在分支被采用时执行**，所以循环底部的 `bnel` 能承载循环自身的活——
`-O1` 下同一个循环就把 `mult` 放进那个槽里。

两个实用点：

* **函数体末尾出现 `bnel`/`beql`/`bgtzl` ⇒ 那是循环**。候选若在那里生成 `bne`+`nop`，说明循环形状不同
  （或是 `-Os` 的重构：把某个循环变成 `bne` + 无条件 `b` 回边）。
* 汇编写 **`beql`/`bnel`**，而 **objdump 在与 `$0` 比较时印 `beqzl`/`bnezl`** —— 两种拼法都要 grep。

**这个代码库的指令分布**（170 个随机匹配源，各按自己的档位）：

```
addiu 384  move 322  ld 267  sd 235  jal 185  li 131  jr 123  lw 87  lui 84  nop 64
j 60  sw 56  addu 54  sh 30  lh 28  sll 27  sb 27  beqz 26  mult 22  slti 21 …
```

`ld`/`sd` 排第 3/4 ⇒ 这个代码库搬运的是 **64 位数据**（[L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long)），而 `move` 排第 2。

**T2**｜源码锚点：EE/MIPS 的 likely 分支模式（未从出厂树读到行号）｜常量：`bnel` 与 objdump 的 `beqzl` 拼法｜
falsifies：「循环回边与 if 用同样的分支形式」与「`beql` 在反汇编里总是写成 `beql`」。
**杠杆**：函数体末尾的 likely 分支 ⇒ 循环；候选的循环差两条指令时，先看目标回边是不是 likely。

---

## L-EE-046 · 每一条 `move` 都是 64 位的 `daddu`

对对象字解码可知：**`move` 永远是 `daddu $d,$s,$0`（funct `0x2d`）**，**从不**是 `addu`（funct `0x21`）——
即使 C 类型是 `int`。

| 函数 | 类型 | 编码 | 实际含义 |
| --- | --- | --- | --- |
| `int b = a;` | 32 位 | `0080102d` | `daddu v0,a0,zero` |
| `long long b = a;` | 64 位 | `0080102d` | `daddu v0,a0,zero` |
| `int x = 0;` | 32 位 | `0000102d` | `daddu v0,zero,zero` |

**陷阱**：objdump **把 `daddu $d,$s,$0` 印成 `move`**，于是

* 真实代码的助记符统计里是 **`move` 322 次、`daddu` 0 次**（[L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) 的 170 文件样本）——
  `daddu` 只在第三个操作数不是 `$0` 时才出现；
* 重建时写 `addu $d,$s,$0` **对不上字节**，尽管助记符看起来都叫 `move`。

实用统计（60 个真实文件、125 条 `move`）：**48 条（38%）落在分支/跳转的延迟槽**、57 条普通、19 条是 `move $d,$0`（置零）；
目标寄存器以实参寄存器为主（`a0` 46、`a1` 18、`a2` 7）⇒ 多数拷贝是**实参搬运**。

**T2**｜源码锚点：该 port 的 move 模式（未从出厂树读到行号；结论来自对象字解码）｜常量：funct `0x2d` 对 `0x21`｜
falsifies：「`move` 展开为 `addu`」与「助记符能告诉你拷贝是 32 位还是 64 位」。
**杠杆**：按**编码**而不是助记符核对拷贝；实参交换表现为「一条临时寄存器 + 三条 `move`」，其后若是尾位置则是 `j`。

---

## L-EE-047 · 打印出来的助记符是**别名**——要比编码，不要比拼写

对对象字解码（`-O2 -G0`）：

| 源码 | 打印 | **实际编码** |
| --- | --- | --- |
| `return 5;` | `li v0,5` | **`ADDIU $2,$0,5`** |
| `return -5;` | `li v0,-5` | `ADDIU $2,$0,0xfffb` |
| `return 0xffff;` | `li v0,0xffff` | **`ORI $2,$0,0xffff`**（零扩展） |
| `return 0x12345;` | `lui v0,0x1` + `ori v0,v0,0x2345` | 两条真指令——**没有 `li` 别名** |

**`li` 是伪指令**：有符号 16 位内 → `ADDIU`，到 `0xffff` → `ORI`，更大 → `lui`+`ori` 两条（objdump 直接印两条）。

对 **60 个真实匹配源**的普查显示映射是**多对一**：

| 编码 | 打印出的助记符 |
| --- | --- |
| `op=0x09`（ADDIU） | `addiu` ×110 / **`li` ×35** |
| `SPECIAL fn=0x00`（SLL） | **`nop` ×23** / `sll` ×3 |
| `op=0x04`（BEQ） | **`beqz` ×7** / `b` ×2 |
| `op=0x05`（BNE） | **`bnez` ×3** / `bne` ×1 |

而样本里**没有任何助记符对应两种基编码**。手册现在收集到的别名全表：

| 显示为 | 基指令 | 出处 |
| --- | --- | --- |
| `li $r,imm`（小 / ≤0xffff） | `ADDIU` / `ORI` | 本条 |
| `li`（更大） | `LUI` + `ORI` | 本条 |
| `move $d,$s` | **`DADDU $d,$s,$0`** | [L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu) |
| `nop` | `SLL $0,$0,0` | 本条 |
| `beqz` / `bnez` / `b` | `BEQ $r,$0` / `BNE $r,$0` / `BEQ $0,$0` | 本条 |
| `ulw` / `usw` | `LWR`+`LWL` / `SWR`+`SWL` | [L-EE-044](LAWS.md#l-ee-044--unaligned-access-three-sources-and-ulwusw-do-not-exist-in-the-object) |
| 对 `$0` 的 `beql`/`bnel` | 印成 `beqzl`/`bnezl` | [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) |
| `jal $31,$reg` | `jalr` | [L-EE-039](LAWS.md#l-ee-039--indirect-calls-are-jalr-and-never-become-tail-jumps) |
| `li.s`（2.96） | 汇编期展开为装载序列 | [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) |

**T2**｜源码锚点：汇编器的伪指令集（未从出厂树读到行号；表格来自对象字解码）｜常量：opcode `0x09` 与 `0x0d`｜
falsifies：「助记符能唯一确定编码」与「`li` 是一条真指令」。
**杠杆**：两段文本看起来一样但字节不同时，比**编码**；手写汇编对目标前，先弄清伪指令**展开成几条**（`li` 可能 1 或 2 条，`ulw` 是 2 条）。

---

## L-EE-048 · COP2/VU0 指令**不可能**由 C 生成

**这是对重建最重要的限制**：本编译器绝不会从 C 生成 COP2/VU0 代码。

| 探测 | 结果 |
| --- | --- |
| `mode(V4SI)` / `mode(V4SF)` 的装载/存储/拷贝 | **`lq`/`sq`（通用寄存器）**——从不是 `lqc2`/`sqc2` |
| 两个向量相加 | **编译错误**（`invalid operands to binary +`） |
| 按值返回向量 | **编译错误**（`output_operand: invalid expression as operand`） |
| `asm` 对向量用 `"v"` 约束 | `impossible register constraint in 'asm'` |

后端**确实**带 VU0 机制——`--target-help` 列出 **`-mvu0-use-REG1-REG2`**，cc1 导出
`vu0_register_operand`（`0x081723b0`）、`vu0_dest_operand`（`0x08172460`）、`vu0_field_operand`（`0x08172490`）、
`vu0_float_operand`、`vu0_int_register_operand`、`vu0_reg_imm5_operand`、`mips_vu0_use_range`（`0x0830fb98`）——
但**没有任何 C 构造能到达它**，也没有 `__builtin_ee_*`/`__builtin_vu*` 内建。

**唯一可行通路是内联汇编**：

```c
int v[4], w[4];
asm volatile("lqc2 $vf1,0(%0)" :: "r"(v));     /* 生成 lqc2 */
asm volatile("sqc2 $vf2,0(%0)" :: "r"(w));     /* 生成 sqc2 */
```

⇒ 二进制里**每一条 COP2 指令都来自原始源码的手写汇编**——`lqc2`、`sqc2`、`qmtc2`、`qmfc2`、`cfc2`、`ctc2`
以及整个 `v*` 向量家族。**这些位置用 C 重建永远匹配不上**；重建必须在那里写内联汇编，否则该函数无法用 C 复现。

**T1**｜源码锚点：后端的 VU0 操作数谓词与 `-mvu0-use-`（`config/mips/mips5900.md`；未从出厂树读到行号）｜二进制锚点：上列符号｜
falsifies：「128 位/浮点向量类型会让编译器使用 VU0」与「COP2 指令可能来自普通 C」。
**杠杆**：目标函数里出现 COP2 助记符时，别去找 C 写法——那是**内联汇编**区域；要么为它预留预算，要么跳过该函数。

---

## L-EE-049 · 变量移位、取负、浮点比较——以及第二个乘法器

| C | 汇编 | **对象** |
| --- | --- | --- |
| `a << n`（变量） | `sll $d,$s,$t` | **`sllv`** |
| `a >> n` 有符号 / 无符号 | `sra` / `srl $d,$s,$t` | **`srav`** / **`srlv`** |
| `-a`（int） | `subu $d,$0,$s` | **`negu`** |
| `-a`（float） | — | **`neg.s`** |
| float 拷贝 | — | **`mov.s`** |
| `a <= b` / `a < b` / `a == b`（float） | — | **`c.le.s`** / `c.lt.s` / `c.eq.s` + `bc1t` |
| `a + b`（float） | — | `add.s` |

**又两对别名**（补进 [L-EE-047](LAWS.md#l-ee-047--the-printed-mnemonic-is-an-alias--compare-encodings-not-spellings) 的表）：汇编的 `sll`/`sra`/`srl $d,$s,$t` 在对象里是
**`sllv`/`srav`/`srlv`**；`subu $d,$0,$s` 是 **`negu`**。⇒ 二进制里出现这些助记符是**普通 C 表达式**，不是手写汇编。

### EE 有**两个**整数乘法器

| 形状 | `mult` | `mult1` |
| --- | ---: | ---: |
| 1 个乘法 | 1 | 0 |
| 2 个独立乘法 | 1 | 0 |
| **3 个独立乘法** | 2 | **1** |
| **依赖的两个乘法**（`x = a*b; return x*b;`） | 1 | **1** |

调度器在乘法可以重叠时把其中一个挪到第二个单元——但**只在 `-O2`/`-O3`**：同一个三乘法夹具在 `-O1`/`-Os` 生成 `mult`×3，
在 `-O2`/`-O3` 生成 `mult`×2 + `mult1`×1。⇒ 目标里的 `mult1` 是**调度信号兼档位线索**，不是内联汇编。

**另外两处拼写**：`multu` **不是**普通的无符号 32 位乘法（那是 `mult`）——它出现在**32 位无符号乘法需要 64 位结果**时；
64 位变量移位在对象里有三种拼写：`dsllv`、`dsrlv`、`dsrav`。

**未决**：`madd.s` 在二进制里存在，但**没有任何普通 C 浮点表达式**能生成它——`a*b+c` 恒为 `mul.s`+`add.s`。
记为**未解释**，不做猜测。

**T2**｜源码锚点：后端的运算符模式与乘法单元（`config/mips/mips.md`；未从出厂树读到行号）｜常量：`sllv`、`negu`、`mult1`｜
falsifies：「`sllv`/`srlv`/`negu` 说明是手写汇编」与「`mult1` 需要内联汇编」。
**杠杆**：候选用 `sll`、目标用 `sllv` ⇒ 形状一致（同一份 C）；目标有 `mult1`、候选只有 `mult` ⇒ 乘法表达式之间的**距离/独立性**不同。

---

## L-EE-050 · COP1 累加器：**一个表达式里求和多个乘积**时用 `mula.s`/`madd.s`

| 浮点表达式 | 生成 |
| --- | --- |
| `a*b + c`（1 个乘积） | `mul.s` + `add.s` |
| **`a*b + c*d`** | **`mula.s` + `madd.s`** |
| **`a*b + c*d + e*g`** | **`mula.s` + `madda.s` + `madd.s`** |
| `a*b + c*d + e` | `mula.s` + `madd.s` + `add.s` |
| **`a*b - c*d`** | **`mula.s` + `msub.s`** |
| **语句形式** `s = a*b; s += c;` | `mul.s` + `add.s` —— **不用累加器** |
| 循环累加 `for (…) s += p[i]*q[i];` | `mul.s` + `add.s` —— 不用累加器 |

⇒ **一个表达式里求和 ≥2 个乘积**时用 **COP1 累加器**：第一个乘积 `mula.s`，后续每个 `madd.s`
（链中需要中间值时用 `madda.s`），减法用 `msub.s`。累加器是硬寄存器 **71**（`FP_ACC`，[L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)）——确实被用到。
而**语句形式**与循环累加**不用**它 ⇒ 累加器是「源码把乘积之和**写成一个表达式**」的信号。

**减法用的是同一套累加器机制**：表达式中**相减乘积**（`c - a*b - d*e`）生成 `mul.s` + **`suba.s`** + **`msub.s`**
（其他形状出现 `msuba.s`）。⇒ 该家族是：乘积**求和**用 `mula.s`/`madd.s`/`madda.s`，**求差**用 `mul.s`/`suba.s`/`msub.s`/`msuba.s`。

**这也解开了 [L-EE-049](LAWS.md#l-ee-049--variable-shifts-negation-float-compare--and-the-second-multiplier) 的未决项**：`madd.s` 其实是普通 C。

同轮另外两项：

* **浮点存储是 `swc1`**（汇编 `s.s`），装载是 `lwc1`（`l.s`）——此前漏了存储那一半；
* 64 位运算在对象里带后缀：**`dsra32`、`dsrl32`、`dsllv`、`dsrlv`、`dnegu`**（汇编写 `dsra $d,$s,32`、`dsll $d,$s,$t`、`dsubu $d,$0,$s`）。

**T2**｜源码锚点：后端的累加器模式（未从出厂树读到行号）｜常量：`mula.s`、`madd.s`、`swc1`｜
falsifies：「`madd.s` 无法由 C 生成」与「浮点乘加一定用累加器」。
**杠杆**：目标里 `mula.s`/`madd.s` ⇒ 源码在**一个表达式**里求和了 ≥2 个乘积；若候选给出 `mul.s`+`add.s`，说明源码被拆成了多条语句。

---

## L-EE-051 · 零比较、浮点分支与被内联的 `sqrtf`

**与零比较只有在「控制流位置」才分支。**

| 源码 | 生成 |
| --- | --- |
| `return a < 0;`（**值**） | 用 `slti` 物化——无分支（[L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)） |
| `if (a < 0) return 1; return 0;` | **无分支**——if-conversion（[L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)） |
| **`while (n > 0) { … }`** | **`blez`**（取反的出口测试）+ 回边 |
| **`while (n >= 0) { … }`** | **`bltz`** + 回边 |

**取反的出口测试是档位无关的**（`-O1`/`-O2`/`-Os` 都是 `blez`/`bltz`），但**回边不是**：`-O2`/`-O3` 用 likely 形式
`bgtzl`/`bgezl`（延迟槽里放循环自身的活），`-Os` 则是普通 `b` 且循环体被重构。

⇒ 循环条件表现为**取反的零测试**：`while (n > 0)` 以 `blez` 退出；回边用 likely 形式（与 [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) 一致）。

浮点上，形式本身携带源码信息：

| 源码 | 生成 |
| --- | --- |
| `if (a >= b) …` | `c.le.s`（**交换操作数**）+ `bc1t` |
| **`if (!(a < b)) …`** | **`bc1f`** —— 源码**取反**了条件 |
| `a < 0.0f ? -a : a` | `c.lt.s` + **`bc1tl`** + `neg.s` |

并且 **`sqrtf` 按名字被识别并内联**：

```c
extern float sqrtf(float);
float f(float a){ return sqrtf(a); }   /* → sqrt.s $f0,$f12，没有调用 */
```

**被内联的数学函数名是一张很短的封闭名单**：`sqrtf` → `sqrt.s`、`fabsf` → `abs.s`；其余试过的 libm 名
（`sinf`、`cosf`、`floorf`、`copysignf`、`fminf`、`powf` …）都是普通的**尾调用**（`j sinf`，[L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2)）。
likely 分支的拼写是 `bgtzl`/`bgezl`/`bltzl`/`blezl` 与 `bc1tl`/`bc1fl`。

**T2**｜源码锚点：后端的分支与 `sqrtf` 模式（未从出厂树读到行号）｜常量：`blez`、`bc1f`、`sqrt.s`｜
falsifies：「零比较总是物化或总是同一种分支」与「`sqrtf` 是 libm 调用」。
**杠杆**：目标里 `bc1f` ⇒ 源码**取反**了浮点条件；REGIMM 分支 ⇒ 是控制流的零测试而不是值；`sqrt.s` ⇒ 源码里有 `sqrtf`。

---

## L-EE-052 · 没有延迟 `nop`——浮点顺序完全由调度决定

| 源码 | `-O2` 生成 |
| --- | --- |
| `float f(float *p, float *q){ return *p + *q; }` | `l.s` ; `l.s` ; `j $31` ; **`add.s`**（在延迟槽里） |
| `int f(float *p){ return (int)*p; }` | `l.s` ; **`cvt.w.s` 紧跟** ; `j $31` ; `mfc1` |
| `float f(float *p){ return *p; }` | `j $31` ; **`l.s`**（在延迟槽里） |
| `float x = *p; return x > 0.0f;` | `l.s` ; `mtc1` ; `c.lt.s` ; `bc1t` |

**在 `-O1`/`-O2`/`-Os` × 5 种浮点形状下统计 `nop`，全部为 0。** 本编译器**不**为 COP1 的装载、移动、比较做填充。

结论对匹配有实际意义：**浮点指令顺序完全由优化与调度决定**，绝不由延迟填充决定。所以**不要去找「缺的 `nop`」**——
顺序差异必须用**源码形状**的杠杆解释（见 [FIELD-GUIDE](FIELD-GUIDE.md)）。

同一次测量还显示这个顺序有多自由：`p[0]*p[1] + p[2]*p[3]` 的四次装载被重排成偏移 **0, 4, 12, 8**；
浮点累加循环在 `-O2`（`mtc1 $0,$f1`）与 `-Os`（`mtc1 $0,$f0` + `mov.s $f1,$f0`）顺序不同。

**T3**（否定性知识：**「不存在」本身就是结论**）｜源码锚点：该 port 的调度描述（未从出厂树读到行号）｜常量：`l.s`、`mfc1`｜
falsifies：「浮点装载与其首次使用之间应当出现 load-delay 或 COP1-latency `nop`」。
**杠杆**：浮点序列顺序不同 ⇒ 这是**源码形状**的信号；候选里多出的 `nop` 另有来源，去查延迟槽规则（[L-EE-009](LAWS.md#l-ee-009--the-delay-slot-is-filled-the-leftover-nop-is-the-function-ending-jr-ra)）。

---

## L-EE-053 · 复制把硬寄存器偏好记在「全局伪寄存器」那一侧

`set_preference(dest, src)` 对每次 store 运行，方向决定归属：dest 是硬寄存器、src 是全局伪寄存器 ⇒ 偏好记在 **src** 的 allocno；
反之记在 **dest** 的 allocno。会先查 `reg_renumber`，所以被局部着色的伪寄存器贡献的是它的**硬寄存器**，不是伪寄存器号。

实测（`func_001d4b88`，`-Os -fno-thread-jumps`，effect-diff）：842 次可解码调用、84 次改变了掩码；allocno 2 得到 `{5}`（来自 `$a1`）；
allocno 24 得到 `{13,14}`——`$t5/$t6` 是**目的侧**的硬寄存器，位却记在源 allocno 上；allocno 13/11 得到 `{15}`（`$t7`）。
返回点差分与 prune 入口快照一致 ⇒ 方向是**观测**到的，不是重放出来的。

**T2**｜源码锚点 `global.c:1615`（出厂解析到 `global.c:1967`）｜二进制锚点 `set_preference @ 0x081ae780`｜
falsifies：「偏好只来自形参 ABI home 或同向复制」。
**杠杆**：追 effect-diff，不要重放源码；`reg_renumber` 可能让它指向源码里根本没出现过的寄存器。

## L-EE-054 · 排序前先剪枝：冲突、固定、跨调用的调用者保存、类外寄存器都会被去掉

`prune_preferences` 在 `allocno_order` 排好序之后、第一次 `find_reg` 之前，按优先级**从高到低**对每个 allocno：
去掉 `hard_reg_conflicts`；去掉 `fixed_reg_set`，跨调用（`calls_crossed>0`）时再去掉 `call_used_reg_set`；
去掉类外寄存器；空了就恢复整类重试；并由仍等待分配的冲突 allocno 填 `regs_someone_prefers`。
dump 的 `;; N preferences:` 是**剪枝后**打印的，所以它显示的是结果列表。

实测（同一函数）：expand 改变 **83** 个 allocno 的偏好掩码，prune 改变 **112** 个；6 个没拿到寄存器的 allocno 里，
4 个只带调用者保存偏好（`{5}`/`{13,14}`/`{15}`，`calls_crossed` 2–30）且剪枝后**全空**；另外 2 个（allocno 12/9）本就无偏好——纯压力。

**T2**｜源码锚点 `global.c:903`（出厂解析到 `global.c:1236`）｜二进制锚点 `prune_preferences @ 0x081ac580`｜
falsifies：「dump 里打印的偏好列表就是选择规则看到的列表」。
**杠杆**：先判断偏好是否活过剪枝，再怀疑选择规则；调用者保存偏好扛不过调用，要缩短活跃期或挪走复制。

---

## 仍未解决

* `$L` 计数器精确公式（多标签函数）。
* ~~EE 构建的 `FIRST_PSEUDO_REGISTER`~~ —— **已结清**：`ALL_REGS` 有 **140 个成员**，第一个伪寄存器是 **144**
  （72–75 保留），从活 `cc1` 读出（[L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)）。
* **着色已部分建模。** [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer) 用实测出的候选/选择规则复现留出集 **46.5%** 的决策（此前启发式 34.3%、按 mainline 写的两趟重放 9.1%）；把动态冲突集换成真值后同一规则达 **82.7%** ⇒ 剩余误差主要是**级联**，不是单次判断错。
  [L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect) 解释了为什么照搬 mainline 不行：出厂的 `find_reg` 带 `losers` 与三个标志、并按重试阶梯调用（`alt_regs_p` 在切换）。
  下一步：钉住**处理顺序**（`allocno_compare`）与阶梯的精确语义。