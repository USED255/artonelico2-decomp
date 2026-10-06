
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
M2C_UNK func_0010838c(s32);
extern unsigned char D_009E3900;
void func_00108324(void)
{
  s32 temp_t7;
  s32 var_s0;
  void *temp_t6;
  int new_var;
  var_s0 = 0;
  do
  {
    temp_t6 = (var_s0 * 0x14) + (&D_009E3900);
    if ((*((s32 *) (((s8 *) temp_t6) + 0))) >= 0)
    {
      new_var = 0x10;
      temp_t7 = (*((s32 *) (((s8 *) temp_t6) + 0x10))) - 1;
      *((u32 *) (((s8 *) temp_t6) + new_var)) = temp_t7;
      if (temp_t7 <= 0)
      {
        func_0010838c(var_s0);
      }
    }
    var_s0 += 1;
  }
  while (var_s0 < 4);
}
