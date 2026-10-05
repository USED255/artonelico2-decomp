
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
M2C_UNK func_0011f004();
M2C_UNK func_0011f090(void *, M2C_UNK);
void func_0025a204(void *arg0)
{
  *((s32 *) (((s8 *) arg0) + 0x30)) = -1;
  func_0011f004();
  func_0011f090(arg0, 0x76);
  *((s32 *) (((s8 *) arg0) + 0x3C)) = (*((s32 *) (((s8 *) arg0) + 0x34)) = 0);
  *((s32 *) (((s8 *) arg0) + 0x38)) = 2;
}
