# 速查：看到什么形状 → 对应哪条 law

[English](QUICK-REFERENCE.md) · [手册索引](README.md) · [laws](LAWS.zh-CN.md) · [诊断](DIAGNOSTICS.zh-CN.md)

从眼前的形状出发，而不是从 law 列表出发。

## 序言与帧

| 你看到的 | 对应 |
| --- | --- |
| `.frame $sp,N` **且**保存了 `$fp` | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) —— 那个 `$fp` 是第 10 个被调用者保存寄存器，不是帧指针 |
| `.frame $fp,N` | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) —— 源码里有 `alloca`/VLA，或用了 `-fno-omit-frame-pointer` |
| 同样保存槽下，目标帧**正好大 16 字节** | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) |
| 序言里 `lw …,0($4)`，或函数返回结构体 | [L-EE-030](LAWS.md#l-ee-030--aggregates-8-bytes-by-value-larger-by-reference-returns-use-a-hidden-pointer) —— >8 字节聚合按引用；返回时 `$4` 是返回槽 |
| 实参被放在 `8($sp)` 而不是 `4($sp)` | [L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots) —— 第 9 个实参起按 8 字节槽入栈 |
| 你在数保存槽 | [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) —— 每个 8 B，上限 10 |
| 保存超过 10 个值但帧不再涨 | [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) —— 多出的进 `vars` |
| 目标延迟槽里是 `nop`、你的却是真指令 | [L-EE-009](LAWS.md#l-ee-009--the-delay-slot-is-filled-the-leftover-nop-is-the-function-ending-jr-ra) —— 延迟槽几乎总被填满；剩下的 `nop` 是函数末尾那一个 |
| 对一个既传给调用、又要在调用后使用的值，帧多出一个 8 B 槽 | [L-EE-015](LAWS.md#l-ee-015--the-outgoing-argument-area-doubles-as-storage-for-a-value-used-after-the-call) —— 经出参区传出的值会在调用后**从该槽重读** |
| 需要知道哪些寄存器可分配、调用者保存或被保留 | [L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes) —— 140 个硬寄存器、29 个类；可分配的被调用者保存 GPR 是 `$16`–`$23` 与 `$30` |
| 序言把 `a1`–`t3` 存进连续 8 字节槽 | [L-EE-031](LAWS.md#l-ee-031--a-variadic-function-saves-the-argument-registers-and-calls-__builtin_va_start) —— 该函数**是可变参数**；`jal __builtin_va_start` 可确证 |

## 指令流

| 你看到的 | 对应 |
| --- | --- |
| `li $r,N-1` … `addu $r,$r,-1` … `bgez` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled) —— 定次循环被倒计数 |
| `blez` 守卫 … `addu $r,$r,-1` … `bne $r,$0` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled) —— 变次循环同样倒计数 |
| 循环体被重复 | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled) —— `-funroll-loops` 或手工展开；`-O2`/`-O3` **不**展开 |
| 目标把助手展开了、你在发 `jal` | [L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined) —— 这些旗标下只有 `inline` 会被内联 |
| 比较前有 `andi` | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) —— 窄**无符号**类型 |
| 比较前有 `sll` + `sra` | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) —— 窄**有符号**类型 |
| `sltu`/`beqz` 后接 `lw` + `jr $reg` | [L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count) —— 稠密 switch 成了跳转表 |
| 目标读裸符号，你在用 `lui %hi(sym)` | [L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g) 与 [L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss) —— gp_rel 需要**在本单元**定义在 `.sdata`/`.sbss` |
| `lwc1` 装载浮点 | 3.2 见 [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)；2.96 见 [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) |
| 结构体字段用 `ld` / `sd` | [L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long) —— 该字段是 `long`/`long long`/`double`；这里 `long` 是 8 字节 |
| 本该是调用的地方出现裸 `j <外部符号>` | [L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2) —— 尾调用；`-O1` 下同一源码保留 `jal` + `j $31` |
| `li` + `div`，或 `jal __divdi3` / `__muldi3` | [L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc) —— 除的是非 2 的幂常量，或源码用了 `long long` |
| `jal dpadd` / `dpmul` / `dpcmp` | [L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float) —— 源码在用 `double`；本构建里没有 `add.d` |
| `lui`/`ori` 后接 `mtc1` | [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) —— 2.96 把每个 float 内联构造 |
| 12 字节函数之间隔了 16 字节 | [L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4) —— 默认 8 字节对齐 |
| 引用次数相同的两个值分配顺序不符预期 | [L-EE-001](LAWS.md#l-ee-001--global-allocation-order-is-allocno_compare) —— 优先级是 `(floor_log2(n_refs) * freq) / live_length * (10000 / REG_BR_PROB_BASE)` |
| 把 dump 报「已放置」的值当成了硬寄存器 | [L-EE-008](LAWS.md#l-ee-008--in-23greg-regs-to-allocate-is-the-local-allocation-residue-conflicts-lists-every-allocno) —— `regs to allocate` 是局部分配后的残留，`conflicts` 会列出**所有** allocno |
| 照 mainline 写的分配循环复现不出 dump 里的 disposition | [L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect) —— 出厂 `find_reg` 是两级 `alt_regs` 阶梯，决定通过**副作用**落地 |
| 字段读用 `lh`/`lbu` 而非 `lw`，或写之前出现负数 `li` 后接 `and`/`or` | [L-EE-035](LAWS.md#l-ee-035--bitfields-lsb-first-no-32-bit-straddling-narrowed-reads-and-masked-writes) —— 有符号位域读、或位域写 |
| 目标对同一地址读了两次、你只读一次 | [L-EE-037](LAWS.md#l-ee-037--volatile-is-visible-as-unmerged-accesses) —— 源码用了 `volatile` 指针（或两次读之间隔着调用） |
| 汇编写 `li`、目标却是 `addiu`/`ori`，或两段文本完全相同 | [L-EE-047](LAWS.md#l-ee-047--the-printed-mnemonic-is-an-alias--compare-encodings-not-spellings) —— 助记符是别名；要比编码 |
| 你按 `addu $d,$s,$0` 写拷贝，字节对不上 | [L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu) —— 每条 `move` 都是 64 位 `daddu $d,$s,$0`（funct 0x2d） |
| 循环回边是 `bnel`/`beql`/`bgtzl` | [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) —— likely 形式标记循环；前向分支保持普通形式 |
| 出现 `lwl`+`lwr`（或 `swl`+`swr`）对，或偏移非 4 倍数的 `lw` | [L-EE-044](LAWS.md#l-ee-044--unaligned-access-three-sources-and-ulwusw-do-not-exist-in-the-object) —— 非对齐访问；来自常量 `memcpy`、packed 成员或指针转换 |
| 目标用 `daddu`/`dsubu`/`dsll`/`dsra`/`dsrl`/`slt` | [L-EE-043](LAWS.md#l-ee-043--64-bit-integers-are-native-only-multiply-divide-and-modulo-call-out) —— 64 位整数类型（`long long` 或 8 字节 `long`）；只有乘/除/取模走调用 |
| 目标用 `l.s`/`s.s` 装载，或用 `ld`/`sd` 后接 `jal dp*` | [L-EE-042](LAWS.md#l-ee-042--float-lives-in-cop1-double-lives-in-general-registers) —— `float`（COP1）对 `double`（通用寄存器） |
| 目标用 `lq`/`sq` 搬 16 字节 | [L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return) —— 该处是 **128 位类型**（`mode(V4SI)`/`s128`），不是结构体 |
| 目标是 `ldl`/`ldr`-`sdl`/`sdr` 循环、你在调 `memcpy` | [L-EE-038](LAWS.md#l-ee-038--aggregate-copies-unrolled-to-32-bytes-then-an-inline-ldlldr-loop--never-memcpy) —— 超过 32 字节的拷贝是内联循环，**从不**调 `memcpy` |
| 目标通过寄存器调用（`jalr`）并跟着 `j $31` | [L-EE-039](LAWS.md#l-ee-039--indirect-calls-are-jalr-and-never-become-tail-jumps) —— 源码用了**函数指针**；间接调用永不变成尾跳转 |
| 你预期 `==` 是 `beq`，看到的却是 `xor`+`sltu`；或 `<=` 出现 `xori 0x1` | [L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions) —— 比较结果被**当成值**用时会被物化 |

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
| `;; N regs to allocate:` 行里没有 `(N)` 尺寸后缀 | [L-EE-002](LAWS.md#l-ee-002--allocnosize-is-in-words-and-prints-only-when-it-is-not-1) —— `size` 以**字**为单位，且仅在不为 1 时打印 |
| 按 mainline 标定的压力模型算错溢出数 | [L-EE-003](LAWS.md#l-ee-003--register-pressure-is-wider-on-ee-struct-allocno-is-144-b-hard_reg_set-is-192-bits) —— 这里 `struct allocno` 是 144 B、`HARD_REG_SET` 是 192 位 |
| 从 mainline `config/mips/mips.c` 取的规则复现不出 EE 的选码 | [L-EE-004](LAWS.md#l-ee-004--ee-ships-its-own-backend-configmipsmips5900c) —— EE 有自己独有的 `mips5900.c` |
| 用去重后的指令算频率代理会排错相邻对 | [L-EE-005](LAWS.md#l-ee-005--reg_freq-counts-every-register-occurrence-reg_freq_max-is-1000) —— `REG_FREQ` 按**每次出现**累加块频率（note 级） |
| 引用 mainline 行号解释 EE 行为、但那几行并不是那段代码 | [L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees) —— 行号**不跨树可移植** |
| 怀疑「一个 TU 放多个函数」会改变代码生成 | [L-EE-007](LAWS.md#l-ee-007--there-is-no-translation-unit-level-codegen-state-except-l-numbering) —— 除 `$L` 标签计数器外**没有** TU 级代码生成状态 |
| 你按 `-O2` 假设某单元的行为，而它其实是 `-Os` | [L-EE-034](LAWS.md#l-ee-034---os-is-this-projects-most-common-level-and-the-rules-hold-there) —— `-Os` 是本项目最多的档（687 文件），规则照搬即可 |
