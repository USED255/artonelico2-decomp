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

int LibcStdio_16();            /* 参数个数未知，按 K&R 空原型声明 */
int baseelf_98();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002d5ae0();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002dd678();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002de0d0();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002de0f0();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002de130();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002de140();            /* 参数个数未知，按 K&R 空原型声明 */
int func_002de180();            /* 参数个数未知，按 K&R 空原型声明 */
extern unsigned char D_0083F2C0[];
extern unsigned char D_0093F5C8[];
extern unsigned char D_009E5418[];

void func_0018c41c(void) { s32 temp_t6; s32 var_t5; void *temp_t6_2; int tmp = baseelf_98(0x100, 0x57800); int r = func_002d5ae0(0xA, tmp, 0x57800, 0xB); LibcStdio_16(&D_0093F5C8, r); func_002dd678(func_002de0d0()); func_002dd678(func_002de0f0()); func_002dd678(func_002de130()); func_002dd678(func_002de140()); func_002dd678(func_002de180()); func_002dd678(&D_0083F2C0); var_t5 = 0; do { temp_t6 = var_t5 * 8; var_t5 += 1; temp_t6_2 = (void *)((uintptr_t)&D_009E5418 + temp_t6); ((s32 *)temp_t6_2)[1] = 0; ((s32 *)temp_t6_2)[0] = -1; } while (var_t5 < 0xB); }
