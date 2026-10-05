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

M2C_UNK baseelf_4();                                /* extern */
M2C_UNK func_00104444();                            /* extern */
M2C_UNK func_0011a200(M2C_UNK *);                   /* extern */
M2C_UNK func_0011f1c0(void *);                      /* extern */
M2C_UNK func_001357f4(M2C_UNK);                     /* extern */
M2C_UNK func_00137998(M2C_UNK);                     /* extern */
M2C_UNK func_0013f500(M2C_UNK);                     /* extern */
M2C_UNK func_0015314c(M2C_UNK);                     /* extern */
extern M2C_UNK D_003C9D28;
extern M2C_UNK D_003C9DE8;
extern M2C_UNK D_003C9EA8;
extern M2C_UNK D_003C9F08;
extern M2C_UNK D_003C9F68;
extern M2C_UNK D_003CA058;

void func_002706ac(void *arg0) {
    M2C_FIELD(arg0, s16 *, 0x988) = -1;
    func_00104444();
    func_0013f500(0x1E);
    func_001357f4(-1);
    func_0011f1c0(arg0 + 0x850);
    func_0011f1c0(arg0 + 0x880);
    func_0011f1c0(arg0 + 0x8B0);
    func_0011f1c0(arg0 + 0x8E0);
    func_0011f1c0(arg0 + 0x910);
    func_0011f1c0(arg0 + 0x940);
    func_0015314c(0x6A);
    func_00137998(0xE3);
    func_0011a200(&D_003C9F68);
    func_0011a200(&D_003CA058);
    func_0011a200(&D_003C9F08);
    func_0011a200(&D_003C9EA8);
    func_0011a200(&D_003C9DE8);
    func_0011a200(&D_003C9D28);
    func_0013f500(0x1E);
    baseelf_4();
}
