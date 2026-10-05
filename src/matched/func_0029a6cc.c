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

s32 func_0029a66c();                                /* extern */
s32 func_0029a68c();                                /* extern */
s32 func_0029a6ac();                                /* extern */

s32 func_0029a6cc(s32 arg0, s32 arg1) {
    switch (arg0) {                                 /* irregular */
    default:
        return 1;
    case 0:
        if (arg1 != 1) {
            if (arg1 == 2) {
                return func_0029a68c();
            }
            /* Duplicate return node #6. Try simplifying control flow for better match */
            return 1;
        }
        return func_0029a66c();
    case 2:
        if (arg1 != 0) {
            if (arg1 == 1) {
                return func_0029a6ac();
            }
            /* Duplicate return node #6. Try simplifying control flow for better match */
            return 1;
        }
        /* Duplicate return node #10. Try simplifying control flow for better match */
        return func_0029a68c();
    case 1:
        if (arg1 != 0) {
            if (arg1 == 2) {
                /* Duplicate return node #18. Try simplifying control flow for better match */
                return func_0029a6ac();
            }
            /* Duplicate return node #6. Try simplifying control flow for better match */
            return 1;
        }
        /* Duplicate return node #12. Try simplifying control flow for better match */
        return func_0029a66c();
    }
}
