
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
M2C_UNK baseelf_10(M2C_UNK *);
M2C_UNK baseelf_4();
M2C_UNK baseelf_7();
M2C_UNK baseelf_87(M2C_UNK *);
M2C_UNK baseelf_9(M2C_UNK *);
M2C_UNK func_0013c544();
M2C_UNK func_0013f8dc();
M2C_UNK func_0013fec0(M2C_UNK *);
s16 func_00140034();
s16 func_0026bd30(void *);
s32 func_0026d50c();
M2C_UNK func_0026e0e4();
M2C_UNK func_0026e140();
M2C_UNK func_0026f610(M2C_UNK *);
M2C_UNK func_0027cd10(M2C_UNK *, void *);
extern void *D_007FE564;
extern M2C_UNK D_00A504E0;
extern s32 D_00A50550;
void func_0026f138(void)
{
  M2C_UNK *new_var;
  void *temp_s0;
  void *temp_s0_2;
  *((s64 *) (((s8 *) D_007FE564) + 0x558)) = (s64) ((*((s64 *) (((s8 *) D_007FE564) + 0x558))) & (~2));
  new_var = &D_00A504E0;
  func_0026e0e4();
  *((s16 *) (((s8 *) D_007FE564) + 0x542)) = 1;
  baseelf_4();
  func_0013f8dc();
  loop_1:
  baseelf_7();

  if (!(D_00A50550 & 4))
  {
    temp_s0 = D_007FE564;
    *((s16 *) (((s8 *) temp_s0) + 0x548)) = func_0026bd30(temp_s0 + 0xB0);
    temp_s0_2 = D_007FE564;
    *((s16 *) (((s8 *) temp_s0_2) + 0x54C)) = func_00140034();
    if (func_0026d50c() != 1)
    {
      func_0026e140();
      func_0026f610(new_var);
      baseelf_87(new_var);
      func_0027cd10(new_var, D_007FE564 + 0xB0);
      func_0013fec0(new_var);
      baseelf_9(new_var);
      baseelf_10(new_var);
      goto loop_1;
    }
  }
  baseelf_4();
  func_0013c544();
}
