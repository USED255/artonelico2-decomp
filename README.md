# Ar tonelico II: Melody of Metafalica — matching decompilation

Reverse-engineered C source for the retail PlayStation 2 executable **`SLPS_258.19`** (Ar tonelico II, 日版).
The C in `src/` is compiled with the **original compiler** and compared function-by-function against the
retail binary; a translation unit counts as matched only when the produced bytes are identical.

> **This repository is generated.** It is exported from a private working repository by a manifest-driven
> exporter. Do not open pull requests here — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Status

<!-- STATUS:BEGIN (filled by the exporter from progress/SLPS_258.19_report.json) -->
- Code matched (byte-exact): **see `progress/SLPS_258.19_report.json`**
- Functions matched: same file (`matched_functions` / `total_functions`)
- Progress history: <https://decomp.dev/>
<!-- STATUS:END -->

Only the reverse-engineered **C sources** are counted here — functions that are still provided as assembly
are not claimed as decompiled.

## Layout

```
src/matched/       the product: one C file per recovered function
config/            splat config, symbol table, per-file compiler flags, match ledger
tools/             build driver, objdiff report generation, project checks
progress/          the latest progress report + the accepted baseline
docs/              build instructions and the publication policy
```

## Building

You need **your own copies** of these — none of them are in this repository:

1. Ar tonelico II (Japan), `SLPS_258.19` — the retail executable, extracted from your own disc.
2. The original EE compiler toolchain (`ee-gcc 3.2-ee-040921`, `ee-gcc 2.96`, PS2 binutils) — Sony-licensed,
   not redistributable.
3. `objdiff-cli` (public) and `splat` (public, `pip install`).

Then:

```bash
python3 configure.py --game /path/to/SLPS_258.19        # checks inputs, writes build config
make build                                              # assemble the baseline, link, verify the payload hash
make report                                             # objdiff progress report
```

Details (exact versions, pinned hashes, troubleshooting): [docs/BUILD.md](docs/BUILD.md).

## How matching is verified

1. **Payload hash ratchet** — re-linking the whole executable must reproduce the retail payload byte-for-byte
   (sha1 `7cc42d275750600d1f232b2632447f77205f3fc0`).
2. **Per-function diff** — every C file that replaces assembly must match its original function 100%.
3. **Progress report** — `progress/SLPS_258.19_report.json` is regenerated and must not regress against
   `progress/baseline.json`.

CI enforces all three: a push that adds a source which does not match (or that breaks the ratchet) **fails**,
and no progress artifact is published.

## Legal

- No game code, assets, ROM/ISO images, or Sony SDK binaries are distributed here. You must own the game.
- The reverse-engineered sources in this repository are our own work, licensed **GPL-3.0** (see [LICENSE](LICENSE)).
- Publication rules for this repository: [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md).
- This is an unofficial fan research project, not affiliated with or endorsed by GUST / Banpresto / NIS.
