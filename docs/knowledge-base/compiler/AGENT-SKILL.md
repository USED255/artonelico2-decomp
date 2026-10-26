# Agent skill — attacking a matching diff with this handbook

[Handbook index](README.md) · [简体中文](AGENT-SKILL.zh-CN.md) · [Laws](LAWS.md) · [Diagnostics](DIAGNOSTICS.md) · [Field guide](FIELD-GUIDE.md)

This page is the entry point for an automated agent (or a person in a hurry) that has one job: turn a
wrong matching diff into a source edit that moves it. It is deliberately short. The handbook is the
reference; this is the loop.

> **Starting from a shape rather than a symptom?** Use [QUICK-REFERENCE.md](QUICK-REFERENCE.md): it maps
> what you see in a frame, an instruction stream or a data section to the law that explains it.

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

# 1. Is this region even C? COP2/VU0 and MMI instructions are hand-written assembly and no C
#    spelling will match them - check before spending a loop on it.
python3 tools/compiler/ee-gcc-coverage.py --elf "$TARGET"

# 2. Which pass owns the difference?
python3 tools/compiler/ee-gcc-passdiff.py candidate.c variant.c

# 3. What does the compiler do at that pass?
python3 tools/compiler/laws-query.py pass 23.greg
python3 tools/compiler/laws-query.py find allocation

# 4. What edit moves it?
python3 tools/compiler/laws-query.py guide frame
python3 tools/compiler/laws-query.py guide "live range"

# 5. Observe your own file: frame composition, constant pool, mnemonic histogram. This is the
#    first measurement to take when you are not sure what the compiler did to *your* source.
python3 tools/compiler/ee-gcc-observe.py --src candidate.c --flags="-O2 -G0"

# 6. Frame too large? Decompose it before editing anything: every spill is traced to the line
#    that defined it, and the last use is what sets the live range.
python3 tools/compiler/ee-gcc-spill-map.py --src candidate.c --flags="-O2 -G0"

# 7. Register-allocation residual? Get the compiler's own answer: the order, every find_reg
#    attempt, the allocnos with no register, and which preferences pruning removed. Needs gdb.
python3 tools/compiler/ee-gcc-observe-alloc.py --src candidate.c --flags="-O2 -G0" --prefs

# 8. What is the compiler *actually* doing at the decision point?
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8

# 9. Re-measure. A lever that does not move the reading is not a lever.
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
* Do not report a colouring model as "modelled". The current state is [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer):
  the measured rule reproduces **46.5%** of held-out dispositions (34.3% for the earlier heuristic, 9.1% for a
  mainline-modelled replay), and 82.7% when the dynamic conflict set is held at ground truth. Two levers were
  tried and rejected — a rotating scan start and live-range-derived occupancy. When you add a rule here, test it
  **both** end-to-end and with the oracle context: a rule that gains end-to-end but loses under the oracle is
  compensating for the model's own errors, not modelling the compiler.

## Feeding back

The handbook is versioned, and an unattended agent is expected to leave it better:

1. Found a mechanism the handbook does not have? Add a law to `laws.json` **and** `LAWS.md`
   (the data check fails if only one is updated), with `source_anchor`, `binary_anchor`, `receipt`
   and `scope`.
2. Found a lever that moves a measurement? Add it to `FIELD-GUIDE.md` with the before/after numbers.
3. Disproved a law? Add the falsification to that law and record it in the research repository's
   pitfall ledger.
4. Wrote a new tool? Mention it here — the laws check fails if a `tools/compiler/*.py` is not named on this page.
5. Run `python3 tools/check/test_compiler_laws.py` and `python3 tools/check/test_compiler_tools.py` before you stop. It enforces the tier
   preconditions and re-verifies every binary anchor against the `cc1` on this machine.
