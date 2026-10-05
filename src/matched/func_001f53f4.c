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

M2C_UNK baseelf_127(s32);                           /* extern */
M2C_UNK baseelf_4();                                /* extern */
M2C_UNK func_0013f5e8();                            /* extern */
M2C_UNK func_0013f618(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK); /* extern */
M2C_UNK func_0013f63c(M2C_UNK *);                   /* extern */
M2C_UNK func_0013f6f4(M2C_UNK);                     /* extern */
M2C_UNK func_001f52fc();                            /* extern */
M2C_UNK func_002310bc();                            /* extern */
M2C_UNK func_00231934();                            /* extern */
extern s32 D_007AF2D0;
extern M2C_UNK D_00A504E0;

void func_001f53f4(s32 arg0) {
    func_0013f6f4(0);
    switch (arg0) {                                 /* irregular */
    case 0:
        func_002310bc();
        break;
    case 1:
        func_00231934();
        break;
    case 2:
        func_001f52fc();
        break;
    }
    func_0013f5e8();
    func_0013f6f4(0);
    func_0013f618(0x80, 0x80, 0x80, 0x80);
    func_0013f63c(&D_00A504E0);
    func_0013f5e8();
    baseelf_4();
    baseelf_127(D_007AF2D0 + 0xB1AD0);
}
