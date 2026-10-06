
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
s32 func_001dfa1c();
extern unsigned char D_00BFD378;
void func_001dfce4(void)
{
  s32 temp_v0;
  int new_var;
  void *temp_t5;
  new_var = 1;
  temp_v0 = func_001dfa1c();
  if (temp_v0 != (-new_var))
  {
    temp_t5 = (temp_v0 * 0x34) + (&D_00BFD378);
    *((s16 *) (((s8 *) temp_t5) + 2)) = (s16) (((*((s16 *) (((s8 *) temp_t5) + 2))) + new_var) % 2);
  }
}
