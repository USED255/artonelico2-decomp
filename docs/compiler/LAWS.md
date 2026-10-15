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

**Verification status.** All **13** binary anchors cited in this handbook have been resolved against the
shipped `cc1` with `tools/compiler/ee-gcc-anchor.py` and match their addresses (two laws cite no binary
anchor and are `T3`). Run the same check after any toolchain change. Beware one **ambiguous name**:
`find_reg` occurs twice — `0x08134570` (`reload1.c:1685`) and `0x081acd64` (`global.c:1329`) — so always
disambiguate by address, not by name.

**Evidence paths.** Each law's `evidence` list names where its receipt lives. A bare path is inside this
repository; a `private:` entry points at the project's private research repository (raw evidence dumps,
which are deliberately not published); a `party:` entry points at one of the project's own research
reports there. `tools/check/test_compiler_tools.py` enforces that every **bare** path exists.

**Measurement conditions.** Scope lines name the flags a measurement was taken under. Most probes in this
handbook used `-O2 -G0`. **The project itself builds with `-O2 -falign-functions=4
-ffunction-sections` and passes no `-G`**, so the MIPS default (`MIPS_DEFAULT_GVALUE`, 8) applies. Laws
about address materialisation ([L-EE-011](#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero),
[L-EE-014](#l-ee-014--small-data-addressing-follows--g-objects-up-to-the--g-size-go-to-sdatasbss-and-are-read-as-a-bare-symbol-gp_rel))
are `-G` sensitive; the allocation and scheduling laws are not.

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

## L-EE-013 · Signedness picks `slt` vs `sltu`; a narrower type adds `andi` or `sll`+`sra`; `xori` marks equality

| expression | `int` / `long long` | `unsigned` | `signed char` / `short` | `unsigned char` / `short` |
| --- | --- | --- | --- | --- |
| `x < 100` | `slt` | `sltu` | `sll` `sra` `slt` | `andi` `sltu` |
| `x == 5` | `xori` `sltu …,1` | same | `sll` `sra` `xori` `sltu` | `andi` `xori` `sltu` |
| `x != 0` | `sltu` | `sltu` | `sll` `sra` `sltu` | `andi` `sltu` |
| `(x & 0x10) != 0` | `sra` `andi` | `sra` `andi` | `andi` `srl` `andi` | `andi` `srl` `andi` |

* **Tier T3** (behaviour only; the compare patterns live in the EE backend, which is not on this
  machine)
* **Pass** `00.rtl`, `17.combine`
* **Receipt** 48 synthetic functions (8 types × 5 patterns × 2 contexts) at `-O2 -G0`
* **Falsifies** the external claim that `slt`/`sltiu` versus `xori` distinguishes narrow unsigned
  types (dds-decomp, ee-gcc 2.96, no licence). `xori` marks **equality**; narrowness shows up as an
  `andi` mask (unsigned) or an `sll`+`sra` extension (signed).
* **Lever** read the extension instruction in front of the compare as the **type's shape**: widening
  the type, or changing its signedness, moves exactly that instruction.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`; 48 synthetic functions.

## L-EE-014 · Small-data addressing follows `-G`

* **Tier T2** · **Source anchor** `config/mips/mips.h:4579` — `MIPS_DEFAULT_GVALUE` is **8**, so a build
  that passes no `-G` uses 8. The backend keeps `mips_section_threshold` (EE
  `config/mips/mips5900.c:226`) and treats `-1` as "unset".
* **Binary anchors** `mips_section_threshold @ 0x0823ed20` (the file stores `-1`, the sentinel) and
  `g_switch_value @ 0x0830d0c0`
* **Receipt** one fixture, four settings:

| probe | `-G0` | `-G4` | `-G8` | default |
| --- | --- | --- | --- | --- |
| 4 B global / static | absolute | small-data | small-data | small-data |
| 8 B `double` | absolute | absolute | small-data | small-data |
| 32 B array | absolute | absolute | absolute | absolute |
| `static const int` read | folded to an immediate | — | — | — |
| float constant `$LCn` | absolute | absolute | absolute | absolute |

  `absolute` = `lui %hi` + `%lo`; `small-data` = the bare symbol (`lw $2,g_int`), which assembles to
  `R_MIPS_GPREL16`.
* **Falsifies** the implicit assumption that `-G0` measurements describe the project build. The project
  passes no `-G`, so its default is 8.
* **Lever** before comparing globals, match `-G` to the target build. Objects up to 8 bytes (and not
  constants) become `gp_rel`; larger objects and every constant stay absolute.
* **Scope** `ee-gcc 3.2-ee-040921`; one fixture per setting.

**The boundary, measured.** An object qualifies when its size is **≤ G (inclusive)**: 4-byte objects qualify
at `-G4`, 9-byte objects only from `-G9`, and the **default (no `-G`) behaves exactly like `-G8`**.
Uninitialised small objects land in `.scommon` (merged into `.sbss` at link time); initialised ones in
`.sdata`. Which *declarations* qualify at `-G0` is [L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss).

## L-EE-015 · The outgoing argument area doubles as storage for a value used after the call

| what is passed | after the call | frame cost |
| --- | --- | --- |
| a 4-byte **aggregate** (stack argument) | re-read from the outgoing slot (`lh $15,48($sp)`) | **none** |
| a **scalar** (stack argument) | kept in a callee-saved register (`sd $16,64($sp)`) | **8 B** |

* **Tier T2** · **Source anchor** `calls.c:4284` (`store_one_arg`) · **Binary anchors**
  `store_one_arg @ 0x08087038`, `load_register_parameters @ 0x08083d64`, `emit_push_insn @ 0x080bf178`
* **Receipt** two fixtures at `-Os -G0` with more than eight parameters (so the ninth goes to the
  outgoing area). The aggregate case ends with `vars = 0`; the scalar case pays one save slot. A real
  function shows the same shape as the aggregate case.
* **Falsifies** the assumption that any value used after a call it was passed to must be spilled or
  pinned in a callee-saved register.
* **Lever** pass the *same* aggregate expression to the call and use it again afterwards. Introducing a
  local copy of that aggregate creates a second live object and costs a slot.
* **Scope** `ee-gcc 3.2-ee-040921` at `-Os -G0`; a 4-byte aggregate and a scalar.

## L-EE-016 · The EE register file: 140 hard registers in 29 classes

Read from a **live** `cc1` (gdb, breakpoint at `local_alloc`, after `init_reg_sets_1` filled the tables):

| registers | class |
| --- | --- |
| 0–31 | `GR_REGS` (GPRs) |
| 32–63 | `FP_REGS` |
| 64–67 | `HI_REG`, `LO_REG`, `HI1_REG`, `LO1_REG` (the EE's second multiply/divide unit) |
| 68 / 69–70 / 71 | `ST_REGS` / `ELIM_REGS` / `FP_ACC_REG` |
| 72–75 | reserved (in `fixed_reg_set`, no class) |
| 76 / 77–79 | `VU0_ACC_REG` / `VU0_Q_REG`, `VU0_I_REG`, `VU0_R_REG` |
| 80–111 | `COP0_REGS` |
| 112–143 | `VU0_REGS` |

`ALL_REGS` spans **140** registers (`FIRST_PSEUDO_REGISTER`), `N_REG_CLASSES` is **29**, and a
`HARD_REG_SET` is 192 bits.

`fixed_reg_set` leaves `0, 1, 26, 27, 28, 29, 31` fixed among the GPRs (zero, at, k0, k1, gp, sp, ra);
`call_used_reg_set` leaves `2–15, 24, 25` caller-saved. Therefore the **allocatable callee-saved GPRs are
exactly `{16..23, 30}`** — eight `$s0`–`$s7` plus `$fp` — which is why the save area caps at **10 slots**
once `$ra` is included ([L-EE-012](#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers)).

* **Tier T1** · **Source anchor** `config/mips/mips5900.c` (the file that owns the EE register file; its
  `mips.h` `REG_CLASS_CONTENTS` is not on this machine) · **Binary anchors**
  `reg_class_contents @ 0x08309140`, `reg_class_size @ 0x083094c0`, `fixed_reg_set @ 0x0830a310`,
  `call_used_reg_set @ 0x083093f8`
* **Receipt** the table above, read from a live process. The static read returns zeros: these arrays live
  in `.bss` and are filled at startup.
* **Falsifies** the assumption that the shipped EE register file can be approximated by the mainline MIPS
  one — and the earlier guess that these tables are unreadable.
* **Lever** allocate only inside `reg_class_contents[class] − fixed_reg_set`, and for a call-crossing
  allocno also remove `call_used_reg_set`.
* **Scope** `ee-gcc 3.2-ee-040921`, read on this machine. These are compiler constants.

## L-EE-017 · The shipped `find_reg` is not mainline's — a two-step ladder whose decision is a side effect

The shipped binary's own debug info gives the signature, and it is not the mainline one:

```
shipped   global.c:1336   find_reg (num, losers, alt_regs_p, accept_call_clobbered, retrying)
mainline  global.c        find_reg (struct allocno *allocno, HARD_REG_SET *allocnos_live)
```

Two further observations from the same session (gdb trace plus the listing):

* The function is called as a **two-step ladder**, and the ladder appears **twice**:

| step | address | in | EE source line |
| --- | --- | --- | --- |
| 1 (`alt_regs_p=0`) | `0x81aa4ba` | `global_alloc` | `global.c:400` |
| 2 (`alt_regs_p=1`) | `0x81aa520` | `global_alloc` | `global.c:407` |
| 1 (`alt_regs_p=0`) | `0x81aad68` | `global_init` | `global.c:772` |
| 2 (`alt_regs_p=1`) | `0x81aadbe` | `global_init` | `global.c:777` |

  `find_reg` also **calls itself recursively** at `global.c:1540` (that is what `retrying` is for). `losers` was
  NULL and the other flags zero in every observed external call.
* **The return value is discarded.** The instruction after each external call immediately overwrites `%eax`
  (`0x81aad6d`, `0x81aa4bf`). The caller then reads a **signed 16-bit** per-register array (`cmpw` + `js`) to
  decide that an allocno got no register; one path also consults `reg_alternate_class`. The table is
  **`reg_renumber`** (`0x82ea1ec`, a `short` array), so the choice is a **side effect** and an earlier reading of
  `-1` in `%eax` was leftover.

The same listing confirms `sizeof (struct allocno) == 144`: the allocno array is indexed by scaling the number
by 9 and shifting left 4 ([L-EE-003](#l-ee-003--the-ee-register-pressure-model-is-wider-struct-allocno-is-144-b-and-hard_reg_set-is-192-bits)).

* **Tier T1** · **Source anchor** `global.c:1336` (DWARF) · **Binary anchors** `find_reg @ 0x081acd64`
  (global.c) and `find_reg @ 0x08134570` (reload1.c — always disambiguate by address)
* **Falsifies** both the assumption that a replay built on mainline's `find_reg` can reproduce the shipped
  decisions, and the reading that `find_reg` *returns* the chosen register
* **Lever** model a two-step ladder (`alt_regs_p` 0 then 1) that writes its result as a side effect; treat a
  negative signed per-register entry as "no register"
* **Scope** `ee-gcc 3.2-ee-040921`, observed with gdb and objdump on this machine; two external call sites and
  one recursive site were located, and the flags other than `alt_regs_p` were zero in the traced sample

---

## L-EE-018 · Global allocation: preference first, then the lowest register left, after two passes that first avoid registers other allocnos prefer

The rule, fitted by measurement (see the receipt):

1. **Pool** = `reg_class_contents[class] − fixed_reg_set`; for a **call-crossing** allocno also minus
   `call_used_reg_set` ([L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)).
2. **Banned** = the allocno's `hard_reg_conflicts` ∪ the registers of the **already-placed conflicting
   allocnos**. Do *not* ban every already-assigned register: that double-counts what the conflict table
   already expresses and costs about 6 points.
3. **Choice** = the first entry of the allocno's preference list that is still available; otherwise the
   **lowest-numbered** candidate.
4. **Two passes.** The first pass also avoids the registers that **other** allocnos prefer (the EE-only
   `regs_someone_prefers` field); the second pass drops that exclusion. This is what `alt_regs_p`
   toggles in the observed ladder ([L-EE-017](#l-ee-017--the-shipped-find_reg-is-not-mainlines--it-is-a-two-step-ladder-whose-decision-is-a-side-effect)).

| rule | held-out accuracy (527 allocnos) |
| --- | ---: |
| mainline-modelled two-pass replay (v2) | 9.1% |
| preference-first heuristic banning all assigned (previous best) | 34.3% |
| runtime tables + v2 rule (v4) | 9.9% |
| this rule (v5) | **41.0%** |
| this rule plus the two passes of step 4 (v6) | **46.5%** |
| v6, with the dynamic conflict set held at ground truth | **82.7%** |

* **Tier T2** · **Source anchor** `global.c:400` (the ladder of
  [L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect));
  the rule itself is measured, not read · **Binary anchors** `reg_renumber @ 0x082ea1ec`,
  `allocno @ 0x082e8a54`, `allocno_order @ 0x082e8a58`
* **Falsifies** two assumptions of the earlier replays: that banning every already-assigned register is
  safe (it costs ~6 points), and that mainline's two-pass scan is the shipped algorithm (12.8%)
* **Lever** use the pool and ban-set above when predicting an allocation; the residual is mostly
  **cascade** — one wrong early pick poisons the later conflict sets (41.0% → 82.7% with a correct
  context), so getting the processing order and each decision right matters more than widening the pool
* **Scope** `ee-gcc 3.2-ee-040921`, GPR allocnos, served-out split on this machine

**Preference semantics, measured exactly:** of the 427 allocnos that carry a preference list, **323 pick the first entry
that is still available** and **none picks a later entry** — "first available preference" is the whole rule. Where there
is no preference the pick is *not* the lowest candidate (334 of 461 such cases, with the true register inside the computed
candidate set every time), so something else decides the scan.

**How to tell a rule from a compensation.** Step 4 gains 5.5 points end-to-end but leaves the oracle-context score
**unchanged** (82.7% → 82.7%), and it matches both an EE-only struct field and the observed ladder — so it is a rule.
The rejected "rotating start" below looks similar end-to-end but *loses* 3 points under the oracle, which is how a
compensation for the replay's own errors is identified.

**A rejected hypothesis — the "rotating start".** Scanning from `pseudo mod 32` lifts the corpus score from 38.9% to
49.1%, which looks like a real rule. It is not: with the dynamic conflict set held at ground truth the rotation scores
**60.5%** against **63.5%** without it, so it only compensates for this replay's own errors. Do not adopt it.

**A second rejected hypothesis — live-range occupancy.** Rebuilding the conflict set from the **block-level** live sets
in the `16.life` dump scores **30.6%** against **42.1%** for the dumped `conflicts` list: block granularity merges
allocnos that are live at different points, so the dumped list (built from instruction-level liveness) remains the
better occupancy source. Two levers have now been tried and rejected — the rotating start and live-range occupancy —
and the remaining gap to the oracle ceiling is **cascade**, which needs instruction-level live ranges or the shipped
source.

**Addressing detail, verified live:** `allocno_order[i]` holds an **allocno index** and
`allocno[index].reg` holds the **pseudo** register number, so the dump's `;; N regs to allocate:` list already
prints the pseudos **in allocation order** — for one fixture the live order `[3,1,2,0,…]` maps to the printed
`152 150 151 149 …`. Re-sorting that list by an external proxy (n_refs descending 41.8%, `live_length`
ascending 42.0%, against 38.9% for the printed order) changes the error pattern but is not a better rule:
**the order is not the lever, per-decision accuracy is.**

---

## L-EE-019 · The float rule is version-specific: 2.96 inlines, 3.2 uses the pool

This project uses **two** compilers: `3.2-ee-040921` for the game code and `2.96-ee-001003-1` for the CRI
middleware. Most rules transfer; the float-constant rule does not.

`float f(void) { return V; }`, object code, `-O2 -G0`:

| V | 3.2 | 2.96 |
| --- | --- | --- |
| `0.0f` | `mtc1` (zero register) | `mtc1` |
| `0.5f`, `1.0f`, `2.5f`, `-1.0f`, `100.0f` | `lui addiu lwc1` — **pool** | `lui mtc1` — **inline** (low 16 bits zero) |
| `0.01f`, `3.14f`, `123.456f`, `1e30f` | **pool** | `lui ori mtc1` — **inline** |

Doubles **do** agree: `move` for `0.0`, `li` + `dsll32` when the low 32 bits are zero, otherwise the pool
(`lui` + `ld`) — [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero).

Re-run on 2.96 and agreeing: the narrow-compare idioms
([L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality)),
the switch threshold
([L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count)) and
`-G0` absolute addressing
([L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g)).

* **Tier T3** (behaviour only; no source and no binary anchor for either backend)
* **Receipt** the two tables above, read from the **object code** — 2.96 prints `li.s` in the assembly,
  which is a pseudo-instruction and misleads
* **Falsifies** the assumption that one compiler's constant rule transfers to the other
* **Lever** before changing a float constant's spelling, check which compiler builds that source
* **Scope** both compilers at `-O2 -G0`, synthetic fixtures

---

## L-EE-020 · The pass pipeline is `-O` sensitive

`ee-gcc -<level> -G0 -da -c` on one loop fixture:

| level | dumps | missing relative to `-O2` |
| --- | ---: | --- |
| `-O0` | **9** | 01.sibling, 08.null, 09.cse, 11.gcse, 12.loop, 14.bp, 15.cse2, 17.combine, 18.ce, 19.regmove, 20.sched, 21.range, 27.rnreg, 28.ce2, 29.sched2, 31.bbro, 33.dbr |
| `-O1` | **20** | **01.sibling, 11.gcse, 19.regmove, 20.sched, 21.range, 29.sched2** |
| `-O2` | **26** | — |
| `-Os` | **26** | same set as `-O2` |

The **decision rules do not change** with the level: at `-O1` a `0.5f` constant still loads from the pool, a
low-word-zero `double` is still built with `li` + `dsll32`, and a dense six-case switch still becomes a
table — only the instruction order and the register moves differ, which is what the six missing passes do.
That is why some functions in this project match only at `-O1`.

* **Tier T1** · **Source anchor** `toplev.c:3316` (the pipeline driver) · **Binary anchors**
  `global_alloc @ 0x081aa2c4`, `rest_of_compilation @ 0x0815a854`
* **Receipt** the inventory above, plus the four rule checks at `-O1` and `-O2`
* **Falsifies** the assumption that one pass inventory describes this compiler
* **Lever** check the `-O` level before comparing code shape — and count `-da` dumps only for a compile
  that **succeeded**: a rejected source (for example a C99 `for`-declaration under C89) leaves just two
  dumps, so a missing dump may mean the compile stopped, not that the pass did not run
* **Scope** `ee-gcc 3.2-ee-040921` at `-O0/-O1/-O2/-Os`, one loop fixture for the inventory and four
  synthetic fixtures for the rules

---

## L-EE-021 · `gp_rel` needs a definition in this unit placed in `.sdata`/`.sbss`

[L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g) gives the `-G` threshold. This is the other
half: which *declarations* become small data.

| declaration (defined in this unit) | `-G0` | default (`-G8`) |
| --- | --- | --- |
| `int g;` | `lui %hi` — absolute | **bare symbol** — `gp_rel` |
| `int g __attribute__((weak));` | **absolute** — `weak` alone does nothing | bare symbol |
| `int g __attribute__((section(".sbss")));` | **bare symbol** ✔ | bare symbol |
| `int g __attribute__((section(".sdata"))) = 7;` | **bare symbol** ✔ | bare symbol |
| `extern int g;` (no definition here) | absolute | **absolute** |
| `extern int g __attribute__((section(".sbss")));` | absolute | **absolute** |

So at `-G0` — the flag the CRI sources use — the only way to get `gp_rel` is to **define** the object in
this unit inside `.sdata`/`.sbss`. `weak` is not the operative part, and an `extern` declaration can never
be made small-data: the definition has to be in the same translation unit.

`objdump -t` confirms the placement: `section(".sbss")` lands in `.sbss`, `section(".sdata")` in `.sdata`,
while a weak object without an attribute lands in `.bss`.

* **Tier T2** · **Source anchor** `varasm.c` (the small-data decision; no line could be read from the
  shipped tree) · **Binary anchors** `mips_section_threshold @ 0x0823ed20`, `g_switch_value @ 0x0830d0c0`
* **Falsifies** the reading that a *weak* small-data definition is what produces `gp_rel`
* **Lever** when a target uses the bare symbol and the candidate uses `lui %hi`, define the object in this
  unit inside `.sdata`/`.sbss` — that is what the project's `gp_rel` candidates do; an `extern` cannot
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2` with `-G0`/`-G8`/default, synthetic declarations

---

## L-EE-022 · Function alignment: 8 bytes by default, 4 with `-falign-functions=4`

Four 12-byte functions, `-O2 -G0`:

| flags | alignment in the assembly | symbol offsets | `.text` |
| --- | --- | --- | ---: |
| none | `.align 2` + **`.p2align 3,,7`** (8 bytes) | 0x0, 0x10, 0x20, 0x30 | **0x40** |
| `-falign-functions=4` | `.align 2` only | 0x0, 0xc, 0x18, 0x24 | **0x30** |
| `-ffunction-sections` | one `.text.N` per function, still `.p2align 3` | 0 in each | 0x10 each |
| **`-falign-functions=4 -ffunction-sections`** (what this project uses) | `.text.N` + `.align 2` only | 0 in each | **0xc each — no padding** |

So the default is **8-byte** alignment, which pads a 12-byte function to 16; `-falign-functions=4` drops it to
4 and the functions pack tightly. `-ffunction-sections` alone does **not** remove the 8-byte alignment.

* **Tier T2** · **Source anchor** `varasm.c` (the alignment directive; not read from the shipped tree) ·
  **Constants** the emitted `.p2align 3,,7` and `.align 2`
* **Falsifies** the assumption that `-ffunction-sections` alone removes inter-function padding, and that
  the default alignment is 4 bytes
* **Lever** when objdiff shows a *size or offset* mismatch while the instructions agree, check the
  alignment flags before rewriting anything
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, four one-instruction functions

---

## L-EE-023 · At these flags only an `inline` declaration is inlined

`-G0`, judging by whether `jal helper` and the `helper:` label survive:

| declaration | -O0 | -O1 | -O2 | -O3 / `-O2 -finline-functions` |
| --- | --- | --- | --- | --- |
| `static int helper(...)` | call | call | **call** | inlined |
| `static inline int helper(...)` | call | **inlined** | **inlined** | inlined |
| `inline int helper(...)` | call | **inlined** | **inlined** | inlined |
| `static __attribute__((always_inline))` | call | call | **call** | inlined |
| `static inline __attribute__((always_inline))` | **inlined** | inlined | inlined | inlined |

At the project's flags — `-O2`, **without** `-finline-functions` — a plain `static` helper **always keeps its
call**, even when it is small and called exactly once (a sweep over 1–12 statements and 1 or 3 call sites
found no size that inlines). `always_inline` **needs `inline`** to have any effect, as the 3.2 manual says;
with it, the function inlines even at `-O0`.

* **Tier T2** · **Source anchor** the inliner (`cgraphunit.c`/`integrate.c`; no line read from the shipped
  tree) · **Constants** `-finline-functions` off at `-O2`, on at `-O3`
* **Falsifies** the expectation that `-O2` inlines a small static function called once, and that
  `always_inline` works alone
* **Lever** if the target has a helper expanded and your candidate emits `jal`, add `inline` (or check
  whether that unit was built with `-O3`/`-finline-functions`)
* **Scope** `ee-gcc 3.2-ee-040921` at `-G0`, `-O0`–`-O3`, synthetic single-helper units

---

## L-EE-024 · A saved `$fp` is not a frame pointer

| fixture (`-O2 -G0`) | `.frame` first operand | frame |
| --- | --- | ---: |
| locals all in registers | `$sp,0` | 0 |
| eight call-crossing values | **`$sp`,80** | 80 — `$fp` is saved, but as a register |
| `__builtin_alloca` | **`$fp`,64** | 64 — a real frame pointer |
| VLA (`int v[n]`) | **`$fp`,96** | 96 — a real frame pointer |
| eight values + `-fno-omit-frame-pointer` | **`$fp`,96** | **96** (was 80) |
| eight values + `-fomit-frame-pointer` | `$sp`,80 | 80 — same as the default |

1. **`-O2` omits the frame pointer by default here** (explicit `-fomit-frame-pointer` reproduces the default).
2. A saved `$fp` in a normal function is only the **tenth callee-saved register**
   ([L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)) — the judgement is the
   **first operand of `.frame`**: `$sp` = no frame pointer, `$fp` = one.
3. `.frame $fp,…` comes from **alloca/VLA** or from **`-fno-omit-frame-pointer`**; the latter adds **16 bytes**
   even with no dynamic stack (80 → 96 above), which objdiff shows as a size or offset mismatch.

* **Tier T2** · **Source anchor** `function.c` (prologue/frame-pointer choice; no line read from the shipped
  tree) · **Constants** 80 vs 96 in the same fixture
* **Falsifies** the reading that a saved `$fp` in the prologue means a frame pointer is used
* **Lever** read `.frame`'s first operand; when the target frame is exactly 16 bytes larger with the same
  callee saves, suspect `-fno-omit-frame-pointer` or a dynamic stack
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic functions including `alloca` and a VLA

---

## Open items

* The exact `$L` counter formula (multi-label functions).
* ~~`FIRST_PSEUDO_REGISTER` for the EE build~~ — **settled**: **140**, read from a live `cc1`
  ([L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)).
* **Colouring is now partially modelled.** [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer)
  reproduces **46.5%** of held-out decisions with a measured candidate/selection rule, against 34.3% for
  the earlier heuristic and 9.1% for a mainline-modelled two-pass replay. The same rule reaches **82.7%**
  when the dynamic conflict set is held at ground truth, so the residual is dominated by **cascade**
  rather than by the per-decision rule. Two levers were tried and rejected (a rotating scan start, and
  live-range-derived occupancy). [L-EE-017](LAWS.md#l-ee-017--the-shipped-find_reg-is-not-mainlines--a-two-step-ladder-whose-decision-is-a-side-effect)
  explains why a mainline port cannot work: the shipped `find_reg` takes a `losers` set plus three flags
  and is called in a retry ladder (`alt_regs_p` toggling). Next: pin the **processing order**
  (`allocno_compare`) and the ladder's precise semantics.
* ~~`freq` accumulation~~ — settled: the per-occurrence rule wins by measurement (L-EE-005).
