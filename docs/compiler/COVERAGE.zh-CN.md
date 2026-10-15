# 覆盖率 —— 这本手册解释了一个二进制的多少

编译器行为手册只有在**足够完整**、能覆盖你实际看到的代码时才有用。这是**可测量**的主张，不是印象：
取一份反汇编，收集助记符，问「手册在哪里提到过它」。剩下的会自己分类。

```sh
# 项目自带的 objdump 直接管道进来
mips-ps2-decompals-objdump -d prog.elf | python3 tools/compiler/ee-gcc-coverage.py --asm -

# 汇编清单，或直接给 ELF
python3 tools/compiler/ee-gcc-coverage.py --asm func.s
python3 tools/compiler/ee-gcc-coverage.py --elf prog.elf

python3 tools/compiler/ee-gcc-coverage.py --selftest
```

工具给出三个数字与两张表：

| | 含义 |
| --- | --- |
| **explained by a rule** | 该助记符在 `docs/compiler/` 里被点名，**并且**编译器能从 C 发出它 |
| **assembly-only** | 编译器**不可能**从 C 发出它，所以它来自手写汇编 |
| **unexplained** | 两者都不是 —— 这才是手册真正的缺口 |

**分类在「是否被提到」之前**，这是有意的：在讲内联汇编的句子里点名 `mthi`，**不能**把它变成「已解释」。
（本工具早期版本正是这么做的，把自己的覆盖率**虚报了 1.3 个百分点**；下面是修正后的口径。）

`OTHER` 是最有意义的数字：它是手册**自己的待办列表**，而且**可以被压到零**。
`ASM_ONLY` 不是缺口，而是一个**结论**——见下。

## 为什么 `ASM_ONLY` 是结论而不是缺口

[L-EE-048](LAWS.md#l-ee-048--cop2vu0-instructions-cannot-come-from-c) 用实测证明：本编译器**不会从 C 生成任何 COP2/VU0 代码**——
`mode(V4SI)`/`mode(V4SF)` 的装载与存储用的是通用寄存器里的 `lq`/`sq`，向量算术与按值返回向量**是编译错误**，
通往 `lqc2`/`sqc2` 的唯一路径是内联汇编。**MMI 打包运算**同理：`mode(V8HI)`/`mode(V16QI)`/`mode(V4SI)` 的值
只用 `lq`/`sq` 搬运。特权指令（`syscall`、`sync`、`cache`、`mfc0`、陷阱指令）**没有任何内建**——
这个编译器里没有 `__builtin_ee_*`。

所以当工具把一条指令判为 `ASM_ONLY`，它给的是**可执行的结论**：**二进制里的那片区域在原始源码中是汇编写的，
纯 C 重建不可能匹配。**诊断流程见 [DIAGNOSTICS](DIAGNOSTICS.md) §5：要么以**内联汇编**承载，要么把该函数放一边。

## 分类表

`ASM_ONLY` 覆盖三个家族：

* **COP2 / VU0** —— `lqc2`、`sqc2`、`qmfc2`、`qmtc2`、`cfc2`、`ctc2` 以及整个 `v*` 宏模式集
  （`vadd`、`vmul`、`vopmula`、`vftoi4` …）；
* **MMI 打包运算** —— `padd*`、`psub*`、`pmax*`、`pmin*`、`pcpy*`、`pext*`、`pand`/`por`/`pnor`、
  `qfsrv`、`mtsab`，以及第二个乘除单元（`mult1`、`div1`、`mflo1`、`mthi1` …）；
* **特权/系统** —— `syscall`、`sync`、`cache`、`pref`、`mfc0`/`mtc0`、`tlb*`、`eret`、陷阱指令，
  以及 HI/LO 与 COP1 控制寄存器写入（`mthi`、`mtlo`、`ctc1`）。

注意 `mult1` 需要小心：**第二个乘法器本身是 C 可达的**（[L-EE-049](LAWS.md#l-ee-049--variable-shifts-negation-float-compare--and-the-second-multiplier)——`-O2`/`-O3` 下调度器在乘法可重叠时使用它），
而它的 HI/LO 伙伴 `mflo1`/`mthi1` 不是。工具是**按助记符**分类的，所以把它的输出当作**起点**；
当一个助记符跨越这条线时，以 law 为准。

## 这个方法找到了什么

在编写本手册的过程中持续运行该审计，参考二进制（一个 9 MB 的 `.text`）上的 `OTHER` 已被压到**零**：
其中每一种助记符现在要么有规则解释，要么被归类为「只能来自汇编」。手册剩下的工作是**深度**而不是广度——
但**方法本身才是重点**，它在你的二进制上同样可用：

```sh
mips-ps2-decompals-objdump -d your.elf | python3 tools/compiler/ee-gcc-coverage.py --asm -
```

如果你的 `OTHER` 非空，那就是一个**值得报告的发现**：要么手册缺一条规则，要么工具里的 `classify()` 缺一个家族。

## 覆盖率不等于正确性

本页测量的是**广度**：一条指令的来源是否被解释。它对「某个重建是否匹配」**什么也没说**。
后者在别处：症状优先的 [QUICK-REFERENCE](QUICK-REFERENCE.md)、[LAWS](LAWS.md) 里的杠杆表、
[PASSES](PASSES.md) 的逐 pass 视角；而主张的**可执行**那一半在夹具套件里
（`tools/compiler/ee-gcc-observe.py --selftest`、`--matrix`）。
