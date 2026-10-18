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

## 3.5 Getting the compiler's own answer (ground truth)

When a question is "which register did the compiler pick, and why?", do not infer it from the
disassembly — ask the compiler. The packaged recipe is one command:

```sh
python3 tools/compiler/ee-gcc-observe-alloc.py --src candidate.c --flags="-O2 -G0" --prefs
```

It reports the allocation order, every `find_reg` attempt (with `alt_regs_p`), the allocnos that got no
register, and — with `--prefs` — the preference edits made by `expand_preferences` and
`prune_preferences` before ordering ([L-EE-053](LAWS.md#l-ee-053--a-copy-records-a-hard-register-preference-on-whichever-side-is-a-global-pseudo),
[L-EE-054](LAWS.md#l-ee-054--preferences-are-pruned-before-ordering-conflicts-fixed-caller-saved-for-call-crossing-values-and-out-of-class-registers-are-removed)).
It also compiles a second time with `-da` and checks its live reading against the
`;; Register dispositions:` lines, so the two measurement paths are compared rather than assumed to agree.

Three facts this establishes: `allocno_order[i]` holds an **allocno index**, `allocno[num].reg` holds the
**pseudo register number**, and `reg_renumber[pseudo]` holds the decision. The dispositions a `-da` dump
prints (`;; Register dispositions: 169 in 2 …`) are exactly that table.

**Read the order at the first `find_reg`, not after `global_alloc` returns.** `allocno_order` is freed at
the end of `global_alloc`; a dump taken after the return can look plausible and be wrong — a measured
failure mode is "the first entries match, the rest is stale heap". The first `find_reg` runs after
`qsort` and before the free. `reg_renumber` is a static array, so the decisions themselves can be read at
either point; the observer reads them at each `find_reg` return.

**If you write your own tracer**, two traps: gdb's `FinishBreakpoint` never fires under `--batch`, so use
explicit return-address breakpoints; and the entry arguments are on the stack (`$esp+4/8/12/16/20`),
because reading DWARF parameter names at a `*addr` breakpoint resolves to the wrong scope (measured:
`alt=16`). Disambiguate the two `find_reg` symbols by address
([L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)).

## 3.6 A size or offset mismatch is not an instruction mismatch

If the instructions agree but objdiff reports a different size, or function symbols sit at different
offsets, check the alignment flags before rewriting anything. The default function alignment is **8 bytes**,
so a 12-byte function is padded to 16; `-falign-functions=4` lowers it to 4 and removes the padding, and
`-ffunction-sections` alone does not
([L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)).
This project builds with `-O2 -falign-functions=4 -ffunction-sections`, so every function section should be
exactly the function's size.

## 3.7 Read `.frame`'s first operand before anything else

`.frame $sp,80,$31` and `.frame $fp,96,$31` differ in a way that survives the whole function: the first
operand is the base register. `$sp` means no frame pointer — and a saved `$fp` in that function is just the
tenth callee-saved register, not evidence of one. `$fp` means a real frame pointer, which comes from
`alloca`/VLA in the source or from `-fno-omit-frame-pointer`; the latter adds 16 bytes
([L-EE-024](LAWS.md#l-ee-024--a-saved-fp-is-not-a-frame-pointer)).
If the target frame is exactly 16 bytes larger with the same callee saves, this is the first thing to check.

## 5. Stop when the target is inline assembly

If the target contains COP2/VU0 mnemonics (`lqc2`, `sqc2`, `qmtc2`, `qmfc2`, `cfc2`, `ctc2`, or any `v*` vector
instruction) then **no C spelling will ever reproduce it**: this compiler emits those only from inline assembly
([L-EE-048](LAWS.md#l-ee-048--cop2vu0-instructions-cannot-come-from-c)). Treat the region as hand-written assembly — either carry it as inline
assembly in the reconstruction or set the function aside; do not spend the diagnostic loop on it.

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
