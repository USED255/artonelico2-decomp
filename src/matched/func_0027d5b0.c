
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
M2C_UNK func_00144390();
M2C_UNK func_00145324(void *, s16, s16);
extern M2C_UNK D_0054AA00;
void func_0027d5b0(void *arg0)
{
  s8 *new_var;
  func_00144390();
  new_var = (s8 *) (&D_0054AA00);
  func_00145324(arg0, *((s16 *) (new_var + 0x140)), *((s16 *) (new_var + 0x142)));
  *((s8 *) (((s8 *) arg0) + 0x1FC7)) = 0;
  *((s8 *) (((s8 *) arg0) + 0x1FC5)) = 2;
  *((s8 *) (((s8 *) arg0) + 0x1FC6)) = 4;
  *((s32 *) (((s8 *) arg0) + 0x202C)) = (s32) ((*((s32 *) (((s8 *) arg0) + 0x202C))) & 0xFEFFFFFF);
}
