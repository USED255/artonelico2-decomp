# Quick reference: what you see → which law

[简体中文](QUICK-REFERENCE.zh-CN.md) · [Handbook index](README.md) · [Laws](LAWS.md) · [Diagnostics](DIAGNOSTICS.md)

Start from the shape in front of you, not from the law list.

## In the prologue and the frame

| You see | Law |
| --- | --- |
| `.frame $sp,N` **and** a saved `$fp` | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) — that `$fp` is the tenth callee-saved register, not a frame pointer |
| `.frame $fp,N` | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) — `alloca`/VLA in the source, or `-fno-omit-frame-pointer` |
| the target frame is exactly 16 bytes larger with the same callee saves | [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) |
| `lw …,0($4)` in a prologue, or a structure-returning function | [L-EE-030](LAWS.md#l-ee-030--aggregates-8-bytes-by-value-larger-by-reference-returns-use-a-hidden-pointer) — >8-byte aggregates by reference, and `$4` becomes the return slot |
| an argument stored at `8($sp)` instead of `4($sp)` | [L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots) — stack arguments are 8-byte slots from the ninth argument |
| you are counting save slots | [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) — 8 B each, saturating at 10 |
| saving more than 10 values but the frame stops growing | [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers) — the extra values go to `vars` |
| the target has a `nop` in a delay slot where you have a real instruction | [L-EE-009](LAWS.md#l-ee-009--the-delay-slot-is-filled-the-leftover-nop-is-the-function-ending-jr-ra) — delay slots are almost always filled; the leftover `nop` is the function-end one |
| the frame grows one 8 B slot for a value that is also passed to a call | [L-EE-015](LAWS.md#l-ee-015--the-outgoing-argument-area-doubles-as-storage-for-a-value-used-after-the-call) — a value passed in the outgoing area is re-read from that slot after the call |
| you need to know which registers are allocatable, caller-saved or reserved | [L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes) — 140 hard registers in 29 classes; allocatable callee-saved GPRs are `$16`–`$23` and `$30` |
| a prologue stores `a1`–`t3` into consecutive 8-byte slots | [L-EE-031](LAWS.md#l-ee-031--a-variadic-function-saves-the-argument-registers-and-calls-__builtin_va_start) — the function is **variadic**; `jal __builtin_va_start` confirms it |

## In the instruction stream

| You see | Law |
| --- | --- |
| `li $r,N-1` … `addu $r,$r,-1` … `bgez` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled) — a constant-trip loop, counted down |
| `blez` guard … `addu $r,$r,-1` … `bne $r,$0` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled) — a variable-trip loop, also counted down |
| the loop body is repeated | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled) — `-funroll-loops` or a hand-unrolled source; `-O2`/`-O3` never unroll |
| the target has a helper expanded, yours emits `jal` | [L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined) — only `inline` is inlined at these flags |
| `andi` before the compare | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) — a narrow **unsigned** type |
| `sll` + `sra` before the compare | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) — a narrow **signed** type |
| `sltu`/`beqz` then `lw` + `jr $reg` | [L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count) — a dense switch became a table |
| `lui %hi(sym)` where the target reads a bare symbol | [L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g) and [L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss) — gp_rel needs a definition **here** in `.sdata`/`.sbss` |
| `lwc1` loading a float | [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero) on 3.2; on 2.96 check [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) |
| `ld` / `sd` on a struct field | [L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long) — the field is `long`/`long long`/`double`; `long` is 8 bytes here |
| a bare `j <external symbol>` where you expected a call | [L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2) — a tail call; at `-O1` the same source keeps `jal` + `j $31` |
| `li` + `div`, or `jal __divdi3` / `__muldi3` | [L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc) — a non-power-of-two constant divisor, or a source using `long long` |
| `jal dpadd` / `dpmul` / `dpcmp` | [L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float) — the source uses `double`; there is no `add.d` in this build |
| `lui`/`ori` then `mtc1` | [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) (2.96 materialises every float inline) |
| 12-byte functions are 16 bytes apart | [L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4) — 8-byte alignment by default |
| two values with equal reference counts allocate in an unexpected order | [L-EE-001](LAWS.md#l-ee-001--global-allocation-order-is-allocno_compare) — the priority is `(floor_log2(n_refs) * freq) / live_length * (10000 / REG_BR_PROB_BASE)` |
| a value the dump reports was placed is treated as a hard register | [L-EE-008](LAWS.md#l-ee-008--in-23greg-regs-to-allocate-is-the-local-allocation-residue-conflicts-lists-every-allocno) — `regs to allocate` is the residue after local allocation, `conflicts` lists every allocno |
| a port of mainline's allocation loop does not reproduce the recorded dispositions | [L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect) — the shipped `find_reg` is a two-step `alt_regs` ladder whose decision is a side effect |
| a field read uses `lh`/`lbu` instead of `lw`, or a write has a negative `li` before `and`/`or` | [L-EE-035](LAWS.md#l-ee-035--bitfields-lsb-first-no-32-bit-straddling-narrowed-reads-and-masked-writes) — signed bitfield read, or a bitfield write |
| the target loads the same address twice where you load it once | [L-EE-037](LAWS.md#l-ee-037--volatile-is-visible-as-unmerged-accesses) — the source used a `volatile` pointer (or a call sits between the reads) |
| the target has `sllv`/`srlv`/`negu`, `mov.s`/`neg.s`, or `mult1` | [L-EE-049](LAWS.md#l-ee-049--variable-shifts-negation-float-compare--and-the-second-multiplier) — ordinary C: register shifts, negation, float ops, and the second multiplier |
| the target contains `lqc2`/`sqc2`/`qmtc2`/`v*` | [L-EE-048](LAWS.md#l-ee-048--cop2vu0-instructions-cannot-come-from-c) — COP2/VU0 is **inline assembly**; no C type produces it |
| the assembly says `li` but the target has `addiu`/`ori`, or two streams look equal as text | [L-EE-047](LAWS.md#l-ee-047--the-printed-mnemonic-is-an-alias--compare-encodings-not-spellings) — mnemonics are aliases; compare encodings |
| you wrote `addu $d,$s,$0` for a copy and the bytes do not match | [L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu) — every `move` is the 64-bit `daddu $d,$s,$0` (funct 0x2d) |
| the loop back edge is `bnel`/`beql`/`bgtzl` | [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) — the likely form marks a loop; forward branches stay plain |
| an `lwl`+`lwr` (or `swl`+`swr`) pair, or a `lw` at a non-multiple-of-4 offset | [L-EE-044](LAWS.md#l-ee-044--unaligned-access-three-sources-and-ulwusw-do-not-exist-in-the-object) — unaligned access; from a constant `memcpy`, a packed member, or a pointer cast |
| the target uses `daddu`/`dsubu`/`dsll`/`dsra`/`dsrl`/`slt` | [L-EE-043](LAWS.md#l-ee-043--64-bit-integers-are-native-only-multiply-divide-and-modulo-call-out) — a 64-bit integer type (`long long` or the 8-byte `long`); only mul/div/mod call out |
| the target loads a value with `l.s`/`s.s`, or with `ld`/`sd` plus `jal dp*` | [L-EE-042](LAWS.md#l-ee-042--float-lives-in-cop1-double-lives-in-general-registers) — `float` (COP1) versus `double` (general registers) |
| the target moves 16 bytes with `lq`/`sq` | [L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return) — a 128-bit type (`mode(V4SI)`/`s128`), not a struct |
| the target has an `ldl`/`ldr`-`sdl`/`sdr` loop where you call `memcpy` | [L-EE-038](LAWS.md#l-ee-038--aggregate-copies-unrolled-to-32-bytes-then-an-inline-ldlldr-loop--never-memcpy) — copies above 32 bytes are inline loops; `memcpy` is never called |
| the target calls through a register (`jalr`) plus `j $31` | [L-EE-039](LAWS.md#l-ee-039--indirect-calls-are-jalr-and-never-become-tail-jumps) — the source used a **function pointer**; indirect calls never become tail jumps |
| you expected `beq`/`bne` for `==` but see `xor` + `sltu`, or `xori 0x1` for `<=` | [L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions) — comparisons used as values are materialised |

## In the data

| You see | Law |
| --- | --- |
| the same `.word` once per function | [L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function) — the constant pool is per function |
| two functions sharing one `.ascii` | [L-EE-027](LAWS.md#l-ee-027--strings-are-pooled-per-translation-unit-not-per-function) — strings are pooled per translation unit, at every `-O` |
| the pool order differs from yours | [L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function) — first-use order, not sorted |
| you cannot find a `.rdata` section in an object | [L-EE-027](LAWS.md#l-ee-027--strings-are-pooled-per-translation-unit-not-per-function) — the object calls it `.rodata` |

## In the process

| You see | Law |
| --- | --- |
| a pass dump you expected is missing | [L-EE-020](LAWS.md#l-ee-020--the-pass-pipeline-is--o-sensitive) — the inventory depends on `-O`, and a failed compile leaves a partial set |
| a size or offset mismatch while the instructions agree | [L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4), then [L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer) |
| the source is CRI middleware | [CROSS-2.96.md](CROSS-2.96.md) — which rules transfer and which do not |
| every instruction agrees but the registers do not | [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer) — and read its rejected levers before inventing your own |
| no `(N)` size suffix appears in the `;; N regs to allocate:` line | [L-EE-002](LAWS.md#l-ee-002--allocnosize-is-in-words-and-prints-only-when-it-is-not-1) — `size` is in words and is printed only when it is not 1 |
| a mainline-calibrated pressure model predicts the wrong spill count | [L-EE-003](LAWS.md#l-ee-003--register-pressure-is-wider-on-ee-struct-allocno-is-144-b-hard_reg_set-is-192-bits) — `struct allocno` is 144 B and `HARD_REG_SET` is 192 bits here |
| a rule taken from mainline `config/mips/mips.c` does not reproduce EE code selection | [L-EE-004](LAWS.md#l-ee-004--ee-ships-its-own-backend-configmipsmips5900c) — EE ships its own `mips5900.c`, which mainline does not have |
| a frequency proxy built from de-duplicated instructions mis-ranks adjacent pairs | [L-EE-005](LAWS.md#l-ee-005--reg_freq-counts-every-register-occurrence-reg_freq_max-is-1000) — `REG_FREQ` is accumulated per note, one block frequency per occurrence |
| a mainline line number is cited for an EE behaviour and the lines do not contain that code | [L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees) — line numbers are not portable between trees |
| you suspect a one-TU-many-functions build changes codegen | [L-EE-007](LAWS.md#l-ee-007--there-is-no-translation-unit-level-codegen-state-except-l-numbering) — there is no TU-level codegen state except the `$L` label counter |
| you are assuming `-O2` behaviour for a unit that was built with `-Os` | [L-EE-034](LAWS.md#l-ee-034---os-is-this-projects-most-common-level-and-the-rules-hold-there) — `-Os` is this project's most common level (687 files) and takes every rule as written |
