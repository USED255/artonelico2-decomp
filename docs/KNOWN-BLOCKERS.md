# Known blockers and stop conditions

This page records what **cannot** be closed with the current toolchain, so that contributors do not
spend hours re-discovering it. Everything below was measured on the Japanese build
(`SLPS_258.19`, payload `sha1:7cc42d275750600d…`) with `ee-gcc 3.2-ee-040921`.

> Scope: the *main* metric counts **reconstructed C only**. Byte-identical assembly transcriptions are
> a separate metric — see [TRANSCRIPTION.md](TRANSCRIPTION.md).

## 1. Tooling traps (these produce false results)

| Trap | What happens | Do instead |
| --- | --- | --- |
| `objcopy --only-section=.text` on ee-gcc objects | Fails on the old ELF and **silently returns empty bytes for both sides** — a naive byte compare then reports "identical". | `objdump -s -j .text` and compare the hex. |
| `objdump -d` for exact byte comparison | **Silently skips instructions** it cannot decode (18 observed in one vector-heavy function). | Compare raw section bytes, not the disassembly. |
| `ee-as` with `.set noreorder` + `.word` | Emits **20 extra bytes** of padding. | Use the default reorder mode (but note it inserts `nop`s in branch delay slots). |
| Trusting a recorded `-O*` flag | The winning tier is often not the recorded one (`-O3` and `-O2 -fno-optimize-sibling-calls` both appeared; a record saying `-O1` sometimes needs `-O3`). | Always sweep `-O1 / -O2 / -O3 / -Os` and keep the one that reaches 100. |
| Comparing objdiff percentages only | Byte-identical `.text` with **different relocation target symbol names** still scores < 100. | Check the relocation symbol, not just the bytes. |

## 2. Unreachable code-generation forms

Some retail instruction sequences cannot be produced from ordinary C with this compiler, because GCC
folds the source away first. Two confirmed examples:

- **`lh` + `sltiu`**: the retail code loads a `short` (signed) and compares it **unsigned**, e.g.
  `lh t7,0x20(a0)` followed by `sltiu t7,t7,0x2`. Writing `(unsigned)short_var < 2` in source makes
  GCC 3.2 fold back to `slti`, so the pair is unreachable. Five source variants were tried; all stop
  at the same diff.
- **`beqzl` (branch-likely)**: GCC only emits branch-likely forms when it has branch prediction
  information. `__builtin_expect` alone does **not** trigger it without `-fbranch-probabilities`.

**Stop condition**: if a single remaining diff is one of these forms, accept it and move on.

## 3. Register-allocation residuals

Functions in the 95–100 % band frequently miss only on **register assignment** (`arg_diff` /
`DIFF_ARG_MISMATCH` on operands) or on prologue instruction ordering (`DIFF_INSERT`).

- Rewriting the source to reshuffle evaluation order (local temporaries, reordered `+` chains) did
  **not** change the score in any measured case.
- The local permuter was also fed an improved 93.75 % source as a seed and returned 0 hits.

**Stop condition**: three source variants without a score change ⇒ the residual is allocator
behaviour; stop.

## 4. Channels that are exhausted

| Channel | Scale tried | Result |
| --- | ---: | --- |
| Local permuter on the ≥ 80 % near-miss bands | 361 samples | 9 hits (**2.5 %**), and 0 hits in the last three consecutive batches |
| LLM-generated drafts (Cohere / Codestral) | 24 samples | 0 conversions (Cohere 2/12 compile, Codestral 10/12 compile, none match) |
| `objcopy`-based byte comparison | — | see §1: not usable at all |

## 5. What *does* still work

- **Type / structure recovery** on near misses: declare a struct whose size equals the retail **stride**
  and put the member at the retail **field offset**, then index it — 3/3 success. Fixing the *element
  type* of a table (e.g. `unsigned int` → `char[]`) corrects a 4× stride error.
- **Signedness sweep**: a `DIFF_REPLACE` on the *first* branch where the retail direction is opposite
  means the drafted global is declared `unsigned` but the retail code treats it as signed. Fixing the
  declaration improved every case tried (2/2).
- **`diff_kind` localisation**: objdiff's JSON carries `instructions[].diff_kind`, which is a reliable
  way to enumerate the exact remaining differences without writing a byte parser.

## 6. Reporting a blocker

If you hit something new, please open an issue with:

1. the symbol, its retail size, and the current objdiff score;
2. the exact `diff_kind` list (or the disassembly pair);
3. the source variants you tried and their scores.

That is enough for someone else to reproduce — and possibly to find the form that works.

## 7. Verifying a report before publishing

The published numbers must come from a **green `matching-gate` run on the merge commit**. Two checks
gate that, and a mismatch means *do not publish*:

1. `report_provenance.json` → `source_commit` equals the merge commit you are publishing;
2. `payload_check.ok == true` (and `baseline_sha1 == mixed_sha1 == 7cc42d27…`).

Two traps that produce a *plausible-looking but wrong* artifact:

- Running `gh run download` with an **empty run id** silently falls back to "the latest run" — and a
  pull-request run carries the **synthetic merge ref** (`refs/pull/N/merge`), whose SHA is not a commit
  on `main`. Resolve the run id from the merge commit's **push** event and abort when it is empty.
- A report job that cannot see the baseline binary reports `payload_check.ok = false` with
  `baseline_sha1: null` — that artifact is not publishable even if every other number looks right.

