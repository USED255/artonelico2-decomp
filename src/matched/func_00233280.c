
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
s32 func_001e41b8(M2C_UNK);
void *func_001e5c4c(M2C_UNK, M2C_UNK);
M2C_UNK func_00228938(s32, M2C_UNK *, M2C_UNK);
s32 func_00229748(s32, s32);
extern s32 D_007AF2D0;
extern M2C_UNK D_00970DC8;
extern M2C_UNK D_00BB9298;
void func_00233280(void)
{
  s16 temp_v0_2;
  int new_var2;
  s32 var_a1;
  s8 *new_var;
  void *temp_v0;
  new_var = (s8 *) (&D_00BB9298);
  if ((((*((s8 *) (new_var + 0xEC))) != 0) || ((*((s8 *) (new_var + 0x104))) != 0)) && (func_001e41b8(0x18) == 0))
  {
    temp_v0 = func_001e5c4c(0, 1);
    if (temp_v0 != 0)
    {
      new_var2 = D_007AF2D0 + 0xBF110;
      temp_v0_2 = *((s16 *) (((s8 *) temp_v0) + 0x14A));
      var_a1 = 0;
      if (temp_v0_2 != 0)
      {
        var_a1 = temp_v0_2 != 2;
      }
      if (func_00229748(new_var2, var_a1) >= 3)
      {
        func_00228938(D_007AF2D0 + 0xC08C0, &D_00970DC8, 0x96);
      }
    }
  }
}
