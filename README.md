# Ar tonelico II: Melody of Metafalica — matching decompilation

[English](README.md) | [简体中文](README.zh-CN.md)

This repository contains reverse-engineered C source for the PlayStation 2 game
**Ar tonelico II: Melody of Metafalica** (Japanese release `SLPS_258.19`).

The source in `src/matched/` compiles with the original compiler toolchain.
The build compares the result with the retail binary byte by byte. A function is
**matched** when the two byte sequences are equal.

> **Contributions are welcome.** This repository is generated: a private exporter
> writes it from a working repository, and a maintainer imports an accepted change
> there. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the steps.

## Status

The file `progress/SLPS_258.19_report.json` contains the current numbers:

- matched functions,
- matched code bytes,
- total functions and total code bytes.

The file `progress/baseline.json` contains the accepted baseline. CI does not
publish a report that is worse than the baseline.
Progress history: <https://decomp.dev/>.

## Layout

```
src/matched/    the product: one C file for each recovered function
config/         splat configuration, symbol table, compiler flags, match ledger
tools/          build driver, report generator, repository checks
progress/       the current report and the accepted baseline
docs/           build instructions and the publication policy
```

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

## How CI verifies the result

CI runs three checks:

1. **Payload hash.** The linked executable must equal the retail payload.
   The sha1 value is `7cc42d275750600d1f232b2632447f77205f3fc0`.
2. **Function match.** Each changed file in `src/matched/` must match its
   original function 100%.
3. **No regression.** The new report must not be worse than the baseline.

If one check fails, CI stops and publishes no progress report.

## Legal

- This repository contains no game code, no game asset, and no ROM image.
  You must own the game.
- The reverse-engineered source is our work. The licence is GPL-3.0.
  See [LICENSE](LICENSE).
- Read [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md).
- This project is not affiliated with GUST, Banpresto, or NIS.
