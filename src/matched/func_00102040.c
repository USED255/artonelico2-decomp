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

s32 func_00101b94();                                /* extern */
s32 func_002d4368(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK *); /* extern */
s32 func_002d4548(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK *); /* extern */
extern M2C_UNK D_009E2750;

s32 func_00102040(s32 arg0, M2C_UNK arg1, M2C_UNK arg2, M2C_UNK arg3) {
    s32 var_t7;
    s32 var_v0;

    var_t7 = 0;
    if (func_00101b94() == 0) {
        if (arg0 == 0) {
            var_v0 = func_002d4368(arg1, arg2, arg3, &D_009E2750);
        } else {
            var_v0 = func_002d4548(arg1, arg2, arg3, &D_009E2750);
        }
        var_t7 = var_v0;
    }
    return var_t7;
}
