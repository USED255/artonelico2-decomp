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

M2C_UNK func_0035f3d8(s32, M2C_UNK, M2C_UNK, void *); /* extern */
extern M2C_UNK func_0035F580;

void func_0035f5c0(void *arg0) {
    M2C_FIELD(arg0, s32 *, 0x1D8) = 0;
    M2C_FIELD(arg0, M2C_UNK **, 0x3C) = &func_0035F580;
    M2C_FIELD(arg0, s32 *, 0x38) = 1;
    M2C_FIELD(arg0, void **, 0x1E0) = (void *) (arg0 + 0x1E4);
    M2C_FIELD(arg0, s32 *, 0x1DC) = 3;
    func_0035f3d8(M2C_FIELD(arg0, s32 *, 4), 4, 0, arg0);
    func_0035f3d8(M2C_FIELD(arg0, s32 *, 8), 9, 1, arg0);
    func_0035f3d8(M2C_FIELD(arg0, s32 *, 0xC), 0xA, 2, arg0);
}
