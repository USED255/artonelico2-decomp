# 导出政策：可公开数据分级（EXPORT-POLICY）

> **适用范围（2026-10-05 修订，决策 [D-0012](../kb/DECISIONS.md)）**：本规则**只约束「导出到公开仓库（`at2-public/`）的内容」**；
> **私有主仓库（`at2/`）不设入库限制、永不推送、不跑 CI**（[AGENTS.md](../../AGENTS.md) §0）。
> 即：`✅ 可公开 / ❌ 不可公开` 的判定管的是**导出清单**，不是「私有仓库能不能 git add」。
> 原文件名 `PUBLICATION-POLICY.md`（位于 `docs/kb/`）于 2026-10-05 更名为本文件并移入 `docs/rules/`（P3 文档重组）。
>
> **本文件是「哪些数据可以导出到公开仓库」的唯一权威**（用户 2026-10-04 指示；决策记录
> [DECISIONS D-0008](../kb/DECISIONS.md)，修订 D-0004 第 3 条「若要推到远端，必须是私有仓库」）。
> 与本文件冲突的旧表述以本文件为准 —— 各报告中「机器派生数据一律不入库」的说法，在 §2 分级表覆盖的范围内**自动失效**；
> 但**司法实务结论不受政策影响**（尤其「静态重编译产物的合理使用地位比模拟器更弱」仍然成立，见 §3.3）。
> **机器校验（2026-10-05 起）**：~~在私有仓库内跑 `make check-public`（= `tools/check_docs.py --only publication`）~~
> ← **该命令已随私有仓库解绑删除（D-0012）**；判定改由**导出清单 + 公开仓库 CI**承担
> （[CI.md](CI.md) 的 `validate` 作业：清单完整性 / 不可公开类别 / 报告不变量与不回归）。最后更新：2026-10-05。

---

## 0. 一句话判据

**判据不是「人工撰写 vs 机器生成」，而是「转换性的功能性重实现」 vs 「逐字转录 / 受保护表达的复制 / 第三方材料 / 专有工具」。**

- 前者（我方对功能与思想的新表达：源码、符号与地址等结构化事实、进度指标、构建配置）→ **可公开**，可以入库、可以推公开仓库。
- 后者（原版二进制的完整或大段转录、原版资产、他人作品、Sony 工具链）→ **不可公开**，绝不入库、绝不推送。

> **保险丝：default-deny。** 美国法下「**公开发表**反编译成果」**没有任何判例正面支持**（Sega/Connectix 的合理使用都以「复制是中间性的、
> 成品不含原件材料」为前提）；日本、欧盟的成文法对「把反编译所得信息提供给公众」有明确限制（§4.3）。
> 因此本政策对任何存疑内容**一律先判不可公开**，由用户/Lead 复核后才可能改为可公开。

---

## 1. 判定流程（对每个候选文件按顺序问三个问题）

| # | 问题 | 判为「是」时 |
| --- | --- | --- |
| **Q1 转换性** | 这份内容是「对功能/思想的重新表达」，还是「对原作表达的复制或机械转录」（逐条指令、逐字节、逐段伪码）？ | 属转录 → **❌ 不可公开** |
| **Q2 替代性** | 公开后，第三方是否**不再需要自备原版**就能得到游戏的可表达内容（美术、音乐、文本、整段代码）？ | 可替代 → **❌ 不可公开** |
| **Q3 第三方与工具** | 是否包含第三方作品、专有工具链（Sony SDK / `ee-gcc`）、密钥或规避技术措施的材料？ | 命中 → **❌ 不可公开**（第三方材料除非其许可证明确允许再分发） |

三条都过 → **✅ 可公开**。存疑 → **⚠️ 逐案评估**：默认**不公开**，并在 [OPEN-ISSUES](../kb/OPEN-ISSUES.md) 登记，由用户/Lead 复核后放行。

---

## 2. 分级表（权威清单）

