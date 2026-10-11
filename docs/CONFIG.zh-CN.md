# 配置文件说明

[English](CONFIG.md) | [简体中文](CONFIG.zh-CN.md)

`config/` 目录存放构建输入。本页逐个说明这些文件。
本页写明谁读该文件、谁写该文件，以及能否手改。

请先读 [docs/BUILD.zh-CN.md](BUILD.zh-CN.md)，那里讲构建步骤。

## 1. 文件总览

| 文件 | 写入方 | 读取方 | 能否手改 |
| --- | --- | --- | --- |
| `symbol_addrs.txt` | `tools/project/gen_symbol_addrs_jp.py` | splat 与若干工具 | 不能。请重新生成。 |
| `matched_symbols.txt` | 维护者与匹配工具 | 混合构建与报告 | 不能。维护者替你补条目。 |
| `compiler_map.tsv` | 维护者 | 混合构建与报告工具 | 可以，但很少需要。 |
| `source_flags.tsv` | 维护者与匹配工具 | 混合构建与报告工具 | 可以。 |
| `jtbl_tables.tsv` | 维护者 | 混合构建 | 可以，但很少需要。 |
| `reloc_addrs.txt` | 维护者 | splat | 可以，但很少需要。 |
| `linker_script_extra.ld` | 维护者 | 改动检测 | 可以，但很少需要。 |
| `match_meta.tsv` | `tools/build/gen_match_meta.py` | 匹配工具 | 不能。该文件由工具生成。 |

## 2. `config/symbol_addrs.txt` —— splat 符号表

本文件给 splat 提供每个函数的地址与名字。文件里有 10,923 个函数条目。

格式来自 splat 上游，是固定格式。不要改格式。`splat/util/symbols.py` 逐行解析：

```
<name> = <address>; // type:<type> size:<size>
```

解析规则如下：

- 每条数据行只含一个分号。
- `=` 左边是名字，右边是地址。
- 地址是十六进制，带 `0x` 前缀。
- 第一个 `//` 之后是属性表。每个属性是一个 `name:value` 对。
- 以 `//` 开头的行是注释。

`tools/project/gen_symbol_addrs_jp.py` 生成该文件。生成器读两个私有输入：

1. Ghidra 函数清单 `<name>.functions.tsv`。
2. `tools/project/erx_tables.py` 产出的 `.erx.lib` 导出注册表文本。

生成器优先采用 `.erx.lib` 的库槽号名字。Ghidra 名字 `FUN_xxxxxxxx` 转成
`func_xxxxxxxx`。`.erx.lib` 里非函数入口的地址不写 `type:label`（私有笔记 P-06）。

读取方：splat 通过 `splat.yaml` 的 `symbol_addrs_path` 选项读该文件。
`tools/project/ghidra_draft.py`、`tools/project/jtbl_draft.py`、
`tools/report/gen_function_report.py` 与 `tools/report/match_workqueue.py` 也读该文件。

## 3. `config/matched_symbols.txt` —— 混合构建的唯一开关

本文件是已 C 化函数台账。它是混合构建的**唯一开关**。构建步骤见
[docs/BUILD.zh-CN.md](BUILD.zh-CN.md)。

规则如下：

- 台账里的符号，其 `.text` 由 `src/matched/<source>.c` 提供。编译器
  `ee-gcc 3.2-ee-040921` 编译该文件。文件 `asm/cod/<symbol>.s` 不再参与汇编与链接。
- 不在台账里的符号，仍由 splat 拆出的 `asm/cod/<symbol>.s` 提供。
- 新增一个已 C 化函数分两步。先写 `src/matched/<symbol>.c`，再在本文件加一行。

格式为每行一项：

```
<symbol> [<source-basename>]
```

- `#` 起注释，行尾注释也生效。
- 第二列可选，是源文件基名。缺省时默认等于符号名。构建随后读
  `src/matched/<source-basename>.c`。
- 第二列可以与符号名不同。一个源文件可以提供多个符号。

**外部贡献者不要手改本文件。** 匹配验证通过后由维护者补条目。
见 [CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md)。

台账分四段。每个段标记行都是精确锚点。匹配工具在标记之间插入内容。

- `per-function compare samples` —— 10 个手写样板，全部 objdiff 100%。
- `matching batch: trivial auto-match` —— 由
  `tools/project/auto_match_trivial.py` 生成。
- `matching batch: stubs` —— 由 `tools/project/auto_match_stub.py` 生成。
- `CRI middleware` —— 项目按 MIT 许可复用 `recvx-decomp` 的源。

读取方：`build_mixed.sh` 直接读该台账。`tools/build/matched_ledger.py` 是唯一解析实现。
`tools/build/decomp_build.py`、`tools/build/gen_objdiff_full.py` 与
`tools/build/gen_match_meta.py` 都用该解析实现。

### 3.1 默认编译参数

构建用以下参数编译每个匹配源：

```
-O2 -falign-functions=4 -ffunction-sections
```

- `-O2` 与 per-function compare 探针一致。项目在该参数下取得 100%。
- `-falign-functions=4` 把函数起始对齐从默认 8 字节压到 4 字节。原版有大量函数
  位于 `4 mod 8` 的地址上。默认 8 字节对齐会让 `ld` 插入 4 字节填充，其后全部
  地址漂移。
- `-ffunction-sections` 让每个函数占一个 `.text.<symbol>` 段。链接脚本据此把每个
  函数按原位放置。

### 3.2 走别的优化档的源

