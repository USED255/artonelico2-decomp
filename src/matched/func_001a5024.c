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

s32 func_0018cf08();                                /* extern */
s32 func_0019e3dc(s16, M2C_UNK);                    /* extern */
s32 func_0019e864(M2C_UNK);                         /* extern */
s32 func_0019ea50(s32);                             /* extern */
M2C_UNK func_001a1df8(M2C_UNK);                     /* extern */
M2C_UNK func_001b3dd0();                            /* extern */
extern s16 D_00BC0950;

s32 func_001a5024(void) {
    s32 temp_v0;
    s32 temp_v0_2;
    s32 var_s0;
    s32 var_s1;

    var_s1 = 0;
    temp_v0 = func_0019e3dc(D_00BC0950, 1);
    var_s0 = temp_v0;
    if ((temp_v0 != 0) || (temp_v0_2 = func_0019e864(1), var_s0 = temp_v0_2, (temp_v0_2 != 0))) {
        var_s1 = 1;
        if ((func_0018cf08() != 0) || (func_0019ea50(var_s0) != 0)) {
            func_001a1df8(1);
        } else {
            func_001b3dd0();
        }
    }
    return var_s1;
}