| 类 | 内容 | 例子 | 判定 | 依据 |
| --- | --- | --- | --- | --- |
| **A** | 人工撰写的源码、脚本、配置、文档 | `routebjp/src/matched/*.c`（人工反推并 objdiff 验证）、`tools/`、`*.sh`、`docs/`、README | ✅ 可公开 | Q1 过（我方表达）；社区惯例：匹配反编译项目的源码一律公开 |
| **B** | 我方工具从原版派生的**结构化事实** | 符号名与地址（`symbol_addrs` 类）、函数边界、尺寸、调用图、索引表、函数↔源文件映射 | ✅ 可公开 | 事实不受版权保护；社区惯例普遍提交 `symbol_addrs.txt` |
| **C** | 进度与质量指标 | objdiff `report.json`（unit 名/字节数/匹配百分比）、难度画像、hash 与计数 | ✅ 可公开 | 无原作表达；[R15](../kb/reports/R15-路线B-decomp.dev发表方案.md) §3.1 的站点惯例即以此为准 |
| **D** | 构建配置 | splat YAML、链接脚本、编译标志、`objdiff.json`、`compile_config.json` | ✅ 可公开 | 我方编写的配置；不含 SDK 头文件 |
| **E** | 以反编译器草稿为起点、**经人工语义加工**（命名/类型/控制流改写，**与指令不逐行对应**）并验证的等价 C | `auto_match_*` 收割入库的 C（须在 `matched_symbols.txt` 标注来源类别） | ✅ 可公开（**须做相似度抽查**：不得与原实现逐行/逐字节对应） | Q1 过（有独立表达选择）；判例见 §4.1 Google v. Oracle |
| **F** | 反编译器 / 切分工具的**全量输出**，或**仅做格式化**的机械反编译 C（与 `.s` 逐条对应） | 整包 Ghidra 伪 C、m2c 未加工草稿、splat 反汇编树（`routebjp/asm/`） | ❌ 不可公开 | 实质仍是转录 → Q1/Q2 不过；§4.1 Atari（verbatim copying）|
| **G** | 原版二进制 / 镜像 / 载荷，及其**完整或大段转录**（含**逐条照抄**原反汇编的 `.s`） | `*.iso`、`*.rom`、`out/binaries/`、`routebjp/src/matched/*.s`（145 个桩） | ❌ 不可公开 | Q1/Q2 皆不过；判例见 §4.1 Atari v. Nintendo |
| **H** | 专有工具链二进制与头文件 | Sony `ee-gcc`（3.2 / 2.96）、PS2 SDK 头文件与库 | ❌ 不可公开 | 再分发授权未解决（[R15](../kb/reports/R15-路线B-decomp.dev发表方案.md) §9-2） |
| **I** | 游戏资产 | 模型 / 贴图 / 音频 / 文本 / 字库的整段或可替代导出 | ❌ 不可公开 | Q2 不过（可替代原作表达）；**格式文档与解析脚本属 A/D 类，可以公开** |
| **J** | 第三方材料 | 社区 wiki 备份（`docs/community-wiki/*`）、他人文章、他人补丁包、汉化译文 | ❌ 默认不可公开 | 除非其许可证明确允许再分发（Unlicense / MIT / CC0 等），入库时须保留 LICENSE 与出处 |
| **K** | 规避与密钥材料 | 解密脚本的密钥、绕过保护的工具与方法说明 | ❌ 不可公开 | 美国 DMCA §1201(a)(2)（向公众提供规避手段）与 (f) 的极窄例外；台湾著作權法 §80-2（见 §4.3） |

> **注意**：`✅` 只是「**可以**公开」，不等于「必须公开」；每类具体推送哪些文件，由发表方案（[R15](../kb/reports/R15-路线B-decomp.dev发表方案.md)）与用户逐次确认决定。
>
> **两处「本项目口径 ≠ 社区基线」的坦白**（写清楚，避免下次误引社区惯例）：
> 1. **H 类（专有工具链）比社区更严**：`zeldaret/oot` 实际**公开入库**了 SGI IDO 5.3/7.1 编译器二进制（附 SGI Freeware Legal Notice）；
>    而 mwcc（`melee`）等则是「下载到被 gitignore 的目录」。我们仍把 Sony `ee-gcc`/SDK 判 ❌，理由是**再分发授权未解决**（无 LICENSE，见 §7-6）
>    —— 这是**自选的高于社区基线**的约束，不要写成「社区惯例」。
> 2. **C 类（进度报告）社区惯例是「不入库、由 CI 生成并作为 artifact 上传」**（`pokemonsnap` 的 `.gitignore` 直接忽略 `/report.json`；
>    `melee`/`tww`/`pokemonsnap` 都是 upload-artifact）。我们允许把它入库（方案 A），理由是**公开仓库跑不了需要原版镜像的构建**；
>    这是**有意的例外**，不是社区惯例。

