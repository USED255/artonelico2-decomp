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

As of 2026-10-25 ([progress/baseline.json](progress/baseline.json), build `d41a5de`,
report `sha256:307fcf819c07…`, payload `sha1:7cc42d275750600d…`):

- Matched functions: **4,281 / 10,923 (39.19%)**
- Matched code: **233,156 / 2,276,780 bytes (10.24%)**

The main metric counts reconstructed C only — see [docs/TRANSCRIPTION.md](docs/TRANSCRIPTION.md).

CI does not publish a report that is worse than the baseline. Progress history:
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

Full index: [docs/README.md](docs/README.md). The [knowledge base](docs/knowledge-base/README.md)
keeps the reference material that does not change every day:

| | |
| --- | --- |
| [docs/BUILD.md](docs/BUILD.md) | how to configure and build |
| **[docs/knowledge-base/compiler/README.md](docs/knowledge-base/compiler/README.md)** | **the EE GCC 3.2 code generation handbook** — every law is source-anchored, anchored to the shipped `cc1`, and verified by behaviour |
| [docs/knowledge-base/KNOWN-BLOCKERS.md](docs/knowledge-base/KNOWN-BLOCKERS.md) | what cannot be matched with this toolchain, and where to stop |
| [docs/knowledge-base/FORMATS.md](docs/knowledge-base/FORMATS.md) | the disc's asset and module formats, as measured |
| [docs/knowledge-base/TOOLCHAIN.md](docs/knowledge-base/TOOLCHAIN.md) | which compiler built what, and how to verify your copy |
| [docs/knowledge-base/GLOSSARY.md](docs/knowledge-base/GLOSSARY.md) | terms and abbreviations used by this project |

The handbook's tools live in `tools/compiler/`. Every page has a Chinese edition next to it
(`*.zh-CN.md`).

## Legal

- This repository contains no game code, no game asset, and no ROM image.
  You must own the game.
- The reverse-engineered source is our work. The licence is GPL-3.0.
  See [LICENSE](LICENSE).
- Read [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md).
- This project is not affiliated with GUST, Banpresto, or NIS.
