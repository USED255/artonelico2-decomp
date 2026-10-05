
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
M2C_UNK func_001357f4(s16);
M2C_UNK func_001371b0();
s16 func_001db350(s16);
extern M2C_UNK D_00AF0850;
void func_0028559c(void *arg0)
{
  s16 temp_s1;
  s16 var_v0;
  M2C_UNK *new_var;
  var_v0 = func_001db350(*((s16 *) (((s8 *) arg0) + 0x2564)));
  if (((*((s16 *) (((s8 *) arg0) + 0))) != 0) && ((*((s8 *) (((s8 *) arg0) + 0x25B7))) == 4))
  {
    var_v0 = (((*((s16 *) (((s8 *) arg0) + 0x2564))) ^ 1) == 0) ? (0xE2) : (var_v0);
  }
  temp_s1 = *((s16 *) (((s8 *) arg0) + 0x2562));
  if (temp_s1 != var_v0)
  {
    *((s16 *) (((s8 *) arg0) + 0x2562)) = var_v0;
    if (temp_s1 != (-1))
    {
      func_001371b0();
    }
    func_001357f4(*((s16 *) (((s8 *) arg0) + 0x2562)));
    if (temp_s1 != (-1))
    {
      new_var = &D_00AF0850;
      *((s32 *) (((s8 *) new_var) + 0xC)) = 0;
      *((s32 *) (((s8 *) new_var) + 0x10)) = 4;
    }
  }
}
