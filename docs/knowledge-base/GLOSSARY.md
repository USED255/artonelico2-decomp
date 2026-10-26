# Glossary

[English](GLOSSARY.md) | [简体中文](GLOSSARY.zh-CN.md)

Terms used by this project's documents and by the matching-decompilation community. A term may
appear before the page that explains it; the linked page is authoritative.

## 1. Platform and hardware

| Term | Meaning |
| --- | --- |
| **EE** | Emotion Engine, the PS2 main CPU: a MIPS III / R5900 derivative with 128-bit MMI instructions and two vector units. |
| **IOP** | The PS2 I/O processor, an R3000A core. Games load IRX modules into it. |
| **VU0 / VU1** | The two vector units. VU0 is used either as inline COP2 macro instructions or as a microprogram; VU1 mainly runs graphics microcode. |
| **GS** | Graphics Synthesizer, the PS2 graphics hardware. |
| **SPU2** | The PS2 sound processing unit. |
| **SIF / DMA** | The channel between the EE and the IOP. |
| **R5900** | The EE CPU core. A disassembler needs R5900 support (for example Ghidra's `r5900:LE:32:default`) to decode it correctly. |
| **R3000A** | The IOP CPU core. |
| **MMI** | Multimedia Instructions: the EE's 128-bit instruction group. |
| **COP2** | The coprocessor-2 instruction space. On the EE it carries the vector unit moves (`lqc2`, `qmfc2`, …). |
| **HLE** | High-level emulation: reimplementing a called library on the host instead of emulating the hardware. A different route from matching decompilation; this repository does not use it. |

## 2. Disc formats and modules

All of these are described in [FORMATS.md](FORMATS.md).

| Term | Meaning |
| --- | --- |
| **ERX** | A Gust dynamic module format: a 32-bit MIPS ELF (`e_type = 0xFF91`). This game has 11. |
| **`.erx.lib`** | The export-symbol registry section in the main executable. It is what gives this project its named symbols. |
| **RPK / AFS** | The large asset container (`RPK.BIN`) and its inner archive format. The game's AFS is a compact Gust variant, not the standard CRI one. |
| **LZR** | The compression block format used inside `RPK.BIN`. |
| **`.evd`** | The event-script container, and the largest source of game text. |
| **IRX / `.irx.lzr`** | IOP modules, loaded at run time. |
| **CRI / CRI-MW** | The third-party middleware (ADX audio, Sofdec video). Compiled with `ee-gcc 2.96`, not 3.2. |
| **ADX / SFD** | CRI audio / CRI video (`SFD` is a bare MPEG-1 Program Stream). |
| **DVP** | The VU1 microcode overlay sections (`.DVP.*`) in the main executable. |

## 3. Matching decompilation

| Term | Meaning |
| --- | --- |
| **matching decompilation** | Reconstructing C source that compiles, with the original compiler, to the **same bytes** as the retail function. It is the only reverse-engineering form that can be checked automatically. |
| **matched function** | A function whose rebuilt object is byte-identical to the retail one. The main progress metric counts matched functions whose source is C. |
| **transcription** | Copying the target instructions verbatim into an assembly block instead of reconstructing C. The object matches byte for byte, but no C was recovered. Counted as a separate metric; see [TRANSCRIPTION.md](../TRANSCRIPTION.md). |
| **fakematch** | A byte match that the original developer's source could not have produced. The community treats it as invalid. |
| **splat** | A binary splitter (from N64 projects, with PS2 support) that produces per-function assembly and a linker script. |
| **spimdisasm** | The MIPS disassembler behind splat. |
| **m2c** | A decompiler that drafts C from assembly. It does not lift this game's MMI/COP2 code well. |
| **permuter** | `decomp-permuter`: an automatic search over small instruction reorderings, compiling and comparing each candidate. Used to close near misses. |
| **objdiff** | A per-function byte comparison tool. Its report is the project's progress source. |
| **decomp.me / decomp.dev** | The community collaboration site / the progress tracker that reads objdiff reports. |
| **TU** | Translation unit: one compiler input. Which functions share a TU is a key constraint in matching. |
| **GP / FP** | The general-purpose register set / the floating-point register set. Allocation competition between them drives most differences in large functions. |
| **baseline** | The build that reassembles the whole split tree and links it, to prove the split is faithful. |
| **mixed build** | Replacing matched functions with our C, leaving the rest as assembly, then linking and verifying the payload. |
| **payload** | The concatenation of the executable's loadable segments, compared byte for byte with the retail payload. |
| **per-symbol section** | The build layout where each matched function is placed in its own `.text` section `func_XXXXXX` (and the same for data), so a single function can be replaced. |

## 4. Project conventions

| Term | Meaning |
| --- | --- |
| **main metric** | The headline percentage: matched functions whose matched source is reconstructed C. |
| **transcription metric** | A separate subtotal for functions matched by verbatim assembly transcription. Never added to the main metric. |
| **matching-gate** | The CI workflow that rebuilds the payload and verifies a change against the retail binary. |
| **progress report** | `progress/SLPS_258.19_report.json`, written by a verified build; decomp.dev reads it. |
| **baseline report** | `progress/baseline.json`, the last published report. CI refuses to publish a worse one. |

## 5. Abbreviations

| Abbreviation | Full form |
| --- | --- |
| EE | Emotion Engine |
| IOP | I/O Processor |
| VU0 / VU1 | Vector Unit 0 / 1 |
| GS | Graphics Synthesizer |
| SPU2 | Sound Processing Unit 2 |
| SIF | Sub-system Interface |
| DMA | Direct Memory Access |
| R5900 / R3000A | The EE / IOP CPU core models |
| MMI | Multimedia Instructions |
| COP2 | Coprocessor 2 |
| HLE | High-Level Emulation |
| ERX | Gust dynamic module format |
| RPK | Gust asset container format |
| AFS | Inner archive format |
| LZR | Compression block format |
| EVD | Event-script container |
| IRX | IOP module format |
| CRI | CRI Middleware |
| ADX / SFD | CRI audio / video format |
| TU | Translation Unit |
| GP / FP | General-purpose / floating-point register set |
| CI | Continuous Integration |

## 6. See also

- [KNOWN-BLOCKERS.md](KNOWN-BLOCKERS.md) — the traps that produce false results.
- [compiler/README.md](compiler/README.md) — the code generation handbook.
- [FORMATS.md](FORMATS.md) — the formats named above, in detail.
