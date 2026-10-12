
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
extern M2C_UNK D_005856D0;
void func_00140ef0(void)
{
  s32 temp_t7;
  s32 var_t1;
  M2C_UNK *new_var;
  if (new_var || var_t1)
  {
    var_t1 = 2;
  }
  else
  {
    var_t1 = 2;
  }
  do
  {
    new_var = &D_005856D0;
    temp_t7 = var_t1 * 0x30;
    *((s16 *) (((s8 *) (temp_t7 + (*((s32 *) (((s8 *) new_var) + 0))))) + 8)) = -1;
    var_t1 += 1;
    *((s16 *) (((s8 *) (temp_t7 + (*((s32 *) (((s8 *) new_var) + 0x2C))))) + 8)) = -1;
    *((s16 *) (((s8 *) (temp_t7 + (*((s32 *) (((s8 *) new_var) + 0x58))))) + 8)) = -1;
  }
  while (var_t1 < 4);
  *((s16 *) (((s8 *) (*((void **) (((s8 *) new_var) + 0xDC)))) + 0xC8)) = -1;
}
