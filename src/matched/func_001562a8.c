
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
M2C_UNK func_00155d04();
M2C_UNK func_00155ddc(void *, M2C_UNK);
M2C_UNK func_00157a2c(void *);
void func_001562a8(void *arg0, M2C_UNK arg1, s32 arg2, s32 arg3)
{
  func_00155d04();
  func_00155ddc(arg0, arg1);
  *((u32 *) (((s8 *) arg0) + 0x30)) = (*((u32 *) (((s8 *) arg0) + 0x144)) = arg2);
  *((u32 *) (((s8 *) arg0) + 0x68)) = arg3;
  if (((u32) (arg3 - 1)) < 2U)
  {
    func_00157a2c(arg0);
  }
}
