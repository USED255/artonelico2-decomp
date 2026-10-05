
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
void func_002791f0(void *arg0, s32 arg1)
{
  s8 *new_var;
  s32 temp_t6;
  s8 *new_var2;
  s32 temp_t6_2;
  new_var = (s8 *) arg0;
  new_var2 = new_var;
  temp_t6 = *((s32 *) (new_var2 + 0x100));
  if (!(temp_t6 & 0x20))
  {
    temp_t6_2 = temp_t6 & (~0x10);
    temp_t6_2 = temp_t6_2 | ((arg1 & 1) * 0x10);
    *((u32 *) (new_var + 0x100)) = temp_t6_2;
    if (!(temp_t6_2 & 0x10))
    {
      *((s32 *) (((s8 *) arg0) + 0x100)) = (s32) (temp_t6_2 & (~3));
    }
  }
}
