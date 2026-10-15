# Source study — what source we have, what we do not, and how to anchor anyway

[简体中文](SOURCE-STUDY.zh-CN.md) · [Handbook index](README.md) · [Laws](LAWS.md) · [Pass map](PASSES.md)

Every law in this handbook names where its rule came from. This page records what that source actually is,
so a reader can tell a verified rule from a measured one.

## 1. What is available

| Source | Status | Use |
| --- | --- | --- |
| **mainline gcc-3.2.3** | available (`sha256 9229434c…`) | the **semantic** reference for generic passes: allocation, liveness, scheduling, constants |
| **mainline gcc-3.2.2** | available (`sha256 7035a828…`) | control: comparing both shows the drift below is the EE snapshot's, not a point release's |
| **shipped `cc1`** | available on any machine with the toolchain | the **authority** for line numbers, struct layouts and constants; it is not stripped and carries DWARF |
| **community EE patches** (`gcc-3.2.2-PS2.patch`, `gcc-3.2.3-PS2.patch`) | available in the history of the community toolchain scripts | a semantic reference for **EE instruction semantics** only (MMI, VU macro mode, R5900 constraints). **Not** the shipped tree — see §4 |
| **Sony `config/mips/mips5900.c`** | **not available** | the shipped backend has it (152 functions) and it is where the EE register model lives |
| **Sony 3.2-ee-040921 source tree** | **not available** | — |
| **Jürgen Urban's R5900 patch (2013)** | available ([gcc-patches attachment](https://gcc.gnu.org/pipermail/gcc-patches/2013-January/356066.html)) | minimal ISA enablement only (`-mno-llsc`, `trunc.w.s`); it does not define register classes |

## 2. How a rule is anchored without the shipped tree

The shipped `cc1` is the authority. `tools/compiler/ee-gcc-anchor.py` turns a symbol into an address, a
source line, a struct layout or a constant:

```sh
CC1=~/eecc/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8
```

A `T1` law needs the source rule **and** the binary anchor **and** agreeing behaviour. Where the source
is unavailable, the law is `T2` (binary anchor or source rule, plus behaviour) or `T3` (behaviour
only) — and it says so.

## 3. Line numbers are not portable

The shipped compiler is **not** stock gcc-3.2.3. Measured median drift per file
(EE definition line minus mainline definition line):

| file | drift | reading |
| --- | ---: | --- |
| `global.c` | **+341** | patched (allocation, colouring) |
| `regmove.c` | **+1920** | patched |
| `haifa-sched.c` | **+263** | patched (scheduling) |
| `gcse.c` | **+137** | patched |
| `reload1.c`, `calls.c`, `local-alloc.c`, `regclass.c`, `ifcvt.c`, `combine.c`, `flow.c`, `reorg.c` | 0 … −13 | effectively mainline |
| `cse.c`, `jump.c`, `function.c`, `loop.c` | −22 … −68 | point-release-sized |

Comparing against gcc-3.2.2 moves every median by at most one line, so the drift belongs to the EE
snapshot. **Cite the line `addr2line` reports for your `cc1`** ([L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)).

## 4. Why the community EE patches are not the shipped tree

The community toolchain history contains `patches/gcc-3.2.2-PS2.patch` (184,804 B, 32 files) and
`patches/gcc-3.2.3-PS2.patch` (160,132 B, 26 files). They add real EE support — `core-mmi.h`,
`core-vumm.h`, `r5900.h`, `crti5900.asm`, `t-r5900` — and patch `mips.c`, `mips.h`, `mips.md`.

Their **register model is a different one**:

