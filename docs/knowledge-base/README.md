# Knowledge base

[English](README.md) | [简体中文](README.zh-CN.md)

Reference material about this game and its toolchain. The operational documents (build, policy,
transcription, contribution) stay one level up in [docs/](../README.md).

## 1. Compiler handbook

The [EE GCC 3.2 code generation handbook](compiler/README.md) records what the compiler that built
the game code does, at the flags this project builds with. Every entry carries a tier, a source
anchor, a binary anchor, a receipt and a scope. `make check` verifies the data and re-checks every
binary anchor against the `cc1` on your machine.

| Page | Contents |
| --- | --- |
| [compiler/README.md](compiler/README.md) | the handbook index, the evidence tiers, and the tools |
| [compiler/LAWS.md](compiler/LAWS.md) | what the compiler does: allocation order, struct widths, frequency accounting, the EE backend |
| [compiler/QUICK-REFERENCE.md](compiler/QUICK-REFERENCE.md) | start from the shape in front of you and find the law that explains it |
| [compiler/DIAGNOSTICS.md](compiler/DIAGNOSTICS.md) | from "the diff looks wrong" to "this pass owns it" |
| [compiler/FIELD-GUIDE.md](compiler/FIELD-GUIDE.md) | the source spellings that move a measurement |
| [compiler/CASE-STUDY.md](compiler/CASE-STUDY.md) | one function end to end, including a rejected edit |
| [compiler/CASE-STUDY-LARGE.md](compiler/CASE-STUDY-LARGE.md) | a large function, read through its frame |
| [compiler/ABI.md](compiler/ABI.md) | the calling convention on one page |
| [compiler/PASSES.md](compiler/PASSES.md) | the `-da` dumps, and which source file owns each one |
| [compiler/CROSS-2.96.md](compiler/CROSS-2.96.md) | which rules transfer to the 2.96 compiler that builds the CRI middleware |
| [compiler/SOURCE-STUDY.md](compiler/SOURCE-STUDY.md) | what compiler source exists, and how a rule is anchored |
| [compiler/COVERAGE.md](compiler/COVERAGE.md) | how much of a binary the handbook explains, measured |
| [compiler/VERIFY.md](compiler/VERIFY.md) | the pinned toolchain, and what each check verifies |
| [compiler/AGENT-SKILL.md](compiler/AGENT-SKILL.md) | the loop for an automated agent |
| [compiler/laws.json](compiler/laws.json) | the same laws as data, for tools and agents |

## 2. Project reference

| Page | Contents |
| --- | --- |
| [KNOWN-BLOCKERS.md](KNOWN-BLOCKERS.md) | what cannot be closed with this toolchain, and the stop conditions |
| [FORMATS.md](FORMATS.md) | the disc's asset and module formats, as measured |
| [TOOLCHAIN.md](TOOLCHAIN.md) | which compiler built what, the build flags, and how to verify your copy |
| [LANGUAGE.md](LANGUAGE.md) | why the matched source is C, and when a translation unit may need C++ |
| [GLOSSARY.md](GLOSSARY.md) | terms, formats and abbreviations used by this project |

## 3. How this section is maintained

- A new compiler mechanism, or a lever that moves a measurement, becomes a law or a field-guide row
  in `compiler/`. A hard function match is not finished until its mechanism is written down there.
- A new measured fact about the disc goes into `FORMATS.md`; a new compiler or build fact goes into
  `TOOLCHAIN.md`. Keep both free of numbers that move with progress.
- Every page has an English original and a Chinese edition next to it (`*.zh-CN.md`). The English
  page is the primary one.
- Nothing here may contain a game asset, a ROM image, a copied assembly listing, or the Sony
  toolchain. See [PUBLICATION-POLICY.md](../PUBLICATION-POLICY.md).
