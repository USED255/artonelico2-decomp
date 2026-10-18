# EE 调用约定（一页）

[English](ABI.md) · [手册索引](README.md) · [laws](LAWS.zh-CN.md) · [速查](QUICK-REFERENCE.zh-CN.md)

本机 `-O2 -G0` 实测；每行都链到带 receipt 的 law。

## 实参

| 实参 | 位置 |
| --- | --- |
| `int`、指针 | `$4`–`$11` —— **八个**整数寄存器（[L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots)） |
| `long long`、`double` | **各占一个 64 位 GPR**，接着 `$4`–`$11` 序列 —— **不是寄存器对** |
| `float` | `$f12`–`$f19` —— **独立**的八个额度 |
| 第 9 个整数/长整型实参起 | 入栈，**8 字节槽**：`0($sp)`、`8($sp)`…（按源码顺序） |
| 聚合 ≤ 8 字节 | **按值**入寄存器（[L-EE-030](LAWS.md#l-ee-030--aggregates-8-bytes-by-value-larger-by-reference-returns-use-a-hidden-pointer)） |
| 聚合 > 8 字节 | **按隐形引用** —— `$4` 里是地址 |
| 变参里的浮点 | 提升为 `double`，走**整数**序列（[L-EE-031](LAWS.md#l-ee-031--a-variadic-function-saves-the-argument-registers-and-calls-__builtin_va_start)） |

## 数据模型

| 类型 | 尺寸 | 说明 |
| --- | ---: | --- |
| `char` / `short` / `int` | 1 / 2 / 4 | |
| **`long`** | **8** | 默认 `-mlong64`；只有 `-mlong32` 才变 4（[L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long)） |
| `long long`、`double`、`long double` | 8 | `long double` 同 `double` |
| 指针 | **4** | 32 位地址 |

对齐 = 自身尺寸，故 8 字节成员按 8 对齐。

## 返回值

| 结果 | 位置 |
| --- | --- |
| `int`、指针 | `$2` |
| `long long`、`double` | `$2` —— 一个 64 位 GPR |
| `float` | `$f0` |
| 聚合 | **`$4` 里的隐藏指针**，使其余实参**整体后移一位**；指针在 `$2` 返回 |

## 帧与序言

| 量 | 规则 |
| --- | --- |
| 帧大小 | `round16(vars + 8 × regs + args)`（[L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers)） |
| 保存寄存器 | 每个 8 字节，上限 **10**（`$s0`–`$s7`、`$fp`、`$ra`） |
| 出参区 | `round16(8 × max(0, n − 8))`（[L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots)） |
| 帧指针 | 默认省略；`.frame $fp,…` 表示 `alloca`/VLA 或 `-fno-omit-frame-pointer`（[L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer)） |
| 变参序言 | 保存 `$5`–`$11` 中「具名参数之后」的部分，然后调 `__builtin_va_start`（[L-EE-031](LAWS.md#l-ee-031--a-variadic-function-saves-the-argument-registers-and-calls-__builtin_va_start)） |

## 算术

| 类型 | 生成 |
| --- | --- |
| `float` | COP1：`add.s`、`mul.s`、`cvt.s.w`、`trunc.w.s`（[L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float)） |
| `double` | **libgcc 软浮点调用**：`dpadd`、`dpsub`、`dpmul`、`dpdiv`、`dpcmp`、`dptoli`、`dptoul`、`dptofp`、`litodp`、`fptodp` —— **本构建里没有 `add.d`** |

## 反推目标函数签名

1. **若函数返回聚合，`$4` 是返回指针** —— 声明的实参要**往后数一位**（`S8 make8(int x)` 里 `x` 从 `$5` 读）。
2. 序言 `lw …, 0($4)` ⇒ 实参是 **> 8 字节聚合（按引用）**；`sd $4, 0($sp)` 后从栈读 ⇒ **≤ 8 字节（按值）**。
3. 一串 `sd` 从 `a1`–`t3` 存进连续 8 字节槽 ⇒ 该函数**是可变参数**；`jal __builtin_va_start` 可确证。
4. 函数体里有 `jal dpadd` 这类调用 ⇒ 源码在做 **`double`** 运算。
5. 帧比 `round16(vars + 8 × regs + args)` **正好大 16** ⇒ 怀疑帧指针（[L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer)）。

## 范围

`ee-gcc 3.2-ee-040921`、`-O2 -G0`。**未测**：union、位域、经变参传结构体、`va_list` 的确切布局、2.96 的 ABI——
两个编译器之间什么能迁移见 [CROSS-2.96.zh-CN.md](CROSS-2.96.zh-CN.md)。
