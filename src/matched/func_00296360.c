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

M2C_UNK func_00270e64(void *, M2C_UNK *);           /* extern */
M2C_UNK func_00270e6c(void *, M2C_UNK *);           /* extern */
M2C_UNK func_002932f4(void *, M2C_UNK);             /* extern */
M2C_UNK func_002995bc(void *);                      /* extern */
M2C_UNK func_00299c34(void *, M2C_UNK);             /* extern */
M2C_UNK func_0029b08c(void *, M2C_UNK *);           /* extern */
extern M2C_UNK D_009BC770;
extern M2C_UNK D_009BC7A8;
extern M2C_UNK D_009BC7D0;

void func_00296360(void *arg0) {
    void *temp_s1;

    temp_s1 = arg0 + 0x6DC8;
    M2C_FIELD(arg0, u8 *, 0x6DC8) = (u8) M2C_FIELD(arg0, u8 *, 0x6DCC);
    M2C_FIELD(arg0, u8 *, 0x6DC9) = (u8) M2C_FIELD(arg0, u8 *, 0x6DCB);
    M2C_FIELD(arg0, s8 *, 0x6DCA) = 0x10;
    func_00270e64(temp_s1, &D_009BC7A8);
    func_00270e6c(temp_s1, &D_009BC770);
    func_0029b08c(arg0 + 0x74D0, &D_009BC7D0);
    M2C_FIELD(arg0, s16 *, 0x67A4) = 5;
    func_002932f4(arg0 + 0x8B0, -1);
    func_00299c34(arg0, 7);
    func_002995bc(arg0);
    M2C_FIELD(arg0, s8 *, 0x79C8) = 0;
}
