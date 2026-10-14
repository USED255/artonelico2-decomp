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

---

## 仍未解决

* `$L` 计数器的精确公式（多标签函数未测）。
* 分类别着色重放：已记录的 26.1% 精度早于本次 EE `find_reg` 锚点。
* `freq` 需在真实多基本块函数上核对，而不只是读源码。
