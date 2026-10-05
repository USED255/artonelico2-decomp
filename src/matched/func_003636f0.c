
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
s64 func_0036b090(s32, s16, M2C_UNK, M2C_UNK);
void func_003636f0(void *arg0, M2C_UNK arg1, M2C_UNK arg2)
{
  s64 temp_v0;
  u16 new_var2;
  s8 *new_var;
  u16 var_t7;
  temp_v0 = func_0036b090(*((s32 *) (((s8 *) arg0) + 0x54)), *((s16 *) (((s8 *) arg0) + 0xE)), arg1, arg2);
  if (temp_v0 == (-1))
  {
    new_var2 = *((u16 *) (((s8 *) arg0) + 0xC));
    var_t7 = new_var2 & 0xEFFF;
  }
  else
  {
    *((s32 *) (((s8 *) arg0) + 0x50)) = (s32) (((s64) (temp_v0 << 0x20)) >> 0x20);
    var_t7 = (*((u16 *) (((s8 *) arg0) + 0xC))) | 0x1000;
  }
  new_var = ((s8 *) arg0) + 0xC;
  *((u16 *) new_var) = var_t7;
}
