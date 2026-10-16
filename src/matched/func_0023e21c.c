
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
M2C_UNK baseelf_153(s32, M2C_UNK *, M2C_UNK, M2C_UNK);
s16 func_0023d794(s16);
s16 func_0023d7f8(s16);
extern M2C_UNK D_00472B28;
void func_0023e21c(s32 arg0, void *arg1)
{
  s8 *new_var2;
  s8 *new_var;
  new_var = (s8 *) arg1;
  if ((*((s8 *) (((s8 *) arg1) + 0x1926))) != 0)
  {
    new_var2 = (s8 *) (&D_00472B28);
    *((s16 *) (new_var2 + 0xC8)) = func_0023d794(*((s16 *) (new_var + 0x133C)));
    *((s16 *) (new_var2 + 0xF8)) = func_0023d7f8(*((s16 *) (((s8 *) arg1) + 0x133C)));
    baseelf_153(arg0, &D_00472B28, 0, 0);
  }
}
