
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
M2C_UNK func_001b3904();
M2C_UNK func_001b3ce0();
M2C_UNK func_001b3dd0();
M2C_UNK func_001b5984(s32);
M2C_UNK func_001b5a70(s32, s32);
M2C_UNK func_001b5cd4(s32);
s32 func_001d7b04();
M2C_UNK func_001d8318(s32, s32);
extern M2C_UNK D_007A0A00;
void func_001d7db0(s32 arg0, s32 arg1)
{
  s32 temp_s2;
  s32 temp_v0;
  M2C_UNK *new_var;
  new_var = (s8 *) (&D_007A0A00) + arg1 * 0x34;
  temp_s2 = *((s32 *) (((s8 *) new_var) + 0x30));
  temp_v0 = func_001d7b04();
  if ((temp_v0 != 0) && (temp_s2 != 0))
  {
    func_001b5984(arg1);
    func_001b3904();
    func_001d8318(temp_s2, temp_v0);
    func_001b5a70(temp_v0 + 4, arg1);
    func_001b5cd4(temp_v0);
    func_001b3ce0();
    func_001b3dd0();
  }
}
