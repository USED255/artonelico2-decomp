
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
M2C_UNK func_001c4790();
void func_001cc0a0(void *arg0)
{
  int new_var;
  new_var = 0xF8;
  if (arg0 != 0)
  {
    if ((((unsigned int) (((s64) ((*((s64 *) (((s8 *) arg0) + new_var))) << 0x1A)) >> 0x20)) & 0xF) == 1)
    {
      func_001c4790();
    }
  }
}
