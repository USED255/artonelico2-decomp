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
/* m2c 对 128 位整数（lq/sq、MMI）用 s128/u128；用 GCC 的向量模式类型让赋值/取址可用 */
typedef int s128 __attribute__((mode(V4SI)));
typedef int u128 __attribute__((mode(V4SI)));   /* 与 s128 同型，避免 s128/u128 互相赋值报类型错 */
typedef int          s64_ __attribute__((unused));
#define NULL 0
/* m2c 在无法把栈访问还原成局部变量时会直接写 `sp`（$29）；给个占位声明让它至少能编译，
   能不能对上交给 objdiff 判断（这类草稿通常对不上，但不占额外成本）。 */
extern unsigned char *sp;
/* m2c --valid-syntax 用到的通用占位宏（自己写，避免生成物依赖工作区外的头文件） */
typedef s32 M2C_UNK;   typedef s8  M2C_UNK8;
typedef s16 M2C_UNK16; typedef s32 M2C_UNK32; typedef s64 M2C_UNK64;
#define M2C_FIELD(expr, type_ptr, offset) (*(type_ptr)((s8 *)(expr) + (offset)))
#define M2C_BITWISE(type, expr) ((type)(expr))
#define M2C_LIKELY(x) (x)
#define M2C_UNLIKELY(x) (x)

M2C_UNK func_0018cedc();                            /* extern */
M2C_UNK func_0018d694();                            /* extern */
M2C_UNK func_0018f174();                            /* extern */
M2C_UNK func_0018ff18();                            /* extern */
M2C_UNK func_0018ff48();                            /* extern */
M2C_UNK func_00191860();                            /* extern */
M2C_UNK func_00191c24();                            /* extern */
M2C_UNK func_00193dd8();                            /* extern */
M2C_UNK func_0019f4bc();                            /* extern */
M2C_UNK func_0019f578();                            /* extern */
M2C_UNK func_001a069c();                            /* extern */
M2C_UNK func_001a66bc();                            /* extern */
M2C_UNK func_001da7d8();                            /* extern */
M2C_UNK func_001de94c();                            /* extern */
M2C_UNK func_001e0274();                            /* extern */
M2C_UNK func_001e0f6c();                            /* extern */
M2C_UNK func_001e1010();                            /* extern */
M2C_UNK func_001f010c();                            /* extern */
M2C_UNK func_002352b4();                            /* extern */
M2C_UNK func_002362a0();                            /* extern */
M2C_UNK func_0023fb78();                            /* extern */
M2C_UNK func_0024501c();                            /* extern */
M2C_UNK func_00247248();                            /* extern */
M2C_UNK func_00247a9c();                            /* extern */
M2C_UNK func_0024e5b8();                            /* extern */
M2C_UNK func_00255570();                            /* extern */
M2C_UNK func_0025a9ec();                            /* extern */
M2C_UNK func_00270d28();                            /* extern */
M2C_UNK func_0029c020();                            /* extern */
M2C_UNK func_0029e07c();                            /* extern */
M2C_UNK func_0029e728();                            /* extern */
extern s32 D_009DFCA8;
extern s32 D_009DFCE0;
extern s16 D_009DFD02;

void func_0018d004(void) {
    D_009DFCA8 = 0;
    D_009DFCE0 = 0;
    D_009DFD02 = 0;
    func_00191c24();
    func_00191860();
    func_001f010c();
    func_001e0f6c();
    func_001e1010();
    func_0029e728();
    func_0018d694();
    func_0018f174();
    func_0018ff18();
    func_0018ff48();
    func_00270d28();
    func_001da7d8();
    func_002352b4();
    func_002362a0();
    func_00247248();
    func_0024501c();
    func_00247a9c();
    func_0023fb78();
    func_0024e5b8();
    func_0029e07c();
    func_0029c020();
    func_00255570();
    func_00193dd8();
    func_001a069c();
    func_001de94c();
    func_001a66bc();
    func_001e0274();
    func_0018cedc();
    func_0019f578();
    func_0019f4bc();
    func_0025a9ec();
}
