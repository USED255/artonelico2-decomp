# Field guide — source spellings that move a measurement

[Handbook index](README.md) · [Laws](LAWS.md) · [Diagnostics](DIAGNOSTICS.md)

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

**Dose-response** (synthetic, k values live across calls): frame 32/48/64/80/96 for k = 2/4/6/8/10,
with `regs=` 4/6/8/10/10 — **8 B per saved register, saturating at 10**.

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

---

## Recorded but not yet measured locally

These come from other projects or from unlicensed write-ups. They are **leads**, not rules: measure
them here before relying on them.

| Lead | Origin | Status |
| --- | --- | --- |
| ~~`switch` needs five or more distinct cases to become a jump table~~ | dds-decomp (ee-gcc 2.96, unlicensed) | **verified and refined on 3.2**: five cases are necessary but not sufficient — the span must also satisfy `range <= 10 * count` ([L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count)) |
| `slt`/`sltiu` against `xori` distinguishes narrow unsigned types | dds-decomp | unverified |
| The scheduler's tie-break reads a physical source line number, so folding statements onto one line is a lever | n64-decomp-workbench (IDO 5.3, CC0) | mechanism not confirmed for ee-gcc 3.2; scheduling drift is large (`haifa-sched.c` +263), so it needs the anchor method |
| A discarded-value statement can be load-bearing with zero instructions | n64-decomp-workbench (IDO 5.3) | unverified under ee-gcc 3.2 |