---

## 3. 四个最容易搞错的边界

### 3.1 「字节匹配的 C 源码」为什么可以公开

匹配反编译的产物与原程序**字节一致**，但它是**用另一种语言对功能的重新实现**（含命名、类型、控制流、数据结构的语义恢复），
属于 Q1 意义上的转换性表达，也是整个 decomp 社区公开的常态（见 §4.2）。**但这条只对「非逐行对应」的实现成立**：
若某文件其实是反编译器输出**仅做格式化**（与指令一一对应），按 §2-F 判 ❌。
风险要说清：**「反编译源码是否构成衍生作品」在商业游戏上从未被法院检验过**（[B 报告](../kb/reports/B-完整反编译路线调研.md) 已有此结论），
所以这是**有判例支撑但未被直接检验**的灰色地带。[推断]

### 3.2 「逐条照抄的 `.s`」为什么不行

`splat` 的全量反汇编、`auto_match_stub.py` 逐条照抄生成的 `.s`，是**同一表达的机械转录**（指令、寄存器、立即数一一直录），
没有任何转换性。判例对此的表述很直接：Sega 称反汇编是 "wholesale copying"（977 F.2d at 1527）；
Atari 称 "Even for works warranting little copyright protection, **verbatim copying is infringement**."（975 F.2d at 843）。
而 Sega / Connectix 的合理使用保护的是**为逆向工程所必需的中间复制**，**不等于**可以把转录结果发行给公众：
Sega 明确 "does not, of course, insulate Accolade from a claim of copyright infringement with respect to its finished products."（at 1527–28），
Connectix 的立足点是 "none of the Sony copyrighted material was copied into, or appeared in, Connectix's final product."（203 F.3d at 601）。
⇒ 本项目因此把 `routebjp/src/matched/*.s`（145 个）判为 ❌（[O-24](../kb/OPEN-ISSUES.md)），
`routebjp/asm/`（splat 树）继续由 `.gitignore` 拦住。

**社区证据（不要声称「社区禁止 `.s`」——那是不准确的）**：人工**维护**的 `.s` 在社区是**接受甚至必需**的
（`sm64` 的 `asm/` 被 README 定义为 "handwritten assembly code"、`oot` 有 43 个手写 `.s`、`pokemonsnap` 的 `ultralib` 有 54 个）；
被普遍排除的是**机器生成物**：`dtk-template` README「No game assets are committed to the repository」、
`tww` CONTRIBUTING 明确拒收 "directly copy-pasted from Ghidra" 的贡献、`mm`/`pokemonsnap` 的 `.gitignore` 直接忽略 `asm/`、
`DKR-R` 的 `ASSET_POLICY.md`「Never commit or distribute … extracted … material」。我们的判据正是「**机器生成 + 逐条照抄**」这一条，
而不是文件扩展名。[已核实，URL 见 §8]

### 3.3 路线 A（静态重编译）的逐条翻译产物仍不可公开

既有结论不变：静态重编译产物是原二进制的**逐条翻译**，合理使用地位**比模拟器更弱**，不能照搬 Connectix 判例
（[DECISIONS D-0004](../kb/DECISIONS.md) 理由、主报告 §8、[T4](../kb/reports/T4-移植案例与工程方案调研.md)）。
社区惯例同向：N64Recomp 一类项目**只发行工具与配置**，要求用户自备 ROM 在本地生成，从不发行重编译输出。
可公开的只有：重编译器/工具、配置、以及人工撰写的部分。

### 3.4 第三方材料不是「引用」而是「再分发」

