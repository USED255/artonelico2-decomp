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
#define NULL 0
/* m2c --valid-syntax 用到的通用占位宏（自己写，避免生成物依赖工作区外的头文件） */
typedef s32 M2C_UNK;   typedef s8  M2C_UNK8;
typedef s16 M2C_UNK16; typedef s32 M2C_UNK32; typedef s64 M2C_UNK64;
#define M2C_FIELD(expr, type_ptr, offset) (*(type_ptr)((s8 *)(expr) + (offset)))
#define M2C_BITWISE(type, expr) ((type)(expr))
#define M2C_LIKELY(x) (x)
#define M2C_UNLIKELY(x) (x)

M2C_UNK baseelf_170(void *, M2C_UNK);               /* extern */
M2C_UNK func_0013f500(M2C_UNK);                     /* extern */
M2C_UNK func_0014e800(M2C_UNK);                     /* extern */
M2C_UNK func_0014e9f8();                            /* extern */
M2C_UNK func_0014f1ac(M2C_UNK);                     /* extern */
s32 func_0026e900(M2C_UNK);                         /* extern */

s32 func_0026ffec(void *arg0) {
    s32 var_v0;

    func_0014f1ac(0x1E);
    baseelf_170(arg0, 6);
    func_0014e800(0x6D);
    if (func_0026e900(1) != 0) {
        func_0014f1ac(0x1E);
        func_0013f500(0x1E);
        func_0014e9f8();
        var_v0 = 0;
        M2C_FIELD(arg0, s16 *, 0x986) = 1;
    } else {
        func_0014f1ac(0x1E);
        func_0013f500(0x1E);
        func_0014e9f8();
        var_v0 = -1;
    }
    return var_v0;
}
