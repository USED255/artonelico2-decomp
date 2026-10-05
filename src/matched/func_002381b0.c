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

M2C_UNK func_0012c30c(M2C_UNK *);                   /* extern */
M2C_UNK func_001357f4(M2C_UNK);                     /* extern */
M2C_UNK func_0023874c(s32);                         /* extern */
M2C_UNK func_0024fb74(s32);                         /* extern */
M2C_UNK func_00270e18(s32);                         /* extern */
M2C_UNK func_00270e64(s32, M2C_UNK);                /* extern */
M2C_UNK func_00270e6c(s32, M2C_UNK *);              /* extern */
extern M2C_UNK D_0097B840;
extern M2C_UNK D_00AD8000;

void func_002381b0(s32 arg0) {
    s32 temp_s1;

    temp_s1 = arg0 + 0x40C;
    func_0012c30c(&D_00AD8000);
    func_001357f4(0xE2);
    func_0024fb74(arg0 + 0x440);
    func_0023874c(arg0 + 0x420);
    func_00270e18(temp_s1);
    func_00270e64(temp_s1, 0);
    func_00270e6c(temp_s1, &D_0097B840);
}