社区 wiki 的整页备份、他人补丁包、汉化译文一旦入库，就是**再分发他人作品**（引用与链接才是安全做法）。
`docs/community-wiki/*`（14 个 pmwiki 备份）因此判为 ❌（[O-25](../kb/OPEN-ISSUES.md)）：本地研究保留、公开仓库只留
[SOURCES](../kb/SOURCES.md) 的引用与链接。

---

## 4. 依据

### 4.1 司法实务（美国判例为主）[已核实：引用与要旨均按下方 URL 核对]

| 判例 | 引用 | 判决要旨（与本政策相关的部分） |
| --- | --- | --- |
| **Sega Enterprises Ltd. v. Accolade, Inc.** | 977 F.2d 1510（9th Cir. 1992-10-20，1993-01-06 修正） | 反汇编以取得不受保护的功能要素，**作为法律问题**属合理使用；但明言合理使用**只覆盖中间复制**："does not, of course, insulate Accolade from a claim of copyright infringement with respect to its finished products."（at 1527–28）→ 支撑「为研究而反编译」正当，**不**支撑「发行转录结果」 |
| **Sony Computer Entertainment v. Connectix Corp.** | 203 F.3d 596（9th Cir. 2000-02-10） | 开发模拟器过程中的**中间复制**属合理使用；立足点是 "none of the Sony copyrighted material was copied into, or appeared in, Connectix's final product."（at 601）→ 中间产物 ≠ 可公开产物 |
| **Atari Games Corp. v. Nintendo of America Inc.** | 975 F.2d 832（Fed. Cir. 1992-09-10） | 反向工程本身可作为抗辩，但**仅限「理解」**；"This limited exception is not an invitation to misappropriate protectable expression."（at 842–43）；"Even for works warranting little copyright protection, verbatim copying is infringement."（at 843）→ 支撑 §2-F/G |
| **Google LLC v. Oracle America, Inc.** | 593 U.S. 1（2021）；141 S. Ct. 1183 | 只复制接口 declaring code、**自己写了全部 implementing code** → 转换性使用成立。法院明示 "we assume, for argument's sake, that the material was copyrightable" → 支撑 §2-E「功能性重实现可公开」，**不**支撑公开他人实现代码 |
| Micro Star v. FormGen（154 F.3d 1107，9th Cir. 1998） · Lewis Galoob v. Nintendo（964 F.2d 965，9th Cir. 1992） · Midway v. Artic Int'l（704 F.2d 1009，7th Cir. 1983） | — | 派生物**一旦固定并发行**，就走上独立的侵权路径（Micro Star 判发行地图档侵权；Galoob 之所以胜诉正因效果未固定）；**发行行为本身可被单独追诉**（Artic 销售加速板=帮助侵权）→ 支撑「内部使用 ≠ 可发表」 |

> **关键结论（必须写进任何对外说明）**：**美国没有任何判例正面判定「公开发表反编译清单/逐字转录」是合理使用**；
> 上述合理使用结论都以「复制是**中间性**的、成品不含原件材料」为前提。⇒「公开发表」在判例上是**未解决地带**，
> 不是受保护地带。[已核实（判决原文见 §8）] + [推断]

> **【引用纪律 · 不要再犯】** 网上（含 LLM 生成的内容）常把 Atari 案说成「法院认定复制 **10 字节** lockout 代码侵权」——
> 这是把任天堂的 lockout 程序名 **`10NES`** 误读成了「10 字节」。判决全文只出现 "the 10NES program"，**没有 "10 bytes"**。
> 引用时请用判决原句（"verbatim copying is infringement", 975 F.2d at 843），不要用这个数字神话。[已核实]
> 同理：Sega 案的合理使用是**中间复制**层面的结论（at 1527–28），不要引成「发行反编译产物合法」。

> 佐证（本项目已引用过的二次资料）：US Copyright Office 的 Sony v. Connectix 合理使用判例摘要
> <https://copyright.gov/fair-use/summaries/sony-connectix-9thcir2000.pdf>；Cornell LII 的 reverse engineering 条目
> <https://www.law.cornell.edu/wex/reverse_engineering>（见 [B 报告](../kb/reports/B-完整反编译路线调研.md) §来源）。

