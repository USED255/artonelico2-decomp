
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
M2C_UNK func_00184efc(s32, s32, s32);
extern M2C_UNK D_0061D7E0;
void baseelf_69(void *arg0, s32 arg1)
{
  s16 temp_t6;
  s32 temp_a2;
  s32 var_a1;
  s8 *new_var;
  s8 temp_t6_2;
  new_var = &D_0061D7E0;
  temp_t6 = *((s16 *) (((s8 *) (*((void **) (((s8 *) arg0) + 0)))) + 0xE));
  if (temp_t6 >= 0)
  {
    temp_t6_2 = *((temp_t6 * 0x60) + new_var);
    var_a1 = -1;
    switch (temp_t6_2)
    {
      case 6:
        var_a1 = 3;
        break;

      case 0:
        var_a1 = 1;
        break;

    }

    if (var_a1 >= 0)
    {
      new_var = (s8 *) arg0;
      temp_a2 = *((s32 *) (new_var + 0x10));
      if (temp_a2 >= 0)
      {
        func_00184efc(arg1 + 0x2360, var_a1, temp_a2);
      }
    }
  }
}
