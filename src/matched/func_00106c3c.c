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

extern unsigned char D_00A50548[];

void func_00106c3c(float param_1, float *param_2)
{
    unsigned char b0 = D_00A50548[66];
    if (b0 < 0x58) {
        float f0 = param_2[0];
        int diff = 0x58 - b0;
        float fdiff = (float)diff * param_1;
        f0 = f0 - fdiff;
        param_2[0] = f0;
    }
    b0 = D_00A50548[66];
    if (b0 > 0xA8) {
        float f0 = param_2[0];
        int diff = b0 - 0xA8;
        float fdiff = (float)diff * param_1;
        f0 = f0 + fdiff;
        param_2[0] = f0;
    }
    unsigned char b1 = D_00A50548[67];
    if (b1 < 0x58) {
        float f0 = param_2[1];
        int diff = 0x58 - b1;
        float fdiff = (float)diff * param_1;
        f0 = f0 - fdiff;
        param_2[1] = f0;
    }
    b1 = D_00A50548[67];
    if (b1 > 0xA8) {
        float f0 = param_2[1];
        int diff = b1 - 0xA8;
        float fdiff = (float)diff * param_1;
        f0 = f0 + fdiff;
        param_2[1] = f0;
    }
    unsigned char b2 = D_00A50548[65];
    if (b2 < 0x58) {
        float f0 = param_2[2];
        int diff = 0x58 - b2;
        float fdiff = (float)diff * param_1;
        f0 = f0 + fdiff;
        param_2[2] = f0;
    }
    b2 = D_00A50548[65];
    if (b2 > 0xA8) {
        float f0 = param_2[2];
        int diff = b2 - 0xA8;
        float fdiff = (float)diff * param_1;
        f0 = f0 - fdiff;
        param_2[2] = f0;
    }
}