**美国以外**：**日本与欧盟的成文法对「把反编译所得信息提供给公众」有明确限制**（比美国法更硬 —— 美国法只是「未解决」）：

| 法域 | 条文（已按原文核对） | 对「发表」的含义 |
| --- | --- | --- |
| **日本** | 著作権法 **第 30 条の 4**（情報解析等）：「…必要と認められる限度において…利用することができる。**ただし、…著作権者の利益を不当に害することとなる場合は、この限りでない。**」<br>**第 47 条の 3**（旧 47 条の 2）：複製物の所有者が「**自ら**…実行するために必要と認められる限度において」複製できる<br>**第 47 条の 7**：依第 30 条の 4 作成之复制物，**「…思想若しくは感情を自ら享受し若しくは他人に享受させる目的のために公衆に譲渡する場合は、この限りでない」**（且可转让清单**不含**第 47 条の 3） | 解析（情報解析）本身有依据；但**向公众转让**受第 47 条の 7 但书与第 30 条の 4 但书双重限制，「把整份反编译源码发表」**没有安全港**。[已核实（e-Gov 条文原文）] |
| **欧盟** | 指令 **2009/24/EC 第 6(2) 条**：所获信息不得 (a) 用于互操作性以外目的；**(b) "to be given to others, except when necessary for the interoperability of the independently created computer program"**；(c) 用于开发/生产/销售**表达上实质相似**的程序。<br>第 5(3) 条只允许「加载/显示/运行过程中」观察研究（黑箱），第 6(3) 条要求不损害权利人正当利益 | **第 6(2)(b) 直接限制把反编译所得信息提供给他人** ⇒ 在欧盟，公开发表反编译源码属**明文受限**。[已核实（EUR-Lex 条文原文）] |
| **台湾** | 著作權法 **第 59 條**：合法重製物所有人「得因配合其所使用機器之需要，修改其程式，或因備用存檔之需要重製其程式。**但限於該所有人自行使用。**」<br>**第 65 條**：四要素合理使用（无反编译专门条款）<br>**第 80-2 條**：禁止破解/規避防盗拷措施，且「破解、破壞或規避防盜拷措施之設備、器材、零件、技術或**資訊**，未經合法授權不得製造、輸入、**提供公眾使用**或為公眾提供服務」；第 3 项列举豁免（含第 8 款「為進行還原工程者」） | 自用修改/備份有依据；**公开发表**无成文法依据；规避手段/信息的公开受 §80-2 限制（豁免条款对各款的适用范围本机未做判例级核实）。[已核实（条文原文，经 Wayback 官方页面）] |

⇒ 综合结论：**本政策采取 default-deny**；「可公开」的判定只覆盖 §2 明确列出的类别。

### 4.2 社区惯例（6 个顶级项目 HEAD 全树清点的结果）[已核实，URL 见 §8]

- **普遍公开**：人工撰写的 `src/**.c`/`.h`；**人工维护**的 `.s`（`sm64` 的 `asm/` 被 README 定义为 "handwritten assembly code"、`oot`/`mm` 各 43 个、`pokemonsnap` 的 `ultralib` 54 个）；
  符号表 / splits / 链接脚本 / `spec`（`oot`、`melee`、`pokemonsnap`）；资产**抽取描述**（`oot` 的 `assets/xml/**` 763 个、`tww` 的 2457 个资源 `.h`）；构建配置与 `configure.py`。
- **普遍不公开**：原版 ROM/ISO/DOL（各 README 一律写「自备 ROM」）；splat 生成的 `asm/`、`data/`（`mm`、`pokemonsnap` 直接 `.gitignore`）；
  `m2c`/`ctx.c`/`*.s.c` 等机器输出（`melee`）；从 ROM 抽出的图形/音频/文本二进制（`oot`、`tww`、`pokemonsnap`）。
- **惯例的边界是模糊的（必须如实写，别当成铁律）**：
  - `zeldaret/oot` **公开入库了 SGI IDO 5.3/7.1 编译器二进制**（34 个，附 SGI Freeware Legal Notice）—— 故「专有工具链一律不入库」**不是**社区普遍事实；
  - `n64decomp/sm64` 提交了 24 个 RSP 微码 `.bin` 与 193 个动画数值表 `assets/anims/*.inc.c` —— 机器/原版派生数据也有被公开的先例；
  - 因此本政策对 H/I 类的 ❌ 是**保守取向**，依据是「本方不掌握再分发授权」而不是「社区都这么做」。
