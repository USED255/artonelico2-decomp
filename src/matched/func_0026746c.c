
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
M2C_UNK func_00126138(void *);
M2C_UNK func_0017e7b8();
M2C_UNK func_0017e940(s32);
void func_0026746c(s32 arg0, void *arg1)
{
  s16 temp_s0;
  s16 temp_s1;
  void *new_var;
  if (arg1 != 0)
  {
    temp_s1 = *((s16 *) (((s8 *) arg1) + 0xC));
    new_var = arg1;
    temp_s0 = *((s16 *) (((s8 *) arg1) + 0xE));
    *((s16 *) (((s8 *) new_var) + 0xC)) = 0x140;
    *((s16 *) (((s8 *) new_var) + 0xE)) = 0x160;
    func_0017e7b8();
    func_00126138(new_var);
    *((s16 *) (((s8 *) new_var) + 0xC)) = temp_s1;
 do { *((s16 *) (((s8 *) new_var) + 0xE)) = temp_s0; func_0017e940(arg0); } while (0);
  }
}
