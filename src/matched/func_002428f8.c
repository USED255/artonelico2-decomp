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

int baseelf_153();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0011299c();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0011e440();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0013df00();            /* 参数个数未知，按 K&R 空原型声明 */
int func_0013e2fc();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char D_00472DC8[];

void func_002428f8(s32 arg0, void *arg1) {
    s32 var_t4;
    u8 temp_a0;
    void *temp_t6;
    void *var_t5;

    func_0013df00(arg1);
    func_0013e2fc((void *)((uintptr_t)arg1 + 0x28));
    temp_a0 = *(u8 *)((uintptr_t)arg1 + 0x28);
    if (temp_a0 == 0) {
        return;
    }
    func_0011299c(temp_a0);
    func_0011e440(&D_00472DC8, 1, 0xC, -1);
    var_t4 = 0;
    var_t5 = (void *)((uintptr_t)arg1 + 0x20);
    do {
        if (*(s16 *)((uintptr_t)var_t5 + 0xE) != -1) {
            temp_t6 = (void *)((uintptr_t)&D_00472DC8 + (uintptr_t)(var_t4 * 0x90));
            *(s16 *)((uintptr_t)temp_t6 + 0x98) = 0;
            *(s16 *)((uintptr_t)temp_t6 + 0x38) = 0;
            *(u16 *)((uintptr_t)temp_t6 + 0x68) = (u16)*(s16 *)((uintptr_t)var_t5 + 0xE);
        }
        var_t4 += 1;
        var_t5 = (void *)((uintptr_t)var_t5 + 2);
    } while (var_t4 < 4);
    baseelf_153(arg0, &D_00472DC8,
                *(s16 *)((uintptr_t)arg1 + 0x4) + *(s32 *)((uintptr_t)arg1 + 0x4C),
                *(s16 *)((uintptr_t)arg1 + 0x6) + *(s32 *)((uintptr_t)arg1 + 0x50));
    func_0011299c(0x80U);
}
