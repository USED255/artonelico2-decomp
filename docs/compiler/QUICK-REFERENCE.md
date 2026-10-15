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

## In the instruction stream

| You see | Law |
| --- | --- |
| `li $r,N-1` … `addu $r,$r,-1` … `bgez` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-and-are-not-unrolled) — a constant-trip loop, counted down |
| `blez` guard … `addu $r,$r,-1` … `bne $r,$0` | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-and-are-not-unrolled) — a variable-trip loop, also counted down |
| the loop body is repeated | [L-EE-025](LAWS.md#l-ee-025--loops-count-down-and-are-not-unrolled) — `-funroll-loops` or a hand-unrolled source; `-O2`/`-O3` never unroll |
| the target has a helper expanded, yours emits `jal` | [L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined) — only `inline` is inlined at these flags |
| `andi` before the compare | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) — a narrow **unsigned** type |
| `sll` + `sra` before the compare | [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) — a narrow **signed** type |
| `sltu`/`beqz` then `lw` + `jr $reg` | [L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count) — a dense switch became a table |
| `lui %hi(sym)` where the target reads a bare symbol | [L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g) and [L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss) — gp_rel needs a definition **here** in `.sdata`/`.sbss` |
| `lwc1` loading a float | [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero) on 3.2; on 2.96 check [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) |
| `li` + `div`, or `jal __divdi3` / `__muldi3` | [L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc) — a non-power-of-two constant divisor, or a source using `long long` |
| `jal dpadd` / `dpmul` / `dpcmp` | [L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float) — the source uses `double`; there is no `add.d` in this build |
| `lui`/`ori` then `mtc1` | [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) (2.96 materialises every float inline) |
| 12-byte functions are 16 bytes apart | [L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4) — 8-byte alignment by default |

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
