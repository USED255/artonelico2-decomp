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

int eekernel_47();            /* 参数个数未知，按 K&R 空原型声明 */
int eekernel_53();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002c9b58();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002c9dd8();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char D_00585544[];
extern unsigned char D_009E3B8C[];
extern unsigned char D_009E3BC0[];
extern unsigned char D_009E3CC0[];

int func_0013ca58(void) { eekernel_47(eekernel_53(), 9); *(unsigned int *)&D_009E3B8C[0] = 0; s32 v0 = func_002c9b58(0); *(unsigned int *)&D_00585544[0] = v0; if ((v0 & 0xFFFF) == 0) { volatile s32 stack_arr[8]; stack_arr[1] = 2; stack_arr[0] = 2; stack_arr[2] = 0; s32 v0_2 = func_002c9dd8(stack_arr, &D_009E3BC0); *(unsigned int *)&D_00585544[0] = v0_2; *(unsigned int *)&D_009E3CC0[0] = v0_2 & 0xFFFF; } return *(unsigned int *)&D_00585544[0]; }
