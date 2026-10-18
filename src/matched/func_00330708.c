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

M2C_UNK LibcString_8(s8 *, M2C_UNK, M2C_UNK);       /* extern */
extern s32 D_0082AD0C;
extern s8 D_00A34D10;
extern s8 D_00A34E50;
extern s8 D_00A35050;

void func_00330708(void) {
    s32 temp_v0;
    s32 var_s1;
    s8 *var_s0;
    void *temp_v0_2;

    temp_v0 = D_0082AD0C - 1;
    D_0082AD0C = temp_v0;
    if (temp_v0 == 0) {
        var_s1 = 0x27;
        var_s0 = &D_00A34D10;
        do {
            temp_v0_2 = M2C_FIELD(var_s0, void **, 0);
            if (temp_v0_2 != NULL) {
                M2C_FIELD(temp_v0_2, M2C_UNK (**)(s32), 0x14)(M2C_FIELD(var_s0, s32 *, 4));
            }
            var_s1 -= 1;
            var_s0 += 8;
        } while (var_s1 >= 0);
        LibcString_8(&D_00A34D10, 0, 0x140);
        LibcString_8(&D_00A34E50, 0, 0x200);
        LibcString_8(&D_00A35050, 0, 9);
        D_00A35050 = 0;
    }
}
