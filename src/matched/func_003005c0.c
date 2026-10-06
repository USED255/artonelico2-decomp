
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
long func_003005c0(void *arg0, void *arg1)
{
  void *new_var;
  if (arg1)
  {
    *((s64 *) (((s8 *) arg0) + 0x158)) = (s64) (*((s64 *) (((s8 *) arg1) + 0)));
  }
  else
  {
    *((s64 *) (((s8 *) arg0) + 0x158)) = (s64) (*((s64 *) (((s8 *) arg1) + 0)));
  }
 do { new_var = arg1; *((s64 *) (((s8 *) arg0) + 0x160)) = (s64) (*((s64 *) (((s8 *) new_var) + 8))); } while (0);
}
