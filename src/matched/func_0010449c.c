
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
extern volatile char D_00A38A88;
void func_0010449c(s32 arg0)
{
  s8 *new_var3;
  void *temp_a0;
  void *new_var4;
  int new_var;
  s8 *new_var2;
  new_var = arg0;
  new_var *= 0x18;
  temp_a0 = new_var + (&D_00A38A88);
  new_var4 = temp_a0;
  new_var3 = ((s8 *) temp_a0) + 0xC;
  new_var2 = (s8 *) new_var4;
  *((s32 *) (new_var2 + 0xC)) = (s32) (0x10000 | (*((s32 *) new_var3)));
}
