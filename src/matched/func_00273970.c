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

M2C_UNK baseelf_153(s32, M2C_UNK *, s16, s16);      /* extern */
M2C_UNK func_0011299c(u8);                          /* extern */
M2C_UNK func_0013e2fc(void *);                      /* extern */
extern M2C_UNK D_003BFF18;

void func_00273970(s32 arg0, void *arg1) {
    u8 temp_t7;

    func_0013e2fc(arg1);
    temp_t7 = M2C_FIELD(arg1, u8 *, 0);
    if (temp_t7 != 0) {
        func_0011299c(temp_t7);
        baseelf_153(arg0, &D_003BFF18, M2C_FIELD(arg1, s16 *, 6), M2C_FIELD(arg1, s16 *, 8));
        func_0011299c(0x80U);
    }
}
