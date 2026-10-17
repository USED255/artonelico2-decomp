
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
M2C_UNK func_00244604(s16, s16, s16, s16);
M2C_UNK func_002446d0(s16);
extern M2C_UNK D_007E8EB8;
void func_00243374(void *arg0)
{
  s16 temp_a1;
  s16 temp_t6;
  M2C_UNK *new_var;
  void *temp_t7;
  temp_t6 = *((s16 *) (((s8 *) arg0) + 0xD92));
  if (temp_t6 != (-1))
  {
    new_var = &D_007E8EB8;
    if ((*((s16 *) ((((s8 *) new_var) + (temp_t6 * 0x16)) + 4))) == (-1))
    {
      func_002446d0(*((s16 *) (((s8 *) arg0) + 0xD90)));
    }
    temp_a1 = *((s16 *) (((s8 *) arg0) + 0xD92));
    temp_t7 = (s32) (((s8 *) new_var) + (temp_a1 * 0x16));
    func_00244604(*((s16 *) (((s8 *) arg0) + 0xD90)), temp_a1, *((s16 *) (((s8 *) temp_t7) + 2)), *((s16 *) (((s8 *) temp_t7) + 4)));
    *((s8 *) (((s8 *) arg0) + 0xF7E)) = 1;
  }
}
