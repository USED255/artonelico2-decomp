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

int func_0011f1ac();            /* 参数个数未知，按 K&R 空原型声明 */
int func_00193d28();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0025446c();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char D_007F3F50[];

void func_00254a84(s32 arg0, void *arg1) {
    s32 s0 = 0;
    s16 s1;
    s32 s2 = arg0;
    void *s3 = arg1;
    s32 t6 = *(s32 *)((u8 *)s3 + 0x960);
    t6 = t6 * 12;
    s1 = *(s16 *)(D_007F3F50 + t6);
    do {
        s32 offset = s0 * 12;
        s16 *p = (s16 *)(D_007F3F50 + offset);
        if (*p == s1) {
            s16 valA = *(s16 *)((u8 *)p + 0xA);
            if (valA >= 0 && func_00193d28(valA) != 2) {
                func_0025446c(s2, s3, s0);
            }
        }
        s0 += 1;
    } while (s0 < 0x1A);
    s32 *cnt_ac = (s32 *)((u8 *)s3 + 0xAAC);
    if (*cnt_ac > 0) {
        (*cnt_ac)--;
        if (*cnt_ac == 0) {
            func_0011f1ac((void *)((u8 *)s3 + 0xA18));
        }
        return;
    } else {
        s32 *cnt_aa8 = (s32 *)((u8 *)s3 + 0xAA8);
        if (*cnt_aa8 > 0) {
            (*cnt_aa8)--;
        }
        return;
    }
}
