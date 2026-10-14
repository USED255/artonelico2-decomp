# Compiler laws — ee-gcc 3.2-ee-040921

[简体中文](LAWS.zh-CN.md) · [Handbook index](README.md) · [Pass map](PASSES.md) · machine-readable index: [`laws.json`](laws.json)

This page records **what the compiler does**, not what to do about it. The levers that follow from
each law live in [FIELD-GUIDE.md](FIELD-GUIDE.md); the workflow that finds the owning pass lives in
[DIAGNOSTICS.md](DIAGNOSTICS.md).

## How to read an entry

| Field | Meaning |
| --- | --- |
| **Tier** | `T1` source rule **+** factory-binary anchor **+** matching behaviour; `T2` source rule **or** binary anchor, plus behaviour; `T3` behaviour evidence only |
| **Source anchor** | the mainline file and line that states the rule. Mainline is a *semantic* reference: line numbers do **not** transfer (see [L-EE-006](#l-ee-006--line-numbers-are-not-portable-between-trees)) |
| **Binary anchor** | the symbol and address inside the shipped `cc1`, read with [`tools/compiler/ee-gcc-anchor.py`](../../tools/compiler/ee-gcc-anchor.py) |
| **Receipt** | the measurement behind the law, with its scope |
| **Falsifies** | a claim this law replaced. Almost every law here replaced a plausible, wrong belief — reading only the conclusions would hide that |
| **Scope** | what was actually covered. There are no impossibility claims on this page: a closed lever is recorded with the space that was covered |

**The rule that matters most:** cite the line number `addr2line` reports for the **shipped** `cc1`,
and keep the mainline line only as a cross-reference with its measured offset.

Mainline reference: **gcc-3.2.3** (`sha256 9229434c…`). Comparing the same functions against
gcc-3.2.2 changes the offsets by at most one line, so the drift measured in L-EE-006 is the EE
snapshot's, not a point-release artefact.

---

## L-EE-001 · Global allocation order is `allocno_compare`

```
pri = (int)( (floor_log2(n_refs) * freq) / live_length * (10000 / REG_FREQ_MAX) * size )
```

`floor_log2(n_refs)`, `freq`, `live_length` and `size` all live in `struct allocno`; the factor
`10000 / REG_FREQ_MAX` is **10** (`REG_FREQ_MAX == 1000`). Equal priorities break by allocno index
ascending, so the sorted order is deterministic.

* **Tier T1** · **Source anchor** `global.c:614` (mainline; the shipped binary resolves the same
  function to `global.c:789`, delta +175)
* **Binary anchor** `allocno_compare @ 0x081ab288`; field offsets `size=4`, `n_refs=12`,
  `freq=16`, `live_length=20`; double `10.0 @ 0x0821e360`
* **Pass** `16.life`, `23.greg`
* **Receipt** 75 functions / 1,079 allocnos / 1,004 adjacent pairs: exact order 33/75, mean Kendall
  tau 0.873, 26 inversions (2.6%). Constants corrected afterwards (R33 §4.3).
* **Falsifies** dds-decomp's `floor_log2(refs) * refs * hard_reg_width` shape — all four local
  controls failed.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`. Not tested on 2.96.

Quantised consequences: a reference count only steps up when it crosses a power of two; moving a use
into a hotter block raises priority linearly; shortening a live range raises it proportionally.

## L-EE-002 · `allocno.size` is in **words**, and prints only when it is not 1

`PSEUDO_REGNO_SIZE(N)` divides the mode size by `UNITS_PER_WORD`. `SImode` is 1 word, `DImode` and
`DFmode` are 2. The `;; N regs to allocate:` printer appends `(N)` only when `size != 1`.

* **Tier T1** · **Source anchor** `regs.h:116`; print condition `global.c:1937` (EE binary:
  `global.c:2265`)
* **Binary anchor** `allocno_compare @ 0x081ab288` (`fimull 0x4(...)`, struct offset `size=4`)
* **Pass** `23.greg`
* **Receipt** zero `(N)` occurrences across the whole local corpus, including DFmode allocnos that
  do reach global allocation.
* **Falsifies** the reading that `size` is a byte count — the R28 tool substituted the lreg
  `N bytes` field. The two differ by a constant factor of four, so ordering was unaffected, but the
  unit in that model is wrong.
* **Scope** `ee-gcc 3.2-ee-040921`; semantics verified in mainline `regs.h`.

## L-EE-003 · Register pressure is wider on EE: `struct allocno` is 144 B, `HARD_REG_SET` is 192 bits

* **Tier T1** · **Source anchor** `global.c:96` (EE declaration line from DWARF; mainline declares
  the same struct at line 87, with the same field names and order)
* **Binary anchor** `allocno_compare @ 0x081ab288`; `struct allocno` `byte_size = 144`, member step
  24 B, `hard_reg_conflicts @24`, `hard_reg_preferences @48`, `hard_reg_copy_preferences @72`
* **Pass** `23.greg`, `24.postreload`
* **Receipt** DWARF byte size 144; member step 24 B = 192 bits; the disassembly stride is 144 B
  (`lea (%edi,%edi,8)` then `shl $0x4`).
* **Falsifies** the assumption that mainline's `HARD_REG_SET` width applies: mainline sizes it from
  `HARD_REG_SET_LONGS` and `FIRST_PSEUDO_REGISTER`, far below 192 bits. EE carries VU0 and ACC
  register classes (`VU0_Q_REG`, `FP_ACC_REG`, `HILO_REGS`, `COP0_AND_GR_REGS`, …).
* **Scope** `ee-gcc 3.2-ee-040921`.

## L-EE-004 · EE ships its own backend: `config/mips/mips5900.c`

* **Tier T1** · **Source anchor** `config/mips/mips5900.c` — **absent from mainline gcc-3.2.3**
  (`config/mips/` was checked)
* **Binary anchor** `uns_arith_operand @ 0x0817178c` (one of 152 functions that resolve into that
  file)
* **Receipt** the shipped `cc1` embeds 135 source paths, `config/mips/mips5900.c` among them; 152
  text symbols resolve to it.
* **Scope** `ee-gcc 3.2-ee-040921`.

## L-EE-005 · `REG_FREQ` counts every register occurrence; `REG_FREQ_MAX` is 1000

`flow.c` adds one block frequency per register note, so a read-modify-write of one register inside
one instruction counts twice. `regs.h:79` defines `REG_FREQ_MAX 1000`, which makes the
`allocno_compare` factor 10.

* **Tier T1** · **Source anchor** `flow.c:2733` (also `flow.c:3413`, `flow.c:3578`); `regs.h:79`
* **Binary anchor** `life_analysis @ 0x080ce2d8`; double `10.0 @ 0x0821e360`
* **Receipt** source lines read; the binary's 10.0 constant confirms the factor. R28 recorded six
  functions with one inversion each while using a de-duplicated instruction proxy.
* **Falsifies** the reading that the factor is 1 — the misread is recorded in the research repository
  as pitfall `P-108`. **Read the `#define`, not the comment.**
* **Scope** `ee-gcc 3.2-ee-040921`.

## L-EE-006 · Line numbers are not portable between trees

* **Tier T1** · **Source anchor** `global.c:614` vs the shipped binary's `global.c:789`
* **Binary anchor** `find_reg @ 0x081acd64` (the global colouring `find_reg`; the `reload1.c` one is
  a different static symbol at `0x08134570`)
* **Receipt** median drift (EE line minus mainline gcc-3.2.3 line), per file: `global.c` +341,
  `gcse.c` +137, `haifa-sched.c` +263, `regmove.c` +1920, `reload1.c` 0, `local-alloc.c` -4,
  `cse.c` -22, `jump.c` -47, `loop.c` -68, `function.c` -55, `ifcvt.c` -6.
* **Falsifies** transplanting mainline line numbers into EE citations — the first R28 write-up
  quoted mainline line numbers only.
* **Scope** `ee-gcc 3.2-ee-040921` against gcc-3.2.2 and 3.2.3.

## L-EE-007 · There is no translation-unit level codegen state except `$L` numbering

* **Tier T3** (controlled experiment; no source or binary anchor yet)
* **Receipt** six TU configurations, compared with absolute addresses and jump-table deltas
  normalised: instruction stream, `.sdata` and jump tables identical; only `$L` numbering shifts by
  one per preceding labelled function, and label names do not change emitted bytes.
* **Falsifies** the fear that adding unrelated functions to a translation unit perturbs the target
  function.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2`. The exact `$L` counter formula is still open.

---

## Open items

* The exact `$L` counter formula (multi-label functions).
* A per-class colouring replay: the recorded 26.1% accuracy predates the EE `find_reg` anchor.
* `freq` accumulation checked against a real multi-block function, not only the source.
