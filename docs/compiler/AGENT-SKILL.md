# Agent skill — attacking a matching diff with this handbook

[Handbook index](README.md) · [Laws](LAWS.md) · [Diagnostics](DIAGNOSTICS.md) · [Field guide](FIELD-GUIDE.md)

This page is the entry point for an automated agent (or a person in a hurry) that has one job: turn a
wrong matching diff into a source edit that moves it. It is deliberately short. The handbook is the
reference; this is the loop.

## Ground rules

1. **Never edit the build.** The model is read-only. No new compiler flags, no changed
   `source_flags.tsv`, no changed build scripts. If a lever seems to need one, stop and escalate.
2. **Only 100.0 counts as matched.** A heuristic improvement is not a result.
3. **Never write an unanchored strong claim.** Every statement about compiler behaviour is either
   `T1` (source + binary anchor + behaviour), `T2`, `T3`, or it is not written. Look up the law
   instead of recalling it: `laws-query.py` is the memory.
4. **No game content in anything published.** Anchors are compiler-internal symbols, addresses,
   line numbers and constants.
5. **Record the falsification.** If a law led you wrong, say so in the same place you used it.

## The loop

```sh
# 0. What does the diff actually say?
#    Read it in this order: control flow -> instruction shape -> register allocation -> stack.
#    Below ~80% match this is a structural problem: rewrite the C, do not consult the model.

# 1. Which pass owns the difference?
python3 tools/compiler/ee-gcc-passdiff.py candidate.c variant.c

# 2. What does the compiler do at that pass?
python3 tools/compiler/laws-query.py pass 23.greg
python3 tools/compiler/laws-query.py find allocation

# 3. What edit moves it?
python3 tools/compiler/laws-query.py guide frame
python3 tools/compiler/laws-query.py guide "live range"

# 4. What is the compiler *actually* doing at the decision point?
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8

# 5. Re-measure. A lever that does not move the reading is not a lever.
```

## Reading a law when you have one

* `tier` tells you how much to trust it. `T1` means the code was located in the shipped `cc1`.
* `source anchor` line numbers are **mainline** and do **not** transfer
  ([L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)). For the real line,
  anchor the symbol yourself.
* `receipt` is what was measured, and `scope` is what it covered. Read both before generalising.
* `falsifies` is a claim this law replaced. Almost every law here replaced a plausible wrong belief.

## Do not

* Do not reason about register allocation from disassembly alone. Use the dumps: the compiler prints
  its own decisions.
* Do not treat `24.postreload` reload bookkeeping as register references; it inflates use counts.
* Do not compare objects across different translation-unit layouts without normalising absolute
  addresses and jump tables.
* Do not trust a lower `-O` level, a different `-G`, or a 2.96 build to reproduce 3.2 behaviour: the
  pass numbering differs and 2.96 builds only the CRI middleware here.
* Do not report a colouring model as "modelled". The current state is recorded in
  [LAWS.md](LAWS.md) open items: a preference-first heuristic reproduces 34.3% of recorded
  dispositions, and a source-faithful replay does worse.

## Feeding back

The handbook is versioned, and an unattended agent is expected to leave it better:

1. Found a mechanism the handbook does not have? Add a law to `laws.json` **and** `LAWS.md`
   (the data check fails if only one is updated), with `source_anchor`, `binary_anchor`, `receipt`
   and `scope`.
2. Found a lever that moves a measurement? Add it to `FIELD-GUIDE.md` with the before/after numbers.
3. Disproved a law? Add the falsification to that law and record it in the research repository's
   pitfall ledger.
4. Run `python3 tools/check/test_compiler_laws.py` before you stop. It enforces the tier
   preconditions and re-verifies every binary anchor against the `cc1` on this machine.
