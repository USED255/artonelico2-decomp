
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
M2C_UNK func_0017a410(s32);
M2C_UNK func_0017a584(s32, M2C_UNK, M2C_UNK, void *);
s32 func_001e86dc();
void func_001e8854(s32 a0, void *arg1, M2C_UNK arg2)
{
  s32 temp_v0;
  s32 var_s0;
  if ((*((s32 *) (((s8 *) arg1) + 0xA0))) == 0)
  {
    temp_v0 = func_001e86dc();
    var_s0 = temp_v0;
    if (temp_v0 != 0)
    {
      if (temp_v0)
      {
        goto block_4;
      }
      else
      {
        goto block_4;
      }
    }
  }
  else
  {
    var_s0 = *((s32 *) (((s8 *) arg1) + 0xA0));
    block_4:
    func_0017a410(var_s0);

    func_0017a584(var_s0, 2, arg2, arg1);
    *((u32 *) (((s8 *) arg1) + 0xA0)) = var_s0;
  }
}
