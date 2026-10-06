
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
M2C_UNK baseelf_117(void *);
extern u8 D_00AD7FFC;
void func_001157f0(void *arg0, void *arg1)
{
  s32 temp_s2;
  int new_var;
  s32 temp_t5;
  s32 temp_t6;
  temp_s2 = *((s32 *) (((s8 *) arg0) + 0x18));
  baseelf_117(arg1);
  temp_t6 = *((s32 *) (((s8 *) arg0) + 0x10));
  temp_t5 = temp_t6 >> 8;
  new_var = (4 * temp_t5) * 4;
  if (temp_t6 & 0xFF)
  {
    *((s16 *) (((s8 *) arg1) + 0x1E)) = (s16) ((u8) (*((s32 *) (((s8 *) arg0) + 0x10))));
  }
  if (temp_t5 > 0)
  {
    *((s16 *) (((s8 *) arg1) + 0x1C)) = (s16) new_var;
  }
  *((u32 *) (((s8 *) arg1) + 0)) = temp_s2;
  *((u8 *) (((s8 *) arg1) + 0x13)) = (u8) D_00AD7FFC;
}
