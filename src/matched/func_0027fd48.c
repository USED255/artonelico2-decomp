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

M2C_UNK baseelf_127(void *);                        /* extern */
M2C_UNK baseelf_6();                                /* extern */
M2C_UNK func_0012c30c(M2C_UNK *);                   /* extern */
M2C_UNK func_0013f8dc();                            /* extern */
M2C_UNK func_00270e18(void *);                      /* extern */
M2C_UNK func_00270e64(void *, M2C_UNK);             /* extern */
M2C_UNK func_00270e6c(void *, M2C_UNK);             /* extern */
M2C_UNK func_0027102c(void *);                      /* extern */
M2C_UNK func_00271080(void *, M2C_UNK);             /* extern */
M2C_UNK func_00277e28(void *);                      /* extern */
M2C_UNK func_0027d1d4(void *);                      /* extern */
M2C_UNK func_0027d5b0(void *);                      /* extern */
M2C_UNK func_0027e684(void *);                      /* extern */
M2C_UNK func_0027e86c(void *);                      /* extern */
extern M2C_UNK D_00AD8000;

void func_0027fd48(void *arg0) {
    s32 var_t7;
    void *temp_s0;
    void *temp_s1;
    void *temp_s2;
    void *var_t6;

    func_0012c30c(&D_00AD8000);
    baseelf_6();
    var_t6 = arg0 + 0x7A30;
    M2C_FIELD(arg0, s8 *, 0x7B4C) = -1;
    M2C_FIELD(arg0, s16 *, 0x7A48) = -1;
    var_t7 = 4;
    do {
        M2C_FIELD(var_t6, s16 *, 4) = 0;
        var_t7 -= 1;
        M2C_FIELD(var_t6, s16 *, 0xE) = 0;
        var_t6 += 2;
    } while (var_t7 >= 0);
    temp_s0 = arg0 + 0x40C;
    temp_s1 = arg0 + 0x4BC;
    temp_s2 = arg0 + 0x7A20;
    func_0027e684(temp_s0);
    func_0027e86c(temp_s0);
    func_0027102c(temp_s1);
    func_00271080(temp_s1, 1);
    M2C_FIELD(arg0, s8 *, 0x4BE) = 0x10;
    M2C_FIELD(arg0, u8 *, 0x4BD) = (u8) M2C_FIELD(arg0, u8 *, 0x4BF);
    func_0027d1d4(arg0 + 0x4D4);
    func_0027d5b0(arg0 + 0x8F8);
    func_00277e28(arg0 + 0x2928);
    M2C_FIELD(arg0, s8 *, 0x7B4D) = 0;
    M2C_FIELD(arg0, s16 *, 0x7A4A) = -1;
    func_0013f8dc();
    baseelf_127(arg0 + 0x2A30);
    func_00270e18(temp_s2);
    func_00270e64(temp_s2, 0);
    func_00270e6c(temp_s2, 0);
    M2C_FIELD(arg0, s8 *, 0x7A22) = 0;
    M2C_FIELD(arg0, u8 *, 0x7A20) = (u8) M2C_FIELD(arg0, u8 *, 0x7A23);
}