| register class | community 3.2.2 patch | shipped `cc1` dumps |
| --- | --- | --- |
| `VU0_Q_REG`, `VU0_I_REG`, `VU0_GR_AND_QI_REGS` | absent | present |
| `COP0_AND_GR_REGS` | absent | present |
| `FP_ACC_REG` | absent | present |
| `HILO_REGS` | absent | present |
| `HI1_REG`, `LO1_REG`, `ST_REGS` | present | — |
| `HARD_REG_SET` width | 3 words (≈96 bits) | **24 B = 192 bits** |
| `FIRST_PSEUDO_REGISTER` | 76 → **79** | far above 79 |

So the patch is a useful reference for **what EE instructions mean**, and it must not be used for the
register file, the register classes, or the allocator. Those have to be read from the binary — which is
why the colouring model is still open (see [LAWS.md](LAWS.md) open items).

## 5. What is still missing, and what would close it

* The exact `FIRST_PSEUDO_REGISTER` and the class contents. The class table
  (`reg_class_contents`, `reg_class_size`, `fixed_reg_set`, `call_used_reg_set`) is **runtime
  initialised** (`.bss`), so a static read returns zeros. Reading it from a live process is the direct
  route; the Sony source would answer it statically.
* The content of the `global.c`, `regmove.c`, `haifa-sched.c` and `gcse.c` patches.
* Where the community patches *are* usable: EE instruction semantics in the backend. Any rule taken
  from them stays `T3` until the shipped binary confirms it.

### 5.1 Searches already run (do not repeat them)

| Route | Result |
| --- | --- |
| community toolchain git history | found `gcc-3.2.2-PS2.patch` and `gcc-3.2.3-PS2.patch` (see §4) |
| Wayback `ps2dev.org` toolchain page (2008) | confirms the community toolchain is gcc-3.2.2 + patches |
| GitHub code search `filename:mips5900.c` | **0 results** |
| Software Heritage origin search `ee-gcc` | nothing relevant |
| gcc-patches: Jürgen Urban, *Support for MIPS r5900* (2013) | patch retrieved; ISA enablement only, **no register classes** |
| Internet Archive: **PS2 Linux Kit DVDs** | discs located and read **remotely** (ISO9660 directory tables over HTTP Range, no full download). Disc 1 = installer; disc 2 = the software tree. `/SCEI/RPMS` holds the **EE toolchain binaries** (`GCC-29`, `GCC-C++`, `GCC-G77`, `GCC-OBJ`, `BINUTILS`); `/SCEI` has **no SRPMS** and the root-level `/SRPMS` + `/SOURCES` are the i386 distribution's. **The kit ships no EE compiler source.** (`SOURCES/EE-031_1.GZ` is the `ee` text editor, not the Emotion Engine.) |
| `mips5900.c` / `ee-gcc 3.2-ee-040921` source, general web | no hit |

**A Sony release does exist for the 2.9 era.** The GitHub repository
[`GirianSeed/ee-gcc`](https://github.com/GirianSeed/ee-gcc/releases) publishes four Sony `ee-gcc` source
packages (all 2.9-generation, 1999). Their shape is the packaging to look for: a `config.sh` with
`--prefix=/usr/local/sce/ee/gcc --target=ee` — **the same prefix and target this toolchain reports in its
DWARF** — plus `COPYING`/`COPYING.LIB`/`COPYING.NEWLIB`, a `sce-patch/patch` context diff and
`src/src.tar.gz`. Sony therefore did ship EE GCC source under the GPL.

That 2.9 release is **not** the shipped 3.2 tree: its patch leaves `config/mips/mips.md` untouched, and
it has no `mips5900.c`, no `mips5900_*` pattern names and none of the VU0/COP0/ACC register classes. The
EE **code generation** arrived in the 3.x line — which is exactly the part still missing.

**Conclusion so far: no public source contains the EE register model** (192-bit `HARD_REG_SET`, `VU0_*`,
`COP0_AND_GR_REGS`, `FP_ACC_REG`, `HILO_REGS`). Every public EE patch found so far has a *smaller*,
different register file. That is why the register-class and colouring laws are `T2`/`T3`, and why the
direct route is to read the tables from a live process.
