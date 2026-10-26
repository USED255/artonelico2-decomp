# 案例研究 2 —— 一个大函数：帧本身就是全部答案

[第一个案例](CASE-STUDY.md)攻的是一个小函数，帧多了 8 字节。**大函数不一样**：那里帧不是舍入误差，
而是**「源码同时让多少个值活着」的测量结果**——而「把代码整理干净」的直觉会把你**推离**目标。

本案例只用一个**合成函数**，所以下面每个数字都能复现，不需要任何游戏数据。

## 残差

把同一份算术写成两种拼法，读 `.frame`：

| 拼法 | frame | `vars` | `regs` |
| --- | ---: | ---: | ---: |
| **A** —— 先算 40 个局部变量，最后统一使用 | **208** | **128** | 10 |
| **B** —— 每个值算完立刻折叠并消费 | **32** | 0 | 3 |

结果完全相同，帧大小**相差 6.5 倍**，`-O2` 与 `-Os` 都一样。

用 [L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers) 核对算术：`frame = round16(vars + 8 × 保存的寄存器 + 传出实参区)`。
A 是 `128 + 8 × 10 = 208` ✓。⇒ 那 128 字节的 `vars` 区是 **16 个溢出值**，帧在告诉你：**源码有 16 个值同时活着**。

## 第一步 —— 先分解帧，再动任何代码

```sh
python3 tools/compiler/ee-gcc-spill-map.py --src A.c --flags="-O2 -G0"
```

```
frame=208 B  vars=128  regs=10 (8 B each)  args=0

vars 区（0..127）访问涉及的源码行：
  line  store  load  offsets / spilled variable names
     5      1     0  [0]   v1
     6      1     0  [4]   v2
     …
```

每次溢出都被溯回**定义它的那一行**——于是「帧太大」变成「这十六条语句各自引入了一个一直活着的值」。
这就是完整的诊断：**不需要猜 pass**。

> 这个工具是**第一步**是有意的。帧偏大只可能有三个归属——vars 区、保存的寄存器、传出实参区——
> 只有分解才能告诉你是哪一个。

## 第二步 —— 找出什么让这些值活着

最可疑的是「那些调用让值一直活着」，所以自然的改法是把每个 `sink(v)` 调用挪到定义 `v` 的下一行。
实测：**frame 208 → 208，`vars` 128 → 128。什么都没动。**

原因在源码里：这些值是被**最后那个求和**消费的。**活跃区间在「最后一次使用」结束**，把某次较早的使用提前毫无作用——
起决定作用的只有最后一次使用。

这个负结果值得记住：**大家最先想到的那个改法，恰好不是能改变数字的那个。**

## 第三步 —— 用真正有效的杠杆

要改变帧，必须改变**最后一次使用的位置**。把每个值在定义处折叠进累加器，算术完全等价：

```c
/* A：批量 */                      /* B：折叠 */
int v1 = p[0] + 0;                 int s = 0;
…                                  …
sink(v1);                          { int v = p[0] + 0; sink(v); s += v; }
s += v1;
```

| | frame | `vars` | `regs` |
| --- | ---: | ---: | ---: |
| A（批量） | 208 | 128 | 10 |
| B（折叠） | 32 | 0 | 3 |

## 要点：**匹配不是优化**

在一个有编译器思维的人眼里，一切「更干净」的方向都从 A 指向 B。当**目标**是 A 时，这个方向恰恰是错的：
帧是 208 字节的目标说明源码**同时让十六个值活着**，而把它们折进累加器的重建**永远匹配不上**——
它离目标有 **176 字节的帧**，这不是局部小改能找回来的。

所以诊断的方向是：

* 候选帧**大于**目标 ⇒ 你让一些值活得比源码更久；把某次使用前移、或拆开表达式来缩短活跃区间。
* 候选帧**小于**目标 ⇒ 源码让一些值活着而你把它折掉了；去找**批量模式**（先算很多、再一起用）、
  **跨调用存活的值**，或源码里声明得早、用得晚的变量。

帧是一枚**结构指纹**。把它当作关于**源码**的证据来读，而不是当作要最小化的分数。

## 复现这些数字

两种拼法都是手册自带套件里的**可执行夹具**，所以本案例的核心主张**每次运行都会被检查**：

```sh
python3 tools/compiler/ee-gcc-observe.py --selftest          # 含两条帧断言
python3 tools/compiler/ee-gcc-observe.py --src A.c --flags="-O2 -G0"
python3 tools/compiler/ee-gcc-spill-map.py --src A.c --flags="-O2 -G0"
```

相关 law：[L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers)（帧的组成）、[L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality)（传出实参区）、
[L-EE-015](LAWS.md#l-ee-015--the-outgoing-argument-area-doubles-as-storage-for-a-value-used-after-the-call)（既传出又保留的值）、[L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled)/[L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function)
（`-O1` 与 `-Os` 的帧行为）、[L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer)（分配器会选哪个寄存器）。
