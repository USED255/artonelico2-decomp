# Case study 2 — a large function, where the frame is the whole story

[The first case study](CASE-STUDY.md) attacks a small function whose frame is 8 bytes too big. Large
functions behave differently: there the frame is not a rounding error, it is a **measurement of how many values
the source kept alive at once**, and the instinct to "clean the code up" moves you *away* from the target.

This study uses one synthetic function, so every number below is reproducible without any game data.

## The residual

Compile two spellings of the same arithmetic and read `.frame`:

| spelling | frame | `vars` | `regs` |
| --- | ---: | ---: | ---: |
| **A** — 40 locals computed, then all used | **208** | **128** | 10 |
| **B** — each value folded and consumed immediately | **32** | 0 | 3 |

Identical results, **6.5× apart in frame size**, at both `-O2` and `-Os`.

Check the arithmetic against [L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers): `frame = round16(vars + 8 × saved regs +
outgoing args)`. For A: `128 + 8 × 10 = 208` ✓. So the 128-byte `vars` block is **16 spilled values**, and the
frame is telling you the source had sixteen live values at once.

## Step 1 — decompose the frame before editing anything

```sh
python3 tools/compiler/ee-gcc-spill-map.py --src A.c --flags="-O2 -G0"
```

```
frame=208 B  vars=128  regs=10 (8 B each)  args=0

vars 区（0..127）访问涉及的源码行：
  line  store  load  offsets / spilled variable names
     5      1     0  [0]   v1
     6      1     0  [4]   v2
     …
```

Every spill is traced back to **the line that defined it**, which turns "the frame is too big" into "these
sixteen statements each introduce a value that stays live". That is the whole diagnosis: no pass guessing
needed.

> The tool is deliberately the *first* step. A frame that is too big has three possible owners — the vars
> block, the saved registers, or the outgoing argument area — and only decomposition tells you which.

## Step 2 — find out what keeps the values alive

The obvious suspect is "the calls keep the values live", so the natural edit is to move each `sink(v)` call
right after the line that defines `v`. Measured: **frame 208 → 208, `vars` 128 → 128. Nothing moves.**

The reason is in the source: the values are consumed by the *final* sum. **The live range ends at the last use,
and interleaving an earlier use changes nothing.** Only the last use matters — here, the summation at the end.

That is the negative result worth keeping: the edit people reach for first is not the edit that moves the
number.

## Step 3 — apply the lever that does move it

To change the frame you must change **where the last use is**. Folding each value into the accumulator at its
definition is the same arithmetic:

```c
/* A: batch */                     /* B: fold */
int v1 = p[0] + 0;                 int s = 0;
…                                  …
sink(v1);                          { int v = p[0] + 0; sink(v); s += v; }
s += v1;
```

| | frame | `vars` | `regs` |
| --- | ---: | ---: | ---: |
| A (batch) | 208 | 128 | 10 |
| B (fold) | 32 | 0 | 3 |

## The point: matching is not optimising

Everything a compiler-minded person calls "cleaner" points from A to B. That is exactly the wrong direction
when the **target** is A: a target whose frame is 208 bytes tells you the source **kept sixteen values live at
once**, and a reconstruction that folds them into an accumulator can never match — it is 176 bytes of frame
away, and no local edit recovers that.

So the direction of the diagnostic is:

* candidate frame **larger** than the target → you are keeping values live that the source consumed earlier;
  shorten a live range by moving a use forward, or split the expression.
* candidate frame **smaller** than the target → the source kept values alive that you are folding away; look
  for a batched pattern (compute many, then use them together), a value that survives a call, or a variable
  the source declared and used late.

The frame is a **structural fingerprint**. Read it as evidence about the source, not as a score to minimise.

## Reproducing the numbers

The two spellings are executable fixtures in the handbook's own suite, so this study's central claim is
checked on every run:

```sh
python3 tools/compiler/ee-gcc-observe.py --selftest          # includes both frame assertions
python3 tools/compiler/ee-gcc-observe.py --src A.c --flags="-O2 -G0"
python3 tools/compiler/ee-gcc-spill-map.py --src A.c --flags="-O2 -G0"
```

Related laws: [L-EE-012](LAWS.md#l-ee-012--frame-composition-outgoing-argsvars8-b-per-saved-register-saturating-at-10-saved-registers) (frame composition), [L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality) (the
outgoing argument area), [L-EE-015](LAWS.md#l-ee-015--the-outgoing-argument-area-doubles-as-storage-for-a-value-used-after-the-call) (a value that is both passed and kept),
[L-EE-025](LAWS.md#l-ee-025--loops-count-down-at--o2-os-at--o1-they-keep-slt-and-are-not-unrolled)/[L-EE-026](LAWS.md#l-ee-026--the-constant-pool-is-per-function) (`-O1` and `-Os` frame behaviour), and
[L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer) (which register the allocator picks).
