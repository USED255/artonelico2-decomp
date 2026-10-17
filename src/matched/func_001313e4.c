
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
M2C_UNK baseelf_140(s32);
M2C_UNK func_0010e504(s32, M2C_UNK);
M2C_UNK func_00166ffc(s32 *, void *, s32);
extern M2C_UNK D_00AD7F40;
void func_001313e4(s32 *arg0, void *arg1)
{
  void *temp_t6;
  int new_var;
  baseelf_140((void *) ((s8 *) arg0 + 0x10));
  new_var = 0x34;
  temp_t6 = *(*((void ***) (((s8 *) arg1) + 8)));
  if ((*((s16 *) (((s8 *) (((*((s16 *) (((s8 *) temp_t6) + 8))) * 0x14) + (*((s32 *) (((s8 *) temp_t6) + 0))))) + 0xE))) >= 0x100)
  {
    if ((*((s32 *) (((s8 *) (&D_00AD7F40)) + new_var))) != 0)
    {
    }
    else
    {
      func_0010e504(*arg0, 1);
    }
    func_00166ffc(arg0, arg1, *((s32 *) (((s8 *) arg1) + 4)));
    if ((*((s32 *) (((s8 *) (&D_00AD7F40)) + new_var))) == 1)
    {
      func_0010e504(*arg0, 0);
      return;
    }
    return;
  }
  func_00166ffc(arg0, arg1, *((s32 *) (((s8 *) arg1) + 4)));
}
