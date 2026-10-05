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

M2C_UNK func_00270e6c(void *, M2C_UNK *);           /* extern */
M2C_UNK func_00278db8(void *, s32);                 /* extern */
M2C_UNK func_002792c0(void *);                      /* extern */
M2C_UNK func_0027d278(void *, M2C_UNK);             /* extern */
M2C_UNK func_0027e5d8(void *, s32);                 /* extern */
extern M2C_UNK D_0099BF08;

void func_0025acf8(void *arg0) {
    void *temp_s1;

    temp_s1 = arg0 + 0x4E8;
    func_00278db8(temp_s1, M2C_FIELD(arg0, s32 *, 0x2A40));
    func_002792c0(temp_s1);
    func_0027d278(arg0 + 0x261C, 0);
    func_0027e5d8(arg0 + 0x5EC, M2C_FIELD(arg0, s32 *, 0x2A44));
    M2C_FIELD(arg0, s32 *, 0xA0C) = (s32) (M2C_FIELD(arg0, s32 *, 0xA0C) & ~0x200);
    func_00270e6c(arg0 + 0x4D4, &D_0099BF08);
    M2C_FIELD(arg0, s8 *, 0x4D6) = 0x10;
    M2C_FIELD(arg0, u8 *, 0x4D5) = (u8) M2C_FIELD(arg0, u8 *, 0x4D7);
}
