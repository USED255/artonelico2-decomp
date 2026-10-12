/* Fixed preamble for m2c drafts (types and our own shim) */
typedef signed char s8;      typedef unsigned char u8;
typedef short s16;           typedef unsigned short u16;
typedef int s32;             typedef unsigned int u32;
typedef long long s64;       typedef unsigned long long u64;
typedef float f32;           typedef double f64;
typedef unsigned char undefined1;  typedef unsigned short undefined2;
typedef unsigned int undefined4;   typedef unsigned long long undefined8;
typedef unsigned char byte;  typedef unsigned char code;
typedef unsigned int uint;
/* m2c uses s128/u128 for 128-bit integers (lq/sq and MMI). GCC vector mode
   types make assignment and address-of work. */
typedef int s128 __attribute__((mode(V4SI)));
typedef int u128 __attribute__((mode(V4SI)));   /* Same type as s128. This avoids type errors on s128/u128 assignment. */
typedef int          s64_ __attribute__((unused));
#define NULL 0
/* m2c writes `sp` ($29) directly when it cannot turn a stack access into a local
   variable. This placeholder declaration lets the file compile at least. objdiff
   decides the match. Such drafts usually do not match, but they cost nothing extra. */
extern unsigned char *sp;
/* Common placeholder macros for m2c --valid-syntax. We define them here, so the
   output does not depend on headers outside the workspace. */
typedef s32 M2C_UNK;   typedef s8  M2C_UNK8;
typedef s16 M2C_UNK16; typedef s32 M2C_UNK32; typedef s64 M2C_UNK64;
#define M2C_FIELD(expr, type_ptr, offset) (*(type_ptr)((s8 *)(expr) + (offset)))
#define M2C_BITWISE(type, expr) ((type)(expr))
#define M2C_LIKELY(x) (x)
#define M2C_UNLIKELY(x) (x)

typedef unsigned char       uint8_t;
typedef signed char         int8_t;
typedef unsigned short      uint16_t;
typedef short               int16_t;
typedef unsigned int        uint32_t;
typedef int                 int32_t;
typedef unsigned long long  uint64_t;
typedef long long           int64_t;
typedef unsigned int        uintptr_t;
typedef int                 intptr_t;
typedef unsigned int        size_t;
typedef int                 ssize_t;
typedef int                 ptrdiff_t;
typedef int                 BOOL;

int baseelf_168();            /* 参数个数未知，按 K&R 空原型声明 */
int baseelf_169();            /* 参数个数未知，按 K&R 空原型声明 */
int baseelf_170();            /* 参数个数未知，按 K&R 空原型声明 */
int baseelf_171();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002457ec();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0024582c();            /* 参数个数未知，按 K&R 空原型声明 */
int func_00245878();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002458c4();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char func_002A1238[];
extern unsigned char func_002A13A8[];
extern unsigned char func_002A18E4[];
extern unsigned char func_002A1A00[];
extern unsigned char func_002a0d38[];
extern unsigned char func_002a0e68[];
extern unsigned char func_002a0e9c[];
extern unsigned char func_002a107c[];
extern unsigned char func_002a10a8[];
extern unsigned char func_002a125c[];
extern unsigned char func_002a12b8[];
extern unsigned char func_002a1770[];
extern unsigned char func_002a1954[];
extern unsigned char func_002a19a4[];
extern unsigned char func_002a19c8[];
extern unsigned char func_002a19e0[];

void func_002a1a20(void)
{
    unsigned long auStack_19e0[826];

    func_002457ec();
    func_00245878();
    auStack_19e0[0] &= ~(1ULL << 33);
    baseelf_168(auStack_19e0, auStack_19e0, 6,
                func_002a0d38, func_002a0e68,
                func_002a107c, func_002a0e9c);
    baseelf_169(auStack_19e0, func_002a10a8, func_002A1238);
    baseelf_169(auStack_19e0, func_002a125c, func_002a12b8);
    baseelf_169(auStack_19e0, func_002A13A8, func_002a1770);
    baseelf_169(auStack_19e0, func_002A18E4, func_002a1954);
    baseelf_169(auStack_19e0, func_002a19a4, func_002a19c8);
    baseelf_169(auStack_19e0, func_002a19e0, func_002A1A00);
    baseelf_170(auStack_19e0, 0);
    baseelf_171(auStack_19e0);
    func_002458c4();
    func_0024582c();
}
