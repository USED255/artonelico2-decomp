# Building this repository

This repository publishes the reverse-engineered C sources and the tooling needed to verify them.
It does **not** ship anything that is copyrighted by someone else.

## 1. What you must provide

| 需要 | 说明 |
| --- | --- |
| `SLPS_258.19` | 日版零售《魔塔大陆2》主程序，从**你自己的光盘**提取（sha1 `766836783c16b8616d3d84cfbd6af70a50b6c052`） |
| `ee-gcc 3.2-ee-040921` | 游戏代码的编译器（Sony 授权，**不可再分发**） |
| `ee-gcc 2.96-ee-001003-1` | CRI 段的编译器（同上） |
| PS2 binutils（decompals fork，binutils 2.40） | 汇编 `splat` 的输出 |
| `objdiff-cli` 3.8.2 | 公开下载：<https://github.com/encounter/objdiff/releases> |
| `splat` 0.50.0 | `pip install splat64` |

版本与 sha256 固定在 [`toolchain.lock.json`](../toolchain.lock.json)；CI 在使用前逐个校验。
把编译器放到 `PATH`（或设 `EE_GCC` / `EE_GCC_CRI` / `PS2_AS`），例如：

```bash
export PATH="$HOME/eecc/ee-gcc3.2-040921/bin:$HOME/eecc/ee-gcc2.96/bin:$HOME/eecc/ps2binutils:$PATH"
```

## 2. Configure and build

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build          # splat split → assemble the baseline → link → hybrid build → assert payload sha1
make report         # objdiff progress report → progress/SLPS_258.19_report.json
```

`make build` 会在三个阶段各断言一次**载荷 sha1**（`7cc42d275750600d1f232b2632447f77205f3fc0`）：
只要有一个字节不同就立刻失败。这是本项目的“棘轮”，也是 CI 的第一道门。

## 3. Check a change

```bash
make delta BASE=origin/main      # 本次改动过的 src/matched/*.c 是否逐个 100% 匹配
make check                       # 仓库自检：导出清单 / 不可公开类别 / 报告不变量（不需要原版也能跑）
```

## 4. CI

| workflow | 何时跑 | 做什么 |
| --- | --- | --- |
| `validate` | 每次 push / PR | `make check`：导出清单完整性、不可公开类别扫描、报告 schema 与“相对基线不回退” |
| `matching-gate` | 默认分支 push、同仓库 PR、手动 | 私有伴生仓库取原版 ELF 与工具链 → `make build`（载荷 sha1）→ `make delta`（改动逐个 100%）→ `make report`（不回归）→ **全绿才上传 `<VERSION>_report` artifact** |

`matching-gate` 需要 secrets（`ORIG_DEPLOY_KEY`）与变量（`PRIVATE_ORIG_REPO`）；fork 的 PR 拿不到，
此时该 job 会**明确跳过**而不是失败。**只要有一项不达标，就不会产生新的进度报告** —— 公开的数字永远是验证过的。

## 5. Troubleshooting

- **`payload sha1 mismatch`**：说明某个替换源产出的字节与零售不一致。先用 `make delta BASE=<上一个好 commit>` 缩小范围。
- **汇编器报 `$t4`–`$t7`**：本项目使用的是 decompals 的 binutils fork（2.40）；官方 binutils 2.45 会拒绝这些别名。
- **`splat` 输出为空**：确认 `splat.yaml` 与你的 ELF 版本一致（本项目只支持 `SLPS_258.19` 日版零售）。
