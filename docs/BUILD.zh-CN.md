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
配置文件说明见 [config/README.zh-CN.md](../config/README.zh-CN.md)。

`make build` 先从零售可执行文件派生载荷，再切分载荷、汇编源码、链接结果，并在每个阶段后校验载荷 sha1。
期望值是 `7cc42d275750600d1f232b2632447f77205f3fc0`。**差一个字节就停止**。

## 3. 检查改动

```bash
make progress                    # 静态上界；不需要工具链
make delta BASE=origin/main      # src/matched/ 里本次改动的文件必须 100% 匹配
make check                       # 仓库自检；不需要原版可执行文件
```

`make progress` 读 `config/matched_symbols.txt` 与 `config/symbol_addrs.txt`，
按符号表字节数打印静态上界。已发布数字见
[progress/SLPS_258.19_report.json](../progress/SLPS_258.19_report.json)。

`make report` 把结果写到 `build/`：`build/SLPS_258.19_report.json` 与
`build/report_provenance.json`（记录了这次运行**量了什么**：构建断言的载荷 sha1、提交号、
工作树是否脏、有多少 C 单元不足 100%）。它**不写** `progress/`：那棵树只由
`tools/maintainer/publish_report.py` 在校验 provenance 之后写入。该目标在任一 C 单元不足 100%
时失败（`--require-c100`）；要探索性报告用 `REPORT_FLAGS=` 覆盖。

## 4. CI

| workflow | 何时跑 | 做什么 |
| --- | --- | --- |
| `validate` | 默认分支 push、每个 PR、手动触发 | push 校验**发布记录**（`PUBLISHED.json`）、禁止材料（含「名字看不出类别」的兜底尺寸线）、报告 schema 与基线；PR 允许任何改动，**只读** `progress/**` 与 `PUBLISHED.json`，且新增/修改的路径必须是 1 MiB 以内的普通 UTF-8 文本文件——符号链接、或工作树里不存在的路径一律拒绝。本仓库自己的分支还可以重命名或删除文件；外部 fork 的 PR 仍只能新增或修改。见 [CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md) |
| `matching-gate` | 默认分支 push、同仓库 PR、手动触发 | 从私有伴生仓库取原版可执行文件与工具链，跑 `make build` / `make delta` / `make report`；**全部通过才发布两个 artifact**：`SLPS_258.19_report`（报告）与 `SLPS_258.19_report_provenance`（证明量了什么的记录）。带 PR 号的手动运行会先核对 PR 来自本仓库**再**做任何 checkout，因此 fork 的脚本永远不会与私有材料同处一个 job |

`matching-gate` 有三种模式，由 [tools/ci/classify_change.py](../tools/ci/classify_change.py)
按改动集合判定，且**默认拒绝**：出错、任何 push、任何手动运行都落到 `full`。

| 模式 | 何时 | 跑什么 |
| --- | --- | --- |
| `skip` | PR 的改动全是文档或纯测试（`tools/check/test_*.py`） | 完全不构建，连私有材料都不下载；仓库检查由 `validate` 负责，它也会跑改动的测试 |
| `fast` | PR 的改动只落在文档、纯测试、`src/matched/**`、`progress/**`，或 `config/**`（**不含** `config/symbol_addrs.txt` 与 `config/reloc_addrs.txt`） | `make build-fast`：基线只装配不链接，随后混合构建、`delta`、报告照跑；混合载荷比的是零售载荷，镜像仍被逐字节验证 |
| `full` | 任何 push、任何手动运行，以及任何触碰构建输入的改动（`splat.yaml`、上面那两个 `config/` 文件、`build*.sh`、`Makefile`、`configure.py`、构建工具、`toolchain.lock.json`、workflows） | 上面那条完整流水线，含基线链接与基线载荷校验；**只有这种模式会发布 artifact** |

两条边界规则：

- **`config/**` 可以是 `fast`，因为 `build.sh` 根本不读 `config/`**：基线链接不可能依赖它；而混合构建从
  `config/` 读的东西（台账、编译标志、编译器表、跳转表表）其效果都已被「混合载荷 == 零售载荷」的逐字节
  比对覆盖。两个例外是 `splat split` 读的文件——它们改变汇编树，而只有基线链接能验那棵树。
