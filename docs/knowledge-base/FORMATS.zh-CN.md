# 光盘格式

[English](FORMATS.md) | [简体中文](FORMATS.zh-CN.md)

本页记录什么：**《魔塔大陆2》**（Ar tonelico II: Melody of Metafalica）零售光盘上的容器与模块
格式，实测对象是日版（`SLPS_258.19`），并以美版（`SLUS_217.88`）作对照。这里写结构与事实，
不含游戏资产、游戏文本或光盘镜像。

测量来自本地自备的光盘镜像。游戏、资产与文本受版权保护。基于本页做任何东西之前，先读
[PUBLICATION-POLICY.zh-CN.md](../PUBLICATION-POLICY.zh-CN.md)。

## 1. 光盘上有什么

| 项 | 是什么 |
| --- | --- |
| `SLPS_258.19` | 主程序：游戏代码、SDK 库层与资产表 |
| `RPK.BIN` | 大资产容器（日版约 366 MB） |
| `ERXS/*.ERX` | 11 个可加载代码模块：是动态库，不是资产包 |
| `SOUND/**/*.AFS`、`VPACK*/*.AFS` | AFS 容器；每个子文件都是 CRI ADX 音频 |
| `MOVIE/**/*.SFD` | CRI Sofdec 影片：裸 MPEG-1 Program Stream |
| `.evd` 条目（在容器内） | 事件脚本，也是游戏文本的最大来源 |
| `.irx` 模块 | 运行时加载的 IOP 模块（本作 13 个） |

两条事实能省很多时间。第一，资产层没有任何加密，下面每种格式都是明文。第二，容器是 Gust
的变体，不是标准 CRI 工具的格式，所以现成工具经常读错。

## 2. AFS 容器（Gust 变体）

本作的 AFS 是 CRI AFS 的紧凑变体：没有 `table_offset` 字段，也没有 footer。布局是：

```
0x0000  "AFS\0"
0x0004  u32 LE    条目数 N
0x0008  N × { u32 LE 绝对偏移; u32 LE 大小 }
        ……零填充……
align2048(8 + 8N)                 第一个子文件；每个子文件按 2048 对齐
align2048(最后一个子文件结束)      文件名表：每条 48 字节 = char name[44] + u32
```

容器大小 = `align2048(最后一个子文件结束) + align2048(48N + 4)`。这条在实测的全部 34 个容器上
成立。文件名表给出每个子文件的原始路径，例如 `sound/voice/<id>/<id>.adx`。

子文件是 CRI ADX：大端 `80 00` 头，带 `(c)CRI` 串。两个语音容器是一对语言版本：`VPACK` 放本地化
（英文）语音，路径在 `sound/voice/`；`VPACKJ` 放日文语音，路径在 `sound/voicej/`。日文条目全部
24 kHz；本地化容器混合 48 kHz 与 24 kHz，其中与日文容器逐字节相同的条目恰好就是 24 kHz 那些。

## 3. `RPK.BIN`：两代结构不同

两代不是同一种格式。

| | 魔塔大陆 1 | 魔塔大陆 2 |
| --- | --- | --- |
| 索引 | `RPK.ID`：纯文本索引（UTF-8 BOM，JSON 风格行），2,703 条 `{ path, id, size }` | 没有索引文件 |
| 布局 | 按索引顺序把 2,703 个文件拼接，每个 2048 对齐；总长与文件大小精确相等 | 16 个 AFS 容器首尾相接，然后是一段 373,116,928 字节、按 2048 对齐的 `LZR\0` 块流（12,100 块） |
| 文件名 | 在 `RPK.ID` 里 | 在主程序的字符串表里（`erxs/*.erx`、`res/Tmap/TX00/*.tm2.lzr`、`fpack/*.fp`、`rpk.bin`、`%s.lzr` 等） |

容器内那 16 个 AFS 与同一张盘上独立的 `/VPACKJ/*.AFS` 逐字节相同，只是顺序不同。

## 4. LZR 压缩

一个 `LZR` 块 = 16 字节头 + 压缩体，按 2048 字节对齐：

