
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
M2C_UNK func_00155b70();
M2C_UNK func_00156e20(void *);
M2C_UNK func_001579d8();
M2C_UNK func_0017ccb8(s32);
void baseelf_76(void *arg0)
{
  s32 var_a0;
  s32 var_s0;
  s32 var_s0_2;
  var_s0 = 0;
  do
  {
    func_0017ccb8((arg0 + (var_s0 * 0x7C0)) + 0x1D740);
    var_s0 += 1;
  }
  while (var_s0 < 3);
  if ((*((s8 *) (((s8 *) arg0) + 0x20784))) != 0)
  {
    *((s8 *) (((s8 *) arg0) + 0x20784)) = 0;
    var_s0_2 = 0;
    if ((*((s32 *) (((s8 *) arg0) + 0x20780))) > 0)
    {
      var_a0 = 0 * 0x280;
      do
      {
        var_a0 = var_s0_2 * 0x280;
        func_00156e20((arg0 + var_a0) + 0x1EE80);
        var_s0_2 += 1;
      }
      while (var_s0_2 < (*((s32 *) (((s8 *) arg0) + 0x20780))));
    }
    *((s32 *) (((s8 *) arg0) + 0x20780)) = 0;
    func_001579d8();
    func_00155b70();
  }
}
