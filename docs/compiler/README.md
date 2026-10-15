# EE GCC 3.2 codegen handbook

[简体中文](README.zh-CN.md) · [Laws](LAWS.md) · [Case study](CASE-STUDY.md) · [Source study](SOURCE-STUDY.md) · [Agent skill](AGENT-SKILL.md) · [Pass map](PASSES.md) · [Diagnostics](DIAGNOSTICS.md) · [Field guide](FIELD-GUIDE.md) · machine-readable index: [`laws.json`](laws.json)

**Verified against the shipped compiler.** All **13** binary anchors cited here have been resolved
against the shipped `cc1` and match their addresses; `python3 tools/check/test_compiler_laws.py`
enforces the tiers and re-verifies the anchors whenever the toolchain is present, and
`tools/check/test_compiler_tools.py` smoke-tests every command this handbook documents (both run inside
`make check`).

This handbook records the behaviour of **`ee-gcc 3.2-ee-040921`** — the compiler that built the
PlayStation 2 Emotion Engine code in this project — at the flags this project builds with:
`-O2 -falign-functions=4 -ffunction-sections`.

It is written for matching decompilation. The goal of a matching build is byte-identical output, so
"why did the compiler emit *this*?" is the question that costs the most time. Each law answers one
such question with evidence, and each lever names the source spelling that moves the measurement.

## What is here

| Page | Contents |
| --- | --- |
| [LAWS.md](LAWS.md) · [中文](LAWS.zh-CN.md) | What the compiler does: allocation order, struct widths, frequency accounting, the EE backend. Every entry carries a tier, a source anchor, a binary anchor, a receipt and a scope |
| [PASSES.md](PASSES.md) · [中文](PASSES.zh-CN.md) | The 26 `-da` dumps of 3.2 (22 for 2.96), which source file owns each one, and how far the shipped source drifts from mainline |
| [DIAGNOSTICS.md](DIAGNOSTICS.md) · [中文](DIAGNOSTICS.zh-CN.md) | From "the diff looks wrong" to "this pass owns it": the first-divergence workflow, its two false signals, and when the model should not be used at all |
| [FIELD-GUIDE.md](FIELD-GUIDE.md) · [中文](FIELD-GUIDE.zh-CN.md) | The source spellings that move a measurement, with the measurement each one moves |
| [CASE-STUDY.md](CASE-STUDY.md) · [中文](CASE-STUDY.zh-CN.md) | One function end to end: the tools, the laws consulted, the edit tried, and why it was rejected |
| [SOURCE-STUDY.md](SOURCE-STUDY.md) · [中文](SOURCE-STUDY.zh-CN.md) | What source exists, what does not, how a rule is anchored, and why the community EE patches are a different tree |
| [AGENT-SKILL.md](AGENT-SKILL.md) · [中文](AGENT-SKILL.zh-CN.md) | The loop an agent (or a hurried person) runs: measure -> localise the pass -> look up the law -> apply the lever -> re-measure |
| [CROSS-2.96.md](CROSS-2.96.md) · [中文](CROSS-2.96.zh-CN.md) | Which of these rules transfer to the 2.96 compiler that builds the CRI middleware, and which does not |
| [`laws.json`](laws.json) | The same laws as data, for tooling and agents |

## Tools

| Tool | What it does |
| --- | --- |
| `tools/compiler/laws-query.py` | query the laws by id, pass, symptom, lever or free text (`--json` for tooling) |
| `tools/compiler/ee-gcc-anchor.py` | resolve a symbol, address, struct or constant in the shipped `cc1`; `selftest` re-checks the anchors this machine can verify |
| `tools/compiler/ee-gcc-passdiff.py` | compile two spellings of one function and report the first pass that diverges |
| `tools/compiler/ee-gcc-spill-map.py` | map a too-large frame onto its blocks and source lines, and trace each spill to the line that defined the value |
| `tools/compiler/ee-gcc-observe.py` | compile thirteen synthetic fixtures and assert what this handbook says must appear (`--selftest`), or print frame/pool/mnemonic observations for your own file |

`make check` runs the law data check, the binary-anchor re-verification and a smoke test of every command
above.

## Evidence tiers

Matching communities produce confident, plausible, wrong rules. The tiers exist to make that visible.

| Tier | Requires |
| --- | --- |
| **T1** | a rule read from the compiler source **and** the same code located in the shipped binary (symbol, address, constant or struct offset) **and** behaviour that agrees |
| **T2** | a source rule **or** a binary anchor, plus agreeing behaviour |
| **T3** | behaviour evidence only |

`T1` needs both anchors because the shipped compiler is not the mainline source. Two differences are
already measured (LAWS.md L-EE-003, L-EE-004), and one *suspected* difference turned out to be a
misread of a source comment (L-EE-005) — a wrong belief that a tier system catches and prose does
not.

Every law also carries a **scope**: what was covered. Nothing here claims a lever is impossible;
closed levers are recorded with the space that was searched.

## The two anchors

The shipped `cc1` is **not stripped and carries DWARF**, so the factory binary is a first-class source
of evidence. Given your own toolchain and a matching `cc1`:

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1

# symbol -> address -> source line, with instructions bound to lines
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64

# struct layout as the compiler itself saw it
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno

# a floating constant the codegen actually multiplies by
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8

# assert the anchors the handbook depends on
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" selftest
```

`python3 tools/check/test_compiler_laws.py` checks `laws.json` against `LAWS.md`, enforces the tier
preconditions, and verifies every binary anchor against the `cc1` on this machine when one is
present.

## Scope and honesty

* Everything is **`ee-gcc 3.2-ee-040921`**. `ee-gcc 2.96-ee-001003-1` builds this project's CRI
  middleware and has its own pass numbering; its rules are not claimed here.
* Mainline **gcc-3.2.3** is the semantic reference, never the line-number reference. The measured
  per-function drift is in L-EE-006.
* This repository contains no game assets, no disassembly of the game, and no compiler binaries.
  Anchors are compiler-internal symbols, addresses, line numbers and constants: symbol-level facts.
* The handbook is versioned and maintained. A new mechanism found while attacking a function is
  expected to come back here as a law or a lever, with its receipt.
