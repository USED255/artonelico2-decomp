
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
M2C_UNK LibcStdio_32(M2C_UNK *);
M2C_UNK func_0013535c();
M2C_UNK func_0013566c();
M2C_UNK func_001357b8(s32);
M2C_UNK func_0025e4dc(s32);
extern M2C_UNK D_00583E50;
extern M2C_UNK D_00916DC0;
extern M2C_UNK D_00AF0850;
extern s32 D_00AF085C;
void func_001357f4(s32 arg0)
{
  void *temp_t6;
  s8 *new_var;
  *((u32 *) (((s8 *) (&D_00AF0850)) + 0)) = arg0;
  if (arg0 < 0)
  {
    func_0013566c();
  }
  else
  {
    if (arg0 < 0x16A)
    {
      new_var = &D_00583E50;
      temp_t6 = (arg0 * 0x10) + new_var;
      new_var = (s8 *) (&D_00AF0850);
      if (((*((s32 *) (new_var + 0x24))) != (*((s16 *) (((s8 *) temp_t6) + 4)))) || ((*((s32 *) (new_var + 0x28))) != (*((s16 *) (((s8 *) temp_t6) + 6)))))
      {
        LibcStdio_32(&D_00916DC0);
        func_0013566c();
        *((u32 *) (new_var + 0)) = arg0;
      }
      func_001357b8(arg0);
      func_0025e4dc(arg0);
    }
    func_0013535c();
  }
  D_00AF085C = 0x80;
}
