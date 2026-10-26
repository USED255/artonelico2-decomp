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
make build-fast     # assemble the baseline without its link, then the mixed build
make report         # write the progress report
```

`make build-fast` is the lane the `matching-gate` workflow uses for a pull request that only
touches `src/matched/**` (plus documentation and the progress report). It still checks the mixed
payload against the retail payload, so the image is verified byte for byte; it skips the separate
assertion that the pure-assembly baseline also rebuilds the retail image, and that one keeps
running on every push to the default branch. Use `make build` when you are changing a build input
(`splat.yaml`, `config/**`, `build*.sh`, the linker script) or when you want that assertion too.

This is a mixed-compiler build: the game code uses `ee-gcc 3.2-ee-040921` and the
CRI middleware uses `ee-gcc 2.96-ee-001003-1`. `config/compiler_map.tsv` states
the compiler for each source file. If a file is absent from the map, the build
uses the game compiler. The two paths come from `EE_GCC` / `EE_GCC_CRI` or
`GCC` / `GCC_CRI`. A source that needs the CRI compiler also needs `-G0` in
`config/source_flags.tsv`. Read [config/README.md](../config/README.md) for the
configuration files.

`make build` derives the payload from the retail executable. Then it splits the
payload, assembles the source, and links the result. It checks the payload sha1
value after each stage. The expected value is
`7cc42d275750600d1f232b2632447f77205f3fc0`. One different byte stops the build.

## 3. Check a change

```bash
make progress                    # the static upper bound. No toolchain is necessary.
make delta BASE=origin/main      # each changed file in src/matched/ must match 100% (a new file needs a ledger line)
make check                       # repository checks. The retail executable is not necessary.
```

`make progress` reads `config/matched_symbols.txt` and `config/symbol_addrs.txt`.
It prints the static upper bound by symbol-table bytes. The published numbers are
in [progress/SLPS_258.19_report.json](../progress/SLPS_258.19_report.json).

`make report` writes its output to `build/`: `build/SLPS_258.19_report.json` plus
`build/report_provenance.json`, the record of what the run measured (the payload sha1 the build
asserted, the commit, the dirty flag, and how many C units are below 100 percent). It never
writes into `progress/`: that tree is written only by `tools/maintainer/publish_report.py`, after
that tool verified the provenance. The target also fails when any C unit is below 100 percent
(`--require-c100`); pass `REPORT_FLAGS=` to get an exploratory report instead.

## 4. CI

| Workflow | When it runs | What it does |
| --- | --- | --- |
| `validate` | Each push to `main`, each pull request, and a manual start | On a push it checks the publication record (`PUBLISHED.json`), the forbidden material (including a size backstop for a restricted file whose name carries no telling extension), the report schema, and the baseline. On a pull request it allows any change **except** the publication content (`progress/**` and `PUBLISHED.json`); an added or changed path must be a regular UTF-8 text file below 1 MiB, so a symbolic link or a path that the working tree does not hold is refused. A branch of this repository may also rename or delete a file. A pull request from an external fork must still only add or change files. Read [CONTRIBUTING.md](../CONTRIBUTING.md). |
| `matching-gate` | A push to the default branch, an internal pull request, or a manual start | Gets the retail executable and the toolchain from a private companion repository. Then it runs `make build`, `make delta`, and `make report`. It publishes two artifacts **only** when all checks pass: `SLPS_258.19_report` (the report) and `SLPS_258.19_report_provenance` (the record that proves what was measured). A manual run with a pull request number verifies that the pull request comes from this repository before any checkout, so a fork's scripts never run next to the private material. A fork pull request that needs a build fails this required check on purpose; a documentation-only fork pull request passes without a build. |

`matching-gate` runs in one of three modes. [tools/ci/classify_change.py](../tools/ci/classify_change.py)
picks the mode from the change set, and it denies by default: an error, a push, and a manual
run are always `full`.

| Mode | When | What runs |
| --- | --- | --- |
| `skip` | A pull request whose changes are all documentation or pure tests (`tools/check/test_*.py`) | No build at all; the private material is not even downloaded. `validate` still checks the repository, and it runs the tests, so a changed test still runs. |
| `fast` | A pull request whose changes are all documentation, pure tests, `src/matched/**`, `progress/**`, or `config/**` **except** `config/symbol_addrs.txt` and `config/reloc_addrs.txt` | `make build-fast`: the baseline is assembled but not linked, then the mixed build, the delta check, and the report run. The mixed payload is compared against the retail payload, so the image is still verified byte for byte. |
| `full` | Every push, every manual run, and any change that touches a build input (`splat.yaml`, the two `config/` files above, `build*.sh`, `Makefile`, `configure.py`, the build tools, `toolchain.lock.json`, the workflows) | The command above, including the baseline link and its payload check. This is the mode that publishes the artifact. |

Two rules explain the boundaries:

- **`config/**` is `fast` because `build.sh` never reads `config/`.** The baseline link therefore
  cannot depend on it, and everything the mixed build reads from `config/` (the ledger, the
  compile flags, the compiler map, the jump-table table) is covered by the mixed payload check,
  which compares the final image against the retail payload byte for byte. The two exceptions are
  the files `splat split` reads: they change the assembly tree, and only the baseline link verifies
  that tree.
- **A change to the verification code itself stays `full`.** `tools/check/check_public_repo.py`,
  the build tools, the workflows, and `Makefile` are what decides *how* the gate runs, so they get
  the whole pipeline. Only the pure tests, which `make check` runs, are `skip`.

The `matching-gate` workflow needs the secret `ORIG_DEPLOY_KEY` and the variable
`PRIVATE_ORIG_REPO`. A pull request from a fork cannot get them. The workflow still
checks out the code and classifies the change. A change that needs a build (`fast` or
`full`) then **fails**: a green `matching` check must mean "verified". A change that is
documentation or a pure test (`skip`) passes without a build. For a no-secret pull
request, the mode comes from the classifier at the base commit, not from the pull
request's own copy. A maintainer reproduces the contribution on a branch of this
repository (only the contribution paths, never the fork's workflows or tools) and
verifies it there.

The gate also restores the packaged `splat split` output when the maintainer has packed it
with [tools/ci/splat_snapshot.py](../tools/ci/splat_snapshot.py). The archive lives in the
private companion repository; this repository only carries `toolchain/splat-snapshot.json`,
which holds hashes and counts, never content. Any mismatch (a stale input, a different retail
executable, a corrupt archive, a member whose content does not match) prints a warning and falls
back to running splat, and the extraction is verified in a staging directory before anything is
copied into the checkout. The gate never depends on the archive: the mixed payload is still
compared against the retail payload.

A maintainer starts the packing job (`.github/workflows/splat-snapshot.yml`). The job runs behind
the protected `splat-snapshot` environment (a required reviewer approves the run) because it uses
a write-scoped deploy key. With that key it pushes the archive straight into the private companion
repository, so the archive never enters this repository's Actions storage. Without the key it falls
back to a handoff artifact with `retention-days: 1`. Either way the maintainer commits
`toolchain/splat-snapshot.json` in this repository.

A failed check produces no new progress report. Therefore the public numbers are
always verified numbers.

Do you want to contribute a matched function? Read [CONTRIBUTING.md](../CONTRIBUTING.md).

## 5. Publish the report

After a green `matching-gate` run on the default branch, download both artifacts. Then write
the report into this repository:

```bash
gh run download <run-id> -R <owner>/<repo> -n SLPS_258.19_report -D .tmp/report
gh run download <run-id> -R <owner>/<repo> -n SLPS_258.19_report_provenance -D .tmp/provenance
python3 tools/maintainer/publish_report.py \
  --report .tmp/report/SLPS_258.19_report.json \
  --provenance .tmp/provenance/report_provenance.json
```

The tool refuses to publish unless the provenance record says the payload sha1 was measured and
matches, every C unit reached 100 percent, the tree was clean, and the run was not a `--limit`
smoke test. It then writes `progress/SLPS_258.19_report.json` and updates `PUBLISHED.json`, and it
checks the numbers (including the denominators) against the baseline. Use `--force --reason "..."`
to override the gate; the reason is recorded in `PUBLISHED.json`.

**Pass `--freeze-baseline` whenever the report content changes.** `progress/baseline.json` is the
frozen reference, and the publication gate refuses a pull request whose baseline does not describe
the report being published (`the baseline provenance does not describe the published report`). The
flag writes the *provenance record* there — what was verified, not a copy of the report — so
"no regression" keeps meaning something. It is not optional, and omitting it is the usual reason a
publication pull request goes red on its first push.

The record's `source_revision` is the commit the *verified run* built (the provenance's
`source_commit`, not the commit that publishes), and the gate checks that too. Use `--refresh`
after a change to `toolchain.lock.json`; it only recomputes hashes and keeps the recorded revision.

`main` is protected by a repository ruleset, so a maintainer lands the result through a pull
request too:

```bash
git switch -c publish/<run-id>
git commit -am "publish: <the verified run>"
git push -u origin publish/<run-id>
gh pr create --base main --fill
```

`validate` recognises a maintainer publication pull request: it must change only `progress/**` and
`PUBLISHED.json`, and it must pass the publication checks (record hashes, `payload_verified`, a
provenance-carrying baseline bound to the report, no regression).

## 6. Troubleshooting

- **`payload sha1 mismatch`** — one replaced source does not agree with the
  retail bytes. Run `make delta BASE=<last good commit>` to find the file.
- **The assembler rejects `$t4` to `$t7`** — use the decompals fork of binutils.
  The official binutils 2.45 rejects these aliases.
- **`splat` writes an empty tree** — check `splat.yaml` against your executable.
  This repository supports the Japanese retail release only.
