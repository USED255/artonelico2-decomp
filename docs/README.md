# Documentation

[English](README.md) | [简体中文](README.zh-CN.md)

Where to start depends on what you are doing.

## 1. Working on the repository

| I want to… | Read |
| --- | --- |
| build the project | [BUILD.md](BUILD.md) |
| know what may be published | [PUBLICATION-POLICY.md](PUBLICATION-POLICY.md) |
| understand the transcription metric | [TRANSCRIPTION.md](TRANSCRIPTION.md) |
| contribute a matched function | [../CONTRIBUTING.md](../CONTRIBUTING.md) |

## 2. Reference material

The [knowledge base](knowledge-base/README.md) keeps what does not change every day: how the
compiler behaves, what the disc contains, and what cannot be matched.

| I want to… | Read |
| --- | --- |
| understand why the compiler emitted this code | [knowledge-base/compiler/README.md](knowledge-base/compiler/README.md) |
| know what cannot be matched, and where to stop | [knowledge-base/KNOWN-BLOCKERS.md](knowledge-base/KNOWN-BLOCKERS.md) |
| read the asset and module formats on the disc | [knowledge-base/FORMATS.md](knowledge-base/FORMATS.md) |
| check which compiler built the game code | [knowledge-base/TOOLCHAIN.md](knowledge-base/TOOLCHAIN.md) |
| decide between C and C++ | [knowledge-base/LANGUAGE.md](knowledge-base/LANGUAGE.md) |
| look up a term or abbreviation | [knowledge-base/GLOSSARY.md](knowledge-base/GLOSSARY.md) |
| browse the whole knowledge base | [knowledge-base/README.md](knowledge-base/README.md) |

Every document has a Chinese edition next to it (`*.zh-CN.md`). The handbook is data-backed:
[`knowledge-base/compiler/laws.json`](knowledge-base/compiler/laws.json) is its machine-readable
index, and `make check` verifies the laws, re-checks every binary anchor against the `cc1` on your
machine, and smoke-tests every command the handbook documents.

Repository-wide entry points: [README.md](../README.md), [CONTRIBUTING.md](../CONTRIBUTING.md),
[tools/README.md](../tools/README.md).
