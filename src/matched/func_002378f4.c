
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
s32 func_00140034();
s32 func_002378f4(void *arg0)
{
  s32 new_var;
  s8 *new_var2;
  new_var = func_00140034();
  if (new_var == 2)
  {
    new_var2 = (s8 *) arg0;
    new_var = 0xE;
    *((s16 *) (new_var2 + 0)) = new_var;
    *((s32 *) (new_var2 + 4)) = (s32) ((*((s32 *) (((s8 *) arg0) + 4))) | 1);
  }
  return -1;
}
