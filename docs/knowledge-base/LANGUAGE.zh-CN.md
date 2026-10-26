# 匹配语言：C 还是 C++

[English](LANGUAGE.md) | [简体中文](LANGUAGE.zh-CN.md)

短答：匹配源码用 **C**。没有任何实测支持把游戏代码整体改成 C++。只有当一个翻译单元（TU）的
零售字节里出现「只有 C++ 前端才会生成」的产物时，那一个 TU 才可能需要 C++。

## 1. 判据

匹配看的不是哪种语言更好用，而是：**原 TU 的编译器产物能不能被再生**。

语言决定编译器在函数体之外**额外**生成什么：

| 产物 | 只有 C++ 前端会生成 | C 能否等价 |
| --- | --- | --- |
| vtable / `type_info` 数据 | 是 | 只能把数据按原地址落位 |
| 构造 / 析构、vptr 存储 | 是 | 能，手写 vptr 存储 |
| 多重继承的 `this` 调整 thunk | 是 | 能，手写汇编 |
| 异常表（`.eh_frame`、`.gcc_except_table`）与清理路径 | 是 | 基本不能：表内容必须逐字节一致 |
| RTTI 字符串、名字改编 | 是 | 不暴露符号名就不需要 |
| 模板实例化、隐式 inline | 是 | 通常能，量大时成本高 |

只要源码不用第一列，C 与 C++ 产出的对象就相同（下面有实测）。所以「用哪个语言」等于「原 TU 有
没有用到第一列」。

## 2. 实测

| 断言 | 测量 |
| --- | --- |
| 原版游戏代码是 C | 预览版的 assert 名单里 **313 个文件，313 个全部以 `.c` 结尾**（没有 `.cpp`、`.cc`、`.cxx`）。日版零售只留下 4 个字面文件名（`CVLQuaternion.c`、`Db.c`、`Hig.c`、`HigZsort.c`），全是 `.c`。 |
| 零售二进制没有 C++ 运行时 | 在载荷里扫 `__cxa`、`__gxx`、`__builtin_new`、`operator new`、`operator delete`、`bad_alloc`、`type_info`、`libstdc++`、`std::`、`__gnu_cxx`，**全部 0 命中**；51 处 `_Z` 命中全是资产文件名。 |
| 异常展开只在 SDK 库区 | `.eh_frame` 只有 1,220 字节，**32 个 FDE** 全在 SDK `libgcc`/`libc` 地址波段；引擎自有的 `baseelf_*`、ERX 槽位一个 FDE 都没有。没有 `.gcc_except_table` 节，`.ctors`/`.dtors` 只有 C 运行时那一条。 |
| 这里 C 与 C++ 产出相同 | 同一份探针用 `ee-gcc -O2`、`ee-g++ -O2`、`ee-g++ -O2 -fno-exceptions -fno-rtti` 编译，**三档 `.text` 哈希相同**。符号名不同；C++ 默认档多一个 0x38 字节的 `.eh_frame`，加上面两个旗标就消失。 |

探针很小、可复现：写一个文件，含一个算术函数、一个循环、一次经函数指针的间接调用、一个
`switch`，分别用两种前端编译后比 `.text` 字节。结论只对**这个**编译器成立，所以在你的副本上实测。

## 3. 什么时候一个 TU 可以切 C++

触发条件：该 TU 的零售字节里出现上表第一列的产物：异常表、RTTI、按原地址落位的 `linkonce`
vtable 段、编译器合成的 thunk、静态局部 guard。

真遇到时，切**那个 TU**，不是整个项目。同编译器项目的已知配方是 `ee-g++ 3.2` 加
`-x c++ -fno-exceptions -fno-rtti -fpermissive -ffunction-sections`。旗标到位后，单 TU 的工作是：

1. `src/matched/` 的扫描同时接受该 TU 的 C++ 扩展名；
2. 编译器映射与「源文件到目标文件」的命名加一个 C++ 档；
3. 把改编后的符号名映射到 per-symbol 段名；
4. 新增的段（`.eh_frame`、`.gnu.linkonce.*`）不得改变载荷。

这些都与「静态数据按原地址落位」耦合，而后者在本项目仍是未解决项。成本是真实的；只有产物真实
存在时收益才存在。

## 4. 什么会改变这个结论

- 在引擎的 TU 里发现编译器生成的 C++ 产物（引擎地址波段里出现异常表或 vtable）。32 个 FDE 全在
  SDK 波段，所以游戏代码里目前没发现。
- 某个函数在 C 下匹配不上，且原因不是源码形状。切语言之前，先确认原因不是
  [KNOWN-BLOCKERS.zh-CN.md](KNOWN-BLOCKERS.zh-CN.md) 里的陷阱。

## 5. 另见

- [compiler/README.zh-CN.md](compiler/README.zh-CN.md) —— 编译器怎么做，以及为什么源码形状比语言
  更重要。
- [compiler/CROSS-2.96.zh-CN.md](compiler/CROSS-2.96.zh-CN.md) —— 构建里的第二个编译器。
- [TOOLCHAIN.zh-CN.md](TOOLCHAIN.zh-CN.md) —— 哪个编译器编了什么。
