# Knowledge base

[English](README.md) | [简体中文](README.zh-CN.md)

Reference material about this game and its toolchain. The operational documents (build, policy,
transcription, contribution) stay one level up in [docs/](../README.md).

## 1. Compiler handbook

The [EE GCC 3.2 code generation handbook](compiler/README.md) records what the compiler that built
the game code does, at the flags this project builds with. The handbook's own index lists every
page: the laws, the pass map, the diagnostics workflow, the case studies, the ABI page, and the
tools.

`laws.json` is the machine-readable copy. `make check` verifies it and re-checks every binary
anchor against the `cc1` on your machine.

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
