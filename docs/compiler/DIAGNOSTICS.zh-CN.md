# 诊断流程 —— 从「diff 不对」走到「哪个 pass 负责」

[English](DIAGNOSTICS.md) · [手册索引](README.md) · [laws](LAWS.md) · [pass 地图](PASSES.md)

匹配 diff 只告诉你**字节不同**，不告诉你**是哪个决定造成的**。本页给出顺序：先做什么、再做什么，然后才允许猜。

## 1. 按决定的先后顺序读残差

前面的差异会制造后面所有的差异，所以按**决定发生的时间顺序**修：

1. **控制流** —— 分支结构、块顺序、出口位置；
2. **指令形状与条数** —— 同样的语句编出不同的指令；
3. **寄存器分配** —— 指令流对上了，寄存器不对；
4. **栈** —— 指令流与寄存器都对上了，栈偏移不对。

匹配率低于约 80% 的候选属于**结构性**差异。下面这些工具会准确地描述它，但帮不上什么忙——先改写 C。

## 2. 找出两种写法第一次分叉的 pass

两种写法都必须是对同一函数**讲得通**的源码。然后：

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1

python3 tools/compiler/ee-gcc-passdiff.py a.c b.c                       # 默认 3.2 -O2 -G0
python3 tools/compiler/ee-gcc-passdiff.py a.c b.c --cc ~/eecc/ee-gcc2.96/bin/ee-gcc
```

工具把两份都编译、逐 pass dump，并归一化跨两次编译无意义的部分（指令 uid 与伪寄存器号），报告第一份不同的 pass。退出码 0 = 每个 pass 都一样；1 = 找到分叉。

## 3. 按分叉的 pass 路由

第一个分叉的 pass 就指出了决策族。pass 名是 3.2 的；2.96 的对应名见 [PASSES.md](PASSES.md)。

| 第一次分叉 | 族 | 去看什么 |
| --- | --- | --- |
| `00.rtl`、`01.sibling` | 源码语义与表达式形状 | 类型与提升、语句结构、操作数顺序、`switch` vs `if` 链 |
| `03.jump`、`13.cfg`、`14.bp` | 控制流 | 分支条件、块布局、跳转表构造 |
| `09.cse`、`11.gcse`、`15.cse2` | 公共子表达式与 TU 上下文 | 别名、重复加载、TU 里能看见什么 |
| `12.loop` | 循环 | 归纳变量、不变量外提、循环权重 |
| `16.life` | 活跃区间 | 哪个值跨调用/跨块还活着 |
| `17.combine`、`18.ce`、`28.ce2` | 指令组合与条件执行 | 表达式怎么嵌套、哪个分支变成条件执行 |
| `19.regmove`、`21.range` | 移动与区间 | 操作数约束、拷贝链 |
| `22.lreg` | 局部分配 | 单块值、费用表、首选类 |
| `23.greg` | 全局分配 | 优先级顺序（[L-EE-001](LAWS.md#l-ee-001--global-allocation-order-is-allocno_compare)）、干扰、着色 |
| `24.postreload` | 重载与溢出 | 哪些值没拿到寄存器、溢出代码形状 |
| `20.sched`、`29.sched2` | 调度 | 语句分组、按源码行的依赖链 |
| `31.bbro`、`33.dbr` | 块重排与延迟槽 | 分支布局、槽里放什么 |

## 3.5 直接问编译器（真值）

当问题是「这个值被分到哪个寄存器」时，不要从反汇编猜——去问编译器。`global_alloc` 跑完后分配才定，
结果写进 **`reg_renumber`**（`short` 数组，`-1` 表示没拿到寄存器）。在 `global_alloc` 返回后的那条指令
（`toplev.c:3316` 调用它）下断点，然后读表：

```sh
# 先找到调用点
objdump -d "$CC1" | grep 'call .*<global_alloc>'
# 再在 gdb 里于返回地址处：
#   for i < max_allocno:  num = allocno_order[i]
#                         pseudo = allocno[num].reg
#                         chosen = reg_renumber[pseudo]
```

这样确立三件事（已在同一输入的 `-da` dump 上核对）：`allocno_order[i]` 是 **allocno 下标**、
`allocno[num].reg` 是**伪寄存器号**、`reg_renumber[pseudo]` 是决策。`-da` dump 打印的
（`;; Register dispositions: 169 in 2 …`）就是这张表，因此「从 dump 量出的」与「运行时读到的」一致——
这正是本手册里重放精度可信的前提。

注意：**逐次追 `find_reg` 不是办法**——它是两级阶梯、结果是副作用
（[L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect)），
长轨迹还会把调试器绊倒。分配后一个断点就能回答。

## 3.6 大小/偏移不符 ≠ 指令不符

如果指令一致、但 objdiff 报大小不同，或函数符号偏移不同，先查**对齐旗标**，别急着改源码。默认函数对齐是 **8 字节**，
12 字节函数会被填到 16；`-falign-functions=4` 降到 4 后去掉填充，而 **`-ffunction-sections` 单独做不到**
（[L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)）。
本项目用 `-O2 -falign-functions=4 -ffunction-sections`，所以每个函数段应当**正好等于函数大小**。

## 3.7 先读 `.frame` 的**首操作数**

`.frame $sp,80,$31` 与 `.frame $fp,96,$31` 的差别会贯穿整个函数：首操作数是**基址寄存器**。`$sp` 表示没有帧指针——
此时函数里被保存的 `$fp` 只是**第 10 个被调用者保存寄存器**，不是帧指针的证据。`$fp` 表示有真帧指针，来源是源码里的
`alloca`/VLA，或 `-fno-omit-frame-pointer`；后者会**多 16 字节**
（[L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer)）。
目标帧在同样保存槽下**正好大 16 字节**时，先查这一条。

## 4. 两个假信号

这两件事都会给出**干净、自信、错误**的答案：

1. **RTL 里的编译器内部指针**：`(note 0x… NOTE_INSN_BLOCK_BEG)` 内嵌一个每次运行都变的指针；不归一化就会在 `00.rtl` 报出并不存在的分叉。`ee-gcc-passdiff.py` 会归一化 note 与 barrier。
2. **源文件名被写进对象**：编译 `a.c` 与 `b.c` 会把两个不同的名字写进对象，于是即使 `.text` 完全相同，两个对象也会在字符串表差一个字节。工具会把两份源码都复制成同一个名字再编译，所以这种差异冒充不了代码差异。

## 5. 什么时候不要用模型

* 匹配率低于约 80%：结构问题，先改写 C；pass 报告是噪声。
* 两种写法**语义不同**：第一个分叉必然是 `00.rtl`，且最终对象不同——这是源码 bug，不是编译器决策。
* 报告 `00.rtl` 分叉但**最终对象相同**：差异被后面的 pass 消除了，两种写法等价，别再追。

## 6. 更深一层

* 决策规则本身在 [LAWS.md](LAWS.md)，每条带源码锚点与二进制锚点。
* 要核验**出厂**编译器在决策点到底怎么做，用 [`tools/compiler/ee-gcc-anchor.py`](../../tools/compiler/ee-gcc-anchor.py)：它把符号变成地址、源码行、结构布局或常量。
* 读 `24.postreload` 的输出要靠上面的归一化：`reload_out (SI) = (reg:SI 2 v0 [149])` 那一段是重载簿记，**不是**寄存器引用；把它当引用会虚高使用次数。

## 记录在案的标定

本流程最初建立时比较过 10 组「两种讲得通的写法」。有用的结论是：**第一分叉的 pass 本身不能决定任何事**；能决定的是最终对象是否不同、以及是否有后续 pass 重新收敛。上面的表负责缩小搜索范围，真正的判定仍然靠测量。
