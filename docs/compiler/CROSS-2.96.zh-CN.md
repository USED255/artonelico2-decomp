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
| 帧构成与保存槽计数 | ✅ 同一形状（未逐值重标定） |

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
