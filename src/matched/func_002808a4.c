
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
void *baseelf_63(s16);
M2C_UNK func_0027a0d8(void *, s8);
void func_002808a4(void *arg0)
{
  s16 *new_var;
  s8 temp_t7;
  new_var = (s16 *) (((s8 *) baseelf_63(*((s16 *) (((s8 *) arg0) + 0x1388)))) + 0xE);
  temp_t7 = (*((s8 *) (((s8 *) arg0) + 0x1392)) = *((s8 *) (((s8 *) (((*((s16 *) (((s8 *) (((*new_var) * 2) + arg0)) + 0x12CE))) * 0x50) + arg0)) + 0xE28)));
  func_0027a0d8(arg0 + 0x1060, temp_t7);
}
