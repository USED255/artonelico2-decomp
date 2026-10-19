# Assembly transcription metric (separate from the main progress)

Some functions in `SLPS_258.19` contain instructions that **no C expression can produce**:
COP2/MMI vector ops (`lq`, `sq`, `vmulax`, `vadd`, `pcpyld`, `pmfhl`, …), COP2 register moves
(`cfc2`, `ctc2`, `qmtc2`), and the raw `break`-based trap stubs.

For a subset of them the only way to reach a byte-identical object is to **transcribe the target
instructions verbatim** into a global `__asm__` block. The resulting object is byte-identical
(objdiff 100 %, equal length, `.text`-only), but there is **no reconstructed C code** — this is
not a semantic decompilation.

## Two metrics, never mixed

| metric | counted | source of truth |
| --- | --- | --- |
| **Main progress (C reconstructed)** | functions whose matched source is C | `config/matched_symbols.txt` minus `config/transcription_symbols.txt` |
| **Assembly transcription** | functions matched by verbatim transcription | `config/transcription_symbols.txt` |

The transcription symbols keep their object in the build (they are part of the byte-identical
image), but they are **excluded from the main progress** in:

- `tools/report/gen_function_report.py` — units listed in `config/transcription_symbols.txt` get the
  `transcription` progress category and `base_path = null`, so the published report does not count
  them as matched;
- `tools/report/progress_report.py` — the headline excludes the transcription category and prints
  it as a separate subtotal;
- `tools/maintainer/publish_report.py` — `PUBLISHED.json` records
  `measures_c_only` (main) and `transcription` (separate) side by side.

## How the transcription sources are written

They are ordinary `src/matched/<symbol>.c` files holding a single global `__asm__` block — no C
function body. The rules that make the object exact:

1. **No C function body** — otherwise GCC appends its own epilogue (`jr ra; nop`).
2. **Every instruction as `.word 0x…`** taken from the **raw section bytes**
   (`objdump -s -j .text`), because `objdump -d` silently skips some instructions.
3. **`.word` stays in the default (reorder) assembler mode**: under `.set noreorder`, `ee-as` adds
   20 bytes of padding at the section start.
4. **Only relocation-carrying instructions become mnemonics** (`%hi`, `%lo(sym)(base)`, `j`/`jal`),
   each wrapped in `.set noreorder` / `.set reorder` so the assembler neither pads nor inserts a
   delay-slot `nop`.
5. Register names are emitted numerically (`$4`, `$15`, …) to avoid `$30`-vs-`s8` naming surprises.

`tools/research/mmi_transcribe*.py` in the research repository implements this; the current
transcriber is `mmi_transcribe6.py`.

## Adding a symbol

1. Verify locally: objdiff 100, equal length, `obj_gate.bad_sections(obj) == []`.
2. Add the source to `src/matched/<symbol>.c`, the ledger line with the `# transcription_asm` tag,
   and its flags to `config/source_flags.tsv`.
3. Append the symbol to `config/transcription_symbols.txt` — **this file gates the metric split**.
