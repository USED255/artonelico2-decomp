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

M2C_UNK func_00125d18(void *);                      /* extern */
s32 func_0012994c(void *);                          /* extern */
s32 func_0028fd38(s32, M2C_UNK, void *);            /* extern */

void func_0028fdd4(s32 arg0, M2C_UNK arg1, void *arg2) {
    if (M2C_FIELD(arg2, s32 *, 0x90) != -1) {
        func_00125d18(arg2);
        if ((func_0012994c(arg2) >= M2C_FIELD(arg2, s32 *, 0x90)) && ((M2C_FIELD(arg2, s32 *, 0x94) != 0) || (M2C_FIELD(arg2, s32 *, 0x94) = 1, (func_0028fd38(arg0, arg1, arg2) == 0)))) {
            M2C_FIELD(arg2, s64 *, 0x88) = (s64) (M2C_FIELD(arg2, s64 *, 0x88) | 8);
        }
    }
}
