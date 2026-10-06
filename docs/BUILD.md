# Build this repository

[English](BUILD.md) | [简体中文](BUILD.zh-CN.md)

This repository contains the reverse-engineered C source and the tools that
verify it. It contains no material that another owner holds.

## 1. Items that you supply

| Item | Note |
| --- | --- |
| `SLPS_258.19` | The Japanese retail executable. Extract it from your own disc. The sha1 value is `766836783c16b8616d3d84cfbd6af70a50b6c052`. |
| `ee-gcc 3.2-ee-040921` | The compiler for the game code. Sony owns it. You cannot redistribute it. |
| `ee-gcc 2.96-ee-001003-1` | The compiler for the CRI sections. Sony owns it. |
| PS2 binutils | The decompals fork of binutils 2.40. It assembles the `splat` output. |
| `objdiff-cli` 3.8.2 | A public tool: <https://github.com/encounter/objdiff/releases>. |
| `splat` 0.50.0 | A public tool: `pip install splat64`. |

The file [toolchain.lock.json](../toolchain.lock.json) contains the versions and
the sha256 values. CI checks each sha256 value before it uses the file.

Put the compilers in `PATH`. You can also set `EE_GCC`, `EE_GCC_CRI`, and
`PS2_AS`.

```bash
export PATH="$HOME/eecc/ee-gcc3.2-040921/bin:$HOME/eecc/ee-gcc2.96/bin:$HOME/eecc/ps2binutils:$PATH"
```

## 2. Configure and build

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build          # split, assemble, link, and check the payload hash
make report         # write the progress report
```

This is a mixed-compiler build: the game code uses `ee-gcc 3.2-ee-040921` and the
CRI middleware uses `ee-gcc 2.96-ee-001003-1`. `config/compiler_map.tsv` states,
per source file, which compiler to use (absent = the game compiler); the two
paths come from `EE_GCC` / `EE_GCC_CRI` (or `GCC` / `GCC_CRI`). A source that
needs the CRI compiler also needs `-G0` in `config/source_flags.tsv`.

`make build` derives the payload from the retail executable. Then it splits the
payload, assembles the source, and links the result. It checks the payload sha1value after each stage. The expected value is
`7cc42d275750600d1f232b2632447f77205f3fc0`. One different byte stops the build.

## 3. Check a change

```bash
make delta BASE=origin/main      # each changed file in src/matched/ must match 100%
make check                       # repository checks; the retail executable is not necessary
```

## 4. CI

| Workflow | When it runs | What it does |
| --- | --- | --- |
| `validate` | Each push, each pull request, and a manual start | On a push it checks the publication record (`PUBLISHED.json`), the forbidden material, the report schema, and the baseline. On a pull request it allows any change **except** the publication content (`progress/**` and `PUBLISHED.json`). Read [CONTRIBUTING.md](../CONTRIBUTING.md). |
| `matching-gate` | A push to the default branch, an internal pull request, or a manual start | Gets the retail executable and the toolchain from a private companion repository. Then it runs `make build`, `make delta`, and `make report`. It publishes the artifact **only** when all checks pass. |

The `matching-gate` workflow needs the secret `ORIG_DEPLOY_KEY` and the variable
`PRIVATE_ORIG_REPO`. A pull request from a fork cannot get them. In that case the
workflow skips the job and does not fail. A maintainer then verifies the commit.

A failed check produces no new progress report. Therefore the public numbers are
always verified numbers.

Do you want to contribute a matched function? Read [CONTRIBUTING.md](../CONTRIBUTING.md).

## 5. Publish the report

After a green `matching-gate` run on the default branch, download the report
artifact. Then write it into this repository:

```bash
gh run download <run-id> -R <owner>/<repo> -n SLPS_258.19_report -D .tmp/report
python3 tools/publish_report.py --report .tmp/report/SLPS_258.19_report.json
```

The tool writes `progress/SLPS_258.19_report.json` and updates `PUBLISHED.json`.
It also checks the numbers against the baseline. Use `--accept-baseline` to make
the new report the baseline. Use `--refresh` after a change to
`toolchain.lock.json`.

## 6. Troubleshooting

- **`payload sha1 mismatch`** — one replaced source does not agree with the
  retail bytes. Run `make delta BASE=<last good commit>` to find the file.
- **The assembler rejects `$t4` to `$t7`** — use the decompals fork of binutils.
  The official binutils 2.45 rejects these aliases.
- **`splat` writes an empty tree** — check `splat.yaml` against your executable.
  This repository supports the Japanese retail release only.
