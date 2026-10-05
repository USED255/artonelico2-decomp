
typedef signed char s8;
typedef unsigned char u8;
typedef short s16;
typedef unsigned short u16;
typedef int s32;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef unsigned char byte;
typedef unsigned char code;
typedef unsigned int uint;
typedef int s128;
typedef int u128;
typedef int s64_;
extern unsigned char *sp;
typedef s32 M2C_UNK;
typedef s8 M2C_UNK8;
typedef s16 M2C_UNK16;
typedef s32 M2C_UNK32;
typedef s64 M2C_UNK64;
M2C_UNK baseelf_153(s32, M2C_UNK *, s32, s32);
M2C_UNK func_0011299c(u8);
M2C_UNK func_0013e2fc(void *);
extern M2C_UNK D_003D1678;
void func_0029dff0(s32 arg0, void *arg1)
{
  u8 temp_t7;
  M2C_UNK *new_var;
  func_0013e2fc(arg1);
  temp_t7 = *((u8 *) (((s8 *) arg1) + 0));
  if (temp_t7 != 0)
  {
    func_0011299c(temp_t7);
    new_var = &D_003D1678;
    *((s32 *) (((s8 *) new_var) + 0xA0)) = (s32) (*((s32 *) (((s8 *) arg1) + 0x10)));
    baseelf_153(arg0, &D_003D1678, *((s32 *) (((s8 *) arg1) + 8)), *((s32 *) (((s8 *) arg1) - -0xC)));
  }
}
