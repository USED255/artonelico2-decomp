# Pass map — ee-gcc 3.2 / 2.96

[Handbook index](README.md) · [简体中文](PASSES.zh-CN.md) · [Laws](LAWS.md)

`ee-gcc` accepts `-da` and writes one RTL dump per pass, named
`<file>.<NN>.<pass>`. The numbering differs between the two compilers in this project, so a pass
table is only valid **inside one compiler**. Compare by pass **name**, never by number.

## Dump inventory

| `ee-gcc 3.2-ee-040921` (26) | `ee-gcc 2.96-ee-001003-1` (22) |
| --- | --- |
| `00.rtl` `01.sibling` `03.jump` `08.null` `09.cse` `10.addressof` `11.gcse` `12.loop` `13.cfg` `14.bp` `15.cse2` `16.life` `17.combine` `18.ce` `19.regmove` `20.sched` `21.range` `22.lreg` `23.greg` `24.postreload` `25.flow2` `27.rnreg` `28.ce2` `29.sched2` `31.bbro` `33.dbr` | `00.rtl` `01.sibling` `02.jump` `03.cse` `04.addressof` `08.gcse` `09.loop` `10.cse2` `11.cfg` `13.life` `14.combine` `15.ce` `16.regmove` `17.sched` `19.lreg` `20.greg` `21.flow2` `22.ce2` `25.sched2` `27.jump2` `28.mach` `29.dbr` |

The numbering says "pass N of 3.2"; `03.jump` in 3.2 is `02.jump` in 2.96. A rule anchored in one
dump must be re-measured in the other compiler.

## Which source file owns which dump

Compiled from: the dump's own text, the symbols in the shipped `cc1` resolved through `addr2line`,
and the mainline definition lines. The mapping is asserted per law, not assumed.

| Dump | Owning source (mainline) | Anchor used here |
| --- | --- | --- |
| `00.rtl` `01.sibling` | `expr.c`, `function.c`, `calls.c`, `stmt.c`, `stor-layout.c` | — |
| `03.jump` | `jump.c` | — |
| `08.null` | `toplev.c` (no-op pass) | — |
| `09.cse` `15.cse2` | `cse.c` | — |
| `10.addressof` | EE-specific pass; look for its printer in the shipped `cc1` | — |
| `11.gcse` | `gcse.c` | — |
| `12.loop` | `loop.c` | — |
| `13.cfg` | `cfg*.c` | — |
| `14.bp` | `predict.c` / `profile.c` | — |
| `16.life` | `flow.c` | `life_analysis @ 0x080ce2d8` |
| `17.combine` | `combine.c` | `combine_instructions @ 0x08185f84` |
| `18.ce` `28.ce2` | `ifcvt.c` | — |
| `19.regmove` | `regmove.c` | `regmove_optimize @ 0x081c4640` |
| `20.sched` `29.sched2` | `haifa-sched.c`, `sched-*.c` | `schedule_block @ 0x081b15d8` |
| `21.range` | range/live-range helpers in the shipped `cc1` | — |
| `22.lreg` | `local-alloc.c` | `local_alloc @ 0x0810a2f4` |
| `23.greg` | `global.c` | `global_alloc @ 0x081aa2c4`, `allocno_compare @ 0x081ab288`, `find_reg @ 0x081acd64` |
| `24.postreload` | `reload1.c`, `reload.c` | `find_reg @ 0x08134570` |
| `25.flow2` | `flow.c` | — |
| `27.rnreg` | register-numbering helpers | — |
| `31.bbro` | `bb-reorder.c` | — |
| `33.dbr` | `reorg.c` | `dbr_schedule @ 0x081cd510` |
| backend | `config/mips/mips5900.c` (152 functions), `mips.md` | `uns_arith_operand @ 0x0817178c` |

## How far the shipped source drifts from mainline

The shipped `cc1` is not built from stock gcc-3.2.3. For each source file below, the table gives the
**median** of `(EE definition line − mainline gcc-3.2.3 definition line)` over the functions present
in the binary. A large positive median means EE inserted code throughout the file; a negative median
means mainline has lines EE does not.

| Source file | Median drift | Reading |
| --- | ---: | --- |
| `global.c` | **+341** | heavily patched (allocation, colouring) |
| `regmove.c` | **+1920** | heavily patched |
| `haifa-sched.c` | **+263** | heavily patched (scheduling) |
| `gcse.c` | **+137** | patched |
| `calls.c` | 0 | same as mainline |
| `reload1.c` | 0 | same as mainline |
| `local-alloc.c` | −4 | same as mainline |
| `ifcvt.c` | −6 | same as mainline |
| `combine.c` | −8 | same as mainline |
| `flow.c` | −13 | same as mainline |
| `reorg.c` | −13 | same as mainline |
| `regclass.c` | −2 | same as mainline |
| `cse.c` | −22 | point-release-sized differences |
| `jump.c` | −47 | point-release-sized differences |
| `function.c` | −55 | point-release-sized differences |
| `loop.c` | −68 | point-release-sized differences |
| `expr.c` | +4 | mixed; check per function |

The same comparison against **gcc-3.2.2** moves every median by at most one line, so the drift above
belongs to the EE snapshot rather than to a point release.

**Use:** cite the line number that `addr2line` reports for your `cc1`. Use mainline for the rule's
semantics, and treat the mainline line as a hint that you correct by the measured offset. Files with
a small drift can be read side by side with mainline; files with a large drift must be confirmed by
disassembly (see [L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)).
