# Case study — attacking one function with the handbook

[简体中文](CASE-STUDY.zh-CN.md) · [Handbook index](README.md) · [Laws](LAWS.md) · [Diagnostics](DIAGNOSTICS.md) · [Field guide](FIELD-GUIDE.md)

This page walks one function end to end: what the tools printed, which laws were consulted, what edit
was tried, and why the edit was **rejected**. It is here to show the shape of the work, including the
part where the model says *no*.

The function is a large recursive routine in this project, roughly 630 lines of C, with 37 call sites
of which 12 are the recursive call. Names and numbers are the project's own; no disassembly is quoted.

## Step 0 — read the residual

```
objdiff            80.18
candidate frame    176 B
target frame       144 B
```

Two facts, one hypothesis: the instruction stream is close (80%), and the frame is 32 B too large. The
first question is never "how do I shrink the frame" but "**which block of the frame is wrong**".

## Step 1 — decompose the frame (L-EE-012)

The frame is `[vars][outgoing args][8 B per saved register]`. Current numbers for both sides:

| block | candidate | target |
| --- | ---: | ---: |
| vars | 48 B | **16 B** |
| outgoing args | 48 B | 48 B |
| saved registers | 10 × 8 B = 80 B | **10 × 8 B = 80 B** |

Both prologues save the same ten registers, so the entire +32 B is the **vars** block. Any plan that
talks about "saving fewer registers" is already wrong.

## Step 2 — find the lines that fill the vars block

```sh
python3 tools/compiler/ee-gcc-spill-map.py --src candidate.c --include include --flags=-Os --trace-values
```

```
frame=176 B  vars=48  regs=10 (8 B each)  args=48
    line  store  load  offsets / spilled variable names
     513      5     0  [8, 16, 24, 32, 40]   param_11
     ...same five slots at 12 call lines...
```

Twelve source lines — exactly the recursive call sites — each write five 8-byte slots. `-fverbose-asm`
labels them, and `--trace-values` says where the stored value was computed: in every case, a few lines
before the call. So the shape is: **values computed before the recursive call, used after it.**

## Step 3 — ask the model what the compiler does with such values

Two laws apply:

* [L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers)
  — the frame layout and the 10-register save cap. Already used in step 1.
* [L-EE-015](LAWS.md#l-ee-015--the-outgoing-argument-area-doubles-as-storage-for-a-value-used-after-the-call)
  — a value passed in the outgoing argument area is **re-read from that slot** after the call when it is
  an aggregate (zero extra frame), while a scalar pays a callee-saved register (8 B).

L-EE-015 predicts a specific, cheap fix for a value that is both *passed* and used *afterwards*: express
it as the same expression in both places instead of copying it into a local. A local copy is a second
live object, and here two such copies would account for the +16…32 B.

## Step 4 — check the target before editing

The model says what the compiler *can* do; only the target says what it *did*. Two checks:

* Both sides have **37 call sites**, so the call structure is not in question.
* The target's own code re-reads a 4-byte aggregate from its outgoing argument slot after the recursive
  call — the same shape L-EE-015 predicts.

That is consistent with the hypothesis and worth one measured edit.

## Step 5 — make the edit and measure

Remove one local copy so the value is passed directly and re-used, then re-measure.

| reading | before | after | movement |
| --- | ---: | ---: | --- |
| frame | 176 B | **160 B** | −16 B (exactly two 8-byte slots) |
| instructions | 1,486 | 1,483 | −3 |
| objdiff | 80.1846 | **78.95184** | **−1.23** |

**The mechanism is confirmed and the route is falsified.** The frame moved by exactly the amount
L-EE-012/L-EE-015 predict, and the match got *worse*: the target really does keep that copy alive. The
edit was reverted.

## Step 6 — what the negative result buys

* The frame model is now quantitatively validated on a real function (8-byte granularity, predicting the
  size of the movement before the edit).
* One hypothesis is dead, with evidence, so the next attempt does not repeat it.
* The remaining target list is explicit: the 12 recursive call sites, and for each one the values
  computed before and used after. The next attempt should change *which values need to survive* — not
  delete the ones the target keeps.

## What generalises

1. **Decompose before you rewrite.** `vars` / `args` / `8 B × regs` turns "the frame is too big" into one
   addressable block.
2. **Map bytes to source lines.** A diagnostic that prints line numbers turns a search into a checklist.
3. **Check the target before trusting the model.** The model describes what the compiler can do; the
   target object says what it did.
4. **A negative result is a result.** The most expensive mistake in matching work is re-trying a route
   that is already known to fail — in either direction.

## Reproducing the tooling parts

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare
python3 tools/compiler/ee-gcc-passdiff.py a.c b.c
python3 tools/compiler/laws-query.py guide frame
python3 tools/compiler/ee-gcc-spill-map.py --src candidate.c --flags=-Os --trace-values
```

Everything above needs your own copy of the game and the toolchain; the handbook ships no game content
and no compiler binaries.
