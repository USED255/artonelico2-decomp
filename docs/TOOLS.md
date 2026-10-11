# Tools in this repository

[English](TOOLS.md) | [简体中文](TOOLS.zh-CN.md)

This page lists the tools in `tools/`. It also tells you which tools an external
contributor needs.

## 1. The contributor chain

An external contributor needs one chain only:

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build
make report
make delta BASE=origin/main
make check
```

`configure.py` checks the retail executable and writes the build configuration.
`make` calls `tools/build/decomp_build.py` and the report tool. The chain needs
your own game disc and the original toolchain.

## 2. Tool list

An external clone can run a Contributor tool. A Maintainer tool needs the
private ELF, the Ghidra output, or the evidence directory. An external clone
cannot run a Maintainer tool.

| Path | Purpose | Audience |
| --- | --- | --- |
| `Makefile` | The build entry point that calls the build driver and the report tool. | Contributor needed |
| `configure.py` | Checks the retail executable and writes the build configuration. | Contributor needed |
| `tools/build/decomp_build.py` | The build driver that splits the payload, assembles, links, and verifies the result. | Contributor needed |
| `tools/build/export_symbols.py` | Converts the `.erx.lib` export table into a decompilation symbol list. | Maintainer internal |
| `tools/build/gen_match_meta.py` | Writes `config/match_meta.tsv`, the machine-readable record of each C match. | Maintainer internal |
| `tools/build/gen_objdiff_full.py` | Generates the full objdiff unit list for the progress report. | Contributor needed |
| `tools/build/gen_splat_yaml.py` | Writes a splat configuration with one subsegment for each function. | Maintainer internal |
| `tools/build/gen_symbol_addrs.py` | Merges the Ghidra function boundaries and the `.erx.lib` names into `symbol_addrs.txt`. | Maintainer internal |
| `tools/build/matched_ledger.py` | Parses the match ledger for the report tool and the delta check. | Contributor needed |
| `tools/check/check_public_repo.py` | Checks the publication record, the forbidden material, and the report rules. | Contributor needed |
| `tools/check/test_matched_ledger.py` | Tests the match ledger parser and the delta check. | Contributor needed |
| `tools/check/test_tool_paths.py` | Tests that each tool resolves the project paths. | Contributor needed |
| `tools/ci/splat-requirements.txt` | Lists the public `splat` version for the CI job. | Contributor needed |
| `tools/project/at2_paths.py` | Resolves the project paths for each repository layout. | Contributor needed |
| `tools/project/auto_match_ghidra.py` | Drafts C source from the Ghidra output, then accepts a 100 percent objdiff result. | Maintainer internal |
| `tools/project/auto_match_m2c.py` | Drafts C source with m2c, then accepts a 100 percent objdiff result. | Maintainer internal |
| `tools/project/auto_match_permuter.py` | Converges a near-match function with the decomp-permuter tool. | Maintainer internal |
| `tools/project/auto_match_stub.py` | Writes hand-written assembly for the syscall and break functions. | Maintainer internal |
| `tools/project/auto_match_trivial.py` | Matches trivial functions from their instruction shapes. | Maintainer internal |
| `tools/project/auto_match_wrapper.py` | Matches thin wrapper functions with two stack-frame templates. | Maintainer internal |
| `tools/project/compiler_id_test_jp.sh` | Identifies the compiler that built a Japanese target function. | Maintainer internal |
| `tools/project/compile_sources.py` | Compiles or assembles only the sources that changed. | Contributor needed |
| `tools/project/erx_tables.py` | Parses the `.erx.lib` export table and the `.erx.stub` import table. | Maintainer internal |
| `tools/project/extract_payload.py` | Extracts the payload from the retail executable. | Contributor needed |
| `tools/project/gen_splat_yaml_jp.py` | Writes the Japanese splat configuration with per-function subsegments. | Maintainer internal |
| `tools/project/gen_symbol_addrs_jp.py` | Writes the Japanese `symbol_addrs.txt` from the Ghidra data and the `.erx.lib` names. | Maintainer internal |
| `tools/project/ghidra_draft.py` | Turns the Ghidra pseudo-C into a compilable draft for one function. | Maintainer internal |
| `tools/project/infer_sig.py` | Infers the argument and return types of a function from its call sites. | Maintainer internal |
| `tools/project/jtbl_draft.py` | Profiles and samples the jump-table pool. | Maintainer internal |
| `tools/project/jtbl_patch.py` | Points a generated jump table at the data symbol in the retail binary. | Contributor needed |
| `tools/project/m2c_draft.py` | Generates an m2c C draft from one assembly file. | Maintainer internal |
| `tools/project/p1a_pseudoc_probe.py` | Tests whether the Ghidra pseudo-C can serve as a match draft. | Maintainer internal |
| `tools/project/screen_flags.py` | Compiles many candidate drafts in one translation unit and scores each symbol. | Maintainer internal |
| `tools/project/shape_lq_sq.py` | Synthesizes the `lq` and `sq` vector shapes for the MMI pool. | Maintainer internal |
| `tools/project/split_asm.py` | Extracts one function from an assembly file for a mixed build. | Contributor needed |
| `tools/publish_report.py` | Writes a verified report into `progress/` and updates `PUBLISHED.json`. | Contributor needed |
| `tools/report/disasm_stats.py` | Reports the disassembly statistics of the PS2 EE main program. | Maintainer internal |
| `tools/report/gen_function_report.py` | Generates the per-function objdiff progress report. | Contributor needed |
| `tools/report/match_workqueue.py` | Sorts the main-program functions into a work queue by difficulty. | Maintainer internal |
| `tools/report/r5900_stats.py` | Reports the R5900 instruction statistics from the raw instruction words. | Maintainer internal |

## 3. Changes in this batch

On 2026-10-11, 4 scripts left the public repository. An external clone cannot
run them. They now live in the private companion repository, directory
`tools/legacy/`.

| Script | Reason | New location |
| --- | --- | --- |
| `build_m2.sh` | The script compiles `src/m2_probe.c` at line 17. The public `src/` contains only `matched/`. | `tools/legacy/build_m2.sh` |
| `tools/build/m2_extract.py` | Only `build_m2.sh` calls this script. The public tree has no other caller. | `tools/legacy/m2_extract.py` |
| `tools/report/c_route_measure.py` | The route C study needs the US image `SLUS_217.88` and its ISO. | `tools/legacy/c_route_measure.py` |
| `tools/report/progress_report.py` | The script reads `routeb/` only. The public tree has no `routeb/` directory. | `tools/legacy/progress_report.py` |

The git history at commit `cd1f47a` still contains these files.

Two tools have a new name:

- `build_hybrid.sh` is now `build_mixed.sh`.
- `tools/report/m3_workqueue.py` is now `tools/report/match_workqueue.py`.

The reproducible path in the public repository is `make build`, then
`build_mixed.sh`, then `make report`.
