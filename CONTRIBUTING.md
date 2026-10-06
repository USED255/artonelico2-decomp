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

Read [docs/BUILD.md](docs/BUILD.md). You must supply your own copy of the game
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
| `validate` | Runs in **contribution mode**. It allows an addition or a change in the contribution paths. It rejects a change outside them, a deletion, a non-text file, and a file above 1 MiB. |
| `matching-gate` | Needs the retail executable and the Sony toolchain. A pull request from a fork cannot get them, so the job skips. A maintainer then verifies your commit, or runs the workflow manually with your pull request number. |

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
| `PUBLISHED.json` | The release record. `tools/publish_report.py` writes it after a verified build. |

You can change all other paths. The maintainers ask you to open an issue first
for `config/`, `splat.yaml`, and the build scripts, because a change there can
affect the whole build.

**A note about a new function.** You do not add a `config/matched_symbols.txt`
entry. A maintainer adds it for you.

## 7. Writing style

English documents in this repository use the **ASD-STE100** style. ASD-STE100 is
Simplified Technical English. Follow these rules:

1. Write one idea in one sentence.
2. Keep a procedure sentence below 20 words. Keep a description sentence below
   25 words.
3. Write a maximum of six sentences in one paragraph.
4. Use the active voice. Use the imperative for instructions.
5. Use simple tenses. Do not use contractions. Do not use a semicolon.
6. Do not write "e.g.", "i.e.", or "etc.". Write "for example", "that is", or
   "and more".
7. Use one word for one meaning. Use the same word for the same thing.
8. Do not use idioms, slang, or vague words.
9. Obey the approved dictionary of ASD-STE100 when you can.

The ASD-STE100 dictionary has a copyright. We do not copy it into this
repository. The standard is at <https://www.asd-ste100.org/>.

Documents in other languages follow the same principles: short sentences, the
active voice, one term for one meaning, and no spoken language.

## 8. Licence

This repository is GPL-3.0. When you submit a contribution, you agree to publish
it under the same licence. You keep the copyright of your work.

## 9. Report a policy problem

Read [docs/PUBLICATION-POLICY.md](docs/PUBLICATION-POLICY.md). Open an issue if
this repository contains material that it must not contain. We treat that report
as a blocker. We remove the material first.
