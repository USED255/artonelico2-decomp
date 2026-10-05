
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
u8 func_0018f0f0(s8, s8);
void func_00283b90(void *arg0)
{
  u8 temp_v0;
  u8 new_var;
  *((u8 *) (((s8 *) arg0) + 0xD04)) = func_0018f0f0(*((s8 *) (((s8 *) arg0) + 0xAA0)), *((s8 *) (((s8 *) arg0) + 0xB40)));
  temp_v0 = func_0018f0f0(*((s8 *) (((s8 *) arg0) + 0xAF0)), *((s8 *) (((s8 *) arg0) + 0xB90)));
  *((u8 *) (((s8 *) arg0) + 0xD05)) = (new_var = temp_v0);
  *((u8 *) (((s8 *) arg0) + 0xAF1)) = new_var;
  *((u8 *) (((s8 *) arg0) + 0xAA1)) = (u8) (*((u8 *) (((s8 *) arg0) + 0xD04)));
}
