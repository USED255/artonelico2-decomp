# agent 技能 —— 用手册攻一个匹配 diff

[English](AGENT-SKILL.md) · [手册索引](README.md) · [laws](LAWS.md) · [诊断流程](DIAGNOSTICS.zh-CN.md) · [杠杆表](FIELD-GUIDE.zh-CN.md)

本页是自动化 agent（或赶时间的人）的入口，只干一件事：把不对的匹配 diff 变成能移动它的源改动。它刻意很短：手册是参考，这里只是循环。

## 硬纪律

1. **绝不改构建**。模型是只读的：不加编译 flag、不改 `source_flags.tsv`、不改构建脚本。若某个杠杆看起来非改不可，停下来上报。
2. **只有 100.0 算匹配**。启发式的改善不是结果。
3. **绝不写无锚点的强断言**。关于编译器行为的每句话，要么是 `T1`（源码 + 二进制锚点 + 行为），要么是 `T2`/`T3`，否则不写。别凭记忆——用 `laws-query.py` 查。
4. **发布物里不含游戏内容**。锚点是编译器内部符号、地址、行号与常量。
5. **记录被推翻的结论**。某条 law 把你带错了，就在用它的同一处写清楚。

## 循环

```sh
# 0. diff 到底在说什么？
#    按这个顺序读：控制流 -> 指令形状 -> 寄存器分配 -> 栈。
#    匹配率低于约 80% 属于结构问题：改写 C，不要问模型。

# 1. 差异归哪个 pass？
python3 tools/compiler/ee-gcc-passdiff.py candidate.c variant.c

# 2. 编译器在那个 pass 怎么做？
python3 tools/compiler/laws-query.py pass 23.greg
python3 tools/compiler/laws-query.py find allocation

# 3. 哪种改动能移动它？
python3 tools/compiler/laws-query.py guide frame
python3 tools/compiler/laws-query.py guide "live range"

# 4. 出厂编译器在决策点**实际**怎么做？
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" symbol allocno_compare --disasm 64
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" struct allocno
python3 tools/compiler/ee-gcc-anchor.py --cc1 "$CC1" const 0x821e360 --bytes 8

# 5. 复测。没移动读数的杠杆不是杠杆。
```

## 读一条 law 时看什么

* `tier` 决定可信度：`T1` 表示那段代码已在出厂 `cc1` 里定位到。
* `source anchor` 的行号是 **mainline**，**不可**直接搬运（[L-EE-006](LAWS.md#l-ee-006--line-numbers-are-not-portable-between-trees)）。要真实行号，自己锚。
* `receipt` 是测了什么，`scope` 是覆盖到哪。泛化前两个都要读。
* `falsifies` 是这条 law 取代的说法。这里几乎每条都取代了一个「合理但错误」的信念。

## 不要做

* 不要只看反汇编就推断寄存器分配。用 dump：编译器会印出自己的决定。
* 不要把 `24.postreload` 的重载簿记当成寄存器引用，它会虚高使用次数。
* 不要跨不同 TU 布局直接比对象，先归一化绝对地址与跳转表。
* 不要指望更低的 `-O`、不同的 `-G` 或 2.96 构建能复现 3.2 的行为：pass 编号不同，2.96 在本项目只编 CRI 中间件。
* 不要把着色模型报告成「已建模」。当前状态见 [L-EE-018](LAWS.md#l-ee-018--global-allocation-preference-first-then-the-lowest-register-left-after-two-passes-that-first-avoid-registers-other-allocnos-prefer)：
  实测规则复现留出集 **46.5%**（此前启发式 34.3%、按 mainline 写的重放 9.1%），把动态冲突集换成真值则 **82.7%**。
  已试并否证两条杠杆（旋转起点、活跃区间占用集）。新增规则时**同时**测端到端与 oracle 上下文：
  端到端涨但 oracle 下跌的，是在补偿模型自身的误差，不是在建模编译器。

## 回填

手册是版本化的，无人值守的 agent 应当把它改得更好：

1. 发现手册没有的机制：往 `laws.json` **和** `LAWS.md` 各加一条（只改一边数据校验会红），带 `source_anchor`、`binary_anchor`、`receipt`、`scope`。
2. 发现能移动读数的杠杆：写进 `FIELD-GUIDE.md`，附改动前后的数字。
3. 推翻了某条 law：把推翻记录写在该条上，并记进研究仓库的踩坑台账。
4. 收工前跑 `python3 tools/check/test_compiler_laws.py`。它强制分级前置条件，并在本机有 `cc1` 时逐条复核二进制锚点。
