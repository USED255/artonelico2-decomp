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

M2C_UNK func_0011f004(void *);                      /* extern */
M2C_UNK func_0011f03c(void *, M2C_UNK *, M2C_UNK, M2C_UNK); /* extern */
M2C_UNK func_0013adc0(void *);                      /* extern */
M2C_UNK func_0023919c();                            /* extern */
M2C_UNK func_00239620();                            /* extern */
M2C_UNK func_00239654(M2C_UNK, M2C_UNK, M2C_UNK);   /* extern */
extern M2C_UNK D_003CE378;

void func_00238eec(void *arg0) {
    M2C_FIELD(arg0, s16 *, 0x40) = -1;
    func_0023919c();
    M2C_FIELD(arg0, s32 *, 0x44) = 0;
    M2C_FIELD(arg0, s8 *, 0x48) = 1;
    func_0013adc0(arg0 + 0x30);
    func_0011f004(arg0);
    func_0011f03c(arg0, &D_003CE378, 0x1B3, 0x14);
    func_00239620();
    func_00239654(0x1E5, 0x46, 0x50);
}
