
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
M2C_UNK func_00125d18(void *);
M2C_UNK func_0013e2fc();
void func_001d6704(void *arg0)
{
  void *var_a0;
  if ((*((void **) (((s8 *) arg0) + 8))) != 0)
  {
    func_0013e2fc();
    var_a0 = arg0 + 0x20;
    if (((u32) ((((int) (((s64) ((*((s64 *) (((s8 *) (*((void **) (((s8 *) arg0) + 8)))) + 0xF8))) << 0x1E)) >> 0x20)) & 0xF) - 1)) < 2U)
    {
      func_00125d18(var_a0);
    }
  }
  else
    if ((*((s32 *) (((s8 *) arg0) + 0xC))) != ((char) 0))
  {
    func_0013e2fc();
    var_a0 = arg0 + 0x20;
    func_00125d18(var_a0);
  }
}