- **进度报告**：惯例是 **CI 生成 → `upload-artifact` → 不入库**（`melee`、`pokemonsnap`、`tww`；`pokemonsnap` 的 `.gitignore` 直接忽略 `/report.json`）。
- **可引用的成文依据（社区没有单点上位规定，但有这些）**：`encounter/dtk-template` README「**No game assets are committed to the repository**」；
  `zeldaret/tww` CONTRIBUTING 明确拒收 "directly copy-pasted from Ghidra" 的贡献；`ThatGuyMcd/DKR-R` 的 `docs/ASSET_POLICY.md`
  （「Never commit or distribute: … Extracted textures, palettes, models, maps, game fonts, audio or cutscenes」+「Allowed: Extraction schemas, offsets and declarative metadata」）。
- **与本项目最接近的先例**：decomp.dev 上的 **26 个 PS2 项目**——公开仓库 + `report.json` artifact，原版镜像与工具链在私有侧
  （私有伴生仓库 / 私有 GHCR 镜像 / self-hosted runner 三种做法，见 [R15](../kb/reports/R15-路线B-decomp.dev发表方案.md) §3.4）。
- **归纳**：通行的判据是「**人工撰写 + 声明式配置进仓库；原版二进制与从它机械生成的东西不进仓库**」，而不是按扩展名或目录名。

---

## 5. 执行（机器防线）

> **2026-10-05 修订（[D-0012](../kb/DECISIONS.md)）**：下表的「私有仓库内防线」**已在私有仓库侧删除**——
> `make check-ignore` / `make check-public` / pre-commit 的版权拦截都不再存在（私有仓库不设入库限制）。
> 防线前移到**导出侧**：导出清单 + 公开仓库 CI（[CI.md](CI.md) 的 `validate` 作业）。
> 原表保留为历史口径（删除线），引用时不要当成现行命令。

| 防线 | 作用 | 命令 |
| --- | --- | --- |
| ~~`.gitignore` 断言~~ | ~~不许被 add 进来（含行尾注释静默失效的检测）~~ | ~~`make check-ignore`~~ |
| ~~**publication 断言**~~ | ~~已入库（`git ls-files`）的文件不得命中不可公开类别~~ | ~~`make check-public`~~ |
| ~~pre-commit 钩子~~ | ~~提交前跑上述两项 + 文档一致性~~ | ~~`make install-hooks`~~ |
| **导出清单校验**（现行） | 公开树文件 ↔ 清单双向比对 + ❌ 类扫描 | 公开仓库 CI `validate`（[CI.md](CI.md) §2.1） |
| 发表前自查 | 见 §5.2 清单 | — |

### 5.1 新增一个「可公开」文件的流程

1. 按 §1 三问判定为 ✅（存疑先登记 OPEN-ISSUES）；
2. 把它加进**导出清单**（不是改私有仓库的 `.gitignore`）；~~若它当前被 `.gitignore` 忽略 → 改 `.gitignore`（注释独占一行）并同步 `guards.json` 的 `must_ignore` / `must_not_be_ignored`~~（2026-10-05 随 D-0012 作废）；
3. 跑导出器生成公开树，并等公开仓库 CI `validate` 转绿（~~`make check-ignore && make check-public`~~ 已删除）；
4. 精确 `git add <路径>` 提交（**禁止** `git add -A`）。

### 5.2 发表（推公开仓库 / 上 decomp.dev）前清单

