# 汇编转录口径（与主进度分开）

[English](TRANSCRIPTION.md) | [简体中文](TRANSCRIPTION.zh-CN.md)

`SLPS_258.19` 里有些函数含有 **任何 C 表达式都产生不了**的指令：
COP2/MMI 向量指令（`lq`、`sq`、`vmulax`、`vadd`、`pcpyld`、`pmfhl` 等）、COP2 寄存器搬运
（`cfc2`、`ctc2`、`qmtc2`），以及以 `break` 实现的原始陷阱桩。

对其中一部分函数来说，要得到字节一致的对象，唯一的办法是把目标指令**逐字转录**进一个全局
`__asm__` 块。得到的目标文件是字节一致的（objdiff 100%、长度相等、只含 `.text`），但里面
**没有重建的 C 代码** —— 这不是语义反编译。

## 两个口径，绝不混用

| 口径 | 计入什么 | 事实源 |
| --- | --- | --- |
| **主进度（重建的 C）** | 匹配源码为 C 的函数 | `config/matched_symbols.txt` 减去 `config/transcription_symbols.txt` |
| **汇编转录** | 由逐字转录匹配的函数 | `config/transcription_symbols.txt` |

转录符号的目标文件仍留在构建里（它们是字节一致镜像的一部分），但在以下位置被**排除出主进度**：

- `tools/report/gen_function_report.py` —— `config/transcription_symbols.txt` 中列出的单元获得
  `transcription` 进度类别且 `base_path = null`，因此发布的报告不会把它们计为已匹配；
- `tools/report/progress_report.py` —— 头条数字排除 transcription 类别，并把它作为单独的合计印出；
- `tools/maintainer/publish_report.py` —— `PUBLISHED.json` 并列记录
  `measures_c_only`（主口径）与 `transcription`（单独口径）。

## 转录源码怎么写

它们是普通的 `src/matched/<symbol>.c` 文件，里面只有一个全局 `__asm__` 块 —— 没有 C 函数体。
让对象保持精确的规则：

1. **不写 C 函数体** —— 否则 GCC 会追加自己的尾声（`jr ra; nop`）。
2. **每条指令都写成 `.word 0x…`**，取自**原始节字节**（`objdump -s -j .text`），因为
   `objdump -d` 会静默跳过某些指令。
3. **`.word` 保持默认（reorder）汇编模式**：在 `.set noreorder` 下，`ee-as` 会在节首多补
   20 字节的填充。
4. **只有带重定位的指令才写成助记符**（`%hi`、`%lo(sym)(base)`、`j`/`jal`），每条用
   `.set noreorder` / `.set reorder` 包住，这样汇编器既不加填充，也不插延迟槽 `nop`。
5. 寄存器名按编号输出（`$4`、`$15` 等），避免 `$30` 与 `s8` 命名造成的意外。

研究仓库里的 `tools/research/mmi_transcribe*.py` 实现了这套做法；当前转录器是
`mmi_transcribe6.py`。

## 新增一个符号

1. 本地验证：objdiff 100、长度相等、`obj_gate.bad_sections(obj) == []`。
2. 把源码加进 `src/matched/<symbol>.c`，台账加一行并带上 `# transcription_asm` 标签，
   再把它的编译标志写进 `config/source_flags.tsv`。
3. 把符号追加到 `config/transcription_symbols.txt` —— **这个文件决定口径如何切分**。
