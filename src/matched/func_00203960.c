
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
M2C_UNK func_002038f4(void *);
M2C_UNK func_002039e4(s32);
void func_00203960(s32 arg0)
{
  int new_var;
  s16 temp_t7;
  u16 temp_t7_2;
  void *temp_s0;
  temp_s0 = arg0 + 0x90;
  func_002038f4(temp_s0 + ((*((s16 *) (((s8 *) temp_s0) + 0x784))) * 0x60));
  temp_t7 = (*((s16 *) (((s8 *) temp_s0) + 0x784)) = ((u16) (*((s16 *) (((s8 *) temp_s0) + 0x784)))) + 1);
  if (temp_t7 >= 0x14)
  {
    *((s16 *) (((s8 *) temp_s0) + 0x784)) = 0;
  }
  new_var = 0;
  temp_t7_2 = (*((u16 *) (((s8 *) temp_s0) + 0x780)) = (*((u16 *) (((s8 *) temp_s0) + 0x780))) - 1);
  if (((s16) temp_t7_2) != new_var)
  {
    func_002039e4(arg0);
  }
}