- **改动验证代码本身仍是 `full`**：`tools/check/check_public_repo.py`、构建工具、workflows、`Makefile`
  决定门禁**怎么跑**，所以走完整流水线；只有 `make check` 会跑的纯测试才是 `skip`。

`matching-gate` 需要 secret `ORIG_DEPLOY_KEY` 与变量 `PRIVATE_ORIG_REPO`。
**fork 的 PR 拿不到**，此时该 job 只跑 notice 步骤，不算失败；之后由维护者复验该 commit。

维护者若已用 [tools/ci/splat_snapshot.py](../tools/ci/splat_snapshot.py) 把 `splat split`
的输出打包，门禁会直接还原归档而不再跑 splat。归档放在私有伴生仓库；本仓库只带
`toolchain/splat-snapshot.json`（哈希与计数，不含内容）。任何不匹配（输入过期、原版可执行文件
不同、归档损坏、**成员内容**对不上）都打警告并回落真 splat；解包会先在暂存目录里校验，通过后
才搬进检出。门禁从不依赖归档：混合载荷仍与零售载荷比对。

打包 job（`.github/workflows/splat-snapshot.yml`）由维护者手动启动，跑在受保护的 `splat-snapshot`
环境之后（需要一位 reviewer 批准），因为它要用写权限部署密钥。有该密钥时，job 把归档**直接推进私有
伴生仓库**，归档因此不会进入本仓库的 Actions 存储；没有该密钥时回落到保留一天的中转 artifact。
两种情况都由维护者在本仓库提交 `toolchain/splat-snapshot.json`。

检查不过就**不产生**新的进度报告。因此公开的数字永远是**验证过的数字**。

想贡献一个已匹配的函数？读 [CONTRIBUTING.zh-CN.md](../CONTRIBUTING.zh-CN.md)。

## 5. 发布报告

默认分支上 `matching-gate` 跑绿之后，下载**两个** artifact，再把报告写进本仓库：

```bash
gh run download <run-id> -R <owner>/<repo> -n SLPS_258.19_report -D .tmp/report
gh run download <run-id> -R <owner>/<repo> -n SLPS_258.19_report_provenance -D .tmp/provenance
python3 tools/maintainer/publish_report.py \
  --report .tmp/report/SLPS_258.19_report.json \
  --provenance .tmp/provenance/report_provenance.json
```

只有 provenance 记录表明「载荷 sha1 实测通过、全部 C 单元 100%、工作树干净、不是 `--limit`
冒烟」时才会发布。随后它写入 `progress/SLPS_258.19_report.json` 并更新 `PUBLISHED.json`，同时与
基线比对数字（**含分母**）。用 `--force --reason "..."` 越过门禁，理由会记进 `PUBLISHED.json`。

**只要这次发布的报告内容变了，就必须带 `--freeze-baseline`。** `progress/baseline.json` 是冻结参照，
而发布门禁会拒绝「基线与所发布报告对不上」的 PR（报 `the baseline provenance does not describe the
published report`）。该参数写进去的是 **provenance 记录**（验证了什么），不是报告副本，这样
「不回归」才有意义。它不是可选项 —— 漏掉它就是发布 PR 第一次推送就变红的常见原因。

记录里的 `source_revision` 是**被验证那次运行**所用的提交（provenance 的 `source_commit`，不是执行发布的
提交），门禁同样校验这一条。改过 `toolchain.lock.json` 后用 `--refresh`：它只重算哈希，并保留已记录的版本。

`main` 受仓库规则集保护，因此维护者也是走 PR 落地：

```bash
git switch -c publish/<run-id>
git commit -am "publish: <这次已验证的运行>"
git push -u origin publish/<run-id>
gh pr create --base main --fill
```

`validate` 认识「维护者发布 PR」：只允许改 `progress/**` 与 `PUBLISHED.json`，且必须通过发布检查
（记录哈希、`payload_verified`、基线带绑定所发布报告且通过的 provenance、不回归）。

## 6. 排障

- **`payload sha1 mismatch`**：某个替换源与零售字节不一致。用 `make delta BASE=<上一个好提交>` 缩小范围。
- **汇编器拒绝 `$t4` 到 `$t7`**：请用 decompals 的 binutils 分支；官方 binutils 2.45 会拒绝这些别名。
- **`splat` 切出空树**：核对 `splat.yaml` 与你的可执行文件。本仓库只支持日版零售。
