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

M2C_UNK func_0011299c(u8);                          /* extern */
M2C_UNK func_0013e2fc(void *);                      /* extern */
s32 func_0027261c(void *);                          /* extern */
M2C_UNK func_00272eb0(void *, M2C_UNK);             /* extern */
M2C_UNK func_0027307c(s32, void *, void *);         /* extern */

void func_002728a8(s32 arg0, void *arg1) {
    M2C_UNK var_a1;
    s32 temp_t5;
    s32 temp_v0;
    s32 var_s1;
    u8 temp_a0;
    void *temp_s0;
    void *temp_s0_2;

    func_0013e2fc(arg1);
    temp_a0 = M2C_FIELD(arg1, u8 *, 0);
    switch (temp_a0) {                              /* irregular */
    case 0x80:
        M2C_FIELD(arg1, s32 *, 0x4F4) = (s32) (M2C_FIELD(arg1, s32 *, 0x4F4) | 0x10000);
block_5:
        func_0011299c(temp_a0);
        temp_v0 = func_0027261c(arg1);
        var_s1 = 0;
        if (M2C_FIELD(arg1, s8 *, 0x4F5) > 0) {
            do {
                temp_t5 = M2C_FIELD(arg1, s32 *, 0x4F4);
                var_a1 = 0;
                if ((temp_t5 & 0x30000) == 0x30000) {
                    if ((temp_t5 & 0x40000) || (var_s1 == temp_v0)) {
                        var_a1 = 1;
                    }
                }
                temp_s0 = arg1 + (var_s1 * 0x18);
                var_s1 += 1;
                temp_s0_2 = temp_s0 + 8;
                func_00272eb0(temp_s0_2, var_a1);
                func_0027307c(arg0, temp_s0_2, arg1 + 0x4E0);
            } while (var_s1 < M2C_FIELD(arg1, s8 *, 0x4F5));
        }
        func_0011299c(0x80U);
        return;
    default:
        M2C_FIELD(arg1, s32 *, 0x4F4) = (s32) (M2C_FIELD(arg1, s32 *, 0x4F4) & 0xFFFEFFFF);
        goto block_5;
    case 0x0:
        return;
    }
}
