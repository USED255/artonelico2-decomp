
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
s32 func_00105160(s16);
M2C_UNK func_00105528(s32);
extern volatile unsigned char D_00A38A88;
void func_00105670(s16 arg0)
{
  volatile unsigned char *new_var2;
  int new_var;
  s32 temp_v0;
  new_var2 = &D_00A38A88;
  if ((*((s16 *) (((s8 *) ((arg0 * 0x18) + new_var2)) + 0xA))) >= 0)
  {
    temp_v0 = func_00105160(arg0);
    new_var = temp_v0 >= 0;
    if (new_var)
    {
      func_00105528(temp_v0);
    }
  }
}
