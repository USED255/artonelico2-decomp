# Field guide — source spellings that move a measurement

[Handbook index](README.md) · [简体中文](FIELD-GUIDE.zh-CN.md) · [Laws](LAWS.md) · [Diagnostics](DIAGNOSTICS.md)

Each entry is a **lever**: a source-level edit, the reading it is expected to move, and the measured
effect. Read [DIAGNOSTICS.md](DIAGNOSTICS.md) first: a lever applied to a structurally different
function measures nothing.

The readings this guide refers to are:

* **objdiff** — the byte-match percentage for one function. Only 100.0 counts as matched.
* **frame size** and **spill count** — from the `24.postreload` dump or the frame map.
* **allocation order** — the `;; N regs to allocate:` list in `23.greg`.

---

## Lever 1 — Shorten a live range that spans a call

**When**: the instruction stream is close, the frame is larger than the target, and the spill count
is high.

**Why**: `live_length` divides the allocation priority
([L-EE-001](LAWS.md#l-ee-001--global-allocation-order-is-allocno_compare)), and a value that stays
live across calls competes for the callee-saved registers. On this target the callee-saved general
set is `$s0–$s8`, and `$s0` is already taken by a constant, so at most eight values can survive a
call in registers.

**Measured** (single function, retail frame 144 B):

| Reading | Candidate | Retail |
| --- | ---: | ---: |
| frame | 176 B | 144 B |
| global allocnos | 64 | — |
| spill points | 280 | — |
| allocnos that got no register | 3 | — |
| saved registers | 10 (s0–s8, ra) = 80 B | **10 (s0–s8, ra) = 80 B** |
| outgoing args | 48 B | 48 B |
| **vars (the spilled block)** | **48 B** | **16 B** |

Both prologues save exactly the same ten registers, so **the entire +32 B is the variable block**
([L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers)).
Two extra 8-byte slots are held by values that could not take one of the nine `$s` registers.

**Find the targets first.** `tools/compiler/ee-gcc-spill-map.py` compiles with `-gdwarf-2 -fverbose-asm`
and maps every stack access back to a source line, split by block:

```sh
python3 tools/compiler/ee-gcc-spill-map.py --cc "$EE_GCC" --src candidate.c \
    --include include --flags=-Os
```

On `func_001d4b88` the candidate writes **5 slots** at **each of 12 recursive call sites**, while the
retail target's `vars` block is only **2 slots** (16 B). That is the target list: those 12 lines are
where values are kept alive across the recursive call.

`-fverbose-asm` also labels each spill with the variable's name, and `--trace-values` attributes a
store to the line that last defined the stored register:

```
    line  store  load  offsets / spilled variable names
     513      5     0  [8, 16, 24, 32, 40]   param_11
```

So the tool answers "what is being kept alive, and where was it computed" — which is what you need in
order to recompute it after the call instead of before.

**Dose-response** (synthetic, k values live across calls): frame 32/48/64/80/96/112/128/144 for
k = 2/4/6/8/10/14/18/24, with `regs=` 4/6/8/10/10/10/10/10 — **8 B per saved register, and the save
area caps at 10 registers**. Past that only `vars` grows. The saved set is `$s0`–`$s7`, `$fp` and
`$ra`; note that this toolchain's objdump prints register 30 as `s8` (the compiler's assembly prints
`$fp`), so do not infer numbers from disassembly names.

A variable-level cross-check on the same function found **12** user variables live across 20 or more
calls against 8 usable callee-saved registers, so at least four must go to the stack — which is
exactly the +32 B = four 8-byte slots. Two independent paths agree, which is why this lever is
recorded as the first one to try.

**Expected movement**: each value removed from the call-crossing set costs one 8-byte slot, so four
values should remove the +32 B.

**Measured — the mechanism holds, the objective did not move the right way.** Removing one value that
was carried across a call (a `struct` copy held only to pass it to a later recursive call, replaced
by passing the parameter directly):

| Reading | Before | After | Movement |
| --- | ---: | ---: | --- |
| frame | 176 B | **160 B** | **−16 B = two 8-byte slots** |
| instructions | 1,486 | 1,483 | −3 |
| objdiff | 80.1847 | **78.95184** | **−1.23** |

So the frame law is confirmed quantitatively — the frame moves in whole 8-byte slots as predicted —
while the *matching* objective got worse: the retail code keeps that value live across the call.
This is the most useful shape a lever can have here: it proves the mechanism and falsifies the
route, so the next attempt should look for a different value, not a different mechanism.

**Negative prior**: rewriting a local so that it is "kept in a register" cost 1.33 points
(79.01 against an 80.34 baseline). The lever is *shortening liveness*, not moving the value into a
register.

## Lever 2 — Use the `floor_log2` step, do not add one reference

**When**: the allocation order is wrong and the values are close in priority.

**Why**: `n_refs` enters through `floor_log2`, so reference counts 1, 2–3, 4–7, 8–15 … are the same
priority. One extra reference usually changes nothing; crossing a power of two changes everything.

**Expected movement**: a value whose reference count crosses 4 or 8 moves up one step; a value with
the same step does not move at all.

## Lever 3 — Move a use into a hotter block

**When**: a value is allocated late but its references are few.

**Why**: `freq` is the sum of the block frequencies of the referencing blocks, and it is a linear
multiplier in the priority formula. Hot blocks in this build carry frequencies near 10,000, cold
blocks near 1,600.

**Expected movement**: moving a use into a hot block raises priority linearly; the reading that moves
is the allocation order, not the instruction count.

## Lever 4 — `size` is only visible when it changes

**When**: a mixed-mode function (32-bit and 64-bit values competing) allocates in an unexpected
order.

**Why**: `size` counts **words** and only prints when it is not 1
([L-EE-002](LAWS.md#l-ee-002--allocnosize-is-in-words-and-prints-only-when-it-is-not-1)). A
`long long` or `double` value carries 2, an `int` carries 1.

**Expected movement**: the two-word values are promoted against one-word values in the same order.
Whether this is observable at all depends on a value reaching global allocation; most 64-bit values
in this corpus are handled by local allocation and never enter the list. Recorded as an open item.

## Lever 5 — Check the source line number you are citing

**When**: a rule you read out of mainline source does not reproduce.

**Why**: the shipped compiler is not stock gcc-3.2.3, and the drift is per file and per function
(`global.c` +341 lines, `local-alloc.c` −4, `regmove.c` +1920;
[L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)).

**Expected movement**: none on the binary. This lever is about not spending a day chasing code that
is not there.

## Lever 6 — Check the constant form before rewriting around it

**When**: a constant-related diff survives every respelling of the expression.

**Why**: float constants come from the constant pool; a double whose low 32 bits are zero is built
inline with `dli` + `dsll` ([L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)).

**Expected movement**: for a float, the form does not depend on the source — look elsewhere in the
function. For a double, changing the value's low 32 bits (for example by adding a tiny term) changes
the form, and that is a real lever; changing a float's spelling is not.

## Lever 7 — Match `-G` before comparing globals

**When**: a global is read as a bare symbol in one build and with `lui %hi`/`%lo` in the other, or an
object lands in a different section.

**Why**: small-data addressing follows `-G` ([L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g)).
The project's `MATCHED_CFLAGS` passes no `-G`, so the MIPS default **8** applies: objects up to 8 bytes
become `gp_rel`, larger objects and all constants stay absolute.

**Expected movement**: fixing `-G` moves the addressing form for every small global in the function —
a whole family of rows at once, not one row. If a diff looks like a systematic addressing mismatch,
check `-G` before rewriting anything.

## Lever 8 — Reuse the outgoing argument area instead of adding a copy

**When**: a value is passed to a call *and* used after it, and the frame is too large.

**Why**: an aggregate written into the outgoing argument area is **re-read from that slot** after the
call, at no extra frame cost; a scalar instead gets a callee-saved register (8 B)
([L-EE-015](LAWS.md#l-ee-015--the-outgoing-argument-area-doubles-as-storage-for-a-value-used-after-the-call)).
So a local copy of an aggregate that is passed to a call and used afterwards is a **second live object**
that costs a slot.

**Expected movement**: removing such a copy shrinks the `vars` block in 8-byte steps (measured: one
removal moved the frame 176 B → 160 B, exactly two 8-byte slots). Check the ratio with
`ee-gcc-spill-map.py` before and after.

**Caution**: on the function measured here the edit shrank the frame but *lowered* objdiff
(80.1846 → 78.95184), i.e. the target really does keep that copy. Confirm against the target's
disassembly (it will show the re-read) before committing to the rewrite.

## Lever 9 — Predict which register the compiler will choose

**When**: the instruction stream matches but registers differ, or you want to know whether a
respelling can move an allocation.

**Why**: the allocation rule is measured ([L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer)):
the pool is the class minus the fixed registers (minus the caller-saved set for a call-crossing
allocno); the banned set is the allocno's hard conflicts plus the registers of the already-placed
conflicting allocnos; the choice is the first available preference, otherwise the lowest candidate; and
a first pass also avoids the registers other allocnos prefer.

**Expected movement**: the measured rule reproduces **46.5%** of held-out decisions (34.3% for a
preference-first heuristic; 82.7% when the occupancy is known exactly). Two levers were tested and
rejected — a rotating scan start and live-range-derived occupancy — so do not spend time on those.

**Caution**: an early wrong pick cascades. When a prediction disagrees with the target, check whether
an *earlier* allocno was predicted wrongly before concluding the rule is wrong.

## Lever 10 — Get `gp_rel` addressing when the unit is built with `-G0`

**When**: the target reads a global as a **bare symbol** (gp_rel) and your candidate emits `lui %hi`/`%lo`.

**Why**: small-data membership needs a **definition in this translation unit** inside `.sdata`/`.sbss`
([L-EE-021](LAWS.md#l-ee-021--gp_rel-needs-a-definition-in-this-unit-placed-in-sdatasbss)). At the default
`-G8` a small object qualifies automatically; at `-G0` it does not, and `weak` does not change that. An
`extern` declaration (no definition here) is **always** absolute, even with a section attribute.

**Expected movement**: the access changes from `lui` + `%lo` to the bare symbol. `objdump -t` should show
the object in `.sbss`/`.sdata`.

**Caution**: this is an addressing change, not a storage change — the project's `gp_rel` candidates rely on
the small-data section being discarded by the linker script. If the object must keep its real storage, a
separate definition is needed.

## Lever 11 — The target inlines a helper, your candidate emits `jal`

**When**: the target has a small helper expanded into its caller, or the reverse (your build keeps a call).

**Why**: at the project's flags (`-O2`, no `-finline-functions`) only a declaration carrying `inline` or
`__inline__` is inlined; a plain `static` helper always keeps its call, even when called once
([L-EE-023](LAWS.md#l-ee-023--at-these-flags-only-an-inline-declaration-is-inlined)).
`always_inline` alone does nothing.

**Expected movement**: adding `inline` to the helper removes the `jal` and the `helper:` label, and the body
appears in the caller. If that does not reproduce the target, check whether the target unit was built with
`-O3`/`-finline-functions`.

**Caution**: this is a *source* difference with a large effect on the instruction stream — confirm the helper
really is expanded in the target before respelling, since an extra `inline` also changes the caller's frame.

## Lever 12 — The target loop is unrolled, or is not in countdown form

**When**: the target repeats a loop body, or keeps an upward induction comparison your build does not.

**Why**: this compiler turns loops into **countdown** loops — a constant trip becomes `li $r,N-1` …
`addu $r,$r,-1` … `bgez`, a variable trip becomes a `blez` guard … `bne $r,$0` — and **neither `-O2` nor
`-O3` unrolls**; unrolling needs `-funroll-loops` or a hand-unrolled source
([L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled)).

**Expected movement**: `-O2 -funroll-loops` turns the eight-trip fixture from 8 into 12 instructions; hand
unrolling produces a visibly repeated body.

**Caution**: do not unroll by hand to imitate a repeated body before checking the flags — and if the target
is *not* in countdown form, the difference is in the source loop shape, not the flags.

---

## Recorded but not yet measured locally

These come from other projects or from unlicensed write-ups. They are **leads**, not rules: measure
them here before relying on them.

| Lead | Origin | Status |
| --- | --- | --- |
| ~~`switch` needs five or more distinct cases to become a jump table~~ | dds-decomp (ee-gcc 2.96, unlicensed) | **verified and refined on 3.2**: five cases are necessary but not sufficient — the span must also satisfy `range <= 10 * count` ([L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count)) |
| ~~`slt`/`sltiu` against `xori` distinguishes narrow unsigned types~~ | dds-decomp | **falsified on 3.2**: `xori` marks equality; narrowness is an `andi` mask or an `sll`+`sra` extension ([L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality)) |
| The scheduler's tie-break reads a physical source line number, so folding statements onto one line is a lever | n64-decomp-workbench (IDO 5.3, CC0) | mechanism not confirmed for ee-gcc 3.2; scheduling drift is large (`haifa-sched.c` +263), so it needs the anchor method |
| A discarded-value statement can be load-bearing with zero instructions | n64-decomp-workbench (IDO 5.3) | unverified under ee-gcc 3.2 |
