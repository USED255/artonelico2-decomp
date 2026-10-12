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

int func_0011299c();            /* 参数个数未知，按 K&R 空原型声明 */
int func_001129d8();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0013787c();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0013fec0();            /* 参数个数未知，按 K&R 空原型声明 */
int func_00144d4c();            /* 参数个数未知，按 K&R 空原型声明 */
int func_00238dbc();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0024f1ec();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0024f364();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0024f8b0();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0024ffd0();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0027cd10();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char jtbl_0097B008[];

void func_00236a00(undefined8 param_1, undefined2 *param_2) {
    undefined8 s0 = param_1;
    undefined2 *s1 = param_2;
    undefined8 uVar1;
    signed short val;
    
    uVar1 = func_001129d8();
    func_0013787c(s0);
    val = *s1;
    switch (val) {
        case 0:
            func_0024ffd0(s0, s1 + 0xb44);
            break;
        case 1:
            func_0024ffd0(s0, s1 + 0xb44);
            func_0013fec0(s0);
            func_00144d4c(s0, s1 + 0x206);
            break;
        case 3:
            func_0013fec0(s0);
            func_0024ffd0(s0, s1 + 0xb44);
            func_0024f1ec(s0, s1 + 0xb7c);
            break;
        case 5:
            func_0024ffd0(s0, s1 + 0xb44);
            func_0013fec0(s0);
            func_0024f364(s0, s1 + 0xb96);
            break;
        case 7:
        case 0xf:
            func_0024f8b0(s0, s1 + 0xb1a);
            break;
        case 8:
            func_0024ffd0(s0, s1 + 0xb44);
            func_0024f8b0(s0, s1 + 0xb1a);
            goto D_00236B0C;
        case 9:
        case 0xb:
        case 0xc:
        case 0xd:
            func_0024ffd0(s0, s1 + 0xb44);
            func_00238dbc(s0, s1 + 0xb60);
            D_00236B0C:
            func_0013fec0(s0);
            break;
        case 0xe:
            func_0024ffd0(s0, s1 + 0xb44);
            func_00238dbc(s0, s1 + 0xb60);
            func_0013fec0(s0);
            func_0027cd10(s0, s1 + 0x63c);
            break;
        case 0x10:
            func_0024f8b0(s0, s1 + 0xb1a);
        case 2:
        case 4:
        case 6:
        case 0x11:
        case 0x12:
            func_0024ffd0(s0, s1 + 0xb44);
            goto D_00236B0C;
    }
    func_0011299c(uVar1);
    return;
}
