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

int func_0010c8c4();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0012c2dc();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char D_00561710[];
extern unsigned char D_00AD8000[];

void func_0012a77c(s32 arg0) {
    s32 i;
    for (i = 0; i < 0x1A; ++i) {
        s32 tmp = arg0 * 0x7C;
        s16 val = *(s16 *)((u8 *)D_00561710 + (tmp + i) * 2);
        if ((u32)(val - 0x16D9) < 0x709U) {
            func_0010c8c4(val);
        }
    }
    func_0012c2dc(&D_00AD8000, arg0);
}