- [ ] ~~`make check` 全绿（含 `publication`：`known_debt` 应为 0）~~ → 2026-10-05 起改为：**导出器跑通 + 公开仓库 CI `validate` 绿**（[CI.md](CI.md)）
- [ ] `git ls-files` 里没有 ❌ 类别：`out/binaries|ghidra`、`routeb(jp)/asm|build`、`*.iso`、`*.rom`、专有工具链、密钥
- [ ] `routebjp/src/matched/*.s`（逐条转录）**由导出器排除**（[O-24](../kb/OPEN-ISSUES.md)）；
      `docs/private/community-wiki/*`（第三方，原 `docs/community-wiki/*`）**已按 [D-0012](../kb/DECISIONS.md) 移出索引并忽略**（[O-25](../kb/OPEN-ISSUES.md)）
- [ ] 报告/文档里没有把「可公开」误读成「游戏数据可以公开」的表述（§3.3）
- [ ] 用户已明确同意「对外发布」这一次动作

---

## 6. 存量债务（政策生效即产生，必须清零后才能公开）

> **2026-10-05 更新（[D-0012](../kb/DECISIONS.md)）**：两条债务在**私有仓库内不再是债务**（不设入库限制）；
> 它们变成**导出器必须排除**的条目，由公开仓库 CI 兜底。下表「现状」列按新口径改写，原口径见删除线。

| 债务 | 数量 | 现状 | 迁移方案 |
| --- | --- | --- | --- |
| [O-24](../kb/OPEN-ISSUES.md)：`routebjp/src/matched/*.s`（逐条照抄的桩） | 145 | ~~已在库；`make check-public` 记 WARN~~ → **私有仓库内合规（D-0012）；导出器必须排除** | 生成器 `auto_match_stub.py` 可公开；生成物改由**私有伴生仓库的原版 ELF** 在本地/CI 重新生成，并加入导出排除清单；`build_hybrid.sh` 增加前置生成步骤；跑 `make routebjp-verify` 确认棘轮不变 |
| [O-25](../kb/OPEN-ISSUES.md)：`docs/private/community-wiki/*`（第三方 pmwiki 备份，原 `docs/community-wiki/*`） | 14 | ~~已在库；`make check-public` 记 WARN~~ → **已移入 `docs/private/` 并 `git rm --cached` + `.gitignore`（2026-10-05，轮次 42）**；导出器排除 | 公开仓库只保留 [SOURCES](../kb/SOURCES.md) 的引用链接 |

---

## 7. 未解决 / 风险（诚实记录）

| # | 项 | 状态 |
| --- | --- | --- |
| 1 | **美国无任何判例正面判定「公开发表反编译清单/转录」是合理使用**（Sega/Connectix 均以「中间复制 + 成品不含原件材料」为前提） | **[未解决]** 判例上属未解决地带 ⇒ 政策 default-deny |
| 2 | 「反编译源码是否构成衍生作品」在商业游戏上无判例 | **[未解决]** 政策只给出保守边界（[B 报告](../kb/reports/B-完整反编译路线调研.md) 同结论） |
| 3 | 日本第 30 条の 4 但书「不当に害する」在「公开发表反编译源码」情形下的适用无判例/官方指引；第 47 条の 7 但书的射程亦无判例 | **[未解决]** 条文已核对，结论按保守方向取 |
| 4 | 台湾著作權法 §80-2 第 3 项豁免对**第 2 项**（向公众提供规避信息）是否同样适用 | **[未核实]** 条文文义（「前二項規定…不適用之」）倾向适用，本机未做判例级核实；本政策仍按 ❌ 处理 |
| 5 | CJEU 判例要旨（SAS Institute C-406/10、Top System C-13/20） | **[未核实]** 仅有 CELEX 标识，EUR-Lex 本机曾返回空响应 |
| 6 | `decompme/compilers` 的 `ee-gcc` 再分发授权（仓库无 LICENSE） | **[未解决]** 见 [R15](../kb/reports/R15-路线B-decomp.dev发表方案.md) §9-2；本文按 ❌ 处理 |
| 7 | 反编译器草稿（`ghidra_draft` 类，1,033 个）是否都达到「人工语义加工、非逐行对应」标准 | **[⚠️ 逐案]** 发表前需抽查：命名/类型/控制流是否被真正恢复，而非整段未改写的反编译输出（§2-E/§3.1） |
| 8 | 「可公开」的判定仍可能有争议个案 | **[机制]** 存疑即 ⚠️ 默认不公开 + OPEN-ISSUES 登记，由用户裁定 |

