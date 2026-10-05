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

M2C_UNK LibcStdio_16(M2C_UNK *, s32, s32);          /* extern */
M2C_UNK baseelf_104(s32);                           /* extern */
s32 func_001023e0();                                /* extern */
M2C_UNK func_0014e354(s32, s32, s32);               /* extern */
s32 iopsmem_13(s32);                                /* extern */
extern M2C_UNK D_008B33E8;

s32 func_00102668(s32 arg0, s32 *arg1) {
    s32 temp_s2;
    s32 temp_v0;

    temp_s2 = func_001023e0();
    LibcStdio_16(&D_008B33E8, arg0, *arg1);
    temp_v0 = iopsmem_13(*arg1);
    func_0014e354(temp_v0, temp_s2, *arg1);
    baseelf_104(temp_s2);
    return temp_v0;
}
