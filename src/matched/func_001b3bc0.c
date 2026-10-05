
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
M2C_UNK func_001c5aec(s32);
s32 func_001cba78(s32);
extern M2C_UNK D_00BC6790;
void func_001b3bc0(s32 arg0)
{
  s32 temp_t7;
  void *temp_s0;
  M2C_UNK *new_var;
  new_var = &D_00BC6790;
  temp_t7 = arg0 * 4;
  temp_s0 = new_var;
  temp_s0 = (temp_t7 + temp_s0) + 0x2070;
  temp_t7 = *((s32 *) (((s8 *) temp_s0) + 8));
  if ((temp_t7 != 0) && (func_001cba78(temp_t7) != 0))
  {
    func_001c5aec(*((s32 *) (((s8 *) temp_s0) + 8)));
  }
}
