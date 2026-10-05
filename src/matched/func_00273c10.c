
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
s32 func_0011f3c0(void *);
M2C_UNK func_0026b020(void *);
M2C_UNK func_00273dd8(void *, M2C_UNK);
s32 func_00273c10(void *arg0)
{
  s16 temp_t5;
  s32 temp_s1;
  s32 temp_t7;
  s32 temp_v0;
  s32 var_v0;
  if ((*((s32 *) (((s8 *) arg0) + 0x42C))) & 1)
  {
    func_0026b020(arg0 + 0x41C);
    temp_v0 = func_0011f3c0(arg0 + 0xA);
    temp_t5 = *((s16 *) (((s8 *) arg0) + 0x410));
    temp_s1 = temp_v0;
    temp_t7 = ((u32) (temp_v0 - 1)) < 2U;
    if ((*((s16 *) (((s8 *) arg0) + 0x42A))) != temp_t5)
    {
      *((s16 *) (((s8 *) arg0) + 0x42A)) = temp_t5;
    }
    if (temp_t7 != 0)
    {
      func_00273dd8(arg0, 0);
      var_v0 = temp_s1;
    }
    var_v0 = temp_s1;
  }
  else
  {
    var_v0 = 5;
  }
  return var_v0;
}
