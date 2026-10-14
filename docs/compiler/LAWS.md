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
* **Receipt** 75 functions / 1,004 adjacent pairs. Counting **every register occurrence** reproduces
  the exact allocation order in **44/75** (mean Kendall tau 0.877); a de-duplicated instruction proxy
  reaches 33/75 (0.873). The source reading wins by 11 functions, and the binary's 10.0 constant
  confirms the `REG_FREQ_MAX = 1000` factor.
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

## L-EE-008 · In `23.greg`, `regs to allocate` is the local-allocation residue; `conflicts` lists every allocno

The `;; N regs to allocate:` line skips allocnos that already have a register (`reg_renumber >= 0`).
The `;; N conflicts:` lines do not: they list every allocno, whether or not local allocation already
placed it.

* **Tier T1** · **Source anchor** `global.c:1926` (the count loop skips at 1922; the conflicts loop at
  1945 has no test). The shipped binary resolves `dump_conflicts` to `global.c:2265`.
* **Binary anchor** `dump_conflicts @ 0x081af134`
* **Pass** `22.lreg`, `23.greg`
* **Receipt** 166 functions: the conflict lines list **10,450** allocnos, `regs to allocate` lists
  **1,079**. The two differ in **166/166** functions; `fx_arith` reports 8 and 0.
* **Falsifies** the reading that the conflict lines list only the allocnos still waiting for a
  register. Treating the extra numbers as hard registers is a measured failure mode: it produced the
  wrong candidate sets in the first colouring replay.
* **Lever** take the still-unplaced set from `regs to allocate`, the interference graph from
  `conflicts`, and classify a number as a hard register only when it is not an allocno (allocno
  numbers are the `;; N conflicts:` keys and the `[N]` brackets in the RTL).
* **Scope** `ee-gcc 3.2-ee-040921`.

## L-EE-009 · The delay slot is filled; the leftover `nop` is the function-ending `jr ra`

* **Tier T2** · **Source anchor** `reorg.c:3582` (`dbr_schedule`; the shipped binary resolves it to
  `reorg.c:3571`). The fillers are `fill_simple_delay_slots` and `fill_slots_from_thread`.
* **Binary anchor** `dbr_schedule @ 0x081cd510`
* **Pass** `20.sched`, `29.sched2`, `33.dbr`
* **Receipt** 10 synthetic functions / 29 branches at `-O2 -G0`: **24 filled (82.8%)**, **0 nops**
  emitted by the compiler, 5 branches followed by a label or the function end. Object-level check on
  `f_dowhile`: the `bgtz` slot holds `addiu`, the function-ending `jr ra` slot holds `nop`. Slot
  contents observed: `addu` 9, `li` 6, `move` 5, `lw`/`sll`/`lui`/`ld` 1 each.
* **Falsifies** the assumption that a `nop` delay slot means the scheduler found nothing to move: at
  this level the compiler emits none, and the leftovers are filled by the assembler.
* **Lever** treat a delay-slot difference as a **scheduling** decision. Regroup statements and check
  what the branch successors provide before editing the expression.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`; 10 synthetic functions. A rule read from
  `reorg.c` was not verified instruction-by-instruction in the binary, which is why this is T2.

## L-EE-010 · A switch becomes a jump table only when `count >= 5` **and** `range <= 10 * count`

`expand_end_case_type` falls back to a compare chain when `count < case_values_threshold ()` or when
the span is more than ten times the number of cases; otherwise it calls `try_tablejump`.
`CASE_VALUES_THRESHOLD` is `HAVE_casesi ? 4 : 5`, and the measurement shows **5**, so this backend has
no `casesi`.

```
count >= 5  AND  (max - min) <= 10 * count   -> jump table
otherwise                                    -> compare chain
```

* **Tier T1** · **Source anchor** `stmt.c:5401` (the decision) and `expr.c:10486` (the constant);
  `try_tablejump` is called at `stmt.c:5509`
* **Binary anchors** `expand_end_case_type @ 0x08154e0c` (`stmt.c:5238`),
  `case_values_threshold @ 0x080cad50` (`expr.c:10431`), `try_tablejump @ 0x080cae48` (`expr.c:10595`)
* **Receipt** 11 synthetic switches at `-O2 -G0`, **all 11 matching the rule**:

| switch | count | range | result |
| --- | ---: | ---: | --- |
| dense 3 / dense 4 | 3 / 4 | 2 / 3 | compare chain |
| dense 5 / 6 / 7 / 8 / 10 / 16 | 5–16 | count−1 | table, **size == count** |
| `{0,1,2,100,1000}` | 5 | 1000 | compare chain |
| `{0,10,20,30,40}` | 5 | 40 ≤ 50 | table with **41** entries |
| `{0,1,2,3,4,100,200,300}` | 8 | 300 > 80 | compare chain |

* **Falsifies** the external claim that five distinct cases are enough (dds-decomp, ee-gcc 2.96, no
  licence). Five is necessary, not sufficient: the span must also fit `range <= 10 * count`.
* **Lever** count the cases and the span before choosing a spelling; pulling case values closer
  together, or adding a range guard ahead of the switch, changes the decision.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`; 11 synthetic switches.

