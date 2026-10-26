# Matching language: C or C++

[English](LANGUAGE.md) | [简体中文](LANGUAGE.zh-CN.md)

Short answer: the matched source is **C**. No measurement supports converting the game code to
C++ as a whole. A single translation unit may need C++ only if the retail bytes contain an
artefact that only the C++ front end generates.

## 1. The criterion

Matching is not about which language is nicer. The question is: **can the compiler product of the
original translation unit be regenerated?**

The language decides what the compiler generates *in addition* to the function body:

| Artefact | Only the C++ front end generates it | Can C reproduce it |
| --- | --- | --- |
| vtable / `type_info` data | yes | only by writing the data at its exact address |
| constructors, destructors, vptr stores | yes | yes, by writing the vptr stores by hand |
| multiple-inheritance `this`-adjusting thunks | yes | yes, as hand-written assembly |
| exception tables (`.eh_frame`, `.gcc_except_table`) and cleanup paths | yes | practically no: the table content must match byte for byte |
| RTTI strings, name mangling | yes | not needed if no symbol name is visible |
| template instantiation, implicit inline | yes | usually, but the cost grows with the count |

If the source does not use the first column, C and C++ produce the same object (measured below).
So "which language" reduces to "did the original translation unit use an artefact from the first
column".

## 2. The measurements

| Claim | Measurement |
| --- | --- |
| The original game code is C | The preview build's assert list names **313 files, and all 313 end in `.c`** (no `.cpp`, `.cc` or `.cxx`). The Japanese retail executable keeps four literal source names (`CVLQuaternion.c`, `Db.c`, `Hig.c`, `HigZsort.c`), all `.c`. |
| The retail binary has no C++ runtime | Scanning the payload for `__cxa`, `__gxx`, `__builtin_new`, `operator new`, `operator delete`, `bad_alloc`, `type_info`, `libstdc++`, `std::`, `__gnu_cxx` finds **zero** hits. The 51 `_Z` hits are all asset file names. |
| Exceptions exist only in the SDK library band | `.eh_frame` is 1,220 bytes and holds **32 FDEs**, all inside the SDK `libgcc`/`libc` address band. No engine function (`baseelf_*`, ERX slot) has an FDE. There is no `.gcc_except_table` section and `.ctors`/`.dtors` hold only the C runtime entry. |
| C and C++ produce the same code here | Compiling one probe with `ee-gcc -O2`, `ee-g++ -O2` and `ee-g++ -O2 -fno-exceptions -fno-rtti` produces **three identical `.text` hashes**. The symbol names differ; the C++ default build adds one 0x38-byte `.eh_frame`, which the flags above remove. |

The probe is small and reproducible. Write a file with one arithmetic function, one loop, one
indirect call through a function pointer and one `switch`, then compile it both ways and compare
the `.text` bytes. The claim is about *this* compiler, so measure it on your copy.

## 3. When a translation unit may switch to C++

Trigger: the retail bytes of that unit contain an artefact from the table above — an exception
table, RTTI, a `linkonce` vtable section at its exact address, a compiler-generated thunk, or a
static-local guard.

If that happens, switch **that unit**, not the project. The known recipe from a same-compiler
project is `ee-g++ 3.2` with `-x c++ -fno-exceptions -fno-rtti -fpermissive
-ffunction-sections`. Once the flags are in place, the per-unit work is:

1. scan `src/matched/` for `.c` and also accept the C++ extension for that unit;
2. add a C++ entry to the compiler map, and to the source-to-object naming;
3. map the mangled symbol name to the per-symbol section name;
4. keep any new section (`.eh_frame`, `.gnu.linkonce.*`) from changing the payload.

All of that interacts with how static data lands at its exact address, which is a separate open
problem in this project. The cost is real; the benefit only exists if the artefact exists.

## 4. What would change this answer

- Finding compiler-generated C++ artefacts in an engine translation unit (an exception table or a
  vtable in the engine's address band). The 32 FDEs are all in the SDK band, so this has not been
  found in the game code.
- A function that cannot be matched in C for a reason other than the source shape. Before
  switching language, check that the reason is not one of the traps in
  [KNOWN-BLOCKERS.md](KNOWN-BLOCKERS.md).

## 5. See also

- [compiler/README.md](compiler/README.md) — what the compiler does, and why the source shape
  matters more than the language.
- [compiler/CROSS-2.96.md](compiler/CROSS-2.96.md) — the second compiler in this build.
- [TOOLCHAIN.md](TOOLCHAIN.md) — which compiler built what.