---

## 8. 来源

1. [DECISIONS D-0008](../kb/DECISIONS.md)（本政策的决策记录；修订 D-0004 第 3 条）与 [D-0004](../kb/DECISIONS.md)
2. [R15 · 路线 B 成果在 decomp.dev 上发表](../kb/reports/R15-路线B-decomp.dev发表方案.md) —— 站点机制、26 个 PS2 先例、我方实测
3. [B · 完整反编译路线调研](../kb/reports/B-完整反编译路线调研.md) —— 本项目已做的判例与许可调研（Connectix / Accolade / Cornell LII）
4. [T4 · 移植案例与工程方案调研](../kb/reports/T4-移植案例与工程方案调研.md) —— 静态重编译的合理使用地位分析
5. 判例引用与判决原文（2026-10-04 核对；`law.resource.org` 为公开判例汇编全文）：
   Sega 977 F.2d 1510 <https://law.resource.org/pub/us/case/reporter/F2/977/977.F2d.1510.92-15655.html> ·
   Atari 975 F.2d 832 <https://law.resource.org/pub/us/case/reporter/F2/975/975.F2d.832.91-1293.html> ·
   Connectix 203 F.3d 596 <https://law.resource.org/pub/us/case/reporter/F3/203/203.F3d.596.99-15852.html> ·
   Micro Star 154 F.3d 1107 <https://law.resource.org/pub/us/case/reporter/F3/154/154.F3d.1107.html> ·
   Galoob 964 F.2d 965 <https://law.resource.org/pub/us/case/reporter/F2/964/964.F2d.965.91-16205.html> ·
   Midway v. Artic 704 F.2d 1009 <https://law.resource.org/pub/us/case/reporter/F2/704/704.F2d.1009.82-1607.html> ·
   Google v. Oracle <https://www.law.cornell.edu/supremecourt/text/18-956>
   （另有维基百科条目用于交叉核对引用号：Sega / Connectix / Google / Atari）
6. **成文法原文（本机逐条核对）**：17 U.S.C. §107 <https://www.law.cornell.edu/uscode/text/17/107> ·
   DMCA §1201 <https://www.law.cornell.edu/uscode/text/17/1201> ·
   日本著作権法 <https://laws.e-gov.go.jp/law/345AC0000000048>（第 30 条の 4 / 47 条の 3 / 47 条の 7 经 e-Gov API 取全文）·
   欧盟指令 2009/24/EC <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024>（第 6(2)(b) 原文核对）·
   台湾著作權法 <https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=J0070017>（经 Wayback 官方页面核对第 59 / 65 / 80-2 条）
7. <https://copyright.gov/fair-use/summaries/sony-connectix-9thcir2000.pdf> · <https://www.law.cornell.edu/wex/reverse_engineering>
8. **社区惯例的一手证据（2026-10-04 清点 HEAD 全树）**：
   <https://github.com/zeldaret/oot>（`.gitignore` / README L51 / `tools/ido5.3_compiler`）·
   <https://github.com/zeldaret/mm>（`.gitignore` 含 `asm/`、`data/`）·
   <https://github.com/doldecomp/melee>（`.gitignore` 含 `*.m2c`、`ctx.c`、`/tools/mwcc_compiler`；`build.yml` upload-artifact）·
   <https://github.com/n64decomp/sm64>（`asm/` = handwritten assembly；`lib/PR/**/*.bin`、`assets/anims/*.inc.c` 为反例）·
   <https://github.com/ethteck/pokemonsnap>（`.gitignore` 含 `asm/`、`assets/`、`/report.json`）·
   <https://github.com/zeldaret/tww>（CONTRIBUTING 拒收 Ghidra 直抄；README「does not contain any game assets or assembly whatsoever」）·
   <https://github.com/encounter/dtk-template>（README「No game assets are committed to the repository」）·
   <https://github.com/ThatGuyMcd/DKR-R/blob/main/docs/ASSET_POLICY.md>（成文的资产政策）
9. [guards.json](../kb/guards.json) `publication` 块（机器断言）· [tools/check_docs.py](../../tools/check/check_docs.py) `check_publication()`