`config/source_flags.tsv` 保存单个源的额外参数。构建把额外参数**追加在默认参数之后**。
`gcc` 取最后一个 `-O`。

### 3.3 `baseelf_85` 说明

台账早期把 `baseelf_85` 记为「已知未解（jal vs j，objdiff 62.9%）」并刻意排除。
后来查明它是 **`-O1` 档**的空壳包装。`-O1` 下 objdiff 100%。见
`config/source_flags.tsv` 与私有笔记 O-05。改回 `-O2` 编译会让载荷短 176 B、
sha1 变红。项目已实测该负面对照。

## 4. `config/compiler_map.tsv` —— 每个源的编译器

本文件指明哪个编译器编译某个源。本作是**混合编译器工程**：

- 游戏代码用 `ee-gcc 3.2-ee-040921`。
- CRI 中间件（ADXT 10.03、ADXRT 3100、ADXF 7.63，Build: Feb 9 2007）用
  `ee-gcc 2.96-ee-001003-1`。

证据出处：私有报告 `docs/kb/reports/R17` §4.2。项目在 `recvx-decomp`（MIT）上实测：
一份 CRI C 用 `ee-gcc 2.96 -O2 -G0` 编译后与日版逐字节一致。例：
`AIFF_GetInfo`，908 B，两侧 sha1 都是 `4e205079...`。

格式为每行一项：

```
<source-basename><TAB>game|cri
```

- `game` 走 `--gcc`（`ee-gcc 3.2-ee-040921`）。
- `cri` 走 `--gcc-cri`（`ee-gcc 2.96-ee-001003-1`）。
- 也可以直接写编译器绝对路径。
- 只列非 game 的源。缺省为 `game`。

两个归档都在 `toolchain.lock.json` 里锁定。CI 安装两个归档并导出 `GCC_CRI`。

读取方：`build_mixed.sh` 用 `--cc-map` 把该文件传给
`tools/project/compile_sources.py`。`tools/report/gen_function_report.py` 也读该文件。

## 5. `config/source_flags.tsv` —— 额外编译参数

本文件保存单个源的额外编译参数。格式为每行一项：

```
<source-basename><TAB><extra-cflags>
```

- 构建把额外参数追加在默认参数之后。
- `#` 起注释。解析器先去掉注释再读该行。
- CRI 源需要 `-G0`。见 [docs/BUILD.zh-CN.md](BUILD.zh-CN.md)。

读取方：`tools/project/compile_sources.py`（`--flags-file`）与
`tools/report/gen_function_report.py`。写入方：维护者匹配工具
`tools/project/auto_match_wrapper.py`、`tools/project/auto_match_ghidra.py` 与
`tools/project/auto_match_permuter.py`。

## 6. `config/jtbl_tables.tsv` —— 跳转表修补表

C 源里可以写真 `switch`。编译器随后在 `.rodata` 里自产一份跳转表。该表与 splat 已切出的
表重复。重复定义会让地址错位（私有笔记 P-23）。

修补表修复这一情形。`tools/project/jtbl_patch.py` 把 C 表的 `%hi` 与 `%lo` 重定位改指到
既有的 splat 符号。此后没有任何 `.text` 重定位指向 C 表，链接器即可丢掉它。

格式为每行一项：

```
<symbol><TAB><jtbl-symbol>
```

读取方：`build_mixed.sh` 用 `--jtbl-tables` 把该文件传给
`tools/project/compile_sources.py`。

## 7. `config/reloc_addrs.txt` —— 手工重定位记录

本文件供维护者补一条重定位记录。格式来自 splat 上游：

```
rom:<address> reloc:<type> symbol:<name> [addend:<number>]
```

- `//` 起注释。
- `rom`、`reloc` 与 `symbol` 三个属性是必需的。

本文件当前为空。空文件是正确的，因为项目没有手工重定位记录。读取方：splat 通过
`splat.yaml` 的 `reloc_addrs_path` 选项读该文件。

## 8. `config/linker_script_extra.ld` —— 额外链接脚本指令

本文件保存额外的链接脚本指令。它设置入口符号：

```
ENTRY(_start);
```

文件内的注释说：用 `-T linker_script_extra.ld` 参数把该文件传给链接器。公开构建目前
没有步骤传它。`tools/build/decomp_build.py` 把它列为共享输入，因此改动该文件会把构建
标记为过期。

## 9. `config/match_meta.tsv` —— 生成的汇总表

`tools/build/gen_match_meta.py` 写该文件。该文件把 `config/matched_symbols.txt`、
`config/source_flags.tsv` 与私有工作队列合并成一张机器可读表，供匹配工具使用。

该文件是生成物。不要手改，也不要入库。`.gitignore` 已排除它。

## 10. 私有流水线依赖的名字

私有流水线从本仓库读一些名字。不要改这些名字：

- `build_mixed.sh` 的 `HYBRID_OUT`、`HYBRID_RESIDUAL` 与 `HYBRID_NO_CACHE` 三个变量。
  这三个变量沿用历史名。公开仓库的混合构建写 `build/mixed/`。
- 私有布局路径 `routebjp/build/hybrid`。该产物目录属于私有仓库。公开仓库不再写它。
- 私有难度工作队列的文件名 `jp_m3_workqueue.tsv`。
- 该工作队列的列名 `hybrid_ok`。
- 私有证据文件名 `hybrid_build_result.txt`。

这些名字是与私有流水线的兼容契约。保持不改。
