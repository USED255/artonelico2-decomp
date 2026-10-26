# Disc formats

[English](FORMATS.md) | [简体中文](FORMATS.zh-CN.md)

What this page records: the container and module formats on the retail disc of
**Ar tonelico II: Melody of Metafalica**, as measured on the Japanese release
(`SLPS_258.19`) and, for comparison, the US release (`SLUS_217.88`). It describes structures,
not content: it contains no game asset, no game text and no disc image.

The measurements were made by reading a locally owned disc image. The game, its assets and its
text are copyrighted. Read [PUBLICATION-POLICY.md](../PUBLICATION-POLICY.md) before you build
anything on top of this page.

## 1. What is on the disc

| Item | What it is |
| --- | --- |
| `SLPS_258.19` | The main executable. Game code, the SDK library layer, and the asset table. |
| `RPK.BIN` | The large asset container (about 366 MB on the Japanese disc). |
| `ERXS/*.ERX` | 11 loadable code modules: dynamic libraries, not asset archives. |
| `SOUND/**/*.AFS`, `VPACK*/*.AFS` | AFS containers. Every child is CRI ADX audio. |
| `MOVIE/**/*.SFD` | CRI Sofdec video: bare MPEG-1 Program Streams. |
| `.evd` entries (inside the container) | Event scripts, and the largest source of game text. |
| `.irx` modules | IOP modules loaded at run time (13 in this game). |

Two facts save a lot of time. First, the asset layer has no encryption: every format below is
plain. Second, the container formats are Gust variants, not the standard CRI tools' formats, so a
standard tool often misreads them.

## 2. AFS containers (Gust variant)

The AFS containers in this game are a compact variant of the CRI AFS format: there is no
`table_offset` field and no footer. The layout is:

```
0x0000  "AFS\0"
0x0004  u32 LE    entry count N
0x0008  N × { u32 LE absolute offset; u32 LE size }
        ...zero padding...
align2048(8 + 8N)                 first child, each child 2048-aligned
align2048(last child end)         name table: 48 bytes per entry = char name[44] + u32
```

The container size is `align2048(last child end) + align2048(48N + 4)`. This held on all 34
containers measured. The name table gives the original path of every child, for example
`sound/voice/<id>/<id>.adx`.

The children are CRI ADX: a big-endian `80 00` header and a `(c)CRI` string. The two voice
containers are a language pair: `VPACK` holds the localized (English) voice in `sound/voice/`,
and `VPACKJ` holds the Japanese voice in `sound/voicej/`. The Japanese entries are 24 kHz; the
localized container mixes 48 kHz and 24 kHz, and the entries that are byte-identical to the
Japanese container are exactly the 24 kHz ones.

## 3. `RPK.BIN`: two different structures

The two generations are not the same format.

| | Ar tonelico 1 | Ar tonelico 2 |
| --- | --- | --- |
| Index | `RPK.ID`, a plain-text index (UTF-8 BOM, JSON-like lines): 2,703 entries of `{ path, id, size }` | No index file |
| Layout | The 2,703 files concatenated in index order, each 2048-aligned; the total matches the file size exactly | 16 AFS containers back to back, then a 373,116,928-byte stream of 2048-aligned `LZR\0` blocks (12,100 blocks) |
| File names | In `RPK.ID` | In the main executable's string table (`erxs/*.erx`, `res/Tmap/TX00/*.tm2.lzr`, `fpack/*.fp`, `rpk.bin`, `%s.lzr`, …) |

The 16 AFS containers inside the Ar tonelico 2 container are byte-identical to the separate
`/VPACKJ/*.AFS` files on the same disc, only in a different order.

## 4. LZR compression

An `LZR` block is a 16-byte header followed by a compressed body, aligned to 2048 bytes:

```
"LZR\0" | flag_bits | data_leng | orig_leng      (four little-endian u32 values)
body length = 16 + (flag_bits + 7) / 8 + data_leng
```

