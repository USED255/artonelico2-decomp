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

M2C_UNK baseelf_35(M2C_UNK, M2C_UNK);               /* extern */
M2C_UNK baseelf_75(void *, M2C_UNK);                /* extern */
M2C_UNK baseelf_76(void *);                         /* extern */
M2C_UNK func_0014c0c8(M2C_UNK);                     /* extern */
M2C_UNK func_0014d04c(M2C_UNK, M2C_UNK);            /* extern */
M2C_UNK func_0014e800(M2C_UNK);                     /* extern */
M2C_UNK func_0014fd9c();                            /* extern */
M2C_UNK func_00153174(M2C_UNK);                     /* extern */
M2C_UNK func_0021e158(M2C_UNK, M2C_UNK);            /* extern */
M2C_UNK func_00232da4(void *);                      /* extern */
M2C_UNK func_00232ed4(M2C_UNK);                     /* extern */
extern void *D_007AF2D0;

void func_0023300c(void *arg0) {
    if (!(M2C_FIELD(arg0, s32 *, 0x14) & 2)) {
        baseelf_35(0x18, 1);
        M2C_FIELD(arg0, s32 *, 0x10) = 0;
        if (M2C_FIELD(D_007AF2D0, s16 *, 0xC1CA8) != 1) {
            func_0014e800(0x79);
            func_0014fd9c();
        }
        func_0014c0c8(0xF6);
        func_0014d04c(0x169, 0xA);
        func_00153174(0x1F);
        M2C_FIELD(arg0, u16 *, 0xE) = (u16) M2C_FIELD(D_007AF2D0, u16 *, 0xA70);
        baseelf_76(D_007AF2D0 + 0x9E0);
        baseelf_75(D_007AF2D0 + 0x9E0, -3);
        func_00232da4(arg0);
        M2C_FIELD(arg0, s32 *, 4) = 0;
        func_00232ed4(0);
        M2C_FIELD(arg0, s32 *, 0x14) = (s32) (M2C_FIELD(arg0, s32 *, 0x14) | 2);
        func_0021e158(0xB, 0);
    }
}
