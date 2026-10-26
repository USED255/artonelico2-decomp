# Toolchain identity

[English](TOOLCHAIN.md) | [简体中文](TOOLCHAIN.zh-CN.md)

A matching build has one hard requirement: the bytes must be identical. That starts with the
compiler. This page records which compiler built what, and how to verify the copy you supply.

This repository does not contain the Sony toolchain, and it does not link to a download of it.
The toolchain is proprietary; you supply your own copy, from your own licensed SDK or from a copy
you are entitled to use.

## 1. Two compilers built this game

| Code | Compiler | Evidence |
| --- | --- | --- |
| Game code (the main `.text`) | `ee-gcc 3.2-ee-040921` | The SDK 3.0.3 generation compiler; named in [toolchain.lock.json](../../toolchain.lock.json) and in the [compiler handbook](compiler/VERIFY.md). |
| CRI middleware (ADX audio, Sofdec video) | `ee-gcc 2.96-ee-001003-1` | The `Append: GCC2096 SCE3100` banner strings sit next to the CRI module banners, in nine places. |
| IOP modules | IOP compiler 2.8.1 generation | The IRX modules are separate binaries; the main build consumes them as data. |

The game code and the CRI modules are compiled by **different compilers**. A function that only
matches with one of them is normal; see [CROSS-2.96.md](compiler/CROSS-2.96.md) for what transfers
between the two.

## 2. Why the exact compiler is required

`ee-gcc` is Sony's branch of Cygnus GNUPro, not a stock FSF release. It adds the EE ABI,
`-mno-abicalls`, `.mdebug.eabi64`, ERX support and its own instruction selection. Two builds that
both say "GCC 3.2" are not interchangeable:

- A current `ps2dev` toolchain (binutils plus GCC 15) targets the same CPU but generates different
  code. It is fine for tooling experiments, and useless for a byte match.
- A stock GCC 3.2 for MIPS produces a different ABI and different relocations.
- Even within the Sony line, the versions are not identical: the pass numbering differs between
  3.2 and 2.96, which is why the handbook has a separate cross-version page.

Matching therefore means: the retail source shape, with the retail compiler, at the retail flags.

## 3. The build flags

The game build compiles C with:

```
-O2 -falign-functions=4 -ffunction-sections
```

Two details that cost time when they are wrong:

- The winning optimisation tier is **not always the recorded one**. Sweep `-O1`, `-O2`, `-O3` and
  `-Os` for a function before you conclude that the source shape is wrong. [KNOWN-BLOCKERS.md](KNOWN-BLOCKERS.md)
  lists this as a trap.
- Sources compiled by the CRI compiler need `-G0`: the small-data (gp-relative) threshold differs
  from the main build. See [config/README.md](../../config/README.md).

The assembler is the decompals fork of GNU binutils 2.40. The official binutils 2.45 rejects the
`$t4` to `$t7` register aliases.

## 4. Verify the copy you have

1. **Version string.** `ee-gcc --version` must print `ee-gcc (GCC) 3.2-ee-040921` for the game
   compiler and `2.96-ee-001003-1` for the CRI compiler.
2. **Pinned hashes.** [toolchain.lock.json](../../toolchain.lock.json) records the sha256 of every
   toolchain archive the CI uses, and the CI checks each value before it builds.
3. **Compiler binary.** [compiler/VERIFY.md](compiler/VERIFY.md) records the sha256 of both `cc1`
   binaries. That is the strongest check: the version string is easy to get wrong, the binary hash
   is not.
4. **Behaviour.** The handbook's checks re-run behavioural probes against your compiler. Run
   `make check`: the parts that need the toolchain run when it is present and skip cleanly when it
   is not.

## 5. What the toolchain cannot do here

Some sections of the retail executable were produced by Sony tools that are not part of the
C compiler: the `.DVP.*` sections (VU1 microcode) and the `.erx.*` sections (the ERX module
mechanism). GNU `ld` does not generate them.

This project does not try to rebuild the container: it keeps the retail ELF container and verifies
the **payload** (the concatenation of the loadable segments) byte for byte. That is the acceptance
rule described in [BUILD.md](../BUILD.md) and [TRANSCRIPTION.md](../TRANSCRIPTION.md).

## 6. Related pages

- [compiler/README.md](compiler/README.md) — the code generation handbook itself.
- [compiler/VERIFY.md](compiler/VERIFY.md) — the pinned toolchain and what each check verifies.
- [compiler/CROSS-2.96.md](compiler/CROSS-2.96.md) — the 2.96 compiler that built the CRI code.
- [../../docs/BUILD.md](../BUILD.md) — the items you supply, and the build commands.
