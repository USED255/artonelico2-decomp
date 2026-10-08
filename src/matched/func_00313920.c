/* m2c 草稿的固定前导（类型 + 我们自己的 shim） */
typedef signed char s8;      typedef unsigned char u8;
typedef short s16;           typedef unsigned short u16;
typedef int s32;             typedef unsigned int u32;
typedef long long s64;       typedef unsigned long long u64;
typedef float f32;           typedef double f64;
typedef unsigned char undefined1;  typedef unsigned short undefined2;
typedef unsigned int undefined4;   typedef unsigned long long undefined8;
typedef unsigned char byte;  typedef unsigned char code;
typedef unsigned int uint;
/* m2c 对 128 位整数（lq/sq、MMI）用 s128/u128；用 GCC 的向量模式类型让赋值/取址可用 */
typedef int s128 __attribute__((mode(V4SI)));
typedef int u128 __attribute__((mode(V4SI)));   /* 与 s128 同型，避免 s128/u128 互相赋值报类型错 */
typedef int          s64_ __attribute__((unused));
#define NULL 0
/* m2c 在无法把栈访问还原成局部变量时会直接写 `sp`（$29）；给个占位声明让它至少能编译，
   能不能对上交给 objdiff 判断（这类草稿通常对不上，但不占额外成本）。 */
extern unsigned char *sp;
/* m2c --valid-syntax 用到的通用占位宏（自己写，避免生成物依赖工作区外的头文件） */
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



void func_00313920(void *arg0) {
    register int v1 asm("v1") = -1;
    register int a1 asm("a1") = 1;
    register int v0 asm("v0") = 3;
    *(volatile s8 *)((u8 *)arg0 + 0x59) = a1;
    *(volatile s32 *)((u8 *)arg0 + 0x38) = v0;
    *(volatile s32 *)((u8 *)arg0 + 0x00) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x04) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x08) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x0C) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x10) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x14) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x18) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x1C) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x20) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x24) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x28) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x2C) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x30) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x34) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x3C) = a1;
    *(volatile s32 *)((u8 *)arg0 + 0x40) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x44) = a1;
    *(volatile s32 *)((u8 *)arg0 + 0x48) = 0;
    *(volatile s32 *)((u8 *)arg0 + 0x4C) = 0;
    *(volatile s16 *)((u8 *)arg0 + 0x50) = v1;
    *(volatile s16 *)((u8 *)arg0 + 0x52) = v1;
    *(volatile s8 *)((u8 *)arg0 + 0x54) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x55) = a1;
    *(volatile s8 *)((u8 *)arg0 + 0x56) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x57) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x58) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x5A) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x5B) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x5C) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x5D) = v1;
    *(volatile s8 *)((u8 *)arg0 + 0x5E) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x5F) = v1;
    *(volatile s8 *)((u8 *)arg0 + 0x64) = v1;
    *(volatile s32 *)((u8 *)arg0 + 0x68) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x60) = v1;
    *(volatile s8 *)((u8 *)arg0 + 0x61) = 0;
    *(volatile s8 *)((u8 *)arg0 + 0x62) = v1;
    *(volatile s8 *)((u8 *)arg0 + 0x63) = v1;
}
