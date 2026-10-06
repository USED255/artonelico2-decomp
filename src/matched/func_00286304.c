
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
M2C_UNK baseelf_153(s32, s32, s16, s16);
M2C_UNK func_0011299c(u8);
M2C_UNK func_0013e2fc(void *);
M2C_UNK func_002864cc(s32, void *);
extern M2C_UNK D_0054AA00;
void func_00286304(s32 arg0, void *arg1)
{
  u8 temp_t7;
  void *temp_t6;
  s8 *new_var;
  M2C_UNK *new_var2;
  new_var = (s8 *) arg1;
  if ((*((s8 *) (new_var + 0x32))) != (-1))
  {
    func_0013e2fc(arg1);
    temp_t7 = *((u8 *) (new_var + 0));
    if (temp_t7 != 0)
    {
      func_0011299c(temp_t7);
      new_var2 = &D_0054AA00;
      temp_t6 = new_var2;
      temp_t6 = ((*((s16 *) (new_var + 0x30))) * 0xC) + temp_t6;
      baseelf_153(arg0, *((s32 *) (((s8 *) temp_t6) + 0)), *((s16 *) (((s8 *) temp_t6) + 8)), *((s16 *) (((s8 *) temp_t6) + 0xA)));
      func_0011299c(0x80U);
      if (((*((s8 *) (new_var + 0x32))) != (-1)) && ((*((s16 *) (new_var + 0x30))) == 0xA0))
      {
        func_002864cc(arg0, arg1 + 6);
      }
    }
  }
}
