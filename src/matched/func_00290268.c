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

M2C_UNK func_001326f4(s32, void *);                 /* extern */
M2C_UNK func_0013787c(s32);                         /* extern */
M2C_UNK func_0027e71c(s32, void *);                 /* extern */
void *func_00290184();                              /* extern */

void func_00290268(s32 arg0) {
    s32 temp_t6;
    void *temp_v0;

    temp_v0 = func_00290184();
    temp_t6 = M2C_FIELD(temp_v0, s32 *, 0xB0);
    switch (temp_t6) {                              /* irregular */
    case 0:
        func_001326f4(arg0, temp_v0 + 0xB4);
        /* fallthrough */
    case 1:
        func_0027e71c(arg0, temp_v0);
        return;
    case 3:
        func_0013787c(arg0);
        return;
    case 2:
        func_0027e71c(arg0, temp_v0);
        /* Duplicate return node #12. Try simplifying control flow for better match */
        func_0013787c(arg0);
        return;
    }
}
