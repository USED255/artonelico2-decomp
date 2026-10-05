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

s32 func_00165bfc(s32 arg0, s32 arg1, void *arg2) {
    s32 var_v0;
    void *temp_t6;

    temp_t6 = M2C_FIELD(arg2, void **, 0x40);
    var_v0 = 0;
    if (((f32) (arg0 - 0x140) <= M2C_FIELD(temp_t6, f32 *, 0xC)) && (M2C_FIELD(temp_t6, f32 *, 0) <= (f32) (arg0 + 0x140)) && ((f32) (arg1 - 0xE0) <= M2C_FIELD(temp_t6, f32 *, 0x10))) {
        var_v0 = 1;
        if (!(M2C_FIELD(temp_t6, f32 *, 4) <= (f32) (arg1 + 0xE0))) {
            var_v0 = 0;
        }
    }
    return var_v0;
}
