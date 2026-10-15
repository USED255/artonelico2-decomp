# 速查：看到什么形状 → 对应哪条 law

[English](QUICK-REFERENCE.md) · [手册索引](README.md) · [laws](LAWS.zh-CN.md) · [诊断](DIAGNOSTICS.zh-CN.md)

从眼前的形状出发，而不是从 law 列表出发。

## 序言与帧

| 你看到的 | 对应 |
| --- | --- |
| `.frame $sp,N` **且**保存了 `$fp` | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) —— 那个 `$fp` 是第 10 个被调用者保存寄存器，不是帧指针 |
| `.frame $fp,N` | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) —— 源码里有 `alloca`/VLA，或用了 `-fno-omit-frame-pointer` |
| 同样保存槽下，目标帧**正好大 16 字节** | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) |
| 你在数保存槽 | [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) —— 每个 8 B，上限 10 |
| 保存超过 10 个值但帧不再涨 | [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) —— 多出的进 `vars` |

## 指令流

| 你看到的 | 对应 |
| --- | --- |
| `li $r,N-1` … `addu $r,$r,-1` … `bgez` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-and-are-not-unrolled) —— 定次循环被倒计数 |
| `blez` 守卫 … `addu $r,$r,-1` … `bne $r,$0` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-and-are-not-unrolled) —— 变次循环同样倒计数 |
| 循环体被重复 | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-and-are-not-unrolled) —— `-funroll-loops` 或手工展开；`-O2`/`-O3` **不**展开 |
| 目标把助手展开了、你在发 `jal` | [L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined) —— 这些旗标下只有 `inline` 会被内联 |
| 比较前有 `andi` | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) —— 窄**无符号**类型 |
| 比较前有 `sll` + `sra` | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) —— 窄**有符号**类型 |
| `sltu`/`beqz` 后接 `lw` + `jr $reg` | [L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count) —— 稠密 switch 成了跳转表 |
| 目标读裸符号，你在用 `lui %hi(sym)` | [L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g) 与 [L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss) —— gp_rel 需要**在本单元**定义在 `.sdata`/`.sbss` |
| `lwc1` 装载浮点 | 3.2 见 [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)；2.96 见 [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) |
| `lui`/`ori` 后接 `mtc1` | [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) —— 2.96 把每个 float 内联构造 |
| 12 字节函数之间隔了 16 字节 | [L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4) —— 默认 8 字节对齐 |

## 数据

| 你看到的 | 对应 |
| --- | --- |
| 同一个 `.word` 每个函数各一份 | [L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function) —— 常量池按函数划分 |
| 两个函数共享一份 `.ascii` | [L-EE-027](LAWS.md#l-ee-027--strings-are-pooled-per-translation-unit-not-per-function) —— 字符串按编译单元合并，任何 `-O` 都合并 |
| 池顺序与你不一致 | [L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function) —— 按首次使用，不排序 |
| 在对象里找不到 `.rdata` 段 | [L-EE-027](LAWS.md#l-ee-027--strings-are-pooled-per-translation-unit-not-per-function) —— 对象里叫 `.rodata` |

## 流程

| 你看到的 | 对应 |
| --- | --- |
| 预期存在的 pass dump 不见了 | [L-EE-020](LAWS.md#l-ee-020--the-pass-pipeline-is--o-sensitive) —— 清单随 `-O` 变；且编译失败只留部分 dump |
| 指令一致但大小/偏移不符 | [L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)，再看 [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) |
| 源码是 CRI 中间件 | [CROSS-2.96.zh-CN.md](CROSS-2.96.zh-CN.md) —— 哪些规则可迁移、哪些不能 |
| 指令全对但寄存器不同 | [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer) —— 并先读它记录的两条**被否证**的杠杆，别重复发明 |
