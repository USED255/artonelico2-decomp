# 构建本仓库

[English](BUILD.md) | [简体中文](BUILD.zh-CN.md)

本仓库包含逆向 C 源码与验证它的工具，不含任何属于他人的材料。

## 1. 你需要自备的东西

| 项目 | 说明 |
| --- | --- |
| `SLPS_258.19` | 日版零售主程序，从你自己的光盘提取；sha1 为 `766836783c16b8616d3d84cfbd6af70a50b6c052` |
| `ee-gcc 3.2-ee-040921` | 游戏代码编译器；属于 Sony，**不可再分发** |
| `ee-gcc 2.96-ee-001003-1` | CRI 段编译器；属于 Sony |
| PS2 binutils | decompals 的 binutils 2.40 分支，用来汇编 `splat` 的输出 |
| `objdiff-cli` 3.8.2 | 公开工具：<https://github.com/encounter/objdiff/releases> |
| `splat` 0.50.0 | 公开工具：`pip install splat64` |

版本与 sha256 固定在 [toolchain.lock.json](../toolchain.lock.json)；CI 使用前逐个校验。

把编译器加入 `PATH`，也可以设 `EE_GCC`、`EE_GCC_CRI`、`PS2_AS`：

```bash
export PATH="$HOME/eecc/ee-gcc3.2-040921/bin:$HOME/eecc/ee-gcc2.96/bin:$HOME/eecc/ps2binutils:$PATH"
```

## 2. 配置与构建

```bash
python3 configure.py --game /path/to/SLPS_258.19
make build          # 切分、汇编、链接、校验载荷哈希
make report         # 生成进度报告
```

这是**混合编译器**构建：游戏代码用 `ee-gcc 3.2-ee-040921`，CRI 中间件用 `ee-gcc 2.96-ee-001003-1`。
`config/compiler_map.tsv` 逐源写明用哪个（缺省 = 游戏编译器），两个路径来自 `EE_GCC` / `EE_GCC_CRI`（或 `GCC` / `GCC_CRI`）；
走 CRI 编译器的源还需要在 `config/source_flags.tsv` 里给 `-G0`。

`make build` 先从零售可执行文件派生载荷，再切分载荷、汇编源码、链接结果，并在每个阶段后校验载荷 sha1。
期望值是 `7cc42d275750600d1f232b2632447f77205f3fc0`。**差一个字节就停止**。

## 3. 检查改动

```bash
make delta BASE=origin/main      # src/matched/ 里本次改动的文件必须 100% 匹配
make check                       # 仓库自检；不需要原版可执行文件
```

## 4. CI

| workflow | 何时跑 | 做什么 |
| --- | --- | --- |
| `validate` | 每次 push、每个 PR、手动触发 | push 校验**发布记录**（`PUBLISHED.json`）、禁止材料、报告 schema 与基线；PR 允许任何改动，**只读** `progress/**` 与 `PUBLISHED.json`。见 [CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md) |
| `matching-gate` | 默认分支 push、同仓库 PR、手动触发 | 从私有伴生仓库取原版可执行文件与工具链，跑 `make build` / `make delta` / `make report`；**全部通过才发布 artifact** |

`matching-gate` 需要 secret `ORIG_DEPLOY_KEY` 与变量 `PRIVATE_ORIG_REPO`。
**fork 的 PR 拿不到**，此时该 job 明确跳过，不算失败；之后由维护者复验该 commit。

检查不过就**不产生**新的进度报告。因此公开的数字永远是**验证过的数字**。

想贡献一个已匹配的函数？读 [CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md)。

## 5. 发布报告

默认分支上 `matching-gate` 跑绿之后，下载报告 artifact，再写进本仓库：

```bash
gh run download <run-id> -R <owner>/<repo> -n SLPS_258.19_report -D .tmp/report
python3 tools/publish_report.py --report .tmp/report/SLPS_258.19_report.json
```

该工具会写入 `progress/SLPS_258.19_report.json` 并更新 `PUBLISHED.json`，同时与基线比对数字。
用 `--accept-baseline` 把新报告接受为新基线；改过 `toolchain.lock.json` 后用 `--refresh`。

## 6. 排障

- **`payload sha1 mismatch`**：某个替换源与零售字节不一致。用 `make delta BASE=<上一个好提交>` 缩小范围。
- **汇编器拒绝 `$t4` 到 `$t7`**：请用 decompals 的 binutils 分支；官方 binutils 2.45 会拒绝这些别名。
- **`splat` 切出空树**：核对 `splat.yaml` 与你的可执行文件。本仓库只支持日版零售。
