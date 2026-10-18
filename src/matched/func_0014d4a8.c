
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
M2C_UNK func_0014d3e4(s16);
M2C_UNK func_0014d540(s32);
extern M2C_UNK D_00AF29A8;
void func_0014d4a8(void)
{
  s16 temp_t7;
  s16 temp_t7_2;
  s32 var_s1;
  void *temp_s0;
  var_s1 = 0;
  do
  {
    temp_s0 = (void *) ((char *) (&D_00AF29A8) + var_s1 * 4);
    if ((*((s16 *) (((s8 *) temp_s0) + 0))) >= 0)
    {
      temp_t7 = (*((u16 *) (((s8 *) temp_s0) + 2))) - 1;
      *((u16 *) (((s8 *) temp_s0) + 2)) = (u16) ((*((u16 *) (((s8 *) temp_s0) + 2))) - 1);
      if (temp_t7 <= 0)
      {
        func_0014d540(var_s1);
        if ((var_s1 + 1) < 0xA)
        {
          temp_t7_2 = *((s16 *) (((s8 *) temp_s0) + 4));
          if (temp_t7_2 >= 0)
          {
            func_0014d3e4(temp_t7_2);
          }
        }
      }
    }
    var_s1 += 1;
  }
  while (var_s1 < 0xA);
}
