# Documentation

[English](README.md) | [简体中文](README.zh-CN.md)

Where to start depends on what you are doing.

| I want to… | Read |
| --- | --- |
| build the project | [BUILD.md](BUILD.md) |
| know what may be published | [PUBLICATION-POLICY.md](PUBLICATION-POLICY.md) |
| **understand why the compiler emitted this code** | **[compiler/README.md](compiler/README.md)** — the EE GCC 3.2 codegen handbook |
| fix a function that compiles but does not match | [compiler/DIAGNOSTICS.md](compiler/DIAGNOSTICS.md), then [compiler/FIELD-GUIDE.md](compiler/FIELD-GUIDE.md) |
| see the handbook's rules and their evidence | [compiler/LAWS.md](compiler/LAWS.md) |
| work one function end to end, including a rejected edit | [compiler/CASE-STUDY.md](compiler/CASE-STUDY.md) |
| know what compiler source exists and how rules are anchored | [compiler/SOURCE-STUDY.md](compiler/SOURCE-STUDY.md) |
| know whether these rules apply to the CRI middleware | [compiler/CROSS-2.96.md](compiler/CROSS-2.96.md) |
| drive the handbook from an agent | [compiler/AGENT-SKILL.md](compiler/AGENT-SKILL.md) |

Every handbook page has a Chinese edition next to it (`*.zh-CN.md`). The handbook is data-backed:
[`compiler/laws.json`](compiler/laws.json) is the machine-readable index, and `make check` verifies the
laws, re-checks every binary anchor against the `cc1` on your machine, and smoke-tests every command the
handbook documents.

Repository-wide entry points: [README.md](../README.md), [CONTRIBUTING.md](../CONTRIBUTING.md),
[tools/README.md](../tools/README.md).
