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

As of 2026-10-15 ([progress/baseline.json](progress/baseline.json), build `5bcaf2c`,
report `sha256:801d7fab1d3d…`, payload `sha1:7cc42d275750600d…`):

- Matched functions: **4,105 / 10,923 (37.58%)**
- Matched code: **224,364 / 2,276,780 bytes (9.85%)**
> **Two metrics.** Main = reconstructed C only (above). Separately, **619 functions / 321,812 bytes** are
> matched by byte-identical assembly transcription (no reconstructed C) and are **not** counted above.
> The byte-identical **match build** total is **4,724 / 10,923 (43.25%)**, code **546,176 B (23.99%)**.
> See [docs/TRANSCRIPTION.md](docs/TRANSCRIPTION.md).


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

## Legal

- This repository contains no game code, no game asset, and no ROM image.
  You must own the game.
- The reverse-engineered source is our work. The licence is GPL-3.0.
  See [LICENSE](LICENSE).
- Read [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md).
- This project is not affiliated with GUST, Banpresto, or NIS.
