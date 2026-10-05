
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
M2C_UNK baseelf_104(s32);
void func_0016f02c(void *arg0)
{
  s32 temp_t7;
  s32 temp_t7_2;
  temp_t7_2 = *((s32 *) (((s8 *) arg0) + 0xE010));
  temp_t7 = temp_t7_2;
  if (temp_t7 != 0)
  {
    baseelf_104(temp_t7);
    *((s32 *) (((s8 *) arg0) + 0xE010)) = 0;
  }
  temp_t7_2 = *((s32 *) (((s8 *) arg0) + 0xEE2C));
  if (temp_t7_2 != 0)
  {
    baseelf_104(temp_t7_2);
    *((s32 *) (((s8 *) arg0) + 0xEE2C)) = 0;
  }
}
