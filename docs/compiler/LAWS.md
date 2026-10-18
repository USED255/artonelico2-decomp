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

**Verification status.** All **40** symbol claims (22 laws, related anchors included) have been resolved
against the shipped `cc1` with `tools/compiler/ee-gcc-anchor.py` and match their addresses; four laws are
`T3` (behaviour-only). `tools/check/test_compiler_laws.py` re-verifies every claim whenever the toolchain is
present. Run the same check after any toolchain change. Beware one **ambiguous name**:
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


**Level note.** Every receipt below is taken at `-O2 -G0` unless the entry says otherwise. Whether a rule holds
at another level is measured, not assumed — see the matrix in [PASSES.md](PASSES.md#which-laws-hold-at-which-optimisation-level).
In this project `-Os` (687 files) and `-O1` (542) are the common levels and there are no `-O0` files.

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

`ALL_REGS` spans **140** registers, `N_REG_CLASSES` is **29**, and a `HARD_REG_SET` is 192 bits. The 140 is
a **member count**, not the pseudo boundary: the numbering runs to 143 (72–75 are reserved), so
`FIRST_PSEUDO_REGISTER` is **144** — which is also why the set rounds to `3 × 64` bits. Read live, the
register-name table `debug_reg_names` (`0x0821f280`) has entries 0..143 and the next slot is not a name.

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

**Preferences are edited before this rule runs.** `expand_preferences` unions the preferences of
copy-related allocnos; `prune_preferences` then clears conflicts, fixed, caller-saved (for a call-crossing
allocno) and out-of-class registers, and fills `regs_someone_prefers`. Both phases are observable with
`tools/compiler/ee-gcc-observe-alloc.py --prefs`: [L-EE-053](#l-ee-053--a-copy-records-a-hard-register-preference-on-whichever-side-is-a-global-pseudo)
records preferences, [L-EE-054](#l-ee-054--preferences-are-pruned-before-ordering-conflicts-fixed-caller-saved-for-call-crossing-values-and-out-of-class-registers-are-removed)
prunes them. Rules 1–4 consume the **post-prune** list, so a preference visible in the RTL is not
necessarily the one the choice sees.

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

**Where to read it**: the `.align` directives inside an assembly listing are *not* function alignment (they
belong to local labels and tables). Function alignment is visible only in the **object**: the `.text` section
reports alignment `2**3` by default and `2**2` with `-falign-functions=4`, and the section comes out 8 bytes
shorter because the padding between two small functions is gone. Same family of trap as
[L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu) — the assembly listing is a hint, the object is the evidence.

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

## L-EE-025 · Loops count down at -O2/-Os (at -O1 they keep `slt`) and are not unrolled

`for (i = 0; i < N; i++) s += a * i;` at `-O2 -G0`:

```asm
        move    $2,$0            # s
        move    $14,$0
        li      $15,7            # N-1  <- immediate countdown counter
$L6:
        addu    $2,$2,$14
        addu    $15,$15,-1
        bgez    $15,$L6
        addu    $14,$14,$4
```

Eight instructions for **N = 4, 8 and 20** — only the immediate changes, so the loop stays **rolled and counts
down**. A variable bound (`i < n`) also counts down, but with a runtime counter: a `blez` guard, `addu
$5,$5,-1`, `bne $5,$0`.

| level | instructions (constant trip 8) |
| --- | ---: |
| `-O1` | 9 |
| `-O2` | 8 |
| `-O3` | 8 |
| `-O2 -funroll-loops` | **12** |

So **neither `-O2` nor `-O3` unrolls here** — unrolling needs `-funroll-loops` or a hand-unrolled source.

* **Level-dependent.** At `-O1` the same loop keeps an **upward** induction — `addu $14,$14,1` / `slt
$15,$14,8` / `bnel` — and the multiply stays inside the loop, so "is the loop a countdown?" is also a read on
the optimisation level. `-O2`, `-Os` and `-O3` count down.

**Tier T2** · **Source anchor** the loop/strength-reduction passes (`loop.c`; no line read from the shipped
  tree) · **Constants** 8 instructions at three trip counts, 12 with `-funroll-loops`
* **Falsifies** the expectation that `-O3` unrolls, and that a constant bound keeps an upward comparison
* **Lever** if the target body is repeated, check for `-funroll-loops` (or a manually unrolled source)
  before restructuring the loop; if the target is not in countdown form, the source loop shape differs
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0` plus `-O1`/`-O3`/`-funroll-loops`, synthetic single-loop
  functions

---

## L-EE-026 · The constant pool is per function

At `-O2 -G0` the constants live in `.rdata` blocks, **one per function**, each entry aligned to its natural
size (`.align 2` for a float/word, `.align 3` for a double).

| situation | entries |
| --- | --- |
| `0.5f` used three times inside one function | **1** (`$LC0`) — deduplicated |
| two functions each returning `0.5f` | **2** (`$LC0`, `$LC1`, both `.word 1056964608`) — **not** shared |

Entries follow **first-use order**: `if (k) return 2.5f; return 0.5f;` numbers them `$LC0` = 2.5f,
`$LC1` = 0.5f — not sorted by value.

* **Tier T2** · **Source anchor** `varasm.c` (constant-pool emission; no line read from the shipped tree) ·
  **Constants** the two `.word`s above
* **Falsifies** the assumption that identical constants are shared across the translation unit, and that the
  pool is sorted by value
* **Lever** if the target shares a constant between two functions (or your candidate does and the target does
  not), the difference is in the source's function boundaries, not the constant; if the *order* differs,
  compare first-use order — and remember a double shifts the following offsets with `.align 3`
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`/`-O1`, synthetic units with floats, a double and strings

---

## L-EE-027 · Strings are pooled per translation unit, not per function

Two functions each returning `"hello"` produce exactly **one** `.ascii "hello\000"` — at `-O0`, `-O1`, `-O2`
and `-Os` alike — and the object's relocations show both referencing the same place. So string pooling is
**unconditional**, and it is the opposite of the constant pool, where the same float in two functions gets
two entries ([L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function)).

Two more things the assembly misleads about:

* it writes `.rdata` with `.align 3` (8-byte) and an explicit `\000`, while the **object's section is
  `.rodata`** (`objdump -h`: size 0x28, alignment `2**3`). If you are looking for a `.rdata` section in an
  object or a dump, you will not find one;
* there is **no suffix sharing**: `"world"` and `"hello world"` are two independent entries.

* **Tier T2** · **Source anchor** `varasm.c` (`const_str_htab`; no line read from the shipped tree) ·
  **Constants** one `.ascii` occurrence, section `.rodata`
* **Falsifies** generalising the per-function constant-pool rule to strings, and expecting a `.rdata`
  section in the object
* **Lever** when two functions disagree about a string, look at the translation-unit boundary (strings never
  merge across units); when reading data offsets, read `.rodata`
* **Scope** `ee-gcc 3.2-ee-040921` at `-G0` with `-O0`–`-Os`, synthetic units with repeated and overlapping
  strings

---

## L-EE-028 · Eight integer arguments travel in $4-$11 and eight float arguments in $f12-$f19; a long long or double takes one 64-bit GPR; the rest go on the stack in 8-byte slots

Sixteen callers, one to sixteen `int` arguments, `-O2 -G0`:

* arguments **1–8 go in `$4`–`$11`** — none of them touches the stack;
* from the **ninth** each argument is stored on the stack at an **8-byte stride**: `0($sp)`, `8($sp)`,
  `16($sp)` … in source order (not 4 bytes, even for `int`);
* the frame's `args=` is that area **rounded up to 16 bytes**: 9–10 arguments → 16, 11–12 → 32, 13–14 → 48,
  15–16 → 64, i.e. `args = round16(8 × max(0, n − 8))`.

The **whole frame** is `round16(vars + 8 × regs + args)`
([L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers)):
a caller with nine arguments has a sum of 24 and a frame of 32.

* **Tier T2** · **Source anchor** the MIPS backend's EABI argument layout (`config/mips/mips.c`; no line read
  from the shipped tree) · **Constants** 8 register arguments, 8-byte slots, 16-byte rounding
* **Falsifies** the assumption that outgoing stack arguments are 4-byte slots, and that `args=` is only
  4-byte aligned
* **Lever** read the call shape out of `args=`: 16 means nine or ten arguments, 32 means eleven or twelve;
  and when a frame differs by 8 or 24 bytes, check the 16-byte rounding before adding a variable
* **Floats use a separate budget**: up to eight `float` arguments travel in **`$f12`–`$f19`**, so a call with
  eight ints and four floats fills `$4`–`$11` *and* `$f12`–`$f15` at once. A `long long` or `double` occupies
  **a single 64-bit GPR** from the same `$4`–`$11` sequence (`dli $4,1` / `dli $5,2` for two `long long`s;
  a callee reads `long long z` with `daddiu a0,a0,1`) — not a register pair.
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`: one to sixteen integer arguments, up to ten floats, mixed
  int/float calls, and `long long`/`double` arguments; varargs and structure arguments were not measured

---

## L-EE-029 · Single precision is hardware, double precision is soft-float

| operation | code |
| --- | --- |
| `float` `+`/`*` | `add.s` / `mul.s` — COP1 |
| `float` conversion | `mtc1` + `cvt.s.w`, `trunc.w.s` + `mfc1` |
| `double` `+`/`-`/`*`/`/` | **`jal dpadd` / `dpsub` / `dpmul` / `dpdiv`** |
| `double` compare | `jal dpcmp` |
| `double` → `int`/`unsigned` | `jal dptoli` / `dptoul` |
| `int`/`float` → `double` | `jal litodp` / `fptodp` |
| `double` → `float` | `jal dptofp` |

Every one of those is an **out-of-line libgcc call**, so a target that does `double` arithmetic contains `jal
dpadd`-style calls and **no `add.d`**. `-mhard-float` does not change it; `-msoft-float` additionally moves
single precision to software; `-O3` behaves like `-O2`.

* **Tier T2** · **Source anchor** the port's `TARGET_` macros and libgcc (`config/mips/mips.h`; no line read
  from the shipped tree) · **Constants** the relocation names `dpadd`, `add.s`
* **Falsifies** the expectation that `add.d` can appear in this build, and that `-mhard-float` gives hardware
  doubles
* **Lever** this is the sharpest fingerprint for a `float`/`double` mix-up: if the target has `jal dpadd` and
  your candidate has `add.s`, a literal like `2.0` that should be `2.0f` (or a variable typed `double`) is the
  usual cause — and the reverse
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0` plus `-mhard-float`/`-msoft-float`/`-O3`, one-operation
  synthetic functions

---

## L-EE-030 · Aggregates: 8 bytes by value, larger by reference; returns use a hidden pointer

Judged from the **callee** side, `-O2 -G0`:

| aggregate | size | prologue | convention |
| --- | ---: | --- | --- |
| `struct { int a; }` | 4 | `move v0,a0` | **by value** in `$4` |
| `struct { char c[8]; }` | 8 | `sd a0,0(sp)` then `lb v0,7(sp)` | **by value** |
| `struct { short a,b,c,d; }` | 8 | `sd a0,0(sp)` then `lh v0,0(sp)` | **by value** |
| `struct { int a,b,c; }` | 12 | `lw t7,0(a0)` | **by reference** |
| `struct { int a,b,c,d; }` | 16 | `lw t5,0(a0)` | **by reference** |
| `struct { char c[9]; }` | 9 | `ldl t4,7(a0)` | **by reference** |

The boundary is **8 bytes inclusive**. For a **returned** aggregate the compiler uses a hidden pointer in
`$4`, which shifts every other argument one slot:

```asm
make8(int x):                 ; S8 make8(int x)
    addiu t7,a1,1             ; x is read from $5 - $4 is the return slot
    sw    a1,0(a0)
    sw    t7,4(a0)
    move  v0,a0               ; the pointer comes back in $2
```

* **Tier T2** · **Source anchor** the aggregate part of the EE EABI (`config/mips/mips.c`; no line read from
  the shipped tree) · **Constant** the 8-byte boundary
* **Falsifies** the assumption that a small structure travels in a register pair, and that a
  structure-returning function's first argument is in `$4`
* **Lever** `lw …,0($4)` in the target's prologue ⇒ a >8-byte aggregate by reference; `sd $4,0($sp)` followed
  by stack reads ⇒ a ≤8-byte aggregate by value. And when the target returns a structure, count the
  arguments one slot later — `$4` is the return pointer
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic 4/8/9/12/16/32-byte aggregates, callee and caller
  side; unions, bitfields and varargs were not measured

---

## L-EE-031 · A variadic function saves the argument registers and calls `__builtin_va_start`

| function | named | saved argument registers | count |
| --- | ---: | --- | ---: |
| `v1(const char *a, ...)` | 1 | `a1 a2 a3 t0 t1 t2 t3` (`$5`–`$11`) | **7** |
| `v2(const char *a, int b, ...)` | 2 | `a2 a3 t0 t1 t2 t3` | **6** |
| `v5(a,b,c,d,e, ...)` | 5 | `t1 t2 t3` | **3** |

The count is **8 − (named parameters)**, each in an **8-byte slot**, placed after the callee-save area (so the
offsets move from function to function). Every variadic function also calls **`__builtin_va_start`**, which
shows up as a relocation — the hardest evidence that a function is variadic.

There is **no floating-point save area**: a `double`-returning variadic function saves only integer registers,
and its caller passes a variadic `1.5f` or `1.5` **as a double in `a1`** (`li a1,2047` then `dsll32 a1,a1,0x13`)
— in the integer register sequence, not in `$f12`
([L-EE-028](LAWS.md#l-ee-028--eight-integer-arguments-travel-in-4-11-and-eight-float-arguments-in-f12-f19-a-long-long-or-double-takes-one-64-bit-gpr-the-rest-go-on-the-stack-in-8-byte-slots)).

* **Tier T2** · **Source anchor** the backend prologue (`config/mips/mips.c`; no line read from the shipped
  tree) · **Constants** the `__builtin_va_start` relocation, the count 7
* **Falsifies** the expectation that a variadic function has an FP register save area and passes its floats in
  `$f12`
* **Lever** a run of `sd` from `a1`–`t3` into consecutive 8-byte slots means *this function is variadic*; and
  at a variadic call site, compare floating-point arguments against `$4`–`$11`, not `$f12`
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic variadic functions with 1/2/5 named parameters; the
  `va_list` layout itself was not decoded

---

## L-EE-032 · Division: hardware `div`, no magic-number constants, 64-bit is libgcc

| expression | code |
| --- | --- |
| `a/b` signed / unsigned | `div` / `divu`, then **`beql $r,$0` + `break 7`** (the zero check), then `mflo` |
Two naming details: the compiler's assembly writes the check as `beql` while objdump prints `beqzl` (same
instruction), and a **constant** divisor carries `break 7` but **no branch** — the divisor is known non-zero,
so the branch is what marks a divisor the compiler cannot prove non-zero.

| `a%b` | the same, ending in **`mfhi`** |
| `a*b` (32-bit) | `mult` + `mflo` — hardware |
| `a/8` signed | `slti` + `movn` + `sra` — no `div` |
| `a/8` unsigned | `srl` |
| `a%8` signed / unsigned | `slti`+`movz`+`sra`+`sll`+`subu` / `andi` |
| **`a/3`, `a/-7`** | **`li $r,3` + `div`** — **no reciprocal multiplication** |
| `long long` `/`, `%`, `*` | `jal __divdi3`, `__moddi3`, **`__muldi3`** |
| `unsigned long long` `/`, `%` | `jal __udivdi3`, `__umoddi3` |

Two things worth knowing: a runtime division is a **three-instruction unit** (`div`/`divu` + `beqzl`+`break` +
`mflo`/`mfhi`), so the trap is not separate logic; and this build has **no magic-number transformation** — a
non-power-of-two constant divisor stays `li` + `div`, which is a direct read on what the source divided by.
Every 64-bit operation is a libgcc call, **including multiplication**, unlike the 32-bit `mult`.

* **Tier T2** · **Source anchor** the MIPS division patterns and libgcc fallbacks (`config/mips/mips.md`; no
  line read from the shipped tree) · **Constants** the relocation names and `break`
* **Falsifies** the expectation that constant division becomes a multiply by a magic number, and that 64-bit
  multiplication is inline
* **Lever** `li`+`div` in the target ⇒ the source divided by a non-power-of-two constant; `slti`/`movn`/`sra`
  ⇒ by a power of two; `jal __divdi3`/`__muldi3` ⇒ the source used `long long` (the same kind of signal as
  `jal dpadd` for `double`)
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic one-operation functions with signed and unsigned
  operands and constant divisors 2, 3, 8 and −7

---

## L-EE-033 · The data model: 4-byte pointers, **8-byte `long`**

| type | size | | type | size |
| --- | ---: | --- | --- | ---: |
| `char` | 1 | | pointer | **4** |
| `short` | 2 | | `float` | 4 |
| `int` | 4 | | `double` | 8 |
| **`long`** | **8** | | `long double` | **8** |
| `long long` | 8 | | | |

The default is **`-mlong64`** — only `-mlong32` makes `long` 4 bytes — so a `long` field is loaded and stored
with `ld`/`sd` and 64-bit arithmetic on a `long` goes to libgcc just like `long long`
([L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc)).

Alignment equals the type's size, so an 8-byte member is 8-aligned:

| struct | offsets | size |
| --- | --- | ---: |
| `{char a; int b;}` | a@0, b@4 | 8 |
| `{char a; short b; int c;}` | a@0, b@2, c@4 | 8 |
| `{char a; double d;}` | a@0, **d@8** | 16 |
| `{char a; long l;}` | a@0, **l@8** (`sd`) | 16 |
| `{char a; long l; int i; void *p;}` | a@0, **l@8**, i@16, p@20 | 24 |

* **Tier T2** · **Source anchor** the port's size macros (`config/mips/mips.h`; no line read from the shipped
  tree) · **Constants** 8 for `long`, 4 for a pointer, 8 for `long double`
* **Falsifies** the assumption that a 32-bit-pointer target has a 32-bit `long` (the usual ILP32 model)
* **Lever** `ld`/`sd` on a field in the target ⇒ that field is `long`/`long long`/`double`, not `int`; a
  struct whose size disagrees with your reconstruction is usually a `long` vs `int` or 8-byte-alignment
  mistake
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic types and structs; bitfields and
  `__attribute__((packed))` were not measured

---

## L-EE-034 · `-Os` is this project's most common level, and the rules hold there

`config/source_flags.tsv` counts **687 files at `-Os`**, 542 at `-O1`, 264 at `-O2` and 98 at `-O3` — so
`-Os`, not `-O2`, is the reference level here. Running the handbook's own fixtures at that level:

```sh
python3 tools/compiler/ee-gcc-observe.py --selftest --flags="-Os -G0"   # 34 passed / 0 failed
```

So the frame rule, the switch threshold (4 cases chain, 5 and 6 table), the inlining gate, the float/double
constant forms and the division idioms all behave as documented at `-Os`. The same suite at `-O1` and `-O3`
fails exactly one fixture each, and both failures are behaviour the handbook already predicts: `-O1` keeps an
upward loop comparison ([L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled)) and `-O3` inlines a plain `static` helper
([L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined)).

One thing does differ: **`-Os` aligns functions to 4 bytes** where `-O2` emits `.p2align 3,,7` (8 bytes)
([L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)). The project's `-falign-functions=4` masks this, but a unit built without
that flag will not match.

* **Tier T2** · **Source anchor** `toplev.c:3316` (the level chooses the pipeline, [L-EE-020](LAWS.md#l-ee-020--the-pass-pipeline-is--o-sensitive)) ·
  **Constants** 687 files at `-Os`, 4-byte alignment
* **Falsifies** the assumption that `-O2` is the reference level for this project, and that `-Os` pads
  functions like `-O2`
* **Lever** run the fixtures at the unit's real level before concluding a rule does not hold; and when a size
  or offset mismatches, remember `-Os` implies 4-byte alignment
* **Scope** `ee-gcc 3.2-ee-040921` at `-O1`/`-O2`/`-Os`/`-O3` with `-G0`; the fixture suite covers the laws
  it asserts, not every rule in the handbook

---

## L-EE-035 · Bitfields: LSB-first, no 32-bit straddling, narrowed reads and masked writes

| structure | size | layout |
| --- | ---: | --- |
| `{unsigned a:1; b:3; c:12; d:16;}` | **4** | bits 0, 1, 4, 16 |
| `{int a:1; b:3; c:12; d:16;}` | **4** | same |
| `{unsigned char a:3; b:5;}` | **1** | container = `unsigned char` |
| `{unsigned short a:4; b:12;}` | **2** | container = `unsigned short` |
| `{unsigned a:20; b:20;}` | **8** | **no straddling** — the second field starts in the second word |

Reads are **narrowed to the smallest aligned access**:

| field | code |
| --- | --- |
| unsigned 3-bit at bit 1 | `lw` + `srl 1` + `andi 0x7` |
| unsigned 16-bit at bit 16 | a bare **`lhu $2,2($4)`** |
| **signed** 12-bit at bit 4 | **`lh $2,0($4)` + `sra 4`** |
| 5 bits inside `unsigned char` | `lbu` + `srl 3` |

Writes are **masked read-modify-writes**, and the mask comes from a **64-bit immediate**:

```asm
lw   $14,0($4)
li   $15,-65536        # 0xffffffffffff0000
ori  $15,$15,0xf
and  $14,$14,$15       # clear
sll  $5,$5,4
or   $14,$14,$5        # insert
sw   $14,0($4)
```

* **Tier T2** · **Source anchor** `stor-layout.c` plus the backend's access patterns (no line read from the
  shipped tree) · **Constants** the mask −65536, sizes 4 and 8
* **Falsifies** the assumption that every bitfield read is a masked `lw` (aligned fields use a narrower load)
  and that a write is a shift-and-insert
* **Lever** `lh`/`lbu` + `sra` ⇒ a **signed** bitfield; `lw` + `srl` + `andi` ⇒ an unsigned one; a bare `lhu`
  ⇒ an aligned 16-bit field; `li` with a negative value before `and`/`or` ⇒ a bitfield **write**
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic 1- to 20-bit fields in `char`, `short` and `int`
  containers; `packed` and fields wider than their container were not measured

---

## L-EE-036 · Tail calls are jumps — but not below `-O2`

`int t1(int a) { return g(a); }`:

| level | code |
| --- | --- |
| `-O0`, **`-O1`** | `jal g` + `j $31` |
| **`-O2`**, `-Os`, `-O3` | **`j g`** — no `jal`, no `jr $31` |

The switch is `-foptimize-sibling-calls`, off below `-O2`: adding it to `-O1` produces `j g`, and
`-O2 -fno-optimize-sibling-calls` restores `jal` + `j $31`. **542 files in this project are built at `-O1`**,
so they contain no tail calls at all.

Every tail position tested becomes a jump at `-O2`: `return g(a)`; with a local (`int x = a+1; return g(x)`);
**both** branches of an `if`/`else` returning from different calls; a `void` call; and `return g(*p)`.

* **Tier T2** · **Source anchor** `calls.c` plus the backend sibcall patterns (no line read from the shipped
  tree) · **Constants** the two forms above
* **Falsifies** the expectation that a function's calls all appear as `jal`, and that the level does not change
  call shape
* **Lever** a target that jumps straight to an external symbol where you expected a call is making a **tail
  call** (level ≥ `-O2`); conversely, at `-O1` every call keeps `jal` + `j $31`, so a reconstruction that
  drops those two instructions is wrong about the level
* **Scope** `ee-gcc 3.2-ee-040921` at `-O0`/`-O1`/`-O2`/`-Os` with `-G0`, synthetic one-call functions

---

## L-EE-037 · `volatile` is visible as unmerged accesses

| source | without `volatile` | with `volatile` |
| --- | --- | --- |
| `*p = *p + 1; *p = *p + 1;` | **one** `lw`, `addu …,2`, one `sw` | **two** `lw` / `addu …,1` / `sw` triples |
| `int a = *p; int b = *p; return a+b;` | **one** `lw` (CSE) | **two** `lw` |
| `gi = gi + 1;` | `lw`, `addu 1`, **`j $31`**, `sw` — store sunk into the delay slot | `lw`, `addu 1`, **`sw`**, `j $31` — order kept |

Two usable judgements:

1. **How many loads**: two `lw` from the same address in the target ⇒ the source read it twice through a
   `volatile` pointer (or a call sits between the reads). Without `volatile` the compiler merges them.
2. **Where the store sits**: without `volatile` a store is often sunk into the following `j $31` delay slot;
   with it, the `sw` stays **before** the jump.

`-Os` produces exactly the same shapes.

* **Tier T2** · **Source anchor** volatility is honoured across the RTL passes (no line read from the shipped
  tree) · **Constants** the merged `addu …,2` against two `addu …,1`
* **Falsifies** the assumption that repeated reads are always separate instructions, and that `volatile` only
  reorders accesses rather than changing how many there are
* **Lever** when your reconstruction has one fewer load than the target, suspect a missing `volatile`; adding
  one wrongly adds a load and shifts every following instruction
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2`/`-Os` with `-G0`; volatile bitfields and atomic builtins were not
  measured

---

## L-EE-038 · Aggregate copies: unrolled to 32 bytes, then an inline `ldl/ldr` loop — never `memcpy`

`void f(struct S *d, struct S *s) { *d = *s; }` at `-O2 -G0`:

| size | form | instructions |
| ---: | --- | ---: |
| 4–**32** | fully unrolled `lw`/`sw` pairs | 2 per word + 2 |
| **36**–256 | **inline loop**: `ldl`/`ldr` + `sdl`/`sdr`, **16 bytes per iteration** | 14–20 |

```asm
        ldl     t3,7(a1)      # unaligned 64-bit load (low pair)
        ldr     t3,0(a1)      #                      (high pair)
        ldl     t4,15(a1)
        ldr     t4,8(a1)
        sdl     t3,7(a0)
        sdr     t3,0(a0)
        ...
        addiu   a1,a1,16
        bne     a1,t7,4 <f+0x4>
```

**No `memcpy`/`memmove` at any size tested (up to 256 bytes)** — the backend expands the copy itself.

* **Tier T2** · **Source anchor** `expr.c` and the backend's movstr patterns (no line read from the shipped
  tree) · **Constants** 32 bytes and 16 bytes per iteration
* **Falsifies** the expectation that a large structure assignment becomes a `memcpy` call, and that copies
  use the aligned `ld`/`sd` pairs
* **Lever** an `ldl`/`ldr`-`sdl`/`sdr` loop in the target ⇒ a copy of **more than 32 bytes**; a run of
  `lw`/`sw` ⇒ a **≤32-byte** copy. Do not confuse `ld`/`sd` (aligned, for `long`/`double`) with
  `ldl`/`ldr`/`sdl`/`sdr` (unaligned, for these loops)
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, 4- to 256-byte structures; structs with padding and
  constant-size `memcpy` were not measured separately

---

## L-EE-039 · Indirect calls are `jalr`, and never become tail jumps

| source | code |
| --- | --- |
| `gfp(a)` — global function pointer | `lw $2,%lo(gfp)($15)` then **`jalr $2`** |
| `v->fn(a,b)` — struct field | `lw $2,0($4)`, set up the arguments, **`jalr $2`** |
| `fp(a)` — parameter | `move $2,$4` then **`jalr $2`** |
| `f()` — void pointer | **`jalr $4`** |

The target travels in an **ordinary allocated register** (`$2`, `$4` measured) — not `$25`/`t9`. The object
disassembles the instruction as **`jalr`**; the assembly writes it as **`jal $31,$reg`**.

**Sibling calls cover direct calls only.** In tail position:

```asm
d:  # return g(a);     direct
        sd      $31,0($sp)
        ld      $31,0($sp)
        j       g              # a bare tail jump
i:  # return gp(a);    indirect
        sd      $31,0($sp)
        lw      $2,%lo(gp)($15)
        jal     $31,$2         # still a real call
        ld      $31,0($sp)
        j       $31            # and still a return
```

`-O1`, `-O2` and `-Os` produce the same shape, so an indirect call says nothing about the level.

* **Tier T2** · **Source anchor** the MIPS backend's indirect-call pattern (no line read from the shipped
  tree) · **Constants** `jalr` and `jal $31,$reg`
* **Falsifies** the expectation that an indirect tail call becomes a jump like a direct one, and that the
  target travels in `$25`/`t9`
* **Lever** a `jalr` with a following `j $31` in the target ⇒ the source called through a **function
  pointer**; if you reconstruct it as a named call it becomes a bare tail jump at `-O2` and the whole shape
  changes
* **Scope** `ee-gcc 3.2-ee-040921` at `-O1`/`-O2`/`-Os` with `-G0`, pointer calls through a global, a struct
  field and a parameter

---

## L-EE-040 · Comparison idioms: materialised as values, branched as conditions

`-O2` and `-Os` are **identical** here.

| expression (result used as a value) | code |
| --- | --- |
| `a == b` | `xor` + **`sltu $r,$r,1`** |
| `a != b` | `xor` + **`sltu $r,$0,$r`** |
| `a == 0` / `a != 0` / `!a` | **`sltu $r,$a,1`** / `sltu $r,$0,$a` / `sltu $r,$a,1` |
| `a < b` signed / unsigned | `slt` / `sltu` |
| `a > b` | `slt` with the **operands swapped** |
| `a <= b` | `slt(u)` with swapped operands + **`xori $r,$r,0x1`** |
| `a && b` | `sltu $r,$0,$b` + **`movz`** — **branchless** |
| `a \|\| b` | **branchy**: `bne`, `beq`, `li $2,1` |
| `a<b ? a : b` | `slt` + **`movz`** |

Used as a **condition** it usually branches: `if (a == b) return g();` is a bare **`bne $4,$5,$L`** with no
`xor`/`sltu`. But when **both arms are simple values** the compiler converts the `if` into a **branchless
select** — `if (a == b) return 1; return 2;` becomes `xor $4,$4,$5` then `movn $2,$15,$4`. So a materialised
`xor` paired with `movn`/`movz` can come from either a ternary or an `if`. Which conditional move is chosen
is **not fixed** — `-O2` uses `movn` with the constants in one order and `-O1` uses `movz` with them swapped — so
compare on the *shape* (branchless select), not on one mnemonic.

Three things that look "almost right" in a diff:

1. `==` is **not** `beq` — as a value it is `xor` + `sltu` against 0/1;
2. `<=` is **not** one instruction — it is an operand-swapped `<` followed by `xori 1`;
3. **`&&` is branchless (`sltu`+`movz`) while `||` is branchy** — they are not symmetric, and min/max use
   `movz` rather than branches.

* **Tier T2** · **Source anchor** the backend's comparison and conditional-move patterns (no line read from
  the shipped tree) · **Constants** the `1` in `sltu` and in `xori`
* **Falsifies** the expectation that `==` compiles to `beq`, that `<=` is a single comparison, and that
  `&&`/`||` compile the same way
* **Lever** `xor`+`sltu` or `xori 0x1` in the target ⇒ the comparison's **result was used as a value**;
  a bare `bne`/`beq` ⇒ it was a **condition**
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2`/`-Os` with `-G0`, one-expression functions; 64-bit and
  floating-point comparisons were not measured

---

## L-EE-041 · 128-bit containers: `lq`/`sq`, a register pair, and no by-value return

**1141 reconstructed source files in this project use `mode(V4SI)`** (`s128`/`u128`) — about a third of them —
so this is the codegen those types produce. `-O2` and `-Os` are identical.

| operation | code |
| --- | --- |
| `v4si x = *p;` | **`lq $2,0($4)`** — 128-bit load |
| `*p = v;` | **`sq $5,0($4)`** — 128-bit store |
| `*d = *s;` (16 bytes) | **`lq $15,0($5)` + `sq $15,0($4)`** — one 128-bit move |
| `((int*)p)[i]` / `… = v` | `sll` + `addu` + **`lw`** / **`sw`** |
| element 0 | `dsll $4,$4,32` + `dsra $4,$4,32` (sign-extract from the 64-bit register) |
| elements 1 or 3 | **`sq $4,0($sp)`** then `lw $2,4($sp)` / `lw $2,12($sp)` |
| passing a `v4si` | in a **register pair** from `$4`; forwarding it needs no work |

**The discriminator** — the same 16 bytes:

| source | code |
| --- | --- |
| `struct S16 { int a,b,c,d; } *d = *s;` | unrolled `lw`/`sw` pairs ([L-EE-038](LAWS.md#l-ee-038--aggregate-copies-unrolled-to-32-bytes-then-an-inline-ldlldr-loop--never-memcpy)) |
| `v4si *d = *s;` | **`lq` + `sq`** |

So `lq`/`sq` in the target means the source used a **128-bit type** at that spot — which is exactly why m2c
emits `V4SI` for these positions.

**Two hard limits.** A 128-bit value **cannot be returned by value**: the compiler errors with
`output_operand: invalid expression as operand`, so a target function returning 16 bytes by value must be a
**structure** with a hidden pointer ([L-EE-030](LAWS.md#l-ee-030--aggregates-8-bytes-by-value-larger-by-reference-returns-use-a-hidden-pointer)), never a vector. And **vector
arithmetic does not exist in 3.2** (`a + b` on two vectors is an error) — these types are opaque 128-bit
containers.

* **Tier T2** · **Source anchor** the EE-specific `lq`/`sq` patterns (no line read from the shipped tree) ·
  **Constants** the mnemonics `lq` and `sq`
* **Falsifies** the assumption that a 16-byte copy always unrolls into `lw`/`sw` pairs, and that a 128-bit
  value can be returned by value like a structure
* **Lever** `lq`/`sq` in the target ⇒ a 128-bit type at that spot; and if you reconstruct a 16-byte return as
  a vector the compiler will refuse — use a structure
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2`/`-Os` with `-G0`, synthetic `mode(V4SI)` load/store/copy/element
  and parameter cases; ABI slots beyond the first pair and unaligned `lq`/`sq` were not measured

---

## L-EE-042 · `float` lives in COP1, `double` lives in general registers

**41 % of this project's reconstructed files use `f32` (1389) or `f64` (1390)**, so being able to tell the two
apart at a glance matters.

| operation | `float` | `double` |
| --- | --- | --- |
| global load | **`l.s $f0,%lo(gf)($15)`** | **`ld $2,%lo(gd)($15)`** — a **GPR** |
| global store | **`s.s $f12,…`** | **`sd $4,…`** |
| arithmetic | `add.s`/`sub.s`/`mul.s`/`div.s` — COP1 | `jal dpadd`/`dpsub`/`dpmul`/`dpdiv` |
| compare | **`c.lt.s` + `bc1t`** | **`jal dpcmp`** + an integer compare |
| `int` → | `mtc1` + `cvt.s.w` | `jal litodp` |
| → `int` | `cvt.w.s` + `mfc1` | `jal dptoli` |
| float ↔ double | `jal fptodp` / `dptofp` | same |
| compare with 0 | `mtc1 $0,$f0` + `c.eq.s` | `dpcmp` |

**The fastest way to type a value in a target**: `l.s`/`s.s`/`c.*.s`/`bc1t` ⇒ **`float`**; `ld`/`sd` into a GPR
followed by `jal dp*` ⇒ **`double`**. And do **not** look for `l.d` or `c.lt.d` — this build has no COP1
double-precision instructions at all ([L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float)).

* **Tier T2** · **Source anchor** the port's mode patterns (no line read from the shipped tree) ·
  **Constants** `l.s`, `dpadd`, `bc1t`
* **Falsifies** the expectation that `double` uses COP1 like `float`, and that a double comparison is a
  `c.lt.d` instruction
* **Lever** this is the type discriminator for the ~40 % of files that use floating point; it complements
  [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)/[L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) (constants) and
  [L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float) (operation lowering)
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic single-operation functions; float arrays, struct
  members and variadic floats were not measured separately

---

## L-EE-043 · 64-bit integers are native; only multiply, divide and modulo call out

**41 % of this project's files use `s64`/`u64`.** Unlike `double`, a 64-bit *integer* uses the R5900's native
64-bit GPR instructions — measured at `-O1`, `-O2` and `-Os` alike, with **no libgcc relocation at all** in the
test set.

| operation | code |
| --- | --- |
| `a + b` / `a - b` / `a + 1` | **`daddu`** / **`dsubu`** / **`daddiu`** |
| `-a` | `dsubu $r,$0,$a` |
| `a << 4`, `a << n` | **`dsll`** |
| `a >> 4` signed / unsigned | **`dsra`** / **`dsrl`** |
| `&`, `|`, `^` | `and` / `or` / `xor` |
| `a < b` | **`slt`** — an inline 64-bit compare |
| `a == b` | `xor` + `sltu …,1` ([L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)) |
| `int` → `long long` | **`move`** — the ABI already sign-extends a 32-bit argument |
| `long long` → `int` | **`dsll $r,$r,32` + `dsra $r,$r,32`** |
| `unsigned` → `long long` | `dsll …,32` + **`dsrl …,32`** |

So within the same 64-bit type the shape depends on the operation: `daddu`/`dsll`/`slt` are inline, while
**multiply, divide and modulo become `jal __muldi3` / `__divdi3` / `__moddi3`**
([L-EE-032](LAWS.md#l-ee-032--division-hardware-div-no-magic-number-constants-64-bit-is-libgcc)).

The `dsll …,32` + `dsra …,32` pair is the **"narrow a 64-bit value to 32 bits"** idiom — the same one that
extracts element 0 of a 128-bit vector ([L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return)), so seeing it tells you a 64-bit
value is being reduced to `int`.

* **Tier T2** · **Source anchor** the EE-specific 64-bit GPR patterns (mainline MIPS would call libgcc; no line
  read from the shipped tree) · **Constants** `daddu`, `dsll`, and the 32 in `dsll`/`dsra`
* **Falsifies** the assumption that 64-bit integer arithmetic is out of line like `double`, and that a 64-bit
  compare needs a helper
* **Lever** `daddu`/`dsubu`/`dsll`/`dsra`/`dsrl`/`slt` in the target ⇒ a 64-bit integer type
  ([L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long)); `dsll …,32` + `dsra …,32` ⇒ that value is being narrowed to 32 bits
* **Scope** `ee-gcc 3.2-ee-040921` at `-O1`/`-O2`/`-Os` with `-G0`, synthetic one-operation functions over
  `long long`/`unsigned long long`

---

## L-EE-044 · Unaligned access: three sources, and `ulw`/`usw` do not exist in the object

| source | assembly | **object** |
| --- | --- | --- |
| pointer cast `*(int*)(p+1)` | `lw $2,1($4)` | **a plain `lw` at offset 1** — the cast is trusted, nothing is synthesised |
| `memcpy(d,s,4)` | `lwl $12,3($5)` + `lwr $12,0($5)` | `lwl`+`lwr`; stored with `swl`+`swr` |
| `memcpy(d,s,8)` | `ldl`+`ldr` | `ldl`+`ldr`; stored with `sdl`+`sdr` |
| `__attribute__((packed))` member | **`ulw $2,1($4)`** / **`usw $5,1($4)`** | **`lwr`+`lwl` / `swr`+`swl` pair** |

**The trap**: `ulw`/`usw` are **assembler pseudo-instructions**. The assembly writes `ulw $2,1($4)`, but the
object contains

```asm
lwr     v0,1(a0)
jr      ra
lwl     v0,4(a0)      # note the +3 offset
```

so **grepping a disassembly for `ulw`/`usw` finds nothing** — you only ever see the `lwl`/`lwr` pair. (Same
family of traps as 2.96's `li.s`, `beql` printed as `beqzl`, and `jalr` written as `jal $31,$reg`.)

Constant-size `memcpy` forms a ladder: 1 → `lbu`/`sb`; 2 → `lb`/`sb` twice; 4 → `lwl`/`lwr` + `swl`/`swr`;
8 → `ldl`/`ldr` + `sdl`/`sdr`; 16 → two of each.

* **Tier T2** · **Source anchor** the EE-specific unaligned patterns (no line read from the shipped tree) ·
  **Constants** `lwl` and the pseudo-instruction `ulw`
* **Falsifies** the expectation that an unaligned pointer cast is handled by the compiler, and that `ulw`/`usw`
  exist in the object
* **Lever** an `lwl`+`lwr` (or `swl`+`swr`) pair ⇒ a 4-byte unaligned access, from either a constant-size
  `memcpy` **or** a packed member — they are the same shape in the object, so use the base and offset pattern to
  tell them apart; a plain `lw` at a non-multiple-of-4 offset ⇒ the source cast a pointer
* **Scope** `ee-gcc 3.2-ee-040921` at `-O1`/`-O2`/`-Os` with `-G0`, synthetic pointer-cast, constant-`memcpy`
  and packed-structure functions; unaligned `double` and 128-bit accesses were not measured

---

## L-EE-045 · Loop back edges are branch-likely; forward branches are not

| source | branch form |
| --- | --- |
| `if (p == 0) return -1;` | **`beq`** — plain |
| `if (x) …`, `if (a && b) …`, if/else chains | `beq` / `bne` — plain |
| `while (n--) …` | `beq` guard + **`bnel`** back edge |
| `for (i=0;i<n;i++)` | `blez` guard + **`bnel`** back edge |
| `do { … } while (n > 0);` | **`bgtzl`** |
| `while (*p == 0) p++;` | `bne` + **`beql`** |

The likely form's **delay slot runs only when the branch is taken**, which is why a `bnel` at the bottom of a
loop can carry the loop's own work — at `-O1` the same loop puts its `mult` in that slot.

Two practical points:

* **`bnel`/`beql`/`bgtzl` at the end of a body ⇒ a loop.** A candidate that produces `bne`+`nop` there has a
  different loop shape (or the `-Os` restructure, which turns one loop into `bne` plus an unconditional `b`).
* The assembly writes **`beql`/`bnel`** while **objdump prints `beqzl`/`bnezl`** against `$0` — grep for both.

**Instruction mix of this codebase** (170 random matched sources, each at its own level):

```
addiu 384  move 322  ld 267  sd 235  jal 185  li 131  jr 123  lw 87  lui 84  nop 64
j 60  sw 56  addu 54  sh 30  lh 28  sll 27  sb 27  beqz 26  mult 22  slti 21 …
```

`ld`/`sd` rank third and fourth — this codebase moves **64-bit data** more than 32-bit
([L-EE-033](LAWS.md#l-ee-033--the-data-model-4-byte-pointers-8-byte-long)), and `move` is second.

* **Tier T2** · **Source anchor** the EE/MIPS branch-likely patterns (no line read from the shipped tree) ·
  **Constants** `bnel` and the objdump spelling `beqzl`
* **Falsifies** the expectation that a loop back edge uses the same branch form as an `if`, and that `beql`
  always appears as `beql` in a disassembly
* **Lever** a likely branch at the bottom of a body ⇒ a loop; and when a candidate's loop differs by two
  instructions, look at whether the back edge is likely in the target
* **Scope** `ee-gcc 3.2-ee-040921` at `-O1`/`-O2`/`-Os` with `-G0`, synthetic loops plus a 170-file sample;
  branch-prediction annotations were not measured

---

## L-EE-046 · Every `move` is a 64-bit `daddu`

Decoding the object words: **`move` is always `daddu $d,$s,$0` (funct `0x2d`)**, never `addu` (funct
`0x21`) — even when the C type is `int`.

| function | type | word | meaning |
| --- | --- | --- | --- |
| `int b = a;` | 32-bit | `0080102d` | `daddu v0,a0,zero` |
| `long long b = a;` | 64-bit | `0080102d` | `daddu v0,a0,zero` |
| `int x = 0;` | 32-bit | `0000102d` | `daddu v0,zero,zero` |

**The trap**: objdump **prints `daddu $d,$s,$0` as `move`**, so

* a mnemonic histogram of real code shows **`move` 322 times and `daddu` not once** (the 170-file sample of
  [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not)) — `daddu` only appears when the third operand is not `$0`;
* writing `addu $d,$s,$0` in a reconstruction **will not match the bytes**, even though the mnemonic `move`
  looks the same.

In practice (125 `move`s over 60 real files): **48 (38 %) sit in branch or jump delay slots**, 57 are ordinary,
19 are `move $d,$0` (zero), and the targets are dominated by argument registers — `a0` 46, `a1` 18, `a2` 7 —
so most copies are **argument shuffling**.

* **Tier T2** · **Source anchor** the port's move pattern (no line read from the shipped tree; the rule comes
  from decoding the object words) · **Constants** funct `0x2d` versus `0x21`
* **Falsifies** the assumption that `move` expands to `addu`, and that the mnemonic tells you whether a copy is
  32-bit or 64-bit
* **Lever** verify copies by their **encoding**, not their mnemonic; an argument swap appears as a temporary
  plus three `move`s, and the tail call after it is a `j`
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, object-word decoding of 32/64-bit copies plus a 60-file
  context sample; moves of floating-point and vector values were not measured

---

## L-EE-047 · The printed mnemonic is an alias — compare encodings, not spellings

Decoding object words at `-O2 -G0`:

| source | printed | **actual encoding** |
| --- | --- | --- |
| `return 5;` | `li v0,5` | **`ADDIU $2,$0,5`** |
| `return -5;` | `li v0,-5` | `ADDIU $2,$0,0xfffb` |
| `return 0xffff;` | `li v0,0xffff` | **`ORI $2,$0,0xffff`** (zero-extending) |
| `return 0x12345;` | `lui v0,0x1` + `ori v0,v0,0x2345` | two real instructions — **no `li` alias** |

**`li` is a pseudo-instruction**: signed-16-bit values become `ADDIU`, up to `0xffff` becomes `ORI`, larger
values become a `lui`+`ori` pair that objdump prints as two instructions.

A census over **60 real matched sources** shows the mapping is many-to-one:

| encoding | mnemonics printed |
| --- | --- |
| `op=0x09` (ADDIU) | `addiu` ×110 / **`li` ×35** |
| `SPECIAL fn=0x00` (SLL) | **`nop` ×23** / `sll` ×3 |
| `op=0x04` (BEQ) | **`beqz` ×7** / `b` ×2 |
| `op=0x05` (BNE) | **`bnez` ×3** / `bne` ×1 |

…while **no mnemonic maps to two base encodings** in the sample. The verified alias table now collected by this
handbook:

| shown as | base instruction | law |
| --- | --- | --- |
| `li $r,imm` (small / ≤0xffff) | `ADDIU` / `ORI` | this one |
| `li` (larger) | `LUI` + `ORI` | this one |
| `move $d,$s` | **`DADDU $d,$s,$0`** | [L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu) |
| `nop` | `SLL $0,$0,0` | this one |
| `beqz` / `bnez` / `b` | `BEQ $r,$0` / `BNE $r,$0` / `BEQ $0,$0` | this one |
| `ulw` / `usw` | `LWR`+`LWL` / `SWR`+`SWL` | [L-EE-044](LAWS.md#l-ee-044--unaligned-access-three-sources-and-ulwusw-do-not-exist-in-the-object) |
| `beql`/`bnel` against `$0` | printed `beqzl`/`bnezl` | [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) |
| `jal $31,$reg` | `jalr` | [L-EE-039](LAWS.md#l-ee-039--indirect-calls-are-jalr-and-never-become-tail-jumps) |
| `li.s` (2.96) | an explicit load sequence | [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool) |

* **Tier T2** · **Source anchor** the assembler's pseudo set (no line read from the shipped tree; the table
  comes from decoding object words) · **Constants** opcodes `0x09` and `0x0d`
* **Falsifies** the expectation that a mnemonic identifies an encoding, and that `li` is a real instruction
* **Lever** when two streams look identical as text but differ in bytes, compare encodings; and before writing
  assembly to match a target, work out how many real instructions your pseudo expands into (`li` may be one or
  two, `ulw` is two)
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, object-word decoding plus a 60-file census; floating-point and
  vector pseudo-instructions are covered by L-EE-019, L-EE-041 and L-EE-044

---

## L-EE-048 · COP2/VU0 instructions cannot come from C

**The single most important limitation for reconstruction**: this compiler never emits COP2/VU0 code from C.

| probe | result |
| --- | --- |
| `mode(V4SI)` / `mode(V4SF)` load, store, copy | **`lq`/`sq` in general registers** — never `lqc2`/`sqc2` |
| `a + b` on two vectors | **compile error** (`invalid operands to binary +`) |
| returning a vector by value | **compile error** (`output_operand: invalid expression as operand`) |
| `asm` with the `"v"` constraint on a vector | `impossible register constraint in 'asm'` |

The backend **does** carry VU0 machinery — `--target-help` lists **`-mvu0-use-REG1-REG2`**, and cc1 exports
`vu0_register_operand` (`0x081723b0`), `vu0_dest_operand` (`0x08172460`), `vu0_field_operand` (`0x08172490`),
`vu0_float_operand`, `vu0_int_register_operand`, `vu0_reg_imm5_operand` and `mips_vu0_use_range`
(`0x0830fb98`) — but **no C construct reaches it**, and there are no `__builtin_ee_*`/`__builtin_vu*` builtins.

**The one working path is inline assembly**:

```c
int v[4], w[4];
asm volatile("lqc2 $vf1,0(%0)" :: "r"(v));     /* emits lqc2 */
asm volatile("sqc2 $vf2,0(%0)" :: "r"(w));     /* emits sqc2 */
```

So **every COP2 instruction in a binary was hand-written assembly in the original source** — `lqc2`, `sqc2`,
`qmtc2`, `qmfc2`, `cfc2`, `ctc2` and the whole `v*` vector family. **Such sites cannot be matched by a C
reconstruction at all**; the reconstruction has to carry inline assembly there, or the function cannot be
reproduced in C.

* **Tier T1** · **Source anchor** the backend's VU0 operand predicates and `-mvu0-use-` (`config/mips/mips5900.md`;
  no line read from the shipped tree) · **Binary anchors** the symbols above
* **Falsifies** the expectation that a 128-bit or float-vector C type makes the compiler use the VU0, and that
  COP2 instructions could come from ordinary C
* **Lever** when a target function contains COP2 mnemonics, do not hunt for a C spelling — that region is
  inline assembly; budget for it or skip the function
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, `mode(V4SI)`/`mode(V4SF)` types and inline assembly; the
  `-mvu0-use-` flag and the VU0 predicates are recorded but were not exercised

---

## L-EE-049 · Variable shifts, negation, float compare — and the second multiplier

| C | assembly | **object** |
| --- | --- | --- |
| `a << n` (variable) | `sll $d,$s,$t` | **`sllv`** |
| `a >> n` signed / unsigned | `sra` / `srl $d,$s,$t` | **`srav`** / **`srlv`** |
| `-a` (int) | `subu $d,$0,$s` | **`negu`** |
| `-a` (float) | — | **`neg.s`** |
| float copy | — | **`mov.s`** |
| `a <= b` / `a < b` / `a == b` (float) | — | **`c.le.s`** / `c.lt.s` / `c.eq.s` + `bc1t` |
| `a + b` (float) | — | `add.s` |

**Two more alias pairs** for the table in [L-EE-047](LAWS.md#l-ee-047--the-printed-mnemonic-is-an-alias--compare-encodings-not-spellings): the assembly's `sll`/`sra`/`srl
$d,$s,$t` become **`sllv`/`srav`/`srlv`** in the object, and `subu $d,$0,$s` becomes **`negu`**. So those
mnemonics in a binary are **ordinary C expressions**, not hand-written assembly.

### The EE has two integer multiplier units

| shape | `mult` | `mult1` |
| --- | ---: | ---: |
| one multiply | 1 | 0 |
| two independent multiplies | 1 | 0 |
| **three independent multiplies** | 2 | **1** |
| **dependent pair** (`x = a*b; return x*b;`) | 1 | **1** |

The scheduler moves a multiply to the second unit when two can overlap — but **only at `-O2`/`-O3`**: the same
three-multiply fixture compiles to `mult` ×3 at `-O1`/`-Os` and `mult` ×2 + `mult1` ×1 at `-O2`/`-O3`. So `mult1`
in a target is a **scheduling signal and a level hint**, not inline assembly.

**Two further spellings**: `multu` is *not* a plain unsigned 32-bit multiply (that is `mult`) — it appears when
a 32-bit unsigned multiply must produce a **64-bit result**; and the 64-bit variable shift has three object
spellings, `dsllv`, `dsrlv` and `dsrav`.

**Open**: `madd.s` appears in binaries, but **no ordinary C float expression produced it** here — `a*b+c`
always compiled to `mul.s` + `add.s`. It is recorded as unexplained rather than guessed at.

* **Tier T2** · **Source anchor** the backend's operator patterns and multiplier units
  (`config/mips/mips.md`; no line read from the shipped tree) · **Constants** `sllv`, `negu`, `mult1`
* **Falsifies** the expectation that `sllv`/`srlv`/`negu` indicate hand-written assembly, and that `mult1`
  needs inline assembly
* **Lever** if a candidate uses `sll` where the target has `sllv` the shapes agree (same C); if the target has
  `mult1` and the candidate only `mult`, the multiplication expressions differ in how far apart they sit
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2`/`-Os` with `-G0`, one-operator functions over `int`, `unsigned` and
  `float`; other multiplier shapes and `madd.s` were not resolved

---

## L-EE-050 · The COP1 accumulator: a sum of products uses `mula.s`/`madd.s`

| float expression | code |
| --- | --- |
| `a*b + c` (one product) | `mul.s` + `add.s` |
| **`a*b + c*d`** | **`mula.s` + `madd.s`** |
| **`a*b + c*d + e*g`** | **`mula.s` + `madda.s` + `madd.s`** |
| `a*b + c*d + e` | `mula.s` + `madd.s` + `add.s` |
| **`a*b - c*d`** | **`mula.s` + `msub.s`** |
| **statement** `s = a*b; s += c;` | `mul.s` + `add.s` — **no accumulator** |
| loop `for (…) s += p[i]*q[i];` | `mul.s` + `add.s` — no accumulator |

So a single expression that **sums two or more products** is evaluated in the **COP1 accumulator**: the first
product is `mula.s`, each further one `madd.s` (with `madda.s` when the chain needs the intermediate value),
and subtraction uses `msub.s`. The accumulator is hard register **71** (`FP_ACC`, [L-EE-016](LAWS.md#l-ee-016--the-ee-register-file-140-hard-registers-in-29-classes)) —
it really is used. The **statement** form and loop accumulation do **not** use it, which makes the accumulator a
signal that the source wrote the sum of products **as one expression**.

**Subtraction uses the same accumulator machinery**: an expression that subtracts products
(`c - a*b - d*e`) compiles to `mul.s` + **`suba.s`** + **`msub.s`** (with `msuba.s` in other shapes). So the
family is `mula.s`/`madd.s`/`madda.s` for sums of products and `mul.s`/`suba.s`/`msub.s`/`msuba.s` for
differences.

**This resolves the open question from [L-EE-049](LAWS.md#l-ee-049--variable-shifts-negation-float-compare--and-the-second-multiplier)**: `madd.s` is ordinary C after all.

Two smaller items in the same pass:

* **float stores are `swc1`** (assembly `s.s`) against `lwc1` (`l.s`) for loads — the store half was missing.
* the 64-bit forms carry **object suffixes**: `dsra32`, `dsrl32`, `dsllv`, `dsrlv`, `dnegu` where the assembly
  writes `dsra/dsrl $d,$s,32`, `dsll/dsrl $d,$s,$t` and `dsubu $d,$0,$s`.

* **Tier T2** · **Source anchor** the backend's accumulator patterns (no line read from the shipped tree) ·
  **Constants** `mula.s`, `madd.s`, `swc1`
* **Falsifies** the earlier note that `madd.s` could not be produced from C, and the assumption that a float
  multiply-accumulate always uses the accumulator
* **Lever** `mula.s`/`madd.s` in the target ⇒ the source summed **at least two products in one expression**;
  and if a candidate produces `mul.s`+`add.s` there, the source probably split the sum into statements
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2` with `-G0`, one to three products plus statement and loop forms;
  `double` uses libgcc instead ([L-EE-029](LAWS.md#l-ee-029--single-precision-is-hardware-double-precision-is-soft-float))

---

## L-EE-051 · Zero comparisons, float branches and an inlined `sqrtf`

**A comparison against zero branches only in control-flow position.**

| source | code |
| --- | --- |
| `return a < 0;` (a **value**) | materialised with `slti` — no branch ([L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)) |
| `if (a < 0) return 1; return 0;` | **branchless** — if-conversion ([L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)) |
| **`while (n > 0) { … }`** | **`blez`** (the inverted exit test) + a back edge |
| **`while (n >= 0) { … }`** | **`bltz`** + a back edge |

The **inverted exit test is level-independent** (`blez`/`bltz` at `-O1`, `-O2` and `-Os` alike), but the
**back edge is not**: at `-O2`/`-O3` it is the likely form `bgtzl`/`bgezl` carrying the loop's own work in its
delay slot, while at `-Os` it is a plain `b` with the body restructured.

So a loop condition appears as the **inverted zero test**: `while (n > 0)` exits on `blez`. Likely forms appear
on the back edge, as [L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not) says.

On floats the form carries information about the source:

| source | code |
| --- | --- |
| `if (a >= b) …` | `c.le.s` with **operands swapped** + `bc1t` |
| **`if (!(a < b)) …`** | **`bc1f`** — the source negated the condition |
| `a < 0.0f ? -a : a` | `c.lt.s` + **`bc1tl`** + `neg.s` |

And **`sqrtf` is recognised by name and inlined**:

```c
extern float sqrtf(float);
float f(float a){ return sqrtf(a); }   /* → sqrt.s $f0,$f12, no call */
```

**Which math names are inlined is a short, closed list**: `sqrtf` → `sqrt.s` and `fabsf` → `abs.s`; every other
libm name tried (`sinf`, `cosf`, `floorf`, `copysignf`, `fminf`, `powf`, …) becomes an ordinary **tail call**
(`j sinf`, [L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2)). The likely branch spellings are `bgtzl`/`bgezl`/`bltzl`/`blezl`
and `bc1tl`/`bc1fl`.

* **Tier T2** · **Source anchor** the backend's branch and `sqrtf` patterns (no line read from the shipped
  tree) · **Constants** `blez`, `bc1f`, `sqrt.s`
* **Falsifies** the expectation that a zero comparison always materialises or always branches the same way,
  and that `sqrtf` is a libm call
* **Lever** `bc1f` in the target ⇒ the source **negated** the float condition; a REGIMM branch ⇒ a
  control-flow zero test, not a value; `sqrt.s` ⇒ a `sqrtf` call in the source
* **Scope** `ee-gcc 3.2-ee-040921` at `-O2 -G0`, synthetic comparisons, loops and float conditions plus
  `sqrtf`; other libm names were not tested for inlining

---

## L-EE-052 · No latency nops — FP order is scheduler-driven

| source | code at `-O2` |
| --- | --- |
| `float f(float *p, float *q){ return *p + *q; }` | `l.s` ; `l.s` ; `j $31` ; **`add.s`** (in the delay slot) |
| `int f(float *p){ return (int)*p; }` | `l.s` ; **`cvt.w.s` immediately** ; `j $31` ; `mfc1` |
| `float f(float *p){ return *p; }` | `j $31` ; **`l.s`** (in the delay slot) |
| `float x = *p; return x > 0.0f;` | `l.s` ; `mtc1` ; `c.lt.s` ; `bc1t` |

**Counting `nop`s over five floating-point shapes at `-O1`, `-O2` and `-Os` gives zero in every case.** This
compiler does **not** pad COP1 loads, moves or compares.

The consequence matters for matching: **floating-point instruction order is decided by optimisation and
scheduling alone**, never by latency padding. So do not hunt for a missing `nop` between a load and its use —
an order difference has to be explained by a source-shape lever
([FIELD-GUIDE](FIELD-GUIDE.md)), not by latency.

The same measurement shows how free that order is: the four loads of `p[0]*p[1] + p[2]*p[3]` are reordered to
offsets **0, 4, 12, 8**, and an FP accumulation loop is ordered differently at `-O2` (`mtc1 $0,$f1`) than at
`-Os` (`mtc1 $0,$f0` plus `mov.s $f1,$f0`).

* **Tier T3** (negative knowledge: the absence is the finding) · **Source anchor** the port's scheduling
  description (no line read from the shipped tree) · **Constants** `l.s`, `mfc1`
* **Falsifies** the expectation that a load-delay or COP1-latency `nop` should appear between a
  floating-point load and its first use
* **Lever** an FP sequence in a different order is a **source-shape** signal; and a candidate's extra `nop`
  comes from somewhere else — check the delay-slot rules ([L-EE-009](LAWS.md#l-ee-009--the-delay-slot-is-filled-the-leftover-nop-is-the-function-ending-jr-ra))
* **Scope** `ee-gcc 3.2-ee-040921` at `-O1`/`-O2`/`-Os` with `-G0`, five FP shapes plus a `double` load;
  integer load delays and 2.96 were not measured here

## L-EE-053 · A copy records a hard-register preference on whichever side is a global pseudo

`set_preference(dest, src)` runs for every store while conflicts are collected. Two directions matter:

* `dest` is a hard register and `src` is a global pseudo → the preference is recorded **on the src allocno**;
* `src` is a hard register and `dest` is a global pseudo → the preference is recorded **on the dest allocno**.

`reg_renumber` is consulted first, so a pseudo that local allocation already placed contributes its **hard
register**, not its pseudo number. The recorded preferences are inputs to
[L-EE-018](#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer)
and are pruned by [L-EE-054](#l-ee-054--preferences-are-pruned-before-ordering-conflicts-fixed-caller-saved-for-call-crossing-values-and-out-of-class-registers-are-removed)
before ordering.

Measured on `func_001d4b88` (`-Os -fno-thread-jumps`, effect-diff at the return point): 842 decoded calls,
84 changed a preference mask. Allocno 2 gained `{5}` from `$a1`; allocno 24 gained `{13,14}` although
`$t5`/`$t6` were the **destination** side — the bits land on the source allocno; allocnos 13 and 11 gained
`{15}` (`$t7`). The diff agrees with the prune-entry snapshot, so the direction is observed, not replayed.

* **Tier T2** · **Source anchor** `global.c:1615` (mainline `set_preference`; the shipped binary resolves it
  to `global.c:1967`) · **Binary anchor** `set_preference @ 0x081ae780`
* **Falsifies** the assumption that a preference only comes from a parameter's ABI home or from a same-direction copy
* **Lever** trace the effect (mask diff) instead of replaying the source; `reg_renumber` can make the
  recorded register one that never appears in the C source
* **Scope** `ee-gcc 3.2-ee-040921` at `-Os -fno-thread-jumps` on one reconstruction (`func_001d4b88`);
  the rule text is mainline gcc-3.2.3

---

## L-EE-054 · Preferences are pruned before ordering: conflicts, fixed, caller-saved for call-crossing values, and out-of-class registers are removed

`prune_preferences` runs after `allocno_order` is sorted and before the first `find_reg`. For every allocno,
in descending priority order, it:

1. removes the registers in the allocno's `hard_reg_conflicts`;
2. removes `fixed_reg_set`, plus `call_used_reg_set` when `calls_crossed > 0`;
3. removes registers outside the allocno's preferred class;
4. if nothing is left, restores the full class and retries;
5. fills `regs_someone_prefers` from the allocnos that conflict with it and still wait for a register.

The dump's `;; N preferences:` lines are printed **after** this step, so they show the post-prune list.

Measured on `func_001d4b88` (`-Os -fno-thread-jumps`): 83 allocnos changed a preference mask at expand and
112 at prune. Of the 6 allocnos that got no register, 4 carried only caller-saved preferences
(`{5}` / `{13,14}` / `{15}`, `calls_crossed` 2–30) and left prune with **empty** sets; the other two
(allocnos 12 and 9) had no preference at all — pure pressure.

* **Tier T2** · **Source anchor** `global.c:903` (mainline `prune_preferences`; the shipped binary resolves it
  to `global.c:1236`) · **Binary anchor** `prune_preferences @ 0x081ac580`
* **Falsifies** the reading that the preference list printed in a dump is the list the choice rule sees
* **Lever** check whether a preference survives pruning before blaming the choice rule; a caller-saved
  preference cannot survive a call, so shorten the live range or move the copy instead
* **Scope** `ee-gcc 3.2-ee-040921` at `-Os -fno-thread-jumps` on one reconstruction (`func_001d4b88`);
  the rule text is mainline gcc-3.2.3

---

## Open items

* The exact `$L` counter formula (multi-label functions).
* ~~`FIRST_PSEUDO_REGISTER` for the EE build~~ — **settled**: `ALL_REGS` has **140 members** and the first
  pseudo register is **144** (72–75 are reserved), read from a live `cc1`
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
