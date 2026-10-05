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

M2C_UNK func_00183b64(void *);                      /* extern */
M2C_UNK func_00184238(void *);                      /* extern */

void func_00184c10(void *arg0) {
    s32 temp_t7;
    s32 temp_t7_2;

    func_00183b64(arg0 + (M2C_FIELD(arg0, s32 *, 0xFA4) * 0x50));
    temp_t7 = M2C_FIELD(arg0, s32 *, 0xFA4) + 1;
    M2C_FIELD(arg0, s32 *, 0xFA4) = temp_t7;
    if (temp_t7 >= 0x32) {
        M2C_FIELD(arg0, s32 *, 0xFA4) = 0;
    }
    temp_t7_2 = M2C_FIELD(arg0, s32 *, 0xFA0) - 1;
    M2C_FIELD(arg0, s32 *, 0xFA0) = temp_t7_2;
    if (temp_t7_2 != 0) {
        func_00184238(arg0);
        return;
    }
    M2C_FIELD(arg0, s32 *, 0xFD0) = 0;
}
