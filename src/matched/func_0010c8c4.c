
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
M2C_UNK func_0010c004();
extern M2C_UNK D_00A50600;
void func_0010c8c4(s32 arg0)
{
  s32 temp_a0;
  s32 temp_a0_3;
  s32 temp_a0_4;
  s32 temp_a0_5;
  void *temp_s0;
  temp_s0 = (M2C_UNK *) ((u8 *) (&D_00A50600) + arg0 * 0x48);
  if (arg0 >= 0xA)
  {
    func_0010c004();
    temp_a0 = *((s32 *) (((s8 *) temp_s0) + 0xC));
    if (temp_a0 != 0)
    {
      baseelf_104(temp_a0);
      *((s32 *) (((s8 *) temp_s0) + 0xC)) = 0;
    }
    arg0 = *((s32 *) (((s8 *) temp_s0) + 0x10));
    if (arg0 != 0)
    {
      baseelf_104(arg0);
      *((s32 *) (((s8 *) temp_s0) + 0x10)) = 0;
    }
    temp_a0_3 = *((s32 *) (((s8 *) temp_s0) + 0x14));
    if (temp_a0_3 != 0)
    {
      baseelf_104(temp_a0_3);
      *((s32 *) (((s8 *) temp_s0) + 0x14)) = 0;
    }
    temp_a0_4 = *((s32 *) (((s8 *) temp_s0) + 0x20));
    if (temp_a0_4 != 0)
    {
      baseelf_104(temp_a0_4);
      *((s32 *) (((s8 *) temp_s0) + 0x20)) = 0;
    }
    temp_a0_5 = *((s32 *) (((s8 *) temp_s0) + 0x24));
    if (temp_a0_5 != 0)
    {
      baseelf_104(temp_a0_5);
      *((s32 *) (((s8 *) temp_s0) + 0x24)) = 0;
    }
    *((s8 *) (((s8 *) temp_s0) + 0x3D)) = 0;
    *((s32 *) (((s8 *) temp_s0) + 0x18)) = 0;
    *((s32 *) (((s8 *) temp_s0) + 0x1C)) = 0;
    *((s8 *) (((s8 *) temp_s0) + 0x40)) = 0;
  }
}
