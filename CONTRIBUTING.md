# Contributing

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

**Contributions are welcome.** This page tells you what we need, how to send it,
and what happens after you send it.

You do not need permission to start. Open an issue first if you want to discuss
a large change.

## 1. What we need

| Kind of contribution | Examples |
| --- | --- |
| **A matched function** | A new file in `src/matched/` that compiles to the same bytes as the retail function. This is the most valuable contribution. |
| **A tool fix** | A correction in `tools/` or in a document. |
| **Documentation** | A correction, or a new translation. The English documents stay primary. |
| **A problem report** | A build problem, or material that must not be in this repository. |

## 2. Before you start

Read [docs/BUILD.md](docs/BUILD.md). When a function compiles but does not match, work through
[docs/compiler/DIAGNOSTICS.md](docs/compiler/DIAGNOSTICS.md) — it routes a residual to the pass that
owns it — and [docs/compiler/FIELD-GUIDE.md](docs/compiler/FIELD-GUIDE.md) for source-level changes that
move the numbers. `python3 tools/compiler/laws-query.py` answers "what does this compiler do at pass X". You must supply your own copy of the game
and the original compiler toolchain. This repository does not contain them.

Check your work on your machine:

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build                       # the payload hash must stay the same
make delta BASE=origin/main      # each changed file in src/matched/ must match 100%
make check                       # repository checks
```

## 3. Send a pull request

1. Fork this repository.
2. Make a branch. Add or change the files.
3. Run the commands in section 2.
4. Open a pull request against `main`.
5. In the description, give your evidence: the tool you used, the command, and
   the result. For a matched function, give the objdiff result (100%).

## 4. What CI does

| Workflow | Your pull request |
| --- | --- |
| `validate` | Runs in **contribution mode**. It allows an addition or a change in the contribution paths. It rejects a change outside them, a non-text file, a symbolic link, a file above 1 MiB, and any changed path that is not a regular file in the working tree (the check fails closed, so a path it cannot inspect is never accepted). A branch of this repository may also rename or delete a file. A pull request from an external fork must still only add or change files. |
| `matching-gate` | Needs the retail executable and the Sony toolchain. A pull request from a fork cannot get them, so the job runs its notice step only; a manual run refuses a fork pull request outright, because the gate would otherwise execute a fork's scripts next to the private material. A maintainer then verifies your commit. An internal pull request picks a mode from your change set: documentation and pure tests run no build at all, and a change that only touches `src/matched/**`, `config/**` (except the two files `splat split` reads), and the progress report assembles the baseline and runs the mixed build, the per-function check, and the report, without the separate baseline link. Any change to a build input or to the tooling that decides how the gate runs takes the whole pipeline. A green run publishes the report and its provenance record; `tools/maintainer/publish_report.py` refuses to publish without a passing provenance. See [docs/BUILD.md](docs/BUILD.md) section 4. |

## 5. What happens after CI

A maintainer reviews your change and merges it. Your name stays in the history.

## 6. Path rules

You can add or change these paths:

- `src/matched/` (`.c` and `.h` files),
- `tools/` (scripts),
- `docs/` and the root `.md` files,
- `LICENSE`, `.gitignore`, `Makefile`, `configure.py`, `toolchain.lock.json`,
  `.github/workflows/`.

These paths are **read-only**. A change there fails the `validate` check:

| Path | Why |
| --- | --- |
| `progress/` | The progress report comes from a verified build. |
| `PUBLISHED.json` | The release record. `tools/maintainer/publish_report.py` writes it after a verified build. |

One exception: **a maintainer** (an `OWNER`, `MEMBER`, or `COLLABORATOR` of a same-repository pull
request) may open a **publication pull request** that changes only `progress/**` and
`PUBLISHED.json`. `validate` then verifies the publication instead of refusing it: the record must
match the files it names, `payload_verified` must be true, the baseline must carry a passing
provenance record bound to the published report, and the numbers must not regress. A pull request
that mixes publication files with anything else is refused.

You can change all other paths. The maintainers ask you to open an issue first
for `config/`, `splat.yaml`, and the build scripts, because a change there can
affect the whole build.

**A note about a new function.** You do not add a `config/matched_symbols.txt`
entry. A maintainer adds it for you. `config/matched_symbols.txt` and
`config/symbol_addrs.txt` are read-only configuration. A maintainer fills them
for you. Read [config/README.md](config/README.md).

## 7. Writing style

Documents in this repository use the **ASD-STE100** style.

The ASD-STE100 dictionary has a copyright. We do not copy it into this
repository. The standard is at <https://www.asd-ste100.org/>.

## 8. Licence

This repository is GPL-3.0. When you submit a contribution, you agree to publish
it under the same licence. You keep the copyright of your work.

## 9. Report a policy problem

Read [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md). Open an issue if
this repository contains material that it must not contain. We treat that report
as a blocker. We remove the material first.
