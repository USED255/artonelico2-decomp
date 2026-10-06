
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
M2C_UNK baseelf_87(s32);
M2C_UNK func_0014d22c(s16);
M2C_UNK func_0017b508(void *, s16, s16, M2C_UNK);
extern char D_0079C7C0;
void func_0019ef4c(s32 arg0, void *arg1, s32 arg2)
{
  s16 temp_t5;
  void *temp_t5_2;
  void *temp_t7;
  temp_t5 = *((s16 *) (((s8 *) arg1) + 0));
  if ((temp_t5 != (-1)) && ((*((s16 *) (((s8 *) arg1) + 2))) == arg2))
  {
    temp_t5_2 = (temp_t5 << 5) + (&D_0079C7C0);
    if ((*((s16 *) (((s8 *) arg1) + 4))) == (*((s16 *) (((s8 *) temp_t5_2) + 0xC))))
    {
      func_0014d22c(*((s16 *) (((s8 *) temp_t5_2) + 0xA)));
    }
    baseelf_87(arg0);
    temp_t7 = ((*((s16 *) (((s8 *) arg1) + 0))) << 5) + (&D_0079C7C0);
    func_0017b508(arg1 + 0x10, *((s16 *) (((s8 *) temp_t7) + 0)), *((s16 *) (((s8 *) temp_t7) + 2)), 0);
    *((s16 *) (((s8 *) arg1) + 4)) = (s16) (((u16) (*((s16 *) (((s8 *) arg1) + 4)))) + 1);
  }
}
