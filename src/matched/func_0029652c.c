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

M2C_UNK func_00270e64(void *, M2C_UNK *);           /* extern */
M2C_UNK func_00270e6c(void *, M2C_UNK *);           /* extern */
M2C_UNK func_00297a2c(void *, void *, M2C_UNK);     /* extern */
M2C_UNK func_0029b08c(void *, M2C_UNK *);           /* extern */
M2C_UNK func_0029b844(void *);                      /* extern */
M2C_UNK func_0029dbc8(void *);                      /* extern */
M2C_UNK func_0029dca4(void *, M2C_UNK, M2C_UNK, M2C_UNK); /* extern */
extern M2C_UNK D_009BC468;
extern M2C_UNK D_009BC7E0;
extern M2C_UNK D_009BC7F8;

void func_0029652c(void *arg0) {
    s32 var_s0;
    void *temp_a1;
    void *temp_s0;
    void *temp_s2;

    temp_s2 = arg0 + 0x6DC8;
    M2C_FIELD(arg0, u8 *, 0x6DC8) = (u8) M2C_FIELD(arg0, u8 *, 0x6DCC);
    M2C_FIELD(arg0, u8 *, 0x6DC9) = (u8) M2C_FIELD(arg0, u8 *, 0x6DCB);
    M2C_FIELD(arg0, s8 *, 0x6DCA) = 0x10;
    func_00270e64(temp_s2, &D_009BC7E0);
    func_0029b08c(arg0 + 0x74D0, &D_009BC7E0);
    temp_s0 = arg0 + 0xABC0;
    M2C_FIELD(arg0, s16 *, 0x67A4) = 6;
    func_0029dbc8(temp_s0);
    func_0029dca4(temp_s0, 4, -1, 0);
    if (M2C_FIELD(arg0, s8 *, 0x79CB) != 0) {
        func_00270e6c(temp_s2, &D_009BC468);
    } else {
        func_00270e6c(temp_s2, &D_009BC7F8);
        var_s0 = 0;
        if (M2C_FIELD(arg0, s16 *, 0x5728) > 0) {
            do {
                temp_a1 = arg0 + (var_s0 * 0x4A0);
                var_s0 += 1;
                func_00297a2c(arg0, temp_a1 + 0x5730, 0x16);
            } while (var_s0 < M2C_FIELD(arg0, s16 *, 0x5728));
        }
    }
    func_0029b844(arg0 + 0x7580);
}
