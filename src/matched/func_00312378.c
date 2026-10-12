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



void func_00312378(void *arg0) {
    register int v1 asm("v1");
    register int a1 asm("a1");
    register int v0 asm("v0");
    v1 = -1;
    a1 = 1;
    v0 = 3;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x59) = a1;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x38) = v0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x00) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x04) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x08) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x0C) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x10) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x14) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x18) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x1C) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x20) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x24) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x28) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x2C) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x30) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x34) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x3C) = a1;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x40) = a1;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x44) = a1;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x48) = 0;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x4C) = 0;
    *(volatile int16_t *)((unsigned char *)arg0 + 0x50) = v1;
    *(volatile int16_t *)((unsigned char *)arg0 + 0x52) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x54) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x55) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x56) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x57) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x58) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x5A) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x5B) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x5C) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x5D) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x5E) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x5F) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x64) = v1;
    *(volatile int32_t *)((unsigned char *)arg0 + 0x68) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x60) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x61) = 0;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x62) = v1;
    *(volatile uint8_t *)((unsigned char *)arg0 + 0x63) = v1;
}
