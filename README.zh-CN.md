# 《魔塔大陆2：少女调合术士》匹配反编译

[English](README.md) | [简体中文](README.zh-CN.md)

本仓库包含 PS2 游戏 **《魔塔大陆2》**（日版零售 `SLPS_258.19`）的**逆向 C 源码**。

`src/matched/` 下的源码用**原版编译器工具链**编译。构建过程把结果与零售二进制**逐字节**比较。
两个字节序列相同时，该函数判定为**已匹配**。

> **本仓库是生成物。** 它由私有导出器从工作仓库写出。**请不要在这里提 PR**，见 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)。

## 进度

当前数字在 `progress/SLPS_258.19_report.json` 里：

- 已匹配函数数，
- 已匹配代码字节数，
- 函数总数与代码字节总数。

`progress/baseline.json` 是已接受的基线。比基线更差的报告，CI **不会**发布。
进度历史：<https://decomp.dev/>。

## 目录

```
src/matched/    产物：每个已还原函数一个 C 文件
config/         splat 配置、符号表、编译档、匹配台账
tools/          构建驱动、报告生成器、仓库自检
progress/       当前报告与已接受基线
docs/           构建说明与发表政策
```

## 构建

以下材料由你自备，本仓库不包含：

1. `SLPS_258.19`，来自你自己的游戏光盘。
2. 原版 EE 编译器工具链。它属于 Sony，**不可再分发**。
3. `splat` 与 `objdiff-cli`，这两个是公开工具。

先读 [docs/BUILD.zh-CN.md](docs/BUILD.zh-CN.md)，再执行：

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build      # 汇编、链接、校验载荷哈希
make report     # 生成进度报告
```

## CI 如何验证结果

CI 跑三项检查：

1. **载荷哈希**：链接出的可执行文件必须与零售载荷一致，sha1 为 `7cc42d275750600d1f232b2632447f77205f3fc0`。
2. **逐函数匹配**：`src/matched/` 里**本次改动**的每个文件，必须 100% 匹配它对应的原函数。
3. **不回退**：新报告不得比基线更差。

任何一项不过，CI 立即停止，**不产出**进度报告。

## 法律

- 本仓库不含游戏代码、不含游戏资产、不含 ROM 镜像。**你必须自备正版游戏**。
- 逆向源码是我们的作品，许可证为 GPL-3.0，见 [LICENSE](LICENSE)。
- 请读 [docs/PUBLICATION-POLICY.zh-CN.md](docs/PUBLICATION-POLICY.zh-CN.md)。
- 本项目与 GUST、Banpresto、NIS 无隶属关系。
