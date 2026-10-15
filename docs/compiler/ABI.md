# The EE calling convention, on one page

[简体中文](ABI.zh-CN.md) · [Handbook index](README.md) · [Laws](LAWS.md) · [Quick reference](QUICK-REFERENCE.md)

Measured on this machine at `-O2 -G0`; each row links to the law with its receipt.

## Arguments

| argument | travels in |
| --- | --- |
| `int`, pointer | `$4`–`$11` — **eight** integer registers ([L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots)) |
| `long long`, `double` | one **64-bit GPR** each, continuing the same `$4`–`$11` sequence — not a register pair |
| `float` | `$f12`–`$f19` — a **separate** budget of eight |
| the 9th integer/long argument onward | the stack, **8-byte slots** at `0($sp)`, `8($sp)`, … in source order |
| aggregate ≤ 8 bytes | **by value** in a register ([L-EE-030](LAWS.md#l-ee-030--aggregates-8-bytes-by-value-larger-by-reference-returns-use-a-hidden-pointer)) |
| aggregate > 8 bytes | **by invisible reference** — the pointer is in `$4` |
| variadic floats/doubles | promoted to `double` and passed in the **integer** sequence ([L-EE-031](LAWS.md#l-ee-031--a-variadic-function-saves-the-argument-registers-and-calls-__builtin_va_start)) |

## Returns

| result | travels in |
| --- | --- |
| `int`, pointer | `$2` |
| `long long`, `double` | `$2` — one 64-bit GPR |
| `float` | `$f0` |
| aggregate | a **hidden pointer in `$4`**, which shifts every other argument one slot; the pointer comes back in `$2` |

## Frame and prologue

| quantity | rule |
| --- | --- |
| frame size | `round16(vars + 8 × regs + args)` ([L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers)) |
| saved registers | 8 bytes each, saturating at **10** (`$s0`–`$s7`, `$fp`, `$ra`) |
| outgoing args | `round16(8 × max(0, n − 8))` ([L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots)) |
| frame pointer | omitted by default; `.frame $fp,…` means `alloca`/VLA or `-fno-omit-frame-pointer` ([L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer)) |
| variadic prologue | saves `$5`–`$11` minus the named parameters, then calls `__builtin_va_start` ([L-EE-031](LAWS.md#l-ee-031--a-variadic-function-saves-the-argument-registers-and-calls-__builtin_va_start)) |

## Arithmetic

| type | code |
| --- | --- |
| `float` | COP1: `add.s`, `mul.s`, `cvt.s.w`, `trunc.w.s` ([L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float)) |
| `double` | **libgcc soft-float calls**: `dpadd`, `dpsub`, `dpmul`, `dpdiv`, `dpcmp`, `dptoli`, `dptoul`, `dptofp`, `litodp`, `fptodp` — there is **no `add.d`** in this build |

## Reading a target signature

1. **If the function returns an aggregate, `$4` is the return pointer** — count the declared arguments one slot
   later (`S8 make8(int x)` reads `x` from `$5`).
2. `lw …, 0($4)` in the prologue ⇒ the argument is an aggregate **> 8 bytes, by reference**. `sd $4, 0($sp)`
   followed by reads from the stack ⇒ an aggregate **≤ 8 bytes, by value**.
3. A run of `sd` from `a1`–`t3` into consecutive 8-byte slots ⇒ the function is **variadic**; `jal
   __builtin_va_start` confirms it.
4. `jal dpadd`-style calls inside the body ⇒ the source is doing **`double`** arithmetic.
5. Frame larger than `round16(vars + 8 × regs + args)` by exactly 16 ⇒ suspect a frame pointer
   ([L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer)).

## Scope

`ee-gcc 3.2-ee-040921` at `-O2 -G0`. Unions, bitfields, structure arguments passed through varargs, the exact
`va_list` layout, and the 2.96 compiler's ABI were **not** measured — see [CROSS-2.96.md](CROSS-2.96.md) for
what does and does not transfer between the two compilers.