Each byte of the body carries four 2-bit opcodes. The opcodes are: copy a literal byte, copy a
run, repeat the previous byte, and a 12+4-bit dictionary back-reference. A community reference
implementation (`lzr-src`, Unlicense) decodes all 12,079 blocks of the Japanese disc.

## 5. `.evd` event scripts

An `.evd` file is an event-script container. The measured structure is
`EventDialogues + EventSequence × 2 + Selections`, with

```
EvdDialogue = i32 style, narrator, portrait, id
            + i16 portraitDiff, data
            + evdstr
evdstr      = i32 size + string area of (size & ~3) + 4 bytes
```

The text is Shift-JIS, uncompressed. All 1,232 index entries of the Japanese disc parse to EOF.
The container is the largest source of game text, which is why translation projects work on it.

## 6. ERX modules

An `.ERX` is not an encrypted script and not an asset archive. It is a 32-bit MIPS ELF shared
object: `\x7fELF`, `e_machine = 8` (MIPS), `e_type = 0xFF91` (a Gust value), with the sections
`.eemod`, `.text`, `.rel.text`, `.erx.lib`, `.erx.stub`, `.rodata`, `.data`, `.sdata`, `.sbss`.

That is why the format resisted the community's unpackers for years: it is a code problem, not a
container problem. The entropy is 2.81–5.20, far below what encryption would produce, and the
modules contain plain ASCII and Shift-JIS strings.

The main executable also carries `.erx.lib` (a registry of exported symbols, one entry per
library slot) and `.erx.stub`. That registry is what gives this project its named symbols.

## 7. Video and audio

- **SFD** is a bare MPEG-1 Program Stream: it starts with a pack header (`00 00 01 BA`) and has
  no CRI container header. It carries MPEG-1 video and ADX audio. FFmpeg reads it directly.
- **ADX** is CRI ADPCM audio. FFmpeg's `adx` demuxer and `adpcm_adx` decoder handle it.

## 8. Tools

| Tool | Licence | What it does |
| --- | --- | --- |
| [FFmpeg](https://ffmpeg.org) | LGPL / GPL | Demuxes and decodes ADX and SFD. |
| `exar2` (asmodean) | Proprietary, free: the author forbids redistribution, modification and embedding | Extracts and repacks `RPK.BIN`, `.evd` and `.fp`; `unlzr` decompresses LZR. |
| `FP_tools` (TerraBreaker) | Free, with C++ source | Unpacks and repacks the `.fp` assets. |
| `rpkextract.rb`, `evdextract.rb` | Free scripts | Extraction only. |
| `FakeLZR` | Free | Writes a valid LZR header without compressing. |
| [gust_tools](https://github.com/VitaSmith/gust_tools) | GPLv3-or-later | Later Gust formats (PC releases); **not** applicable to the PS2 games. |
| [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools) | See the repository | General JRPG tools. |

A working rule from the measurements: assets can be repacked without compression by writing a
valid LZR header, which is what the community patchers do.

## 9. Open questions

These were not resolved by the measurements above:

- The `id` field of the Ar tonelico 1 index is monotonic but has about 96,000 gaps; what fills the
  gaps is unknown.
- Why the Ar tonelico 2 container embeds a copy of the Japanese voice containers is unknown.
- The internals of the Ar tonelico 1 `.evd`, `.fp` and `.ipu` entries were not parsed.
- Whether the Ar tonelico 1 disc has an ERX equivalent was not found.
- Whether the main executable decompresses or decrypts itself at load time was not verified.

## 10. Compliance

- Do not distribute the disc image, the BIOS, or any extracted asset. This page gives structures
  only.
- Formats are facts; a parser you write from this page is your own implementation. Do not copy
  code from a tool whose licence does not allow it.
- Community translation and undub projects distribute patches, not assets, and require the user's
  own copy of the game. That is the safe pattern.
