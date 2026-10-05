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

M2C_UNK func_00106388(M2C_UNK *);                   /* extern */
M2C_UNK func_0014d648();                            /* extern */
M2C_UNK func_00320080();                            /* extern */
M2C_UNK func_003217e0(M2C_UNK *, M2C_UNK);          /* extern */
M2C_UNK func_0032c450();                            /* extern */
extern s32 D_0037608C;
extern M2C_UNK func_0010225C;
extern M2C_UNK func_00102264;

void func_0010228c(void) {
    func_00106388(&func_00102264);
    func_00320080();
    func_0032c450();
    func_0014d648();
    func_003217e0(&func_0010225C, 0);
    D_0037608C = 1;
}