```
"LZR\0" | flag_bits | data_leng | orig_leng      （四个小端 u32）
体长度 = 16 + (flag_bits + 7) / 8 + data_leng
```

体里每个字节装四个 2-bit 操作码：复制字面字节、复制一段、重复前一字节、12+4 位字典回溯。
社区参考实现（`lzr-src`，Unlicense）能解出日版光盘的全部 12,079 个块。

## 5. `.evd` 事件脚本

`.evd` 是事件脚本容器。实测结构是 `EventDialogues + EventSequence × 2 + Selections`，其中

```
EvdDialogue = i32 style, narrator, portrait, id
            + i16 portraitDiff, data
            + evdstr
evdstr      = i32 size + 长度为 (size & ~3) + 4 的字符串区
```

文本是未压缩的 Shift-JIS。日版光盘的 1,232 条索引全部解析到 EOF。它是游戏文本的最大来源，
翻译项目因此都做这个容器。

## 6. ERX 模块

`.ERX` 不是加密脚本，也不是资产包。它是 32 位 MIPS ELF 共享对象：`\x7fELF`、`e_machine = 8`
（MIPS）、`e_type = 0xFF91`（Gust 自定义值），段包括 `.eemod`、`.text`、`.rel.text`、`.erx.lib`、
`.erx.stub`、`.rodata`、`.data`、`.sdata`、`.sbss`。

这也是社区的解包工具多年攻不下它的原因：这是代码问题，不是容器问题。它的熵只有 2.81–5.20，
远低于加密会产生的值，而且模块里有大量明文 ASCII 与 Shift-JIS 字符串。

主程序还带着 `.erx.lib`（导出符号注册表，每个库槽一条）与 `.erx.stub`。本项目的具名符号就来
自这张表。

## 7. 视频与音频

- **SFD** 是裸 MPEG-1 Program Stream：直接以 pack header（`00 00 01 BA`）开头，没有 CRI 容器
  头；内含 MPEG-1 视频与 ADX 音频。FFmpeg 能直接读。
- **ADX** 是 CRI ADPCM 音频。FFmpeg 的 `adx` demuxer 与 `adpcm_adx` 解码器可处理。

## 8. 工具

| 工具 | 许可证 | 做什么 |
| --- | --- | --- |
| [FFmpeg](https://ffmpeg.org) | LGPL / GPL | 解复用并解码 ADX 与 SFD |
| `exar2`（asmodean） | 专有但免费：作者禁止再分发、修改与嵌入其它软件 | 解开并重打包 `RPK.BIN`、`.evd`、`.fp`；`unlzr` 解 LZR |
| `FP_tools`（TerraBreaker） | 免费，含 C++ 源码 | 解包并重打包 `.fp` 资产 |
| `rpkextract.rb`、`evdextract.rb` | 免费脚本 | 只解包 |
| `FakeLZR` | 免费 | 不压缩，只写一个合法的 LZR 头 |
| [gust_tools](https://github.com/VitaSmith/gust_tools) | GPLv3-or-later | 面向更晚的 Gust 格式（PC 版）；**不适用于** PS2 两作 |
| [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools) | 见仓库 | 通用 JRPG 工具集 |

一条来自实测的工作规则：不压缩也能重打包资产，只要写一个合法的 LZR 头；社区补丁工具就是这么做的。

## 9. 未解决项

上面的测量没有解决这些：

- 魔塔大陆 1 索引的 `id` 字段单调递增，但约有 96,000 个空号；空号对应什么未知。
- 魔塔大陆 2 容器为什么内嵌一份日文语音容器副本，未知。
- 魔塔大陆 1 的 `.evd`、`.fp`、`.ipu` 条目内部结构未解析。
- 魔塔大陆 1 光盘是否也有 ERX 等价物，未找到。
- 主程序是否在加载时自解压或自解密，未验证。

## 10. 合规

- 不要分发光盘镜像、BIOS 或任何解出的资产。本页只给结构。
- 格式是事实；你按本页写的解析器是你自己的实现。不要抄许可证不允许的代码。
- 社区的汉化与 undub 项目发的是补丁，不是资产，并要求用户自备游戏。这是安全的模式。
