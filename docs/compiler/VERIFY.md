# Verify — the environment these claims were measured on, and how to re-run them

Every behavioural claim in this handbook was **measured**, not recalled, and the measurements are pinned to a
specific toolchain. This page records that toolchain so you can reproduce the checks, and states plainly what
each check verifies and what it silently skips.

## The compilers

| | 3.2 | 2.96 |
| --- | --- | --- |
| version string | `ee-gcc (GCC) 3.2-ee-040921` | `2.96-ee-001003-1` |
| `cc1` | `…/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1` | `…/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cc1` |
| `cc1` sha256 | `0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d` | `59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5` |
| `cc1` size | 7 201 720 | 5 526 661 |

The game's code is 3.2; the CRI middleware's is 2.96. Code and constants are anchored so that the binary
`cc1` decides: where a symbol or constant is cited, [`ee-gcc-anchor.py`](../tools/compiler/ee-gcc-anchor.py)
resolves it in **this** binary, and the check suite re-resolves it on every run.

**If your `cc1` has a different hash**, the binary anchors may move — addresses, struct sizes and enum values
are properties of the binary. Re-run the anchor suite and treat a moved address as the signal that you are
looking at a different build, not at a wrong law.

## The assembler and disassembler

`objdump` here is **GNU Binutils 2.40** (`mips-ps2-decompals-objdump`), a *modern* binutils rather than the
original SDK tools. This matters: several mnemonic spellings this handbook documents are that disassembler's
choices, not the instruction's name —

* `daddu $d,$s,$0` is printed **`move`** ([L-EE-046](LAWS.md#l-ee-046--every-move-is-a-64-bit-daddu));
* `addu`-based `move` does not exist as a copy in this compiler's output;
* `li` is printed for a small `ADDIU`/`ORI`, and the two-instruction form appears as `lui` + `ori`;
* `beql`/`bnel` against `$0` are printed `beqzl`/`bnezl` ([L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not));
* `ulw`/`usw` never appear in an object — they are assembler pseudo-instructions that expand to `lwr`+`lwl`
  ([L-EE-044](LAWS.md#l-ee-044--unaligned-access-three-sources-and-ulwusw-do-not-exist-in-the-object)).

A different binutils may spell these differently. The laws are stated at the level of the **encoding** wherever
that is what matters, and the check suite verifies the encodings directly
(`move` is funct `0x2d`; `li` is opcode `0x09` or `0x0d`).

## Running everything

```sh
make check                                  # repository checks + law data + anchors + tool smoke tests
python3 tools/check/test_compiler_laws.py   # laws.json <-> LAWS.md, anchors, coverage, drift guards
python3 tools/check/test_compiler_tools.py  # every tool's self-test (skips what the machine lacks)
python3 tools/compiler/ee-gcc-observe.py --selftest   # every fixture, against this compiler
python3 tools/compiler/ee-gcc-observe.py --matrix     # the fixtures at -O0/-O1/-O2/-Os/-O3
python3 tools/compiler/ee-gcc-coverage.py --selftest  # the coverage classifier (no toolchain needed)
```

### What each suite checks, and what it skips

| suite | verifies | skips when |
| --- | --- | --- |
| `test_compiler_laws.py` | every law has a page section and a `laws.json` entry; every anchor resolves; every in-page and cross-page anchor resolves; every law is reachable from the quick reference; the fixture count in the docs equals the tool's; every `tools/compiler/*.py` is named in the skill page; two byte-level encodings | never — it is pure data + the local `cc1`/`objdump` if present |
| `test_compiler_tools.py` | each tool's `--selftest`; a fixture suite that must report `0 failed`; the 2.96 cross-checks | a tool, `cc1`, the 2.96 compiler or `objdump` that this machine lacks (reported as `skip`, never as a pass) |
| `--matrix` | which rules hold at which level | nothing; a level may legitimately fail a fixture, and the matrix reports it rather than hiding it |

The matrix is a **deliberate** part of the harness: it has caught several of this handbook's own errors —
a level-dependent `mult1`, an over-general claim about the loop back edge, and an alignment check that was
reading the wrong artefact. A claim that holds at `-O2` and silently not at `-Os` is found here, not in prose.

## What the handbook is pinned to

* **Level**: `-O2 -G0` unless a law says otherwise; the level matrix records where a rule changes.
* **Alignment**: the project builds with `-falign-functions=4 -ffunction-sections`
  ([L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)) and **no** `-G` and **no** `-mlong*`; a repository check fails if
  `build_mixed.sh`'s `MATCHED_CFLAGS` default and the flags stated here ever disagree.
* **Source**: the semantic anchor is **mainline gcc-3.2.3**; the shipped Sony tree is *not* available, so
  everything EE-specific is measured rather than read ([SOURCE-STUDY](SOURCE-STUDY.md)).
* **Tiers**: `T1` = located in the shipped `cc1` and re-verified in the binary; `T2` = measured behaviour;
  `T3` = context or negative knowledge. A law's tier is the honest statement of how much to trust it.

**Live observation (optional).** `tools/compiler/ee-gcc-observe-alloc.py` drives the `cc1` under `gdb`.
It was tested with gdb 16.3 on the pinned `cc1`; on any other build the hook addresses are resolved from
that binary by symbol and the eight-byte entry guards are skipped with a warning. When gdb is absent the
tool exits with a message, and the check suite reports its selftest as SKIP — never as a pass.

## Reporting a failure

If a check fails on your machine, the useful report is: **which check**, the **`cc1` sha256**, and the
**objdump version**. If an anchor moved, that is a different build. If a fixture fails only at one level, that
is a rule whose level-dependence the handbook has not recorded yet — which is a finding, not noise.
