# Ar tonelico II: Melody of Metafalica — matching decompilation

[English](README.md) | [简体中文](README.zh-CN.md)

[![Progress](https://decomp.dev/USED255/artonelico2-decomp.svg?mode=shield)](https://decomp.dev/USED255/artonelico2-decomp)

This repository contains reverse-engineered C source for the PlayStation 2 game
**Ar tonelico II: Melody of Metafalica** (Japanese release `SLPS_258.19`).

The source in `src/matched/` compiles with the original compiler toolchain.
The build compares the result with the retail binary byte by byte. A function is
**matched** when the two byte sequences are equal.

**Contributions are welcome** — read [CONTRIBUTING.md](CONTRIBUTING.md).

## Status

As of 2026-10-13 ([progress/baseline.json](progress/baseline.json), build `2949d509`,
report `sha256:f3e6f78a971c2117…`, payload `sha1:7cc42d275750600d…`):

- Matched functions: **3,386 / 10,923 (31.00%)**
- Matched code: **177,320 / 2,276,780 bytes (7.79%)**

We do not count the assembly stubs that we copied. CI does not publish a report
that is worse than the baseline. Progress history:
<https://decomp.dev/USED255/artonelico2-decomp>.

## Build

You supply the items below. This repository does not contain them:

1. `SLPS_258.19`, from your own game disc.
2. The original EE compiler toolchain. Sony owns this toolchain. You cannot
   redistribute it.
3. `splat` and `objdiff-cli`. These tools are public.

Read [docs/BUILD.md](docs/BUILD.md). Then run these commands:

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build      # assemble, link, and check the payload hash
make report     # write the progress report
```

## Documentation

Full index: [docs/README.md](docs/README.md). New to the project? Start with:

| | |
| --- | --- |
| [docs/BUILD.md](docs/BUILD.md) | how to configure and build |
| **[docs/compiler/README.md](docs/compiler/README.md)** | **the EE GCC 3.2 code generation handbook** — every law is source-anchored, anchored to the shipped `cc1`, and verified by behaviour |
| [docs/compiler/LAWS.md](docs/compiler/LAWS.md) | the laws themselves, with tiers and receipts |
| [docs/compiler/CASE-STUDY.md](docs/compiler/CASE-STUDY.md) | one function end to end, including a rejected edit |
| [docs/compiler/DIAGNOSTICS.md](docs/compiler/DIAGNOSTICS.md) | from "the diff is wrong" to "which pass is responsible" |
| [docs/compiler/FIELD-GUIDE.md](docs/compiler/FIELD-GUIDE.md) | source-level changes that move the numbers |
| [docs/compiler/SOURCE-STUDY.md](docs/compiler/SOURCE-STUDY.md) | what compiler source exists, what does not, and how a rule is anchored |
| [docs/compiler/AGENT-SKILL.md](docs/compiler/AGENT-SKILL.md) | the loop for an automated agent |

Tools: `tools/compiler/laws-query.py` (query the laws), `tools/compiler/ee-gcc-anchor.py` (resolve a
symbol, address, struct or constant in the shipped compiler), `tools/compiler/ee-gcc-passdiff.py`
(first diverging pass), `tools/compiler/ee-gcc-spill-map.py` (map a too-large frame onto source lines).
Chinese editions of every handbook page sit next to it (`*.zh-CN.md`).

## Legal

- This repository contains no game code, no game asset, and no ROM image.
  You must own the game.
- The reverse-engineered source is our work. The licence is GPL-3.0.
  See [LICENSE](LICENSE).
- Read [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md).
- This project is not affiliated with GUST, Banpresto, or NIS.
