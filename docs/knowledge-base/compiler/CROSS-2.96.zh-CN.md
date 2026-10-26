# 这套手册能迁移到 2.96 编译器吗？

[English](CROSS-2.96.md) · [手册索引](README.md) · [laws](LAWS.zh-CN.md) · [pass 地图](PASSES.zh-CN.md)

本项目用**两个**编译器：游戏代码用 `ee-gcc 3.2-ee-040921`，CRI 中间件用 `ee-gcc 2.96-ee-001003-1`。
手册的规则是在 3.2 上量的，所以「这条能用在 CRI 函数上吗」要**逐条**回答。下面全部用同一组夹具与旗标（`-O2 -G0`）在 2.96 上回测，
并且看的是**对象码**——2.96 的汇编里写的是 `li.s` 伪指令，会被误导。

## 可迁移的

| 规则 | 在 2.96 上 |
| --- | --- |
| 窄类型比较习语：窄无符号先 `andi`、窄有符号先 `sll`+`sra`（[L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality)） | ✅ 一致 |
| switch 阈值：6 路稠密生成表，4 路与稀疏只生成分支链（[L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count)） | ✅ 一致 |
| `-G0` 下全局用 `lui %hi` / `%lo` 绝对寻址（[L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g)） | ✅ 一致 |
| 双精度常量：`0.0` 用 `move`；低位 32 位为 0 用 `li`+`dsll32`；否则走池（[L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)） | ✅ 一致 |
| 帧构成与保存槽计数（[L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers)） | ✅ **逐值一致**：k = 2/4/6/8/10/12/16/20 对应帧 32/48/64/80/96/96/112/128，`regs=` 4/6/8/10/10/10/10/10 |
| 64 位整数运算内联：`daddu`/`dsubu`/`dsll`/`dsra`；64 位乘除走 libgcc（[L-EE-043](LAWS.md#l-ee-043--64-bit-integers-are-native-only-multiply-divide-and-modulo-call-out)） | ✅ 相同 |
| `float` 在 COP1、`double` 在通用寄存器（[L-EE-042](LAWS.md#l-ee-042--float-lives-in-cop1-double-lives-in-general-registers)） | ✅ 相同 |
| 循环回边用 likely 形式（[L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not)） | ✅ 相同 |
| 尾调用是指向目标的 `j`（[L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2)） | ✅ 相同 |
| 相等习语 `xor` + `sltu …,1`（[L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)） | ✅ 相同 |
| `sqrtf` 内联为 `sqrt.s`（[L-EE-051](LAWS.md#l-ee-051--zero-comparisons-float-branches-and-an-inlined-sqrtf)） | ✅ 相同 |
| 128 位容器用 `lq`/`sq` 搬（[L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return)） | ✅ 形状相同；2.96 选的寄存器不同 |
| 默认函数对齐 8 字节（[L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)） | ✅ 同为 `2**3` |

## **不能**迁移的

**浮点常量**。[L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero) 说「非零 float 走常量池」——
这在 **3.2** 成立，在 **2.96** **不成立**：

| `float f(void) { return V; }` | 3.2 | 2.96 |
| --- | --- | --- |
| `0.0f` | `mtc1`（零寄存器） | `mtc1` |
| `0.5f`、`1.0f`、`2.5f`、`-1.0f`、`100.0f` | `lui addiu lwc1`（**池**） | `lui mtc1`（**内联**；低位 16 位为 0） |
| `0.01f`、`3.14f`、`123.456f`、`1e30f` | **池** | `lui ori mtc1`（**内联**） |

⇒ 在 2.96 上浮点**一律内联**，低位 16 位只决定要不要补一条 `ori` —— 见 [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool)。
改浮点常量写法之前，先确认那段源码由哪个编译器构建。

**COP1 累加器。** 3.2 上「一个表达式求和 ≥2 个乘积」会用 COP1 累加器（[L-EE-050](LAWS.md#l-ee-050--the-cop1-accumulator-a-sum-of-products-uses-mulasmadds)）；
2.96 上同一表达式就是普通的乘法加法：

| `float f(float a,float b,float c,float d){ return a*b + c*d; }` | 生成 |
| --- | --- |
| 3.2 | `mula.s $f12,$f13` + `madd.s $f0,$f14,$f15` |
| 2.96 | `mul.s` + `mul.s` + `add.s` —— **没有累加器** |

**16 字节结构体拷贝。** 3.2 展开成 32 位对；2.96 用非对齐对搬 64 位半：

| `struct S{int a,b,c,d;}; void f(struct S *d, struct S *s){ *d = *s; }` | 生成 |
| --- | --- |
| 3.2 | `lw`/`sw` 序列（[L-EE-038](LAWS.md#l-ee-038--aggregate-copies-unrolled-to-32-bytes-then-an-inline-ldlldr-loop--never-memcpy)） |
| 2.96 | **`ldl`/`ldr` + `sdl`/`sdr`** 对 |

**2.96 上根本不存在向量类型。** `mode(V4SI)` 与 `mode(V4SF)` 直接被拒（`no data type`），
所以所有 128 位规则（[L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return)）以及整个 COP2/VU0 的论证（[L-EE-048](LAWS.md#l-ee-048--cop2vu0-instructions-cannot-come-from-c)）
都是**只属于 3.2** 的事。

### 两个值得记住的指纹

本项目**两个编译器都在用**——3.2 编游戏、2.96 编 CRI 中间件——所以这两个形状能告诉你某函数是谁编的：

* 指令流里出现 `mula.s`/`madd.s`/`msub.s` ⇒ **3.2**（2.96 从不发出累加器）；
* 16 字节拷贝是 `ldl`/`ldr` 对 ⇒ **2.96**（该尺寸下 3.2 用 `lw`/`sw`）；
* `mode(V4SI)`/`mode(V4SF)` 的源码能编过 ⇒ **3.2**。

**ABI 不在差异之列。** 初看第 9 个实参时以为有差异——那是**测量伪影**（3.2 会先用 `addu $15,$sp,0`
物化栈地址再装载，看起来与 2.96 的直接 `lw` 不同）。认真核对后，栈布局两边**完全一致**，
所以 [ABI](ABI.md) 里的每条约定对中间件与游戏代码**同样适用**。

## 复现

`tools/compiler/ee-gcc-observe.py` 可以指定编译器，而它的夹具断言的是 **3.2** 行为，所以拿它跑 2.96 本身就是演示：

```sh
python3 tools/compiler/ee-gcc-observe.py --cc ~/eecc/ee-gcc2.96/bin/ee-gcc --selftest
# float-pool 在 2.96 上失败：该值被内联构造
```

看对象码的对照：

```sh
for cc in ~/eecc/ee-gcc3.2-040921/bin/ee-gcc ~/eecc/ee-gcc2.96/bin/ee-gcc; do
  "$cc" -O2 -G0 -c -o /tmp/x.o - <<<'float f(void){return 0.5f;}'   # 然后反汇编
done
```

## 范围

两个编译器、`-O2 -G0`、合成夹具。2.96 那几行是 `T3`（只有行为证据）：两个后端都没有源码，也没有可定位决策点的二进制锚点。
