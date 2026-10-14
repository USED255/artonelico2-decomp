# Diagnostics — from a wrong diff to the pass that owns it

[Handbook index](README.md) · [简体中文](DIAGNOSTICS.zh-CN.md) · [Laws](LAWS.md) · [Pass map](PASSES.md)

A matching diff tells you *that* the bytes differ. It does not tell you *which decision* produced
the difference. This page is the workflow that answers that, in order, before any guesswork.

## 1. Read the residual in the right order

Fix things in the order in which they are decided, because an earlier difference can create every
later one:

1. **Control flow** — branch structure, block order, where the exits are.
2. **Instruction shape and count** — the same statements compiling to different instructions.
3. **Register allocation** — the instruction stream matches, the registers do not.
4. **Stack** — the instruction stream and registers match, the frame offsets do not.

A candidate below roughly 80% match is a **structural** difference. The tools below will describe it
accurately and help you very little; rewrite the C first.

## 2. Find the first pass where two spellings diverge

Both spellings must be *plausible* source for the same function. Then:

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1

python3 tools/compiler/ee-gcc-passdiff.py a.c b.c                       # default: 3.2 -O2 -G0
python3 tools/compiler/ee-gcc-passdiff.py a.c b.c --cc ~/eecc/ee-gcc2.96/bin/ee-gcc
```

The tool compiles both, dumps every pass, normalises the parts that are meaningless across two
compilations (instruction uids and pseudo-register numbers), and reports the first pass whose dump
differs. Exit code 0 means every pass matched; 1 means a divergence was found.

## 3. Route the divergence

The first diverging pass names the decision family. Pass names are from 3.2; see
[PASSES.md](PASSES.md) for the 2.96 equivalents.

| First divergence | Family | Look at |
| --- | --- | --- |
| `00.rtl`, `01.sibling` | source semantics and expression shape | types and promotions, statement structure, operand order, `switch` vs `if` chain |
| `03.jump`, `13.cfg`, `14.bp` | control flow | branch conditions, block layout, jump-table construction |
| `09.cse`, `11.gcse`, `15.cse2` | common subexpressions and TU context | aliasing, repeated loads, what is visible in the translation unit |
| `12.loop` | loops | induction variables, invariant motion, loop weight |
| `16.life` | live ranges | what stays live across a call or a block boundary |
| `17.combine`, `18.ce`, `28.ce2` | instruction combining and conditional execution | how expressions are nested, which branch becomes conditional |
| `19.regmove`, `21.range` | register moves and ranges | operand constraints, copy chains |
| `22.lreg` | local allocation | single-block values, cost table, preference class |
| `23.greg` | global allocation | priority order ([L-EE-001](LAWS.md#l-ee-001--global-allocation-order-is-allocno_compare)), interference, colouring |
| `24.postreload` | reload and spilling | which values failed to get a register, spill code shape |
| `20.sched`, `29.sched2` | scheduling | statement grouping, dependency chains by source line |
| `31.bbro`, `33.dbr` | block reordering and delay slots | branch layout, what fills a delay slot |

## 4. Two false signals

Both of these produce a *clean, confident, wrong* answer. They are the reason a first-divergence
report must be read with care.

1. **Compiler-internal pointers in the RTL.** `(note 0x… NOTE_INSN_BLOCK_BEG)` embeds a pointer that
   changes between runs. Without normalising it, `00.rtl` reports a divergence that is not there.
   `ee-gcc-passdiff.py` normalises notes and barriers.
2. **The source file name is embedded in the object.** Compiling `a.c` and `b.c` puts two different
   names in the object, so the two objects differ by one byte in the string table even when `.text`
   is identical. The tool copies both sources to the same name before compiling, so this cannot
   masquerade as a code difference.

## 5. When not to use the model

* Below ~80% match: structural. Rewrite the C; the pass report is noise.
* When the two spellings differ **semantically**: the first divergence will be `00.rtl` and the
  final object will differ. That is a source bug, not a compiler decision.
* When a divergence is reported at `00.rtl` but the final objects are **identical**: the difference
  was eliminated by a later pass. Both spellings are equivalent; stop pursuing it.

## 6. Going deeper

* The decision rules themselves are in [LAWS.md](LAWS.md), each with a source anchor and a
  binary anchor.
* To check what the *shipped* compiler actually does at a decision point, use
  [`tools/compiler/ee-gcc-anchor.py`](../../tools/compiler/ee-gcc-anchor.py): it turns a symbol into
  an address, a source line, a struct layout or a constant.
* Reading `24.postreload` output needs the normalisation note above: the `reload_out (SI) = (reg:SI 2
  v0 [149])` section is reload bookkeeping, **not** a register reference. Counting those as
  references inflates use counts.

## Calibration on record

Ten pairs of plausible spellings were compared when this workflow was first built. The useful result
is that the *first-divergence pass* alone does not decide anything: what decides is whether the
final objects differ, and whether a later pass re-converges. The table above routes the search; the
measurement still decides.
