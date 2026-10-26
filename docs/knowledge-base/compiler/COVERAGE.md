# Coverage — how much of a binary this handbook explains

A handbook of compiler behaviour is only useful if it is complete enough to account for the code you are
actually looking at. That is a measurable claim, not an impression: take a disassembly, collect its
mnemonics, and ask which of them the handbook mentions anywhere. Whatever is left over classifies itself.

```sh
# the project's objdump piped straight in
mips-ps2-decompals-objdump -d prog.elf | python3 tools/compiler/ee-gcc-coverage.py --asm -

# an assembly listing, or an ELF directly
python3 tools/compiler/ee-gcc-coverage.py --asm func.s
python3 tools/compiler/ee-gcc-coverage.py --elf prog.elf

python3 tools/compiler/ee-gcc-coverage.py --selftest
```

The tool reports three numbers and two lists:

| | meaning |
| --- | --- |
| **explained by a rule** | the mnemonic is named in `docs/knowledge-base/compiler/` **and** the compiler can emit it from C |
| **assembly-only** | the compiler **cannot** emit it from C, so it comes from hand-written assembly |
| **unexplained** | neither — these are the handbook's real gaps |

Classification comes **before** the mention test, and deliberately so: naming `mthi` in a sentence about
inline assembly must not turn it into "explained". (An earlier version of this tool did exactly that and
over-reported its own coverage by 1.3 points; the split below is the corrected one.)

`OTHER` is the interesting number: it is the handbook's own to-do list, and it can be driven to zero.
`ASM_ONLY` is not a gap but a **result** — see below.

## Why `ASM_ONLY` is a result, not a gap

[L-EE-048](LAWS.md#l-ee-048--cop2vu0-instructions-cannot-come-from-c) establishes, by measurement, that this compiler emits **no COP2/VU0 code
from C**: `mode(V4SI)` and `mode(V4SF)` loads and stores use `lq`/`sq` in general registers, vector arithmetic
and by-value vector returns are compile errors, and the only path to `lqc2`/`sqc2` is inline assembly. The same
holds for the **MMI packed arithmetic** family: `mode(V8HI)`, `mode(V16QI)` and `mode(V4SI)` values are moved
with `lq`/`sq` and nothing else. Privileged instructions (`syscall`, `sync`, `cache`, `mfc0`, the trap
instructions) have no builtin at all — there is no `__builtin_ee_*` in this compiler.

So when the tool classifies an instruction as `ASM_ONLY` it is telling you something actionable: **that region
of the binary was written as assembly in the original source, and a C reconstruction cannot match it.** The
diagnostic path is in [DIAGNOSTICS](DIAGNOSTICS.md) §5: carry it as inline assembly, or set the function aside.

## The classification lists

`ASM_ONLY` covers three families:

* **COP2 / VU0** — `lqc2`, `sqc2`, `qmfc2`, `qmtc2`, `cfc2`, `ctc2` and the whole `v*` macro-mode set
  (`vadd`, `vmul`, `vopmula`, `vftoi4`, …);
* **MMI packed arithmetic** — `padd*`, `psub*`, `pmax*`, `pmin*`, `pcpy*`, `pext*`, `pand`/`por`/`pnor`,
  `qfsrv`, `mtsab`, and the second multiply/divide unit (`mult1`, `div1`, `mflo1`, `mthi1`, …);
* **privileged / system** — `syscall`, `sync`, `cache`, `pref`, `mfc0`/`mtc0`, `tlb*`, `eret`, the trap
  instructions, and the HI/LO and COP1-control writes (`mthi`, `mtlo`, `ctc1`).

Note that `mult1` deserves care: the *second multiplier* is reachable from C
([L-EE-049](LAWS.md#l-ee-049--variable-shifts-negation-float-compare--and-the-second-multiplier) — the scheduler uses it at `-O2`/`-O3` when multiplies overlap), while its
HI/LO companions `mflo1`/`mthi1` are not. The tool classifies by mnemonic, so treat its output as a starting
point and follow the law when a mnemonic appears on both sides of the line.

## What this method found

Running the audit while writing this handbook drove `OTHER` to **zero** on the reference binary used during
development (a 9 MB `.text`): every mnemonic in it is now either explained by a rule or classified as
assembly-only. The remaining work on the handbook is depth, not breadth — but the method is the point, and it
works on your binary too:

```sh
mips-ps2-decompals-objdump -d your.elf | python3 tools/compiler/ee-gcc-coverage.py --asm -
```

If `OTHER` is non-empty for you, that is a finding worth reporting — either the handbook is missing a rule, or
`classify()` in the tool is missing a family.

## Coverage is not correctness

This page measures **breadth**: whether an instruction's origin is explained. It says nothing about whether a
particular reconstruction matches. For that, the answers live elsewhere: the symptom-first lookup in
[QUICK-REFERENCE](QUICK-REFERENCE.md), the lever tables in [LAWS](LAWS.md), and the pass-level view in
[PASSES](PASSES.md); and the executable half of the claim is in the fixture suite
(`tools/compiler/ee-gcc-observe.py --selftest`, `--matrix`).
