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

M2C_UNK func_0012b940(M2C_UNK *);                   /* extern */
M2C_UNK func_0012c30c(M2C_UNK *);                   /* extern */
M2C_UNK func_0013f8dc();                            /* extern */
M2C_UNK func_00144390(void *);                      /* extern */
M2C_UNK func_0025a204(void *);                      /* extern */
M2C_UNK func_00270e18(void *);                      /* extern */
M2C_UNK func_0027102c(s32);                         /* extern */
M2C_UNK func_00271080(s32, M2C_UNK);                /* extern */
M2C_UNK func_0027e684(s32);                         /* extern */
M2C_UNK func_0027e86c(s32);                         /* extern */
extern M2C_UNK D_00AD8000;

void func_00259d9c(void *arg0) {
    s32 temp_s1;
    s32 temp_s2;

    temp_s1 = arg0 + 0x40C;
    temp_s2 = arg0 + 0x4BC;
    func_0012c30c(&D_00AD8000);
    func_0027e684(temp_s1);
    func_0027e86c(temp_s1);
    func_0027102c(temp_s2);
    func_00271080(temp_s2, 6);
    M2C_FIELD(arg0, s8 *, 0x4BE) = 0x10;
    M2C_FIELD(arg0, u8 *, 0x4BD) = (u8) M2C_FIELD(arg0, u8 *, 0x4BF);
    func_00270e18(arg0 + 0x4D4);
    func_00144390(arg0 + 0x528);
    func_0025a204(arg0 + 0x4E8);
    M2C_FIELD(arg0, s32 *, 0x17C0) = 0;
    M2C_FIELD(arg0, s32 *, 0x16F4) = -1;
    func_0013f8dc();
    func_0012b940(&D_00AD8000);
}