## L-EE-011 · Float constants come from the pool; a double is inline when its low 32 bits are zero

| constant | form |
| --- | --- |
| `0.0f` | inline `mtc1 $0` |
| any other `float` | constant pool: `lui %hi($LCn)` + `addiu %lo($LCn)` + `l.s` |
| `0.0` (double) | `move $2,$0` |
| `double` whose low 32 bits are zero (`0.5`, `1.0`, `1.5`, `2.5`, `2^52`) | inline `dli` + `dsll` |
| other `double` (`0.01`, `π`, `1.0000000001`) | constant pool + `l.d` |

* **Tier T2** · **Source anchor** `config/mips/mips5900.c:1638` — the EE backend carries
  `mips_move_1word`, which mainline 3.2.3 does not have. The exact case lives in that file, which is
  not on this machine, so the rule is measured rather than read.
* **Binary anchor** `mips_move_1word @ 0x0817298c` (a pointer into the EE backend, not a verification
  of the rule)
* **Receipt** 14 floats and 9 doubles at `-O2 -G0`; every row matches the table above. Floats with a
  zero low halfword (`0.5f`, `1.0f`, `2.5f`, `1.5f`) still come from the pool.
* **Falsifies** the IDO 5.3 rule that a constant's low halfword decides inline versus pool (CC0
  n64-decomp-workbench law L62): on this compiler that split exists for **doubles only**.
* **Lever** if a constant-form difference survives every respelling of the C, check the value's bit
  pattern for doubles; for floats, expect the pool and look elsewhere.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`; 23 synthetic constants.

## L-EE-012 · Frame composition: `[vars][outgoing args][8 B per saved register]`, saturating at 10 saved registers

* **Tier T2** · **Source anchor** `global.c:991` (`find_reg`; the shipped binary resolves it to
  `global.c:1329`). The 8-byte slot and the nine `$s` registers come from the ABI.
* **Binary anchor** `find_reg @ 0x081acd64`
* **Receipt — synthetic dose-response** (`-O2 -G0`, k values live across calls):

| k | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 18 | 24 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| frame | 32 | 48 | 64 | 80 | 96 | 96 | 112 | 128 | 144 |
| `regs=` | 4 | 6 | 8 | 10 | 10 | 10 | 10 | 10 | 10 |
| `vars=` | 0 | 0 | 0 | 0 | 16 | 16 | 32 | 48 | 64 |

  The frame grows **8 B per saved register**, and the save area **caps at 10 registers (80 B)**; past
  that only `vars` grows. The saved registers observed are `$s0`–`$s7` (16–23), `$fp` (30) and
  `$ra` (31).
  **Naming trap**: the objdump in this toolchain prints register 30 as `s8`, while the compiler's own
  assembly prints `$fp` for it. Do not infer register numbers from disassembly names.
* **Receipt — a real function** (`func_001d4b88`): retail frame 144 = vars 16 + args 48 + ten saves
  (80 B); candidate frame 176 = vars **48** + args 48 + **the same ten saves**. Both prologues save
  `s0`–`s8` and `ra`.
* **Falsifies** the reading that a larger candidate frame means more saved registers. On this function
  the entire +32 B is the variable block, so the lever is to stop spilling two more values, not to
  reduce saved registers.
* **Lever** decompose the frame first: `vars / args / 8 B × regs`. Then aim at the block that differs.
* **Scope** `ee-gcc 3.2-ee-040921`; 6 synthetic functions plus one real function. In the synthetic
  corpus a value that cannot take a register is sometimes **rematerialised** instead of spilled, so
  `vars` does not grow one slot per extra value.

---

## Open items

* The exact `$L` counter formula (multi-label functions).
* `FIRST_PSEUDO_REGISTER` for the EE build is bounded but not read exactly (the class tables are
  runtime-initialised); the practical classifier is L-EE-008's lever.
* **Colouring replay is not modelled yet.** On 527 allocnos, a preference-first heuristic reproduces
  **34.3%** of the recorded dispositions, and a replay that follows `find_reg`'s two passes plus its
  preference override reproduces only **9.1%** — implementing more of the source *hurt*. The cause is
  identified: `reg_class_contents`, `fixed_reg_set` and `call_used_reg_set` are runtime-initialised
  (`.bss`), so a static read returns zeros and the exclusion sets in the replay are wrong. Reading
  those tables from a live process is the next step.
* ~~`freq` accumulation~~ — settled: the per-occurrence rule wins by measurement (L-EE-005).
