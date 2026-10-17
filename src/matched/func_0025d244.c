
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
s32 func_00144440(s32);
M2C_UNK func_00145330(s32, M2C_UNK);
M2C_UNK func_0014e800(s16);
M2C_UNK func_0014e9f8();
extern M2C_UNK D_007F68E0;
s32 func_0025d244(void *arg0)
{
  s32 temp_s1;
  s32 temp_s2;
  int new_var;
  s32 temp_v0;
  void *temp_s0;
  void *temp_t5;
  temp_s2 = arg0 + 0x4E8;
  temp_v0 = func_00144440(temp_s2);
  temp_s1 = temp_v0;
  temp_t5 = *((void **) (((s8 *) arg0) + 0xFC8));
  *((s32 *) (((s8 *) temp_t5) + 0x70)) = 0x411;
  temp_s0 = ((*((s16 *) (((s8 *) (((*((s16 *) (((s8 *) arg0) + 0x902))) * 2) + arg0)) + 0xF94))) * 0x10) + ((u8 *) (&D_007F68E0));
  *((s32 *) (((s8 *) temp_t5) + 0x48)) = (s32) (*((s32 *) (((s8 *) temp_s0) + 0)));
  *((s32 *) (((s8 *) temp_t5) + 0x78)) = (s32) (*((s32 *) (((s8 *) temp_s0) + 8)));
  new_var = 1;
  if (temp_v0 == new_var)
  {
    func_0014e9f8();
    func_0014e800(*((s16 *) (((s8 *) temp_s0) + 0xC)));
    func_00145330(temp_s2, new_var);
  }
  return ((2 ^ temp_s1) != 0) ? (-new_var) : (1);
}
